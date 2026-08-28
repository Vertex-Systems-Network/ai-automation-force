from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ai_automation_force_core import (
    Asset,
    AssetKind,
    AudienceProfile,
    AuditFields,
    CastProfile,
    ContentFormat,
    CostRecord,
    GenerationAttempt,
    GenerationRequest,
    Project,
    ProviderModelRef,
    RightsRecord,
)


def now() -> datetime:
    return datetime.now(UTC)


def audit() -> AuditFields:
    current = now()
    return AuditFields(created_at=current, updated_at=current)


def test_schema_version_is_literal_contract() -> None:
    with pytest.raises(ValidationError):
        Project(
            schema_version=2,
            project_id="PRJ-000001",
            title="Bad version",
            audience=AudienceProfile(kind="general"),
            cast=CastProfile(),
            content_format=ContentFormat.MOVIE,
            language="en",
            target_duration_seconds=60,
            audit=audit(),
        )


def test_registry_owned_taxonomy_accepts_configured_custom_values() -> None:
    project = Project(
        project_id="PRJ-000002",
        title="Registry extensibility",
        audience=AudienceProfile(kind="custom"),
        cast=CastProfile(ages=["none", "custom"], genders=["custom"]),
        content_format="custom",
        custom_content_format="interactive-musical-story",
        language="en",
        target_duration_seconds=120,
        audit=audit(),
    )
    assert project.audience.kind == "custom"
    assert project.cast.ages == ["none", "custom"]
    assert project.content_format == "custom"


def test_external_ids_scale_without_breaking_six_digit_ids() -> None:
    project = Project(
        project_id="PRJ-123456789012",
        title="Scaled ID",
        audience=AudienceProfile(kind="general"),
        cast=CastProfile(),
        content_format="movie",
        language="en",
        target_duration_seconds=60,
        audit=audit(),
    )
    assert project.project_id == "PRJ-123456789012"


def test_audit_timestamp_cannot_move_backwards() -> None:
    current = now()
    with pytest.raises(ValidationError, match="updated_at cannot precede created_at"):
        AuditFields(created_at=current, updated_at=current - timedelta(seconds=1))


def test_naive_audit_timestamp_is_rejected() -> None:
    current = datetime.now()
    with pytest.raises(ValidationError):
        AuditFields(created_at=current, updated_at=current)


def test_negative_generation_cost_is_rejected() -> None:
    with pytest.raises(ValidationError):
        CostRecord(
            cost_record_id="CST-000001",
            project_id="PRJ-000001",
            provider_id="gateway",
            model_provider_id="model-vendor",
            model_id="model-v1",
            paid_cost=Decimal("-0.01"),
            recorded_at=now(),
        )


def test_gateway_route_preserves_transport_and_model_vendor() -> None:
    provider = ProviderModelRef(
        provider_id="gateway-api",
        model_provider_id="model-vendor",
        model_id="video-model-v1",
        capability="image-to-video",
        access_class="api-paid",
        registry_verified_at=now(),
    )
    assert provider.provider_id == "gateway-api"
    assert provider.model_provider_id == "model-vendor"


def test_direct_provider_defaults_model_vendor_to_transport_provider() -> None:
    provider = ProviderModelRef(
        provider_id="direct-provider",
        model_id="video-model-v1",
        capability="text-to-video",
        access_class="api-paid",
        registry_verified_at=now(),
    )
    assert provider.model_provider_id == "direct-provider"


def test_generation_attempt_rejects_reverse_timestamps() -> None:
    current = now()
    request = GenerationRequest(
        capability="text-to-video",
        project_id="PRJ-000001",
        idempotency_key="request-0001",
    )
    provider = ProviderModelRef(
        provider_id="direct-provider",
        model_id="video-model-v1",
        capability="text-to-video",
        access_class="api-paid",
    )
    with pytest.raises(ValidationError, match="finished_at cannot precede started_at"):
        GenerationAttempt(
            attempt_id="ATT-000001",
            job_id="JOB-000001",
            attempt_number=1,
            provider=provider,
            request=request,
            started_at=current,
            finished_at=current - timedelta(seconds=1),
        )


def test_asset_and_rights_normalize_direct_model_provider() -> None:
    asset = Asset(
        asset_id="AST-000001",
        project_id="PRJ-000001",
        kind=AssetKind.IMAGE,
        uri="s3://bucket/object",
        sha256="a" * 64,
        mime_type="image/png",
        size_bytes=1,
        provider_id="direct-provider",
        provider_model_id="image-v1",
        audit=audit(),
    )
    rights = RightsRecord(
        rights_record_id="RGT-000001",
        subject_type="asset",
        subject_id=asset.asset_id,
        provider_id="direct-provider",
        model_id="image-v1",
    )
    assert asset.model_provider_id == "direct-provider"
    assert rights.model_provider_id == "direct-provider"
    assert rights.publication_blocked is True
