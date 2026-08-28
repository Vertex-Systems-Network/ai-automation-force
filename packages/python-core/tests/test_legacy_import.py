from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from lullabies_core import (
    LEGACY_CONTENT_MAPPING_VERSION,
    LegacyContentImportError,
    LegacyContentImportResult,
    import_legacy_content_package,
    reconcile_legacy_content_import,
)

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_payload() -> dict[str, object]:
    return json.loads((FIXTURES / "legacy-content-package-v1.json").read_text(encoding="utf-8"))


def fixture_text() -> str:
    return (FIXTURES / "legacy-content-v1.md").read_text(encoding="utf-8")


def test_representative_legacy_package_maps_to_canonical_content_without_mutation() -> None:
    payload = fixture_payload()
    original_payload = copy.deepcopy(payload)
    content_text = fixture_text()

    result = import_legacy_content_package(payload, content_text)

    assert payload == original_payload
    assert result.content.content_id == "CNT-000321"
    assert result.content.active_version_id == "CTV-000321"
    assert result.content.source_legacy_package_path == "content/CNT-000321"
    assert result.content.status == "approved"
    assert result.content_version.content_version_id == "CTV-000321"
    assert result.content_version.content_id == "CNT-000321"
    assert result.content_version.version == 1
    assert result.content_version.content_format == "song"
    assert result.content_version.target_duration_seconds == 120
    assert result.content_version.script_or_lyrics == content_text
    assert result.content_version.character_ids == []
    assert result.content_version.tags == ["preschool", "learning", "counting", "stars"]
    assert result.content_version.originality_fingerprint == "legacy-exact-text-fingerprint"
    assert result.report.mapping_version == LEGACY_CONTENT_MAPPING_VERSION
    assert result.report.unmapped_character_names == ["Mira"]
    assert result.report.unmapped_setting == "A soft illustrated night meadow"


def test_repeat_import_is_deterministic_and_idempotency_ready() -> None:
    payload = fixture_payload()
    content_text = fixture_text()

    first = import_legacy_content_package(payload, content_text)
    second = import_legacy_content_package(copy.deepcopy(payload), content_text)

    assert first == second
    assert first.report.import_key == second.report.import_key
    assert first.report.source_fingerprint_sha256 == second.report.source_fingerprint_sha256
    assert first.content.active_version_id == second.content.active_version_id


def test_reconciliation_creates_when_identity_is_not_persisted() -> None:
    imported = import_legacy_content_package(fixture_payload(), fixture_text())

    decision = reconcile_legacy_content_import(imported)

    assert decision.action == "create"
    assert decision.conflict_fields == []
    assert decision.import_key == imported.report.import_key


def test_reconciliation_is_noop_for_exact_repeat_import() -> None:
    imported = import_legacy_content_package(fixture_payload(), fixture_text())

    decision = reconcile_legacy_content_import(
        imported,
        existing_content=imported.content.model_copy(deep=True),
        existing_content_version=imported.content_version.model_copy(deep=True),
        existing_import_key=imported.report.import_key,
    )

    assert decision.action == "noop"
    assert decision.conflict_fields == []


def test_reconciliation_detects_partial_persistence_state() -> None:
    imported = import_legacy_content_package(fixture_payload(), fixture_text())

    decision = reconcile_legacy_content_import(
        imported,
        existing_content=imported.content,
    )

    assert decision.action == "conflict"
    assert decision.conflict_fields == ["content_version"]


def test_reconciliation_rejects_changed_source_for_same_stable_identity() -> None:
    original = import_legacy_content_package(fixture_payload(), fixture_text())
    changed = import_legacy_content_package(
        fixture_payload(),
        fixture_text() + "\nA deliberately changed line.\n",
    )

    decision = reconcile_legacy_content_import(
        changed,
        existing_content=original.content,
        existing_content_version=original.content_version,
        existing_import_key=original.report.import_key,
    )

    assert decision.action == "conflict"
    assert "import_key" in decision.conflict_fields


def test_reconciliation_detects_canonical_record_drift_even_without_import_key() -> None:
    imported = import_legacy_content_package(fixture_payload(), fixture_text())
    drifted_version = imported.content_version.model_copy(
        update={"title": "Unexpected persisted rewrite"},
        deep=True,
    )

    decision = reconcile_legacy_content_import(
        imported,
        existing_content=imported.content,
        existing_content_version=drifted_version,
    )

    assert decision.action == "conflict"
    assert decision.conflict_fields == ["content_version"]


def test_import_result_round_trips_without_identity_drift() -> None:
    result = import_legacy_content_package(fixture_payload(), fixture_text())
    restored = LegacyContentImportResult.model_validate(result.model_dump())

    assert restored == result
    assert restored.report.canonical_content_id == "CNT-000321"
    assert restored.report.canonical_content_version_id == "CTV-000321"


def test_lullaby_mode_maps_to_spoken_or_sung_without_guessing_provider_behavior() -> None:
    speech = fixture_payload()
    speech["content_type"] = "lullaby"
    speech_audio = speech["audio"]
    assert isinstance(speech_audio, dict)
    speech_audio["audio_mode"] = "speech"
    speech_result = import_legacy_content_package(speech, fixture_text())
    assert speech_result.content_version.content_format == "spoken-lullaby"

    music = fixture_payload()
    music["content_type"] = "lullaby"
    music_audio = music["audio"]
    assert isinstance(music_audio, dict)
    music_audio["audio_mode"] = "music"
    music_result = import_legacy_content_package(music, fixture_text())
    assert music_result.content_version.content_format == "sung-lullaby"


def test_import_rejects_missing_duration_instead_of_inventing_one() -> None:
    payload = fixture_payload()
    payload.pop("target_duration_seconds")

    with pytest.raises(LegacyContentImportError) as exc_info:
        import_legacy_content_package(payload, fixture_text())

    assert exc_info.value.code == "LEGACY_DURATION_REQUIRED"
    assert exc_info.value.field == "target_duration_seconds"


def test_import_rejects_duration_outside_canonical_range() -> None:
    payload = fixture_payload()
    payload["target_duration_seconds"] = 30

    with pytest.raises(LegacyContentImportError) as exc_info:
        import_legacy_content_package(payload, fixture_text())

    assert exc_info.value.code == "LEGACY_DURATION_OUT_OF_CANONICAL_RANGE"


def test_import_rejects_empty_resolved_content_text() -> None:
    with pytest.raises(LegacyContentImportError) as exc_info:
        import_legacy_content_package(fixture_payload(), "  \n")

    assert exc_info.value.code == "LEGACY_CONTENT_TEXT_REQUIRED"
    assert exc_info.value.field == "paths.content"


def test_import_rejects_partial_legacy_metadata() -> None:
    payload = fixture_payload()
    payload.pop("objective")

    with pytest.raises(ValidationError, match="objective"):
        import_legacy_content_package(payload, fixture_text())


def test_import_rejects_unknown_top_level_legacy_fields() -> None:
    payload = fixture_payload()
    payload["unexpected_top_level"] = True

    with pytest.raises(ValidationError, match="unexpected_top_level"):
        import_legacy_content_package(payload, fixture_text())


def test_import_rejects_invalid_legacy_content_id() -> None:
    payload = fixture_payload()
    payload["content_id"] = "CNT-invalid"

    with pytest.raises(ValidationError, match="content_id"):
        import_legacy_content_package(payload, fixture_text())


def test_import_rejects_approval_timestamp_before_creation() -> None:
    payload = fixture_payload()
    payload["approved_at"] = "2026-07-31T23:00:00Z"

    with pytest.raises(LegacyContentImportError) as exc_info:
        import_legacy_content_package(payload, fixture_text())

    assert exc_info.value.code == "LEGACY_APPROVAL_PRECEDES_CREATION"


def test_source_fingerprint_changes_when_exact_content_changes() -> None:
    first = import_legacy_content_package(fixture_payload(), fixture_text())
    second = import_legacy_content_package(
        fixture_payload(),
        fixture_text() + "\nA deliberately changed line.\n",
    )

    assert first.report.source_fingerprint_sha256 != second.report.source_fingerprint_sha256
    assert first.report.import_key != second.report.import_key
    assert first.content.active_version_id == second.content.active_version_id
