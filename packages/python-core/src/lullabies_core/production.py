from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    ApprovalDecision,
    ApprovalId,
    AssetId,
    AssetKind,
    AttemptId,
    AttemptStatus,
    AuditFields,
    CanonicalStatus,
    CommercialUseStatus,
    ContentId,
    CostRecordId,
    JobId,
    JobStatus,
    NonNegativeDecimal,
    ProjectId,
    QARecordId,
    RightsRecordId,
    SchemaVersion,
    ShotId,
    StrictModel,
)


class Asset(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    asset_id: AssetId
    project_id: ProjectId | None = None
    kind: AssetKind
    uri: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    mime_type: str = Field(min_length=3)
    size_bytes: Annotated[int, Field(ge=0)]
    duration_seconds: Annotated[float | None, Field(gt=0)] = None
    width: Annotated[int | None, Field(gt=0)] = None
    height: Annotated[int | None, Field(gt=0)] = None
    parent_asset_ids: list[AssetId] = Field(default_factory=list)
    provider_id: str | None = None
    model_provider_id: str | None = None
    provider_model_id: str | None = None
    generation_attempt_id: AttemptId | None = None
    rights_record_id: RightsRecordId | None = None
    canonical_status: CanonicalStatus = CanonicalStatus.CANDIDATE
    retention_class: str = "project"
    audit: AuditFields

    @model_validator(mode="after")
    def normalize_model_provider(self) -> Asset:
        if self.provider_id is not None and self.model_provider_id is None:
            self.model_provider_id = self.provider_id
        return self


class ProviderModelRef(StrictModel):
    """One executable model route.

    `provider_id` is the transport/billing API provider. `model_provider_id` identifies
    the underlying model vendor. They are identical for direct APIs and may differ for
    gateways/aggregators such as multi-model API services.
    """

    provider_id: str = Field(min_length=1, max_length=120)
    model_provider_id: str | None = Field(default=None, min_length=1, max_length=120)
    model_id: str = Field(min_length=1, max_length=180)
    capability: str = Field(min_length=1, max_length=120)
    access_class: str
    registry_verified_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def normalize_direct_provider(self) -> ProviderModelRef:
        if self.model_provider_id is None:
            self.model_provider_id = self.provider_id
        return self


class GenerationRequest(StrictModel):
    capability: str = Field(min_length=1)
    project_id: ProjectId
    shot_id: ShotId | None = None
    content_id: ContentId | None = None
    prompt_id: str | None = None
    prompt_version: str | None = None
    input_asset_ids: list[AssetId] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    target_duration_seconds: Annotated[float | None, Field(gt=0)] = None
    requires_commercial_rights: bool = True
    requires_character_continuity: bool = False
    idempotency_key: str = Field(min_length=8, max_length=200)


class GenerationAttempt(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    attempt_id: AttemptId
    job_id: JobId
    attempt_number: Annotated[int, Field(ge=1)]
    provider: ProviderModelRef
    request: GenerationRequest
    provider_generation_id: str | None = None
    started_at: AwareDatetime
    finished_at: AwareDatetime | None = None
    output_asset_ids: list[AssetId] = Field(default_factory=list)
    status: AttemptStatus = AttemptStatus.RUNNING
    normalized_error_code: str | None = None
    error_detail: str | None = None
    free_credits_used: NonNegativeDecimal | None = None
    paid_cost: NonNegativeDecimal | None = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    qa_record_ids: list[QARecordId] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_attempt_timestamps(self) -> GenerationAttempt:
        if self.finished_at is not None and self.finished_at < self.started_at:
            raise ValueError("finished_at cannot precede started_at")
        return self


class Job(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    job_id: JobId
    project_id: ProjectId
    job_type: str = Field(min_length=1, max_length=120)
    status: JobStatus = JobStatus.QUEUED
    priority: Annotated[int, Field(ge=0, le=100)] = 50
    idempotency_key: str = Field(min_length=8, max_length=200)
    parent_job_id: JobId | None = None
    dependency_job_ids: list[JobId] = Field(default_factory=list)
    shot_id: ShotId | None = None
    content_id: ContentId | None = None
    attempt_ids: list[AttemptId] = Field(default_factory=list)
    selected_attempt_id: AttemptId | None = None
    retry_budget_remaining: Annotated[int, Field(ge=0)] = 3
    blocked_reason: str | None = None
    claimed_by: str | None = None
    lease_expires_at: AwareDatetime | None = None
    audit: AuditFields

    @model_validator(mode="after")
    def validate_selected_attempt(self) -> Job:
        if self.selected_attempt_id and self.selected_attempt_id not in self.attempt_ids:
            raise ValueError("selected_attempt_id must be present in attempt_ids")
        return self


class QARecord(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    qa_record_id: QARecordId
    subject_type: str
    subject_id: str
    gate: str
    passed: bool
    critical: bool = False
    score: Annotated[float | None, Field(ge=0, le=100)] = None
    findings: list[str] = Field(default_factory=list)
    reviewer: str | None = None
    created_at: AwareDatetime


class CostRecord(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    cost_record_id: CostRecordId
    project_id: ProjectId
    job_id: JobId | None = None
    attempt_id: AttemptId | None = None
    provider_id: str
    model_provider_id: str | None = None
    model_id: str
    free_credits_used: NonNegativeDecimal = Decimal("0")
    paid_cost: NonNegativeDecimal = Decimal("0")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    estimated: bool = False
    recorded_at: AwareDatetime

    @model_validator(mode="after")
    def normalize_model_provider(self) -> CostRecord:
        if self.model_provider_id is None:
            self.model_provider_id = self.provider_id
        return self


class RightsRecord(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    rights_record_id: RightsRecordId
    subject_type: str
    subject_id: str
    provider_id: str | None = None
    model_provider_id: str | None = None
    model_id: str | None = None
    plan_or_tier: str | None = None
    commercial_use: CommercialUseStatus = CommercialUseStatus.UNKNOWN
    watermark_required: bool | None = None
    source_basis: str | None = None
    consent_reference: str | None = None
    evidence_urls: list[str] = Field(default_factory=list)
    verified_at: AwareDatetime | None = None
    publication_blocked: bool = True
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_and_validate_rights(self) -> RightsRecord:
        if self.provider_id is not None and self.model_provider_id is None:
            self.model_provider_id = self.provider_id
        if not self.publication_blocked and self.commercial_use != CommercialUseStatus.ALLOWED:
            raise ValueError("publication may be unblocked only when commercial use is allowed")
        return self


class Approval(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    approval_id: ApprovalId
    project_id: ProjectId
    subject_type: str
    subject_id: str
    decision: ApprovalDecision
    actor: str
    reason: str | None = None
    created_at: AwareDatetime
