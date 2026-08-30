from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    AssetId,
    ProjectId,
    RightsRecordId,
    SchemaVersion,
    StorageObjectId,
    StrictModel,
    external_id_pattern,
)

AssetProvenanceRecordId = Annotated[
    str,
    Field(pattern=external_id_pattern("PRV")),
]


class AssetProvenanceSource(StrEnum):
    """Normalized origin class for one append-only asset provenance assertion."""

    UPLOAD = "upload"
    IMPORT = "import"
    PROVIDER = "provider"
    DERIVED = "derived"


class AssetProvenanceRecord(StrictModel):
    """Immutable origin/evidence linkage for one canonical Asset.

    Canonical approval/rejection remains owned by ``Asset.canonical_status`` and legal
    publication state remains owned by ``RightsRecord``. This record only binds the
    canonical asset to physical/source evidence and a witnessed content hash.
    """

    schema_version: SchemaVersion = SCHEMA_VERSION
    provenance_record_id: AssetProvenanceRecordId
    asset_id: AssetId
    project_id: ProjectId | None = None
    storage_object_id: StorageObjectId | None = None
    source_kind: AssetProvenanceSource
    source_reference: str | None = Field(default=None, min_length=1, max_length=2048)
    import_reference: str | None = Field(default=None, min_length=1, max_length=2048)
    provider_reference: str | None = Field(default=None, min_length=1, max_length=2048)
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    rights_record_id: RightsRecordId | None = None
    created_at: AwareDatetime

    @model_validator(mode="after")
    def validate_source_evidence(self) -> AssetProvenanceRecord:
        if (
            self.source_kind is AssetProvenanceSource.UPLOAD
            and self.storage_object_id is None
        ):
            raise ValueError("upload provenance requires storage_object_id")
        if (
            self.source_kind is AssetProvenanceSource.IMPORT
            and self.import_reference is None
        ):
            raise ValueError("import provenance requires import_reference")
        if (
            self.source_kind is AssetProvenanceSource.PROVIDER
            and self.provider_reference is None
        ):
            raise ValueError("provider provenance requires provider_reference")
        return self
