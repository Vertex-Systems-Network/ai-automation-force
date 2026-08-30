from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import SCHEMA_VERSION, SchemaVersion
from ..provenance import AssetProvenanceRecord, AssetProvenanceSource
from ._db import (
    PersistenceConflictError,
    PersistenceNotFoundError,
    PersistenceReferenceError,
)

AssetProvenancePersistAction = Literal["created", "noop"]


@dataclass(frozen=True)
class AssetProvenancePersistResult:
    action: AssetProvenancePersistAction
    provenance_record_id: str


class PostgresAssetProvenanceRepository:
    """Append-only persistence boundary for M03/WP4 asset provenance evidence."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "asset_provenance_records",
            "asset_parents",
            "assets",
            "projects",
            "rights_records",
            "storage_objects",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"asset provenance persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.provenance_table = metadata.tables["core.asset_provenance_records"]
        self.asset_parents_table = metadata.tables["core.asset_parents"]
        self.assets_table = metadata.tables["core.assets"]
        self.projects_table = metadata.tables["core.projects"]
        self.rights_table = metadata.tables["core.rights_records"]
        self.storage_table = metadata.tables["core.storage_objects"]

    def save(self, record: AssetProvenanceRecord) -> AssetProvenancePersistResult:
        canonical = AssetProvenanceRecord.model_validate(record.model_dump())
        try:
            with self.engine.begin() as connection:
                existing = self._row_by_external(connection, canonical.provenance_record_id)
                if existing is not None:
                    if self._from_row(connection, existing) == canonical:
                        return AssetProvenancePersistResult(
                            "noop",
                            canonical.provenance_record_id,
                        )
                    raise PersistenceConflictError(
                        f"asset provenance {canonical.provenance_record_id} already has different data"
                    )

                asset = self._require_external(
                    connection,
                    self.assets_table,
                    canonical.asset_id,
                    "asset",
                )
                project_id = self._validate_project(connection, canonical, asset)
                storage_id = self._validate_storage(connection, canonical, asset)
                rights_id = self._validate_rights(connection, canonical, asset)
                self._validate_content_hash(canonical, asset)
                self._validate_derived_parent(connection, canonical, asset)

                connection.execute(
                    insert(self.provenance_table).values(
                        id=uuid4(),
                        external_id=canonical.provenance_record_id,
                        schema_version=canonical.schema_version,
                        asset_id=asset["id"],
                        project_id=project_id,
                        storage_object_id=storage_id,
                        source_kind=canonical.source_kind.value,
                        source_reference=canonical.source_reference,
                        import_reference=canonical.import_reference,
                        provider_reference=canonical.provider_reference,
                        content_sha256=canonical.content_sha256,
                        rights_record_id=rights_id,
                        created_at=canonical.created_at,
                    )
                )
        except (PersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database rejected asset provenance {canonical.provenance_record_id}"
            ) from exc
        return AssetProvenancePersistResult("created", canonical.provenance_record_id)

    def load(self, provenance_record_id: str) -> AssetProvenanceRecord:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, provenance_record_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"asset provenance {provenance_record_id} was not found"
                )
            return self._from_row(connection, row)

    def _validate_project(
        self,
        connection: Connection,
        record: AssetProvenanceRecord,
        asset: RowMapping,
    ) -> UUID | None:
        asset_project_id = cast(UUID | None, asset["project_id"])
        if record.project_id is None:
            if asset_project_id is not None:
                raise PersistenceReferenceError(
                    f"project-scoped asset {record.asset_id} requires provenance project_id"
                )
            return None
        project = self._require_external(
            connection,
            self.projects_table,
            record.project_id,
            "project",
        )
        if project["id"] != asset_project_id:
            raise PersistenceReferenceError(
                f"asset provenance project {record.project_id} does not own {record.asset_id}"
            )
        return cast(UUID, project["id"])

    def _validate_storage(
        self,
        connection: Connection,
        record: AssetProvenanceRecord,
        asset: RowMapping,
    ) -> UUID | None:
        if record.storage_object_id is None:
            return None
        storage = self._require_external(
            connection,
            self.storage_table,
            record.storage_object_id,
            "storage object",
        )
        if storage["project_id"] != asset["project_id"]:
            raise PersistenceReferenceError(
                f"storage object {record.storage_object_id} is outside the asset project boundary"
            )
        if str(storage["sha256"]) != str(asset["sha256"]):
            raise PersistenceConflictError(
                f"storage object {record.storage_object_id} hash does not match asset {record.asset_id}"
            )
        return cast(UUID, storage["id"])

    def _validate_rights(
        self,
        connection: Connection,
        record: AssetProvenanceRecord,
        asset: RowMapping,
    ) -> UUID | None:
        asset_rights_id = cast(UUID | None, asset["rights_record_id"])
        if record.rights_record_id is None:
            if asset_rights_id is not None:
                raise PersistenceReferenceError(
                    f"rights-aware asset {record.asset_id} requires provenance rights_record_id"
                )
            return None
        rights = self._require_external(
            connection,
            self.rights_table,
            record.rights_record_id,
            "rights record",
        )
        if rights["id"] != asset_rights_id:
            raise PersistenceReferenceError(
                f"provenance rights {record.rights_record_id} do not match asset {record.asset_id}"
            )
        if str(rights["subject_type"]) != "asset" or str(rights["subject_id"]) != record.asset_id:
            raise PersistenceReferenceError(
                f"rights record {record.rights_record_id} is not bound to asset {record.asset_id}"
            )
        return cast(UUID, rights["id"])

    @staticmethod
    def _validate_content_hash(record: AssetProvenanceRecord, asset: RowMapping) -> None:
        if record.content_sha256 != str(asset["sha256"]):
            raise PersistenceConflictError(
                f"provenance hash does not match canonical asset {record.asset_id}"
            )

    def _validate_derived_parent(
        self,
        connection: Connection,
        record: AssetProvenanceRecord,
        asset: RowMapping,
    ) -> None:
        if record.source_kind is not AssetProvenanceSource.DERIVED:
            return
        parent_id = connection.execute(
            select(self.asset_parents_table.c.parent_asset_id)
            .where(self.asset_parents_table.c.child_asset_id == asset["id"])
            .limit(1)
        ).scalar_one_or_none()
        if parent_id is None:
            raise PersistenceReferenceError(
                f"derived provenance requires an existing parent for asset {record.asset_id}"
            )

    def _from_row(self, connection: Connection, row: RowMapping) -> AssetProvenanceRecord:
        persisted_schema_version = int(row["schema_version"])
        if persisted_schema_version != SCHEMA_VERSION:
            raise PersistenceReferenceError(
                "unsupported asset provenance schema version "
                f"{persisted_schema_version}; expected {SCHEMA_VERSION}"
            )
        schema_version = cast(SchemaVersion, persisted_schema_version)
        return AssetProvenanceRecord(
            schema_version=schema_version,
            provenance_record_id=str(row["external_id"]),
            asset_id=self._external_for_internal(
                connection,
                self.assets_table,
                cast(UUID, row["asset_id"]),
                "asset",
            ),
            project_id=self._optional_external_for_internal(
                connection,
                self.projects_table,
                cast(UUID | None, row["project_id"]),
                "project",
            ),
            storage_object_id=self._optional_external_for_internal(
                connection,
                self.storage_table,
                cast(UUID | None, row["storage_object_id"]),
                "storage object",
            ),
            source_kind=AssetProvenanceSource(str(row["source_kind"])),
            source_reference=(
                str(row["source_reference"]) if row["source_reference"] is not None else None
            ),
            import_reference=(
                str(row["import_reference"]) if row["import_reference"] is not None else None
            ),
            provider_reference=(
                str(row["provider_reference"]) if row["provider_reference"] is not None else None
            ),
            content_sha256=str(row["content_sha256"]),
            rights_record_id=self._optional_external_for_internal(
                connection,
                self.rights_table,
                cast(UUID | None, row["rights_record_id"]),
                "rights record",
            ),
            created_at=row["created_at"],
        )

    def _row_by_external(self, connection: Connection, external_id: str) -> RowMapping | None:
        return connection.execute(
            select(self.provenance_table).where(self.provenance_table.c.external_id == external_id)
        ).mappings().one_or_none()

    @staticmethod
    def _require_external(
        connection: Connection,
        table: object,
        external_id: str,
        label: str,
    ) -> RowMapping:
        typed_table = cast(object, table)
        row = connection.execute(
            select(typed_table).where(typed_table.c.external_id == external_id)  # type: ignore[attr-defined]
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing {label}:{external_id}")
        return row

    @staticmethod
    def _external_for_internal(
        connection: Connection,
        table: object,
        internal_id: UUID,
        label: str,
    ) -> str:
        typed_table = cast(object, table)
        value = connection.execute(
            select(typed_table.c.external_id).where(typed_table.c.id == internal_id)  # type: ignore[attr-defined]
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing {label} external identity for {internal_id}")
        return str(value)

    @classmethod
    def _optional_external_for_internal(
        cls,
        connection: Connection,
        table: object,
        internal_id: UUID | None,
        label: str,
    ) -> str | None:
        if internal_id is None:
            return None
        return cls._external_for_internal(connection, table, internal_id, label)
