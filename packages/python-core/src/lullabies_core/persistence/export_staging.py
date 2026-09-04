from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import SCHEMA_VERSION, AuditFields, SchemaVersion
from ..export_staging import (
    EXPORT_STAGING_LIFECYCLE_CLASS,
    ExportStagingObject,
    PreparedExportStaging,
)
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError
from .storage_object import PostgresStorageObjectRepository

ExportStagingPersistAction = Literal["created", "noop"]


@dataclass(frozen=True)
class ExportStagingPersistResult:
    action: ExportStagingPersistAction
    export_staging_id: str


class PostgresExportStagingRepository:
    """Durable private export-staging provenance and expiry authority."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"export_staging_objects", "storage_objects", "projects"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"export staging tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.staging = metadata.tables["core.export_staging_objects"]
        self.storage = metadata.tables["core.storage_objects"]
        self.projects = metadata.tables["core.projects"]
        self.storage_repository = PostgresStorageObjectRepository(engine)

    def save_prepared(self, prepared: PreparedExportStaging) -> ExportStagingPersistResult:
        record = prepared.record
        storage_object = prepared.storage_object
        if storage_object.storage_object_id != record.staging_storage_object_id:
            raise PersistenceConflictError("prepared export staging storage identity drifted")
        if storage_object.project_id != record.project_id:
            raise PersistenceConflictError("prepared export staging project identity drifted")
        if storage_object.object_key != record.staging_object_key:
            raise PersistenceConflictError("prepared export staging object key drifted")
        if storage_object.sha256 != record.source_sha256:
            raise PersistenceConflictError("prepared export staging SHA-256 drifted")
        if storage_object.lifecycle_class != EXPORT_STAGING_LIFECYCLE_CLASS:
            raise PersistenceConflictError("prepared export staging lifecycle class drifted")

        self.storage_repository.save(storage_object)
        return self.save(record)

    def save(self, record: ExportStagingObject) -> ExportStagingPersistResult:
        try:
            with self.engine.begin() as connection:
                existing = self._row_by_external(connection, record.export_staging_id)
                if existing is not None:
                    if self._from_row(connection, existing) == record:
                        return ExportStagingPersistResult("noop", record.export_staging_id)
                    raise PersistenceConflictError(
                        f"export staging {record.export_staging_id} already has different data"
                    )

                project_internal = self._project_internal(connection, record.project_id)
                source = self._storage_row(connection, record.source_storage_object_id)
                target = self._storage_row(connection, record.staging_storage_object_id)
                self._verify_storage_bindings(
                    record=record,
                    project_internal=project_internal,
                    source=source,
                    target=target,
                )
                connection.execute(
                    insert(self.staging).values(
                        id=uuid4(),
                        external_id=record.export_staging_id,
                        schema_version=record.schema_version,
                        project_id=project_internal,
                        source_storage_object_id=source["id"],
                        staging_storage_object_id=target["id"],
                        source_sha256=record.source_sha256,
                        expires_at=record.expires_at,
                        created_at=record.audit.created_at,
                        updated_at=record.audit.updated_at,
                        created_by=record.audit.created_by,
                        revision=record.audit.revision,
                    )
                )
        except (PersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database rejected export staging {record.export_staging_id}"
            ) from exc
        return ExportStagingPersistResult("created", record.export_staging_id)

    def load(self, export_staging_id: str) -> ExportStagingObject:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, export_staging_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"export staging {export_staging_id} was not found"
                )
            return self._from_row(connection, row)

    def _verify_storage_bindings(
        self,
        *,
        record: ExportStagingObject,
        project_internal: UUID,
        source: RowMapping,
        target: RowMapping,
    ) -> None:
        if source["id"] == target["id"]:
            raise PersistenceConflictError("export staging source and target storage rows match")
        if source["project_id"] != project_internal or target["project_id"] != project_internal:
            raise PersistenceConflictError("export staging storage rows cross project boundary")
        if str(source["sha256"]) != record.source_sha256:
            raise PersistenceConflictError("export staging source SHA-256 changed")
        if str(target["sha256"]) != record.source_sha256:
            raise PersistenceConflictError("export staging target SHA-256 differs from source")
        if str(target["object_key"]) != record.staging_object_key:
            raise PersistenceConflictError("export staging target object key changed")
        if str(target["lifecycle_class"]) != EXPORT_STAGING_LIFECYCLE_CLASS:
            raise PersistenceConflictError(
                "export staging target is not classified as export staging"
            )

    def _from_row(self, connection: Connection, row: RowMapping) -> ExportStagingObject:
        persisted_schema_version = int(row["schema_version"])
        if persisted_schema_version != SCHEMA_VERSION:
            raise PersistenceReferenceError(
                "unsupported export staging schema version "
                f"{persisted_schema_version}; expected {SCHEMA_VERSION}"
            )
        schema_version = cast(SchemaVersion, persisted_schema_version)
        project_id = self._project_external(connection, cast(UUID, row["project_id"]))
        source_id = self._storage_external(connection, cast(UUID, row["source_storage_object_id"]))
        target_id = self._storage_external(connection, cast(UUID, row["staging_storage_object_id"]))
        target = self._storage_row(connection, target_id)
        return ExportStagingObject(
            schema_version=schema_version,
            export_staging_id=str(row["external_id"]),
            project_id=project_id,
            source_storage_object_id=source_id,
            source_sha256=str(row["source_sha256"]),
            staging_storage_object_id=target_id,
            staging_object_key=str(target["object_key"]),
            expires_at=row["expires_at"],
            audit=AuditFields(
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                created_by=(str(row["created_by"]) if row["created_by"] is not None else None),
                revision=int(row["revision"]),
            ),
        )

    def _row_by_external(self, connection: Connection, external_id: str) -> RowMapping | None:
        return connection.execute(
            select(self.staging).where(self.staging.c.external_id == external_id)
        ).mappings().one_or_none()

    def _project_internal(self, connection: Connection, external_id: str) -> UUID:
        value = connection.execute(
            select(self.projects.c.id).where(self.projects.c.external_id == external_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing project:{external_id}")
        return cast(UUID, value)

    def _project_external(self, connection: Connection, internal_id: UUID) -> str:
        value = connection.execute(
            select(self.projects.c.external_id).where(self.projects.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing project row:{internal_id}")
        return str(value)

    def _storage_row(self, connection: Connection, external_id: str) -> RowMapping:
        row = connection.execute(
            select(self.storage).where(self.storage.c.external_id == external_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing storage object:{external_id}")
        return row

    def _storage_external(self, connection: Connection, internal_id: UUID) -> str:
        value = connection.execute(
            select(self.storage.c.external_id).where(self.storage.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing storage row:{internal_id}")
        return str(value)
