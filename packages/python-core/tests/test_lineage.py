from __future__ import annotations

import pytest
from pydantic import ValidationError

from lullabies_core import CommercialUseStatus, ProductionLineageBundle, RightsRecord

from lineage_fixtures import full_lineage_bundle


def test_full_lineage_validates_and_preserves_stable_ids() -> None:
    bundle = full_lineage_bundle()
    restored = ProductionLineageBundle.model_validate(bundle.model_dump())

    assert restored.project_bundle.project.project_id == "PRJ-000500"
    assert restored.content.content_id == "CNT-000500"
    assert restored.project_bundle.shots[0].selected_take_id == "TAK-000500"
    assert restored.project_bundle.takes[0].attempt_id == "ATT-000500"
    assert restored.attempts[0].job_id == "JOB-000500"
    assert restored.assets[1].generation_attempt_id == "ATT-000500"
    assert restored.cost_records[0].attempt_id == "ATT-000500"
    assert restored.assets[1].rights_record_id == "RGT-000500"
    assert restored.rights_records[0].publication_blocked is True

    character = restored.project_bundle.characters[0]
    assert character.active_version_id == "CHV-000501"
    assert character.lock.pinned_character_version_id == "CHV-000500"


def test_lineage_rejects_missing_asset_parent() -> None:
    data = full_lineage_bundle().model_dump()
    data["assets"][1]["parent_asset_ids"] = ["AST-999999"]

    with pytest.raises(ValidationError, match="missing parents"):
        ProductionLineageBundle.model_validate(data)


def test_lineage_rejects_cross_project_job() -> None:
    data = full_lineage_bundle().model_dump()
    data["jobs"][0]["project_id"] = "PRJ-999999"

    with pytest.raises(ValidationError, match="belongs to another project"):
        ProductionLineageBundle.model_validate(data)


def test_lineage_rejects_missing_locked_character_version() -> None:
    data = full_lineage_bundle().model_dump()
    data["project_bundle"]["character_versions"] = [
        version
        for version in data["project_bundle"]["character_versions"]
        if version["character_version_id"] != "CHV-000500"
    ]

    with pytest.raises(ValidationError, match="lock version is missing"):
        ProductionLineageBundle.model_validate(data)


def test_lineage_rejects_asset_attempt_mismatch() -> None:
    data = full_lineage_bundle().model_dump()
    data["assets"][1]["generation_attempt_id"] = "ATT-999999"

    with pytest.raises(ValidationError, match="missing generation attempt"):
        ProductionLineageBundle.model_validate(data)


def test_lineage_rejects_qa_attached_to_wrong_subject() -> None:
    data = full_lineage_bundle().model_dump()
    data["qa_records"][0]["subject_id"] = "AST-000500"

    with pytest.raises(ValidationError, match="QA record belongs to another subject"):
        ProductionLineageBundle.model_validate(data)


def test_lineage_rejects_actual_cost_without_attempt() -> None:
    data = full_lineage_bundle().model_dump()
    data["cost_records"][0]["attempt_id"] = None

    with pytest.raises(ValidationError, match="actual cost .* requires attempt_id"):
        ProductionLineageBundle.model_validate(data)


def test_rights_are_fail_closed_until_commercial_use_is_allowed() -> None:
    with pytest.raises(ValidationError, match="publication may be unblocked"):
        RightsRecord(
            rights_record_id="RGT-000900",
            subject_type="asset",
            subject_id="AST-000900",
            commercial_use=CommercialUseStatus.UNKNOWN,
            publication_blocked=False,
        )

    allowed = RightsRecord(
        rights_record_id="RGT-000901",
        subject_type="asset",
        subject_id="AST-000901",
        commercial_use=CommercialUseStatus.ALLOWED,
        publication_blocked=False,
    )
    assert allowed.publication_blocked is False
