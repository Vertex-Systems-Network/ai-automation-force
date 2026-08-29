from __future__ import annotations

from datetime import datetime
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import SCHEMA_VERSION, AuditFields, SchemaVersion
from ..job_control import operation_fingerprint
from ..storage import StorageBackend
from ..upload_session import (
    UploadMode,
    UploadMutationResult,
    UploadPart,
    UploadSession,
    UploadSessionConflictError,
    UploadSessionStatus,
)
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError


class UploadPersistenceConflictError(PersistenceConflictError, UploadSessionConflictError):
    """Persisted upload state conflicts with the requested mutation."""


class PostgresUploadSessionRepository:
    """Atomic upload-session persistence with resumable parts and command idempotency."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"upload_sessions", "upload_parts", "upload_session_commands", "projects"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"upload persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.sessions = metadata.tables["core.upload_sessions"]
        self.parts = metadata.tables["core.upload_parts"]
        self.commands = metadata.tables["core.upload_session_commands"]
        self.projects = metadata.tables["core.projects"]

    def create(self, session: UploadSession) -> UploadMutationResult:
        if session.status is not UploadSessionStatus.OPEN or session.parts:
            raise UploadPersistenceConflictError("new upload session must be open with no parts")
        immutable_fingerprint = self._creation_fingerprint(session)
        try:
            with self.engine.begin() as connection:
                project_id = self._require_project(connection, session.project_id)
                existing_by_key = connection.execute(
                    select(self.sessions)
                    .where(
                        self.sessions.c.project_id == project_id,
                        self.sessions.c.creation_idempotency_key
                        == session.creation_idempotency_key,
                    )
                    .with_for_update()
                ).mappings().one_or_none()
                if existing_by_key is not None:
                    existing = self._from_row(connection, existing_by_key)
                    if self._creation_fingerprint(existing) != immutable_fingerprint:
                        raise UploadPersistenceConflictError(
                            "upload creation idempotency key is bound to different semantics"
                        )
                    return UploadMutationResult(
                        action="reused",
                        upload_session_id=existing.upload_session_id,
                        status=existing.status,
                        revision=existing.audit.revision,
                    )

                existing_by_id = self._row_by_external(connection, session.upload_session_id)
                if existing_by_id is not None:
                    raise UploadPersistenceConflictError(
                        f"upload session {session.upload_session_id} already exists"
                    )

                connection.execute(
                    insert(self.sessions).values(
                        id=uuid4(),
                        external_id=session.upload_session_id,
                        schema_version=session.schema_version,
                        project_id=project_id,
                        storage_object_external_id=session.storage_object_id,
                        backend=session.backend.value,
                        bucket=session.bucket,
                        object_key=session.object_key,
                        expected_size_bytes=session.expected_size_bytes,
                        expected_mime_type=session.expected_mime_type,
                        original_filename=session.original_filename,
                        mode=session.mode.value,
                        part_size_bytes=session.part_size_bytes,
                        backend_upload_id=session.backend_upload_id,
                        quota_reservation_id=session.quota_reservation_id,
                        creation_idempotency_key=session.creation_idempotency_key,
                        expires_at=session.expires_at,
                        status=session.status.value,
                        observed_size_bytes=None,
                        observed_etag=None,
                        observed_version_id=None,
                        completed_at=None,
                        aborted_at=None,
                        created_at=session.audit.created_at,
                        updated_at=session.audit.updated_at,
                        created_by=session.audit.created_by,
                        revision=session.audit.revision,
                    )
                )
                return UploadMutationResult(
                    action="created",
                    upload_session_id=session.upload_session_id,
                    status=session.status,
                    revision=session.audit.revision,
                )
        except (UploadPersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise UploadPersistenceConflictError(
                f"database rejected upload session {session.upload_session_id}: {exc.orig}"
            ) from exc

    def load(self, upload_session_id: str) -> UploadSession:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, upload_session_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"upload session {upload_session_id} was not found"
                )
            return self._from_row(connection, row)

    def bind_backend_upload_id(
        self,
        upload_session_id: str,
        backend_upload_id: str,
        *,
        now: datetime,
    ) -> UploadMutationResult:
        if not backend_upload_id:
            raise ValueError("backend_upload_id must be non-empty")
        with self.engine.begin() as connection:
            row = self._require_session_for_update(connection, upload_session_id)
            expiry = self._expire_if_due(connection, row, now)
            if expiry is not None:
                return expiry
            session = self._from_row(connection, row)
            if session.mode is not UploadMode.MULTIPART:
                raise UploadPersistenceConflictError(
                    "single upload cannot bind a multipart backend upload id"
                )
            if session.status not in {UploadSessionStatus.OPEN, UploadSessionStatus.UPLOADING}:
                raise UploadPersistenceConflictError(
                    f"cannot bind multipart UploadId while upload is {session.status.value}"
                )
            if session.backend_upload_id is not None:
                if session.backend_upload_id != backend_upload_id:
                    raise UploadPersistenceConflictError(
                        "multipart session is already bound to a different backend UploadId"
                    )
                return UploadMutationResult(
                    action="reused",
                    upload_session_id=upload_session_id,
                    status=session.status,
                    revision=session.audit.revision,
                )
            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.sessions)
                .where(self.sessions.c.id == row["id"])
                .values(
                    backend_upload_id=backend_upload_id,
                    updated_at=now,
                    revision=revision,
                )
            )
            return UploadMutationResult(
                action="recorded",
                upload_session_id=upload_session_id,
                status=session.status,
                revision=revision,
            )

    def record_part(
        self,
        upload_session_id: str,
        part: UploadPart,
        *,
        now: datetime,
    ) -> UploadMutationResult:
        with self.engine.begin() as connection:
            row = self._require_session_for_update(connection, upload_session_id)
            expiry = self._expire_if_due(connection, row, now)
            if expiry is not None:
                return expiry
            session = self._from_row(connection, row)
            if session.mode is not UploadMode.MULTIPART:
                raise UploadPersistenceConflictError("single upload cannot record multipart parts")
            if session.backend_upload_id is None:
                raise UploadPersistenceConflictError(
                    "multipart UploadId must be durably bound before recording parts"
                )
            if session.status not in {UploadSessionStatus.OPEN, UploadSessionStatus.UPLOADING}:
                raise UploadPersistenceConflictError(
                    f"cannot record part while upload is {session.status.value}"
                )
            assert session.part_size_bytes is not None
            if part.size_bytes > session.part_size_bytes:
                raise UploadPersistenceConflictError("part exceeds configured part_size_bytes")

            existing = connection.execute(
                select(self.parts).where(
                    self.parts.c.upload_session_id == row["id"],
                    self.parts.c.part_number == part.part_number,
                )
            ).mappings().one_or_none()
            if existing is not None:
                restored = self._part_from_row(existing)
                if restored != part:
                    raise UploadPersistenceConflictError(
                        f"part {part.part_number} is already bound to different metadata"
                    )
                return UploadMutationResult(
                    action="reused",
                    upload_session_id=upload_session_id,
                    status=session.status,
                    revision=session.audit.revision,
                )

            recorded_bytes = connection.execute(
                select(self.parts.c.size_bytes).where(
                    self.parts.c.upload_session_id == row["id"]
                )
            ).scalars().all()
            total_recorded = sum(int(value) for value in recorded_bytes) + part.size_bytes
            if total_recorded > session.expected_size_bytes:
                raise UploadPersistenceConflictError(
                    "recorded multipart bytes would exceed expected upload size"
                )

            connection.execute(
                insert(self.parts).values(
                    id=uuid4(),
                    upload_session_id=row["id"],
                    part_number=part.part_number,
                    size_bytes=part.size_bytes,
                    etag=part.etag,
                    checksum_sha256=part.checksum_sha256,
                    recorded_at=part.recorded_at,
                )
            )
            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.sessions)
                .where(self.sessions.c.id == row["id"])
                .values(
                    status=UploadSessionStatus.UPLOADING.value,
                    updated_at=now,
                    revision=revision,
                )
            )
            return UploadMutationResult(
                action="recorded",
                upload_session_id=upload_session_id,
                status=UploadSessionStatus.UPLOADING,
                revision=revision,
            )

    def complete(
        self,
        upload_session_id: str,
        *,
        idempotency_key: str,
        observed_size_bytes: int,
        completed_at: datetime,
        observed_etag: str | None = None,
        observed_version_id: str | None = None,
    ) -> UploadMutationResult:
        if len(idempotency_key) < 8:
            raise ValueError("idempotency_key must contain at least 8 characters")
        fingerprint = operation_fingerprint(
            {
                "observed_size_bytes": observed_size_bytes,
                "observed_etag": observed_etag,
                "observed_version_id": observed_version_id,
            }
        )
        with self.engine.begin() as connection:
            row = self._require_session_for_update(connection, upload_session_id)
            prior = self._replay_command(
                connection,
                row,
                "complete",
                idempotency_key,
                fingerprint,
            )
            if prior is not None:
                return prior
            expiry = self._expire_if_due(connection, row, completed_at)
            if expiry is not None:
                self._record_command(
                    connection,
                    row["id"],
                    "complete",
                    idempotency_key,
                    fingerprint,
                    expiry,
                    completed_at,
                )
                return expiry
            session = self._from_row(connection, row)
            if session.status is UploadSessionStatus.ABORTED:
                raise UploadPersistenceConflictError("aborted upload cannot be completed")
            if observed_size_bytes != session.expected_size_bytes:
                raise UploadPersistenceConflictError(
                    "observed upload size does not match the expected size"
                )
            if session.mode is UploadMode.MULTIPART:
                if session.backend_upload_id is None:
                    raise UploadPersistenceConflictError(
                        "multipart UploadId must be durably bound before completion"
                    )
                if not session.parts:
                    raise UploadPersistenceConflictError(
                        "multipart upload cannot complete without recorded parts"
                    )
                if sum(part.size_bytes for part in session.parts) != session.expected_size_bytes:
                    raise UploadPersistenceConflictError(
                        "recorded multipart bytes do not match expected upload size"
                    )

            if session.status is UploadSessionStatus.COMPLETED:
                if (
                    session.observed_size_bytes != observed_size_bytes
                    or session.observed_etag != observed_etag
                    or session.observed_version_id != observed_version_id
                ):
                    raise UploadPersistenceConflictError(
                        "completed upload is bound to different completion evidence"
                    )
                result = UploadMutationResult(
                    action="reused",
                    upload_session_id=upload_session_id,
                    status=session.status,
                    revision=session.audit.revision,
                )
                self._record_command(
                    connection,
                    row["id"],
                    "complete",
                    idempotency_key,
                    fingerprint,
                    result,
                    completed_at,
                )
                return result

            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.sessions)
                .where(self.sessions.c.id == row["id"])
                .values(
                    status=UploadSessionStatus.COMPLETED.value,
                    observed_size_bytes=observed_size_bytes,
                    observed_etag=observed_etag,
                    observed_version_id=observed_version_id,
                    completed_at=completed_at,
                    updated_at=completed_at,
                    revision=revision,
                )
            )
            result = UploadMutationResult(
                action="completed",
                upload_session_id=upload_session_id,
                status=UploadSessionStatus.COMPLETED,
                revision=revision,
            )
            self._record_command(
                connection,
                row["id"],
                "complete",
                idempotency_key,
                fingerprint,
                result,
                completed_at,
            )
            return result

    def abort(
        self,
        upload_session_id: str,
        *,
        idempotency_key: str,
        aborted_at: datetime,
    ) -> UploadMutationResult:
        if len(idempotency_key) < 8:
            raise ValueError("idempotency_key must contain at least 8 characters")
        fingerprint = operation_fingerprint({"command": "abort"})
        with self.engine.begin() as connection:
            row = self._require_session_for_update(connection, upload_session_id)
            prior = self._replay_command(
                connection,
                row,
                "abort",
                idempotency_key,
                fingerprint,
            )
            if prior is not None:
                return prior
            expiry = self._expire_if_due(connection, row, aborted_at)
            if expiry is not None:
                self._record_command(
                    connection,
                    row["id"],
                    "abort",
                    idempotency_key,
                    fingerprint,
                    expiry,
                    aborted_at,
                )
                return expiry
            session = self._from_row(connection, row)
            if session.status is UploadSessionStatus.COMPLETED:
                raise UploadPersistenceConflictError("completed upload cannot be aborted")
            if session.status is UploadSessionStatus.ABORTED:
                result = UploadMutationResult(
                    action="reused",
                    upload_session_id=upload_session_id,
                    status=session.status,
                    revision=session.audit.revision,
                )
                self._record_command(
                    connection,
                    row["id"],
                    "abort",
                    idempotency_key,
                    fingerprint,
                    result,
                    aborted_at,
                )
                return result

            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.sessions)
                .where(self.sessions.c.id == row["id"])
                .values(
                    status=UploadSessionStatus.ABORTED.value,
                    aborted_at=aborted_at,
                    updated_at=aborted_at,
                    revision=revision,
                )
            )
            result = UploadMutationResult(
                action="aborted",
                upload_session_id=upload_session_id,
                status=UploadSessionStatus.ABORTED,
                revision=revision,
            )
            self._record_command(
                connection,
                row["id"],
                "abort",
                idempotency_key,
                fingerprint,
                result,
                aborted_at,
            )
            return result

    def _expire_if_due(
        self,
        connection: Connection,
        row: RowMapping,
        now: datetime,
    ) -> UploadMutationResult | None:
        status = UploadSessionStatus(str(row["status"]))
        if status in {
            UploadSessionStatus.COMPLETED,
            UploadSessionStatus.ABORTED,
            UploadSessionStatus.EXPIRED,
        }:
            if status is UploadSessionStatus.EXPIRED:
                return UploadMutationResult(
                    action="expired",
                    upload_session_id=str(row["external_id"]),
                    status=status,
                    revision=int(row["revision"]),
                )
            return None
        if now < row["expires_at"]:
            return None
        revision = int(row["revision"]) + 1
        connection.execute(
            update(self.sessions)
            .where(self.sessions.c.id == row["id"])
            .values(
                status=UploadSessionStatus.EXPIRED.value,
                updated_at=now,
                revision=revision,
            )
        )
        return UploadMutationResult(
            action="expired",
            upload_session_id=str(row["external_id"]),
            status=UploadSessionStatus.EXPIRED,
            revision=revision,
        )

    def _from_row(self, connection: Connection, row: RowMapping) -> UploadSession:
        persisted_schema_version = int(row["schema_version"])
        if persisted_schema_version != SCHEMA_VERSION:
            raise PersistenceReferenceError(
                "unsupported upload session schema version "
                f"{persisted_schema_version}; expected {SCHEMA_VERSION}"
            )
        project_id = connection.execute(
            select(self.projects.c.external_id).where(self.projects.c.id == row["project_id"])
        ).scalar_one_or_none()
        if project_id is None:
            raise PersistenceReferenceError("upload session project reference is missing")
        part_rows = connection.execute(
            select(self.parts)
            .where(self.parts.c.upload_session_id == row["id"])
            .order_by(self.parts.c.part_number)
        ).mappings().all()
        return UploadSession(
            schema_version=cast(SchemaVersion, persisted_schema_version),
            upload_session_id=str(row["external_id"]),
            project_id=str(project_id),
            storage_object_id=str(row["storage_object_external_id"]),
            backend=StorageBackend(str(row["backend"])),
            bucket=(str(row["bucket"]) if row["bucket"] is not None else None),
            object_key=str(row["object_key"]),
            expected_size_bytes=int(row["expected_size_bytes"]),
            expected_mime_type=str(row["expected_mime_type"]),
            original_filename=(
                str(row["original_filename"]) if row["original_filename"] is not None else None
            ),
            mode=UploadMode(str(row["mode"])),
            part_size_bytes=(
                int(row["part_size_bytes"]) if row["part_size_bytes"] is not None else None
            ),
            backend_upload_id=(
                str(row["backend_upload_id"]) if row["backend_upload_id"] is not None else None
            ),
            quota_reservation_id=(
                str(row["quota_reservation_id"])
                if row["quota_reservation_id"] is not None
                else None
            ),
            creation_idempotency_key=str(row["creation_idempotency_key"]),
            expires_at=row["expires_at"],
            status=UploadSessionStatus(str(row["status"])),
            parts=[self._part_from_row(item) for item in part_rows],
            observed_size_bytes=(
                int(row["observed_size_bytes"])
                if row["observed_size_bytes"] is not None
                else None
            ),
            observed_etag=(
                str(row["observed_etag"]) if row["observed_etag"] is not None else None
            ),
            observed_version_id=(
                str(row["observed_version_id"])
                if row["observed_version_id"] is not None
                else None
            ),
            completed_at=row["completed_at"],
            aborted_at=row["aborted_at"],
            audit=AuditFields(
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                created_by=(str(row["created_by"]) if row["created_by"] is not None else None),
                revision=int(row["revision"]),
            ),
        )

    @staticmethod
    def _part_from_row(row: RowMapping) -> UploadPart:
        return UploadPart(
            part_number=int(row["part_number"]),
            size_bytes=int(row["size_bytes"]),
            etag=(str(row["etag"]) if row["etag"] is not None else None),
            checksum_sha256=(
                str(row["checksum_sha256"]) if row["checksum_sha256"] is not None else None
            ),
            recorded_at=row["recorded_at"],
        )

    @staticmethod
    def _creation_fingerprint(session: UploadSession) -> str:
        return operation_fingerprint(
            {
                "project_id": session.project_id,
                "storage_object_id": session.storage_object_id,
                "backend": session.backend.value,
                "bucket": session.bucket,
                "object_key": session.object_key,
                "expected_size_bytes": session.expected_size_bytes,
                "expected_mime_type": session.expected_mime_type,
                "original_filename": session.original_filename,
                "mode": session.mode.value,
                "part_size_bytes": session.part_size_bytes,
                "backend_upload_id": session.backend_upload_id,
                "quota_reservation_id": session.quota_reservation_id,
                "expires_at": session.expires_at.isoformat(),
            }
        )

    def _require_session_for_update(
        self,
        connection: Connection,
        upload_session_id: str,
    ) -> RowMapping:
        row = connection.execute(
            select(self.sessions)
            .where(self.sessions.c.external_id == upload_session_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"upload session {upload_session_id} was not found")
        return row

    def _row_by_external(
        self,
        connection: Connection,
        upload_session_id: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.sessions).where(self.sessions.c.external_id == upload_session_id)
        ).mappings().one_or_none()

    def _require_project(self, connection: Connection, project_id: str) -> UUID:
        value = connection.execute(
            select(self.projects.c.id).where(self.projects.c.external_id == project_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing project:{project_id}")
        return cast(UUID, value)

    def _replay_command(
        self,
        connection: Connection,
        session_row: RowMapping,
        command_type: str,
        idempotency_key: str,
        fingerprint: str,
    ) -> UploadMutationResult | None:
        row = connection.execute(
            select(self.commands).where(
                self.commands.c.upload_session_id == session_row["id"],
                self.commands.c.command_type == command_type,
                self.commands.c.idempotency_key == idempotency_key,
            )
        ).mappings().one_or_none()
        if row is None:
            return None
        if str(row["request_fingerprint"]) != fingerprint:
            raise UploadPersistenceConflictError(
                f"{command_type} idempotency key is bound to different request semantics"
            )
        return UploadMutationResult(
            action="reused",
            upload_session_id=str(session_row["external_id"]),
            status=UploadSessionStatus(str(row["result_status"])),
            revision=int(row["result_revision"]),
        )

    def _record_command(
        self,
        connection: Connection,
        session_internal_id: UUID,
        command_type: str,
        idempotency_key: str,
        fingerprint: str,
        result: UploadMutationResult,
        occurred_at: datetime,
    ) -> None:
        connection.execute(
            insert(self.commands).values(
                id=uuid4(),
                upload_session_id=session_internal_id,
                command_type=command_type,
                idempotency_key=idempotency_key,
                request_fingerprint=fingerprint,
                result_status=result.status.value,
                result_revision=result.revision,
                occurred_at=occurred_at,
            )
        )
