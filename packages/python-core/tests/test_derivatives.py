from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from lullabies_core.derivatives import (
    DerivativeKind,
    DerivativeRecord,
    DerivativeSpec,
    DerivativeStatus,
    InvalidDerivativeTransitionError,
    assert_derivative_transition,
    derivative_operation_fingerprint,
)

NOW = datetime(2026, 8, 31, 8, 0, tzinfo=UTC)


def thumbnail_spec() -> DerivativeSpec:
    return DerivativeSpec(
        kind=DerivativeKind.THUMBNAIL,
        width=640,
        height=360,
        mime_type="image/jpeg",
        options={"quality": 82, "fit": "cover"},
    )


def fingerprint(spec: DerivativeSpec | None = None) -> str:
    return derivative_operation_fingerprint(
        project_id="PRJ-000001",
        source_asset_id="AST-000001",
        spec=spec or thumbnail_spec(),
    )


def test_derivative_fingerprint_is_semantic_and_deterministic() -> None:
    spec = thumbnail_spec()
    first = fingerprint(spec)
    reordered = DerivativeSpec(
        kind=DerivativeKind.THUMBNAIL,
        width=640,
        height=360,
        mime_type="image/jpeg",
        options={"fit": "cover", "quality": 82},
    )
    second = fingerprint(reordered)
    different = fingerprint(spec.model_copy(update={"width": 320}))

    assert first == second
    assert first != different
    assert len(first) == 64


def test_visual_derivatives_require_dimensions() -> None:
    with pytest.raises(ValidationError, match="requires width and height"):
        DerivativeSpec(kind=DerivativeKind.VIDEO_POSTER, mime_type="image/jpeg")
    with pytest.raises(ValidationError, match="requires width and height"):
        DerivativeSpec(kind=DerivativeKind.VIDEO_PROXY, mime_type="video/mp4")


def test_audio_preview_requires_bounded_duration() -> None:
    with pytest.raises(ValidationError, match="requires max_duration_seconds"):
        DerivativeSpec(kind=DerivativeKind.AUDIO_PREVIEW, mime_type="audio/mpeg")


def test_derivative_record_rejects_semantic_fingerprint_mismatch() -> None:
    with pytest.raises(ValidationError, match="operation_fingerprint does not match"):
        DerivativeRecord(
            derivative_record_id="DRV-000001",
            project_id="PRJ-000001",
            source_asset_id="AST-000001",
            job_id="JOB-000001",
            spec=thumbnail_spec(),
            operation_fingerprint="0" * 64,
            created_at=NOW,
            updated_at=NOW,
        )


def test_completed_derivative_requires_published_output_evidence() -> None:
    with pytest.raises(ValidationError, match="requires output asset and storage object"):
        DerivativeRecord(
            derivative_record_id="DRV-000002",
            project_id="PRJ-000001",
            source_asset_id="AST-000001",
            job_id="JOB-000001",
            spec=thumbnail_spec(),
            operation_fingerprint=fingerprint(),
            status=DerivativeStatus.COMPLETED,
            created_at=NOW,
            updated_at=NOW + timedelta(seconds=1),
            completed_at=NOW + timedelta(seconds=1),
            revision=2,
        )


def test_non_completed_derivative_cannot_publish_outputs() -> None:
    with pytest.raises(ValidationError, match="cannot publish output identities"):
        DerivativeRecord(
            derivative_record_id="DRV-000003",
            project_id="PRJ-000001",
            source_asset_id="AST-000001",
            output_asset_id="AST-000002",
            output_storage_object_id="STO-000002",
            job_id="JOB-000002",
            spec=thumbnail_spec(),
            operation_fingerprint=fingerprint(),
            status=DerivativeStatus.RUNNING,
            created_at=NOW,
            updated_at=NOW,
        )


def test_failed_derivative_requires_error_code_and_no_completion_payload() -> None:
    with pytest.raises(ValidationError, match="failed derivative requires error_code"):
        DerivativeRecord(
            derivative_record_id="DRV-000004",
            project_id="PRJ-000001",
            source_asset_id="AST-000001",
            job_id="JOB-000004",
            spec=thumbnail_spec(),
            operation_fingerprint=fingerprint(),
            status=DerivativeStatus.FAILED,
            created_at=NOW,
            updated_at=NOW + timedelta(seconds=1),
            revision=2,
        )


def test_derivative_transition_matrix_is_fail_closed() -> None:
    assert_derivative_transition(DerivativeStatus.PLANNED, DerivativeStatus.RUNNING)
    assert_derivative_transition(DerivativeStatus.RUNNING, DerivativeStatus.COMPLETED)
    with pytest.raises(InvalidDerivativeTransitionError, match="completed -> running"):
        assert_derivative_transition(DerivativeStatus.COMPLETED, DerivativeStatus.RUNNING)
    with pytest.raises(InvalidDerivativeTransitionError, match="planned -> completed"):
        assert_derivative_transition(DerivativeStatus.PLANNED, DerivativeStatus.COMPLETED)
