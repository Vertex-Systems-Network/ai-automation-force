from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    AssetId,
    CanonicalStatus,
    CommercialUseStatus,
    ProjectId,
    RightsRecordId,
    SchemaVersion,
    StorageObjectId,
    StrictModel,
    external_id_pattern,
)
from .production import Asset, RightsRecord

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


class AssetUsabilityPolicy(StrictModel):
    """Explicit evidence requirements for treating an approved Asset as usable.

    The policy composes existing authorities instead of creating a second approval or
    rights state machine. ``Asset.canonical_status`` remains approval authority and
    ``RightsRecord`` remains publication/legal-rights authority.
    """

    require_storage_binding: bool = True
    require_rights_record: bool = True
    require_commercial_use: bool = True
    require_verified_rights: bool = True
    require_publication_unblocked: bool = True


class AssetUsabilityRejection(StrEnum):
    NOT_CANONICALLY_APPROVED = "not-canonically-approved"
    PROVENANCE_ASSET_MISMATCH = "provenance-asset-mismatch"
    PROVENANCE_PROJECT_MISMATCH = "provenance-project-mismatch"
    PROVENANCE_HASH_MISMATCH = "provenance-hash-mismatch"
    STORAGE_EVIDENCE_REQUIRED = "storage-evidence-required"
    RIGHTS_RECORD_REQUIRED = "rights-record-required"
    RIGHTS_REFERENCE_MISMATCH = "rights-reference-mismatch"
    RIGHTS_SUBJECT_MISMATCH = "rights-subject-mismatch"
    COMMERCIAL_USE_NOT_ALLOWED = "commercial-use-not-allowed"
    RIGHTS_NOT_VERIFIED = "rights-not-verified"
    PUBLICATION_BLOCKED = "publication-blocked"


class AssetUsabilityDecision(StrictModel):
    usable: bool
    rejections: list[AssetUsabilityRejection] = Field(default_factory=list)


def evaluate_asset_usability(
    asset: Asset,
    provenance: AssetProvenanceRecord,
    rights_record: RightsRecord | None,
    policy: AssetUsabilityPolicy | None = None,
) -> AssetUsabilityDecision:
    """Fail closed unless the selected evidence satisfies the explicit usage policy.

    Persistence is responsible for proving referenced database rows and storage hashes
    at write time. This pure decision contract composes the canonical asset state,
    selected provenance assertion and legal-rights state for downstream use gates.
    """

    active_policy = policy or AssetUsabilityPolicy()
    rejections: list[AssetUsabilityRejection] = []

    if asset.canonical_status is not CanonicalStatus.APPROVED:
        rejections.append(AssetUsabilityRejection.NOT_CANONICALLY_APPROVED)
    if provenance.asset_id != asset.asset_id:
        rejections.append(AssetUsabilityRejection.PROVENANCE_ASSET_MISMATCH)
    if provenance.project_id != asset.project_id:
        rejections.append(AssetUsabilityRejection.PROVENANCE_PROJECT_MISMATCH)
    if provenance.content_sha256 != asset.sha256:
        rejections.append(AssetUsabilityRejection.PROVENANCE_HASH_MISMATCH)
    if active_policy.require_storage_binding and provenance.storage_object_id is None:
        rejections.append(AssetUsabilityRejection.STORAGE_EVIDENCE_REQUIRED)

    expected_rights_id = asset.rights_record_id
    if active_policy.require_rights_record and expected_rights_id is None:
        rejections.append(AssetUsabilityRejection.RIGHTS_RECORD_REQUIRED)

    if provenance.rights_record_id != expected_rights_id:
        rejections.append(AssetUsabilityRejection.RIGHTS_REFERENCE_MISMATCH)

    if expected_rights_id is not None:
        if rights_record is None:
            rejections.append(AssetUsabilityRejection.RIGHTS_RECORD_REQUIRED)
        else:
            if rights_record.rights_record_id != expected_rights_id:
                rejections.append(AssetUsabilityRejection.RIGHTS_REFERENCE_MISMATCH)
            if (
                rights_record.subject_type != "asset"
                or rights_record.subject_id != asset.asset_id
            ):
                rejections.append(AssetUsabilityRejection.RIGHTS_SUBJECT_MISMATCH)
            if (
                active_policy.require_commercial_use
                and rights_record.commercial_use is not CommercialUseStatus.ALLOWED
            ):
                rejections.append(AssetUsabilityRejection.COMMERCIAL_USE_NOT_ALLOWED)
            if active_policy.require_verified_rights and rights_record.verified_at is None:
                rejections.append(AssetUsabilityRejection.RIGHTS_NOT_VERIFIED)
            if active_policy.require_publication_unblocked and rights_record.publication_blocked:
                rejections.append(AssetUsabilityRejection.PUBLICATION_BLOCKED)

    # Keep reasons deterministic and unique if multiple reference checks converge.
    unique_rejections = list(dict.fromkeys(rejections))
    return AssetUsabilityDecision(
        usable=not unique_rejections,
        rejections=unique_rejections,
    )
