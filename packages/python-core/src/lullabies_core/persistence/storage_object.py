from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import AuditFields
from ..storage import StorageBackend, StorageObject
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

StorageObjectPersistAction = Literal["created", "noop"]


@dataclass(frozen=True)
class StorageObjectPersistResult:
    action: StorageObjectPersistAction
    storage_object_id: str


class PostgresStorageObjectRepository:
    """Persistence boundary for physical storage metadata introduced by M03."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"storage_objects", "projects"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"storage persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.storage_table = metadata.tables["core.storage_objects"]
        self.project_table = metadata.tables["core.projects"]

    def save(self, storage_object: StorageObject) -> StorageObjectPersistResult:
        try:
            with self.engine.begin() as connection:
                existing = self._row_by_external(connection, storage_object.storage_object_id)
                if existing is not None:
                    if self._from_row(connection, existing) == storage_object:
                        return StorageObjectPersistResult("noop", storage_object.storage_object_id)
                    message = (
                        f"storage object {storage_object.storage_object_id} "
                        "already has different data"
                    )
                    raise PersistenceConflictError(message)
                project_internal = self._optional_project_internal(
                    connection,
                    storage_object.project_id,
                )
                connection.execute(
                    insert(self.storage_table).values(
                        id=uuid4(),
                        external_id=storage_object.storage_object_id,
                        schema_version=storage_object.schema_version,
                        project_id=project_internal,
                        backend=storage_object.backend.value,
                        bucket=storage_object.bucket,
                        object_key=storage_object.object_key,
                        sha256=storage_object.sha256,
                        mime_type=storage_object.mime_type,
                        size_bytes=storage_object.size_bytes,
                        region=storage_object.region,
                        etag=storage_object.etag,
                        version_id=storage_object.version_id,
                        original_filename=storage_object.original_filename,
                        lifecycle_class=storage_object.lifecycle_class,
                        created_at=storage_object.audit.created_at,
                        updated_at=storage_object.audit.updated_at,
                        created_by=storage_object.audit.created_by,
                        revision=storage_object.audit.revision,
                    )
                )
        except (PersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database rejected storage object {storage_object.storage_object_id}"
            ) from exc
        return StorageObjectPersistResult("created", storage_object.storage_object_id)

    def load(self, storage_object_id: str) -> StorageObject:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, storage_object_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"storage object {storage_object_id} was not found"
                )
            return self._from_row(connection, row)

    def _from_row(self, connection: Connection, row: RowMapping) -> StorageObject:
        return StorageObject(
            schema_version=int(row["schema_version"]),
            storage_object_id=str(row["external_id"]),
            project_id=self._external_project(connection, row["project_id"]),
            backend=StorageBackend(str(row["backend"])),
            bucket=(str(row["bucket"]) if row["bucket"] is not None else None),
            object_key=str(row["object_key"]),
            sha256=str(row["sha256"]),
            mime_type=str(row["mime_type"]),
            size_bytes=int(row["size_bytes"]),
            region=(str(row["region"]) if row["region"] is not None else None),
            etag=(str(row["etag"]) if row["etag"] is not None else None),
            version_id=(str(row["version_id"]) if row["version_id"] is not None else None),
            original_filename=(
                str(row["original_filename"]) if row["original_filename"] is not None else None
            ),
            lifecycle_class=str(row["lifecycle_class"]),
            audit=AuditFields(
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                created_by=(str(row["created_by"]) if row["created_by"] is not None else None),
                revision=int(row["revision"]),
            ),
        )

    def _row_by_external(self, connection: Connection, external_id: str) -> RowMapping | None:
        return connection.execute(
            select(self.storage_table).where(self.storage_table.c.external_id == external_id)
        ).mappings().one_or_none()

    def _optional_project_internal(
        self,
        connection: Connection,
        project_id: str | None,
    ) -> UUID | None:
        if project_id is None:
            return None
        value = connection.execute(
            select(self.project_table.c.id).where(self.project_table.c.external_id == project_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing project:{project_id}")
        return cast(UUID, value)

    def _external_project(
        self,
        connection: Connection,
        internal_id: UUID | None,
    ) -> str | None:
        if internal_id is None:
            return None
        value = connection.execute(
            select(self.project_table.c.external_id).where(self.project_table.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(
                f"missing project external identity for internal row {internal_id}"
            )
        return str(value)
