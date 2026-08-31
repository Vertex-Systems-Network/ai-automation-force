from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import SCHEMA_VERSION, SchemaVersion
from ..derivatives import (
    TERMINAL_DERIVATIVE_STATUSES,
    DerivativeRecord,
    DerivativeSpec,
    DerivativeStatus,
    assert_derivative_transition,
)
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

DerivativePersistAction = Literal["created", "reused", "updated", "noop"]


@dataclass(frozen=True)
class DerivativePersistResult:
    action: DerivativePersistAction
    derivative_record_id: str
    status: DerivativeStatus
    revision: int


class DerivativePersistenceConflictError(PersistenceConflictError):
    """Persisted derivative state conflicts with the requested mutation."""


class PostgresDerivativeRepository:
    """Durable, idempotent derivative lineage and lifecycle persistence for M03/WP5."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "derivative_records",
            "projects",
            "assets",
            "asset_parents",
            "storage_objects",
            "jobs",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"derivative persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.derivatives = metadata.tables["core.derivative_records"]
        self.projects = metadata.tables["core.projects"]
        self.assets = metadata.tables["core.assets"]
        self.asset_parents = metadata.tables["core.asset_parents"]
        self.storage_objects = metadata.tables["core.storage_objects"]
        self.jobs = metadata.tables["core.jobs"]

    def create(self, record: DerivativeRecord) -> DerivativePersistResult:
        if record.status is not DerivativeStatus.PLANNED:
            raise DerivativePersistenceConflictError("new derivative record must be planned")
        if record.revision != 1 or record.updated_at != record.created_at:
            raise DerivativePersistenceConflictError(
                "new derivative record must start at revision 1 with updated_at == created_at"
            )

        try:
            with self.engine.begin() as connection:
                project = self._require_external(connection, self.projects, record.project_id, "project")
                source = self._require_external(
                    connection, self.assets, record.source_asset_id, "source asset"
                )
                job = self._require_external(connection, self.jobs, record.job_id, "job")
                self._require_same_project(record, project, source, job)

                existing = self._row_by_external(connection, record.derivative_record_id)
                if existing is not None:
                    restored = self._from_row(connection, existing)
                    if restored != record:
                        raise DerivativePersistenceConflictError(
                            "derivative identity is already bound to different data"
                        )
                    return self._result("reused", restored)

                semantic = self._row_by_operation(
                    connection,
                    project_id=cast(UUID, project["id"]),
                    source_asset_id=cast(UUID, source["id"]),
                    operation_fingerprint=record.operation_fingerprint,
                )
                if semantic is not None:
                    return self._result("reused", self._from_row(connection, semantic))

                connection.execute(
                    insert(self.derivatives).values(
                        id=uuid4(),
                        external_id=record.derivative_record_id,
                        schema_version=record.schema_version,
                        project_id=project["id"],
                        source_asset_id=source["id"],
                        output_asset_id=None,
                        output_storage_object_id=None,
                        job_id=job["id"],
                        derivative_kind=record.spec.kind.value,
                        spec_json=record.spec.model_dump(mode="json"),
                        operation_fingerprint=record.operation_fingerprint,
                        status=record.status.value,
                        created_at=record.created_at,
                        updated_at=record.updated_at,
                        completed_at=None,
                        error_code=None,
                        revision=record.revision,
                    )
                )
                return self._result("created", record)
        except (DerivativePersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise DerivativePersistenceConflictError(
                f"database rejected derivative record {record.derivative_record_id}: {exc.orig}"
            ) from exc

    def load(self, derivative_record_id: str) -> DerivativeRecord:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, derivative_record_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"derivative record {derivative_record_id} was not found"
                )
            return self._from_row(connection, row)

    def transition(
        self,
        derivative_record_id: str,
        *,
        expected_revision: int,
        target_status: DerivativeStatus,
        updated_at: datetime,
        output_asset_id: str | None = None,
        output_storage_object_id: str | None = None,
        completed_at: datetime | None = None,
        error_code: str | None = None,
    ) -> DerivativePersistResult:
        with self.engine.begin() as connection:
            row = self._require_for_update(connection, derivative_record_id)
            current = self._from_row(connection, row)

            if current.status is target_status and current.status not in TERMINAL_DERIVATIVE_STATUSES:
                if any(
                    value is not None
                    for value in (
                        output_asset_id,
                        output_storage_object_id,
                        completed_at,
                        error_code,
                    )
                ):
                    raise DerivativePersistenceConflictError(
                        "non-terminal derivative replay cannot add terminal evidence"
                    )
                return self._result("noop", current)

            requested = self._build_target(
                current,
                target_status=target_status,
                updated_at=updated_at,
                output_asset_id=output_asset_id,
                output_storage_object_id=output_storage_object_id,
                completed_at=completed_at,
                error_code=error_code,
                revision=current.revision + 1,
            )

            if current.status is target_status:
                replay = requested.model_copy(update={"revision": current.revision})
                if replay == current:
                    return self._result("noop", current)
                raise DerivativePersistenceConflictError(
                    "terminal derivative transition replay carries different evidence"
                )

            if int(row["revision"]) != expected_revision:
                raise DerivativePersistenceConflictError(
                    f"stale derivative revision {expected_revision}; current revision is {row['revision']}"
                )
            try:
                assert_derivative_transition(current.status, target_status)
            except ValueError as exc:
                raise DerivativePersistenceConflictError(str(exc)) from exc

            project = self._require_internal(
                connection, self.projects, cast(UUID, row["project_id"]), "project"
            )
            source = self._require_internal(
                connection, self.assets, cast(UUID, row["source_asset_id"]), "source asset"
            )
            if target_status is DerivativeStatus.COMPLETED:
                assert requested.output_asset_id is not None
                assert requested.output_storage_object_id is not None
                output_asset = self._require_external(
                    connection, self.assets, requested.output_asset_id, "output asset"
                )
                output_storage = self._require_external(
                    connection,
                    self.storage_objects,
                    requested.output_storage_object_id,
                    "output storage object",
                )
                self._validate_completed_lineage(
                    connection,
                    project=project,
                    source=source,
                    output_asset=output_asset,
                    output_storage=output_storage,
                )

            connection.execute(
                update(self.derivatives)
                .where(self.derivatives.c.id == row["id"])
                .values(
                    output_asset_id=self._optional_external_internal(
                        connection, self.assets, requested.output_asset_id, "output asset"
                    ),
                    output_storage_object_id=self._optional_external_internal(
                        connection,
                        self.storage_objects,
                        requested.output_storage_object_id,
                        "output storage object",
                    ),
                    status=requested.status.value,
                    updated_at=requested.updated_at,
                    completed_at=requested.completed_at,
                    error_code=requested.error_code,
                    revision=requested.revision,
                )
            )
            return self._result("updated", requested)

    @staticmethod
    def _build_target(
        current: DerivativeRecord,
        *,
        target_status: DerivativeStatus,
        updated_at: datetime,
        output_asset_id: str | None,
        output_storage_object_id: str | None,
        completed_at: datetime | None,
        error_code: str | None,
        revision: int,
    ) -> DerivativeRecord:
        return DerivativeRecord.model_validate(
            {
                **current.model_dump(mode="python"),
                "status": target_status,
                "updated_at": updated_at,
                "output_asset_id": output_asset_id,
                "output_storage_object_id": output_storage_object_id,
                "completed_at": completed_at,
                "error_code": error_code,
                "revision": revision,
            }
        )

    @staticmethod
    def _require_same_project(
        record: DerivativeRecord,
        project: RowMapping,
        source: RowMapping,
        job: RowMapping,
    ) -> None:
        if source["project_id"] != project["id"]:
            raise DerivativePersistenceConflictError(
                f"source asset {record.source_asset_id} is outside derivative project {record.project_id}"
            )
        if job["project_id"] != project["id"]:
            raise DerivativePersistenceConflictError(
                f"job {record.job_id} is outside derivative project {record.project_id}"
            )

    def _validate_completed_lineage(
        self,
        connection: Connection,
        *,
        project: RowMapping,
        source: RowMapping,
        output_asset: RowMapping,
        output_storage: RowMapping,
    ) -> None:
        if output_asset["id"] == source["id"]:
            raise DerivativePersistenceConflictError("derivative output cannot be the source asset")
        if output_asset["project_id"] != project["id"]:
            raise DerivativePersistenceConflictError("derivative output asset is outside project boundary")
        if output_storage["project_id"] != project["id"]:
            raise DerivativePersistenceConflictError(
                "derivative output storage object is outside project boundary"
            )
        if str(output_storage["sha256"]) != str(output_asset["sha256"]):
            raise DerivativePersistenceConflictError(
                "derivative output storage hash does not match output asset"
            )
        parent_link = connection.execute(
            select(self.asset_parents.c.child_asset_id)
            .where(self.asset_parents.c.child_asset_id == output_asset["id"])
            .where(self.asset_parents.c.parent_asset_id == source["id"])
            .limit(1)
        ).scalar_one_or_none()
        if parent_link is None:
            raise DerivativePersistenceConflictError(
                "derivative output asset is not canonically linked to the source asset"
            )

    def _from_row(self, connection: Connection, row: RowMapping) -> DerivativeRecord:
        persisted_schema_version = int(row["schema_version"])
        if persisted_schema_version != SCHEMA_VERSION:
            raise PersistenceReferenceError(
                "unsupported derivative schema version "
                f"{persisted_schema_version}; expected {SCHEMA_VERSION}"
            )
        return DerivativeRecord(
            schema_version=cast(SchemaVersion, persisted_schema_version),
            derivative_record_id=str(row["external_id"]),
            project_id=self._external_for_internal(
                connection, self.projects, cast(UUID, row["project_id"]), "project"
            ),
            source_asset_id=self._external_for_internal(
                connection, self.assets, cast(UUID, row["source_asset_id"]), "source asset"
            ),
            output_asset_id=self._optional_external_for_internal(
                connection, self.assets, cast(UUID | None, row["output_asset_id"]), "output asset"
            ),
            output_storage_object_id=self._optional_external_for_internal(
                connection,
                self.storage_objects,
                cast(UUID | None, row["output_storage_object_id"]),
                "output storage object",
            ),
            job_id=self._external_for_internal(
                connection, self.jobs, cast(UUID, row["job_id"]), "job"
            ),
            spec=DerivativeSpec.model_validate(row["spec_json"]),
            operation_fingerprint=str(row["operation_fingerprint"]),
            status=DerivativeStatus(str(row["status"])),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
            error_code=(str(row["error_code"]) if row["error_code"] is not None else None),
            revision=int(row["revision"]),
        )

    def _row_by_external(self, connection: Connection, external_id: str) -> RowMapping | None:
        return connection.execute(
            select(self.derivatives).where(self.derivatives.c.external_id == external_id)
        ).mappings().one_or_none()

    def _row_by_operation(
        self,
        connection: Connection,
        *,
        project_id: UUID,
        source_asset_id: UUID,
        operation_fingerprint: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.derivatives)
            .where(self.derivatives.c.project_id == project_id)
            .where(self.derivatives.c.source_asset_id == source_asset_id)
            .where(self.derivatives.c.operation_fingerprint == operation_fingerprint)
        ).mappings().one_or_none()

    def _require_for_update(self, connection: Connection, external_id: str) -> RowMapping:
        row = connection.execute(
            select(self.derivatives)
            .where(self.derivatives.c.external_id == external_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"derivative record {external_id} was not found")
        return row

    @staticmethod
    def _require_external(
        connection: Connection,
        table: Table,
        external_id: str,
        label: str,
    ) -> RowMapping:
        row = connection.execute(
            select(table).where(table.c.external_id == external_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing {label}:{external_id}")
        return row

    @staticmethod
    def _require_internal(
        connection: Connection,
        table: Table,
        internal_id: UUID,
        label: str,
    ) -> RowMapping:
        row = connection.execute(
            select(table).where(table.c.id == internal_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing {label} internal row {internal_id}")
        return row

    @classmethod
    def _optional_external_internal(
        cls,
        connection: Connection,
        table: Table,
        external_id: str | None,
        label: str,
    ) -> UUID | None:
        if external_id is None:
            return None
        row = cls._require_external(connection, table, external_id, label)
        return cast(UUID, row["id"])

    @staticmethod
    def _external_for_internal(
        connection: Connection,
        table: Table,
        internal_id: UUID,
        label: str,
    ) -> str:
        value = connection.execute(
            select(table.c.external_id).where(table.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing {label} external identity for {internal_id}")
        return str(value)

    @classmethod
    def _optional_external_for_internal(
        cls,
        connection: Connection,
        table: Table,
        internal_id: UUID | None,
        label: str,
    ) -> str | None:
        if internal_id is None:
            return None
        return cls._external_for_internal(connection, table, internal_id, label)

    @staticmethod
    def _result(action: DerivativePersistAction, record: DerivativeRecord) -> DerivativePersistResult:
        return DerivativePersistResult(
            action=action,
            derivative_record_id=record.derivative_record_id,
            status=record.status,
            revision=record.revision,
        )
