from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping

from ..common import AuditFields
from ..delivery import AssetAccessClass, DeliverySubject, bind_delivery_subject
from ..production import Asset, RightsRecord
from ..provenance import (
    AssetProvenanceRecord,
    AssetProvenanceSource,
    evaluate_asset_usability,
)
from ..storage import StorageBackend, StorageObject
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

DeliveryPolicyAction = Literal["created", "reused", "updated"]


class DeliveryResolutionError(PersistenceConflictError):
    """Canonical rows cannot be resolved into one safe delivery authority."""


@dataclass(frozen=True)
class DeliveryPolicyResult:
    action: DeliveryPolicyAction
    asset_id: str
    access_class: AssetAccessClass
    revision: int


@dataclass(frozen=True)
class ResolvedDeliveryAsset:
    subject: DeliverySubject
    storage_object: StorageObject
    provenance: AssetProvenanceRecord
    rights_record: RightsRecord
    access_class: AssetAccessClass


class PostgresDeliveryRepository:
    """Resolve canonical, rights-aware delivery subjects and persisted access policy."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "asset_delivery_policies",
            "asset_provenance_records",
            "assets",
            "projects",
            "rights_records",
            "storage_objects",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"delivery persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.policies = metadata.tables["core.asset_delivery_policies"]
        self.provenance = metadata.tables["core.asset_provenance_records"]
        self.assets = metadata.tables["core.assets"]
        self.projects = metadata.tables["core.projects"]
        self.rights = metadata.tables["core.rights_records"]
        self.storage = metadata.tables["core.storage_objects"]

    def set_access_class(
        self,
        asset_id: str,
        access_class: AssetAccessClass,
        *,
        now: datetime,
    ) -> DeliveryPolicyResult:
        with self.engine.begin() as connection:
            asset = self._require_external(connection, self.assets, asset_id, "asset")
            project_id = cast(UUID | None, asset["project_id"])
            if project_id is None:
                raise DeliveryResolutionError("delivery policy requires a project-scoped asset")
            existing = connection.execute(
                select(self.policies)
                .where(self.policies.c.asset_id == asset["id"])
                .with_for_update()
            ).mappings().one_or_none()
            if existing is None:
                connection.execute(
                    insert(self.policies).values(
                        id=uuid4(),
                        asset_id=asset["id"],
                        project_id=project_id,
                        access_class=access_class.value,
                        created_at=now,
                        updated_at=now,
                        revision=1,
                    )
                )
                return DeliveryPolicyResult("created", asset_id, access_class, 1)
            if existing["project_id"] != project_id:
                raise DeliveryResolutionError("delivery policy project does not match asset")
            persisted = AssetAccessClass(str(existing["access_class"]))
            if persisted is access_class:
                return DeliveryPolicyResult(
                    "reused",
                    asset_id,
                    persisted,
                    int(existing["revision"]),
                )
            revision = int(existing["revision"]) + 1
            connection.execute(
                update(self.policies)
                .where(self.policies.c.id == existing["id"])
                .values(access_class=access_class.value, updated_at=now, revision=revision)
            )
            return DeliveryPolicyResult("updated", asset_id, access_class, revision)

    def resolve(self, asset_id: str) -> ResolvedDeliveryAsset:
        with self.engine.connect() as connection:
            asset_row = self._require_external(connection, self.assets, asset_id, "asset")
            if asset_row["project_id"] is None:
                raise DeliveryResolutionError("delivery requires a project-scoped asset")

            provenance_rows = list(
                connection.execute(
                    select(self.provenance)
                    .where(self.provenance.c.asset_id == asset_row["id"])
                    .where(self.provenance.c.storage_object_id.is_not(None))
                    .order_by(self.provenance.c.created_at.desc(), self.provenance.c.id.desc())
                ).mappings()
            )
            if not provenance_rows:
                raise DeliveryResolutionError("asset has no storage-backed provenance")
            if len(provenance_rows) != 1:
                raise DeliveryResolutionError(
                    "asset delivery provenance is ambiguous; exactly one "
                    "storage-backed record is required"
                )
            provenance_row = provenance_rows[0]
            storage_row = self._require_internal(
                connection,
                self.storage,
                cast(UUID, provenance_row["storage_object_id"]),
                "storage object",
            )

            rights_id = cast(UUID | None, asset_row["rights_record_id"])
            if rights_id is None:
                raise DeliveryResolutionError("delivery requires an asset rights record")
            rights_row = self._require_internal(
                connection,
                self.rights,
                rights_id,
                "rights record",
            )

            asset = self._asset(connection, asset_row)
            provenance = self._provenance(connection, provenance_row)
            storage = self._storage(connection, storage_row)
            rights = self._rights(rights_row)
            decision = evaluate_asset_usability(asset, provenance, rights)
            if not decision.usable:
                reasons = ", ".join(item.value for item in decision.rejections)
                raise DeliveryResolutionError(f"asset is not delivery-usable: {reasons}")

            policy = connection.execute(
                select(self.policies).where(self.policies.c.asset_id == asset_row["id"])
            ).mappings().one_or_none()
            access_class = AssetAccessClass.PRIVATE
            if policy is not None:
                if policy["project_id"] != asset_row["project_id"]:
                    raise DeliveryResolutionError("delivery policy project does not match asset")
                access_class = AssetAccessClass(str(policy["access_class"]))

            subject = bind_delivery_subject(
                asset,
                provenance,
                storage,
                access_class=access_class,
            )
            return ResolvedDeliveryAsset(
                subject=subject,
                storage_object=storage,
                provenance=provenance,
                rights_record=rights,
                access_class=access_class,
            )

    def _asset(self, connection: Connection, row: RowMapping) -> Asset:
        return Asset(
            schema_version=row["schema_version"],
            asset_id=str(row["external_id"]),
            project_id=self._external_for_internal(
                connection,
                self.projects,
                cast(UUID, row["project_id"]),
                "project",
            ),
            kind=row["kind"],
            uri=str(row["uri"]),
            sha256=str(row["sha256"]),
            mime_type=str(row["mime_type"]),
            size_bytes=int(row["size_bytes"]),
            duration_seconds=(
                float(row["duration_seconds"])
                if row["duration_seconds"] is not None
                else None
            ),
            width=(int(row["width"]) if row["width"] is not None else None),
            height=(int(row["height"]) if row["height"] is not None else None),
            provider_id=(str(row["provider_id"]) if row["provider_id"] is not None else None),
            model_provider_id=(
                str(row["model_provider_id"])
                if row["model_provider_id"] is not None
                else None
            ),
            provider_model_id=(
                str(row["provider_model_id"])
                if row["provider_model_id"] is not None
                else None
            ),
            generation_attempt_id=self._optional_external_for_internal(
                connection,
                self._table("generation_attempts", connection),
                cast(UUID | None, row["generation_attempt_id"]),
                "generation attempt",
            ),
            rights_record_id=self._external_for_internal(
                connection,
                self.rights,
                cast(UUID, row["rights_record_id"]),
                "rights record",
            ),
            canonical_status=row["canonical_status"],
            retention_class=str(row["retention_class"]),
            audit=AuditFields(
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                created_by=row["created_by"],
                revision=int(row["revision"]),
            ),
        )

    def _provenance(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> AssetProvenanceRecord:
        return AssetProvenanceRecord(
            schema_version=row["schema_version"],
            provenance_record_id=str(row["external_id"]),
            asset_id=self._external_for_internal(
                connection,
                self.assets,
                cast(UUID, row["asset_id"]),
                "asset",
            ),
            project_id=self._optional_external_for_internal(
                connection,
                self.projects,
                cast(UUID | None, row["project_id"]),
                "project",
            ),
            storage_object_id=self._optional_external_for_internal(
                connection,
                self.storage,
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
                str(row["provider_reference"])
                if row["provider_reference"] is not None
                else None
            ),
            content_sha256=str(row["content_sha256"]),
            rights_record_id=self._optional_external_for_internal(
                connection,
                self.rights,
                cast(UUID | None, row["rights_record_id"]),
                "rights record",
            ),
            created_at=row["created_at"],
        )

    def _storage(self, connection: Connection, row: RowMapping) -> StorageObject:
        return StorageObject(
            schema_version=row["schema_version"],
            storage_object_id=str(row["external_id"]),
            project_id=self._optional_external_for_internal(
                connection,
                self.projects,
                cast(UUID | None, row["project_id"]),
                "project",
            ),
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
                str(row["original_filename"])
                if row["original_filename"] is not None
                else None
            ),
            lifecycle_class=str(row["lifecycle_class"]),
            audit=AuditFields(
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                created_by=row["created_by"],
                revision=int(row["revision"]),
            ),
        )

    @staticmethod
    def _rights(row: RowMapping) -> RightsRecord:
        return RightsRecord(
            schema_version=row["schema_version"],
            rights_record_id=str(row["external_id"]),
            subject_type=str(row["subject_type"]),
            subject_id=str(row["subject_id"]),
            provider_id=(str(row["provider_id"]) if row["provider_id"] is not None else None),
            model_provider_id=(
                str(row["model_provider_id"])
                if row["model_provider_id"] is not None
                else None
            ),
            model_id=(str(row["model_id"]) if row["model_id"] is not None else None),
            plan_or_tier=(
                str(row["plan_or_tier"]) if row["plan_or_tier"] is not None else None
            ),
            commercial_use=row["commercial_use"],
            watermark_required=row["watermark_required"],
            source_basis=(
                str(row["source_basis"]) if row["source_basis"] is not None else None
            ),
            consent_reference=(
                str(row["consent_reference"])
                if row["consent_reference"] is not None
                else None
            ),
            evidence_urls=list(row["evidence_urls"]),
            verified_at=row["verified_at"],
            publication_blocked=bool(row["publication_blocked"]),
            notes=list(row["notes"]),
        )

    def _table(self, name: str, connection: Connection) -> Table:
        del connection
        metadata = MetaData()
        metadata.reflect(bind=self.engine, schema="core", only=[name])
        key = f"core.{name}"
        if key not in metadata.tables:
            raise PersistenceReferenceError(f"missing required table {key}")
        return metadata.tables[key]

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
            raise PersistenceNotFoundError(f"{label} {external_id} was not found")
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
            raise PersistenceReferenceError(
                f"missing {label} external identity for {internal_id}"
            )
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
