from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import SCHEMA_VERSION, AuditFields, SchemaVersion
from ..job_control import operation_fingerprint
from ..media_security import (
    MediaProbeResult,
    MediaSecurityPolicy,
    QuarantineInspection,
    QuarantineRejectionCode,
    QuarantineStatus,
    ThreatScanResult,
)
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

QuarantineAction = Literal["created", "reused", "inspecting", "accepted", "rejected"]


@dataclass(frozen=True)
class QuarantinePersistResult:
    action: QuarantineAction
    inspection_id: str
    status: QuarantineStatus
    revision: int


class QuarantinePersistenceConflictError(PersistenceConflictError):
    """Persisted quarantine state conflicts with the requested security mutation."""


class PostgresQuarantineInspectionRepository:
    """Durable fail-closed security decisions for completed upload sessions."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"quarantine_inspections", "upload_sessions", "projects"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"quarantine persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.inspections = metadata.tables["core.quarantine_inspections"]
        self.uploads = metadata.tables["core.upload_sessions"]
        self.projects = metadata.tables["core.projects"]

    def create(self, inspection: QuarantineInspection) -> QuarantinePersistResult:
        if inspection.status is not QuarantineStatus.PENDING:
            raise QuarantinePersistenceConflictError("new quarantine inspection must be pending")
        if (
            inspection.observed_size_bytes != 0
            or inspection.detected_mime_type is not None
            or inspection.probe is not None
            or inspection.threat_scan is not None
        ):
            raise QuarantinePersistenceConflictError(
                "new quarantine inspection must not carry observation evidence"
            )

        fingerprint = self._creation_fingerprint(inspection)
        try:
            with self.engine.begin() as connection:
                project_internal_id = self._require_project(connection, inspection.project_id)
                upload_row = self._require_completed_upload(
                    connection,
                    inspection,
                    project_internal_id,
                )
                existing = self._row_by_external(connection, inspection.inspection_id)
                if existing is not None:
                    restored = self._from_row(connection, existing)
                    if self._creation_fingerprint(restored) != fingerprint:
                        raise QuarantinePersistenceConflictError(
                            "quarantine inspection identity is bound to different semantics"
                        )
                    return QuarantinePersistResult(
                        action="reused",
                        inspection_id=restored.inspection_id,
                        status=restored.status,
                        revision=restored.audit.revision,
                    )

                connection.execute(
                    insert(self.inspections).values(
                        id=uuid4(),
                        external_id=inspection.inspection_id,
                        schema_version=inspection.schema_version,
                        upload_session_id=upload_row["id"],
                        project_id=project_internal_id,
                        storage_object_external_id=inspection.storage_object_id,
                        policy=inspection.policy.model_dump(mode="json"),
                        claimed_mime_type=inspection.claimed_mime_type,
                        detected_mime_type=None,
                        expected_size_bytes=inspection.expected_size_bytes,
                        observed_size_bytes=0,
                        status=QuarantineStatus.PENDING.value,
                        rejection_codes=[],
                        probe=None,
                        threat_scan=None,
                        inspected_at=None,
                        created_at=inspection.audit.created_at,
                        updated_at=inspection.audit.updated_at,
                        created_by=inspection.audit.created_by,
                        revision=inspection.audit.revision,
                    )
                )
                return QuarantinePersistResult(
                    action="created",
                    inspection_id=inspection.inspection_id,
                    status=QuarantineStatus.PENDING,
                    revision=inspection.audit.revision,
                )
        except (QuarantinePersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise QuarantinePersistenceConflictError(
                f"database rejected quarantine inspection {inspection.inspection_id}: {exc.orig}"
            ) from exc

    def load(self, inspection_id: str) -> QuarantineInspection:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, inspection_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"quarantine inspection {inspection_id} was not found"
                )
            return self._from_row(connection, row)

    def mark_inspecting(
        self,
        inspection_id: str,
        *,
        now: datetime,
    ) -> QuarantinePersistResult:
        with self.engine.begin() as connection:
            row = self._require_for_update(connection, inspection_id)
            status = QuarantineStatus(str(row["status"]))
            if status is QuarantineStatus.INSPECTING:
                return QuarantinePersistResult(
                    action="reused",
                    inspection_id=inspection_id,
                    status=status,
                    revision=int(row["revision"]),
                )
            if status is not QuarantineStatus.PENDING:
                raise QuarantinePersistenceConflictError(
                    f"cannot start quarantine inspection while status is {status.value}"
                )
            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.inspections)
                .where(self.inspections.c.id == row["id"])
                .values(
                    status=QuarantineStatus.INSPECTING.value,
                    updated_at=now,
                    revision=revision,
                )
            )
            return QuarantinePersistResult(
                action="inspecting",
                inspection_id=inspection_id,
                status=QuarantineStatus.INSPECTING,
                revision=revision,
            )

    def finalize(self, inspection: QuarantineInspection) -> QuarantinePersistResult:
        if inspection.status not in {QuarantineStatus.ACCEPTED, QuarantineStatus.REJECTED}:
            raise ValueError("final quarantine inspection must be accepted or rejected")
        assert inspection.inspected_at is not None

        with self.engine.begin() as connection:
            row = self._require_for_update(connection, inspection.inspection_id)
            persisted = self._from_row(connection, row)
            if self._creation_fingerprint(persisted) != self._creation_fingerprint(inspection):
                raise QuarantinePersistenceConflictError(
                    "quarantine terminal evidence does not match the persisted inspection identity"
                )

            if persisted.status in {QuarantineStatus.ACCEPTED, QuarantineStatus.REJECTED}:
                if self._terminal_fingerprint(persisted) != self._terminal_fingerprint(inspection):
                    raise QuarantinePersistenceConflictError(
                        "quarantine inspection is already terminal with different evidence"
                    )
                return QuarantinePersistResult(
                    action="reused",
                    inspection_id=persisted.inspection_id,
                    status=persisted.status,
                    revision=persisted.audit.revision,
                )

            revision = int(row["revision"]) + 1
            terminal = QuarantineInspection.model_validate(
                {
                    **inspection.model_dump(mode="python"),
                    "audit": AuditFields(
                        created_at=row["created_at"],
                        updated_at=inspection.inspected_at,
                        created_by=(
                            str(row["created_by"]) if row["created_by"] is not None else None
                        ),
                        revision=revision,
                    ).model_dump(mode="python"),
                }
            )
            connection.execute(
                update(self.inspections)
                .where(self.inspections.c.id == row["id"])
                .values(
                    detected_mime_type=terminal.detected_mime_type,
                    observed_size_bytes=terminal.observed_size_bytes,
                    status=terminal.status.value,
                    rejection_codes=[code.value for code in terminal.rejection_codes],
                    probe=(terminal.probe.model_dump(mode="json") if terminal.probe else None),
                    threat_scan=(
                        terminal.threat_scan.model_dump(mode="json")
                        if terminal.threat_scan
                        else None
                    ),
                    inspected_at=terminal.inspected_at,
                    updated_at=terminal.audit.updated_at,
                    revision=revision,
                )
            )
            return QuarantinePersistResult(
                action=cast(QuarantineAction, terminal.status.value),
                inspection_id=terminal.inspection_id,
                status=terminal.status,
                revision=revision,
            )

    def _require_completed_upload(
        self,
        connection: Connection,
        inspection: QuarantineInspection,
        project_internal_id: UUID,
    ) -> RowMapping:
        row = connection.execute(
            select(self.uploads)
            .where(self.uploads.c.external_id == inspection.upload_session_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(
                f"missing upload session:{inspection.upload_session_id}"
            )
        if str(row["status"]) != "completed":
            raise QuarantinePersistenceConflictError(
                "quarantine inspection requires a completed upload session"
            )
        if row["project_id"] != project_internal_id:
            raise QuarantinePersistenceConflictError(
                "quarantine inspection project does not match upload session"
            )
        if str(row["storage_object_external_id"]) != inspection.storage_object_id:
            raise QuarantinePersistenceConflictError(
                "quarantine storage object does not match upload session"
            )
        if int(row["expected_size_bytes"]) != inspection.expected_size_bytes:
            raise QuarantinePersistenceConflictError(
                "quarantine expected size does not match upload session"
            )
        if str(row["expected_mime_type"]) != inspection.claimed_mime_type:
            raise QuarantinePersistenceConflictError(
                "quarantine claimed MIME type does not match upload session"
            )
        return row

    def _from_row(self, connection: Connection, row: RowMapping) -> QuarantineInspection:
        persisted_schema_version = int(row["schema_version"])
        if persisted_schema_version != SCHEMA_VERSION:
            raise PersistenceReferenceError(
                "unsupported quarantine inspection schema version "
                f"{persisted_schema_version}; expected {SCHEMA_VERSION}"
            )
        project_id = connection.execute(
            select(self.projects.c.external_id).where(self.projects.c.id == row["project_id"])
        ).scalar_one_or_none()
        upload_session_id = connection.execute(
            select(self.uploads.c.external_id).where(
                self.uploads.c.id == row["upload_session_id"]
            )
        ).scalar_one_or_none()
        if project_id is None or upload_session_id is None:
            raise PersistenceReferenceError("quarantine inspection references are missing")

        raw_rejections = row["rejection_codes"] or []
        raw_probe = row["probe"]
        raw_scan = row["threat_scan"]
        return QuarantineInspection(
            schema_version=cast(SchemaVersion, persisted_schema_version),
            inspection_id=str(row["external_id"]),
            upload_session_id=str(upload_session_id),
            project_id=str(project_id),
            storage_object_id=str(row["storage_object_external_id"]),
            policy=MediaSecurityPolicy.model_validate(row["policy"]),
            claimed_mime_type=str(row["claimed_mime_type"]),
            detected_mime_type=(
                str(row["detected_mime_type"])
                if row["detected_mime_type"] is not None
                else None
            ),
            expected_size_bytes=int(row["expected_size_bytes"]),
            observed_size_bytes=int(row["observed_size_bytes"]),
            status=QuarantineStatus(str(row["status"])),
            rejection_codes=tuple(
                QuarantineRejectionCode(str(value)) for value in raw_rejections
            ),
            probe=(MediaProbeResult.model_validate(raw_probe) if raw_probe is not None else None),
            threat_scan=(
                ThreatScanResult.model_validate(raw_scan) if raw_scan is not None else None
            ),
            inspected_at=row["inspected_at"],
            audit=AuditFields(
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                created_by=(str(row["created_by"]) if row["created_by"] is not None else None),
                revision=int(row["revision"]),
            ),
        )

    def _require_project(self, connection: Connection, project_id: str) -> UUID:
        value = connection.execute(
            select(self.projects.c.id).where(self.projects.c.external_id == project_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing project:{project_id}")
        return cast(UUID, value)

    def _row_by_external(
        self,
        connection: Connection,
        inspection_id: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.inspections).where(self.inspections.c.external_id == inspection_id)
        ).mappings().one_or_none()

    def _require_for_update(self, connection: Connection, inspection_id: str) -> RowMapping:
        row = connection.execute(
            select(self.inspections)
            .where(self.inspections.c.external_id == inspection_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(
                f"quarantine inspection {inspection_id} was not found"
            )
        return row

    @staticmethod
    def _creation_fingerprint(inspection: QuarantineInspection) -> str:
        return operation_fingerprint(
            {
                "upload_session_id": inspection.upload_session_id,
                "project_id": inspection.project_id,
                "storage_object_id": inspection.storage_object_id,
                "policy": inspection.policy.model_dump(mode="json"),
                "claimed_mime_type": inspection.claimed_mime_type,
                "expected_size_bytes": inspection.expected_size_bytes,
            }
        )

    @classmethod
    def _terminal_fingerprint(cls, inspection: QuarantineInspection) -> str:
        return operation_fingerprint(
            {
                "creation": cls._creation_fingerprint(inspection),
                "detected_mime_type": inspection.detected_mime_type,
                "observed_size_bytes": inspection.observed_size_bytes,
                "status": inspection.status.value,
                "rejection_codes": [code.value for code in inspection.rejection_codes],
                "probe": inspection.probe.model_dump(mode="json") if inspection.probe else None,
                "threat_scan": (
                    inspection.threat_scan.model_dump(mode="json")
                    if inspection.threat_scan
                    else None
                ),
            }
        )
