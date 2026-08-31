from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from lullabies_core.derivatives import (
    DerivativeKind,
    DerivativeRecord,
    DerivativeSpec,
    DerivativeStatus,
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


def test_derivative_fingerprint_is_semantic_and_deterministic() -> None:
    spec = thumbnail_spec()
    first = derivative_operation_fingerprint(
        project_id="PRJ-000001",
        source_asset_id="AST-000001",
        spec=spec,
    )
    reordered = DerivativeSpec(
        kind=DerivativeKind.THUMBNAIL,
        width=640,
        height=360,
        mime_type="image/jpeg",
        options={"fit": "cover", "quality": 82},
    )
    second = derivative_operation_fingerprint(
        project_id="PRJ-000001",
        source_asset_id="AST-000001",
        spec=reordered,
    )
    different = derivative_operation_fingerprint(
        project_id="PRJ-000001",
        source_asset_id="AST-000001",
        spec=spec.model_copy(update={"width": 320}),
    )

    assert first == second
    assert first != different
    assert len(first) == 64


def test_visual_derivatives_require_dimensions() -> None:
    with pytest.raises(ValidationError, match="requires width and height"):
        DerivativeSpec(kind=DerivativeKind.VIDEO_POSTER, mime_type="image/jpeg")


def test_completed_derivative_requires_published_output_evidence() -> None:
    fingerprint = derivative_operation_fingerprint(
        project_id="PRJ-000001",
        source_asset_id="AST-000001",
        spec=thumbnail_spec(),
    )
    with pytest.raises(ValidationError, match="requires output asset and storage object"):
        DerivativeRecord(
            derivative_record_id="DRV-000001",
            project_id="PRJ-000001",
            source_asset_id="AST-000001",
            job_id="JOB-000001",
            spec=thumbnail_spec(),
            operation_fingerprint=fingerprint,
            status=DerivativeStatus.COMPLETED,
            created_at=NOW,
            completed_at=NOW + timedelta(seconds=1),
        )


def test_non_completed_derivative_cannot_publish_outputs() -> None:
    fingerprint = derivative_operation_fingerprint(
        project_id="PRJ-000001",
        source_asset_id="AST-000001",
        spec=thumbnail_spec(),
    )
    with pytest.raises(ValidationError, match="cannot publish output identities"):
        DerivativeRecord(
            derivative_record_id="DRV-000002",
            project_id="PRJ-000001",
            source_asset_id="AST-000001",
            output_asset_id="AST-000002",
            output_storage_object_id="STO-000002",
            job_id="JOB-000002",
            spec=thumbnail_spec(),
            operation_fingerprint=fingerprint,
            status=DerivativeStatus.RUNNING,
            created_at=NOW,
        )
