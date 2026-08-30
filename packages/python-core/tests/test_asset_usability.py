from __future__ import annotations

from ai_automation_force_core import (
    AssetProvenanceRecord,
    AssetProvenanceSource,
    AssetUsabilityRejection,
    CanonicalStatus,
    CommercialUseStatus,
    evaluate_asset_usability,
)
from lineage_fixtures import NOW, full_lineage_bundle


def _provider_provenance():
    bundle = full_lineage_bundle()
    asset = bundle.assets[1]
    return bundle, asset, AssetProvenanceRecord(
        provenance_record_id="PRV-000500",
        asset_id=asset.asset_id,
        project_id=asset.project_id,
        storage_object_id="STO-000500",
        source_kind=AssetProvenanceSource.PROVIDER,
        provider_reference="provider-job-500",
        content_sha256=asset.sha256,
        rights_record_id=asset.rights_record_id,
        created_at=NOW,
    )


def test_approved_asset_is_not_usable_with_unresolved_rights() -> None:
    bundle, asset, provenance = _provider_provenance()
    rights = bundle.rights_records[0]

    decision = evaluate_asset_usability(asset, provenance, rights)

    assert decision.usable is False
    assert decision.rejections == [
        AssetUsabilityRejection.COMMERCIAL_USE_NOT_ALLOWED,
        AssetUsabilityRejection.RIGHTS_NOT_VERIFIED,
        AssetUsabilityRejection.PUBLICATION_BLOCKED,
    ]


def test_asset_becomes_usable_only_when_all_default_policy_evidence_is_satisfied() -> None:
    bundle, asset, provenance = _provider_provenance()
    rights = bundle.rights_records[0].model_copy(
        update={
            "commercial_use": CommercialUseStatus.ALLOWED,
            "verified_at": NOW,
            "publication_blocked": False,
        }
    )

    decision = evaluate_asset_usability(asset, provenance, rights)

    assert decision.usable is True
    assert decision.rejections == []


def test_nonapproved_asset_fails_even_with_sufficient_rights() -> None:
    bundle, asset, provenance = _provider_provenance()
    candidate = asset.model_copy(update={"canonical_status": CanonicalStatus.CANDIDATE})
    rights = bundle.rights_records[0].model_copy(
        update={
            "commercial_use": CommercialUseStatus.ALLOWED,
            "verified_at": NOW,
            "publication_blocked": False,
        }
    )

    decision = evaluate_asset_usability(candidate, provenance, rights)

    assert decision.usable is False
    assert decision.rejections == [AssetUsabilityRejection.NOT_CANONICALLY_APPROVED]


def test_selected_provenance_must_match_canonical_asset_identity_and_hash() -> None:
    bundle, asset, provenance = _provider_provenance()
    rights = bundle.rights_records[0].model_copy(
        update={
            "commercial_use": CommercialUseStatus.ALLOWED,
            "verified_at": NOW,
            "publication_blocked": False,
        }
    )
    mismatched = provenance.model_copy(
        update={
            "project_id": "PRJ-999999",
            "content_sha256": "c" * 64,
        }
    )

    decision = evaluate_asset_usability(asset, mismatched, rights)

    assert decision.usable is False
    assert decision.rejections == [
        AssetUsabilityRejection.PROVENANCE_PROJECT_MISMATCH,
        AssetUsabilityRejection.PROVENANCE_HASH_MISMATCH,
    ]
