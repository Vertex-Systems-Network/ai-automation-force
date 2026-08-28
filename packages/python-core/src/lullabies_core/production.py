from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import Field, model_validator

from .common import AssetKind, AuditFields, CanonicalStatus, JobStatus, SCHEMA_VERSION, StrictModel


class Asset(StrictModel):
    schema_version: int = SCHEMA_VERSION
    asset_id: str = Field(pattern=r"^AST-[0-9]{6}$")
    project_id: str | None = Field(default=None, pattern=r"^PRJ-[0-9]{6}$")
    kind: AssetKind
    uri: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    mime_type: str = Field(min_length=3)
    size_bytes: Annotated[int, Field(ge=0)]
    duration_seconds: Annotated[float | None, Field(gt=0)] = None
    width: Annotated[int | None, Field(gt=0)] = None
    height: Annotated[int | None, Field(gt=0)] = None
    parent_asset_ids: list[str] = Field(default_factory=list)
    provider_id: str | None = None
    provider_model_id: str | None = None
    generation_attempt_id: str | None = Field(default=None, pattern=r"^ATT-[0-9]{6}$")
    rights_record_id: str | None = Field(default=None, pattern=r"^RGT-[0-9]{6}$")
    canonical_status: CanonicalStatus = CanonicalStatus.CANDIDATE
    retention_class: str = "project"
    audit: AuditFields


class ProviderModelRef(StrictModel):
    provider_id: str = Field(min_length=1, max_length=120)
    model_id: str = Field(min_length=1, max_length=180)
    capability: str = Field(min_length=1, max_length=120)
    access_class: str
    registry_verified_at: datetime | None = None


class GenerationRequest(StrictModel):
    capability: str = Field(min_length=1)
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    shot_id: str | None = Field(default=None, pattern=r"^SHT-[0-9]{6}$")
    content_id: str | None = Field(default=None, pattern=r"^CNT-[0-9]{6}$")
    prompt_id: str | None = None
    prompt_version: str | None = None
    input_asset_ids: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    target_duration_seconds: Annotated[float | None, Field(gt=0)] = None
    requires_commercial_rights: bool = True
    requires_character_continuity: bool = False
    idempotency_key: str = Field(min_length=8, max_length=200)


class GenerationAttempt(StrictModel):
    schema_version: int = SCHEMA_VERSION
    attempt_id: str = Field(pattern=r"^ATT-[0-9]{6}$")
    job_id: str = Field(pattern=r"^JOB-[0-9]{6}$")
    attempt_number: Annotated[int, Field(ge=1)]
    provider: ProviderModelRef
    request: GenerationRequest
    provider_generation_id: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    output_asset_ids: list[str] = Field(default_factory=list)
    status: str = "running"
    normalized_error_code: str | None = None
    error_detail: str | None = None
    free_credits_used: Decimal | None = None
    paid_cost: Decimal | None = None
    currency: str = "USD"
    qa_record_ids: list[str] = Field(default_factory=list)


class Job(StrictModel):
    schema_version: int = SCHEMA_VERSION
    job_id: str = Field(pattern=r"^JOB-[0-9]{6}$")
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    job_type: str = Field(min_length=1, max_length=120)
    status: JobStatus = JobStatus.QUEUED
    priority: Annotated[int, Field(ge=0, le=100)] = 50
    idempotency_key: str = Field(min_length=8, max_length=200)
    parent_job_id: str | None = Field(default=None, pattern=r"^JOB-[0-9]{6}$")
    dependency_job_ids: list[str] = Field(default_factory=list)
    shot_id: str | None = Field(default=None, pattern=r"^SHT-[0-9]{6}$")
    content_id: str | None = Field(default=None, pattern=r"^CNT-[0-9]{6}$")
    attempt_ids: list[str] = Field(default_factory=list)
    selected_attempt_id: str | None = Field(default=None, pattern=r"^ATT-[0-9]{6}$")
    retry_budget_remaining: Annotated[int, Field(ge=0)] = 3
    blocked_reason: str | None = None
    claimed_by: str | None = None
    lease_expires_at: datetime | None = None
    audit: AuditFields

    @model_validator(mode="after")
    def validate_selected_attempt(self) -> "Job":
        if self.selected_attempt_id and self.selected_attempt_id not in self.attempt_ids:
            raise ValueError("selected_attempt_id must be present in attempt_ids")
        return self


class QARecord(StrictModel):
    schema_version: int = SCHEMA_VERSION
    qa_record_id: str = Field(pattern=r"^QAR-[0-9]{6}$")
    subject_type: str
    subject_id: str
    gate: str
    passed: bool
    critical: bool = False
    score: Annotated[float | None, Field(ge=0, le=100)] = None
    findings: list[str] = Field(default_factory=list)
    reviewer: str | None = None
    created_at: datetime


class CostRecord(StrictModel):
    schema_version: int = SCHEMA_VERSION
    cost_record_id: str = Field(pattern=r"^CST-[0-9]{6}$")
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    job_id: str | None = Field(default=None, pattern=r"^JOB-[0-9]{6}$")
    attempt_id: str | None = Field(default=None, pattern=r"^ATT-[0-9]{6}$")
    provider_id: str
    model_id: str
    free_credits_used: Decimal = Decimal("0")
    paid_cost: Decimal = Decimal("0")
    currency: str = "USD"
    estimated: bool = False
    recorded_at: datetime


class RightsRecord(StrictModel):
    schema_version: int = SCHEMA_VERSION
    rights_record_id: str = Field(pattern=r"^RGT-[0-9]{6}$")
    subject_type: str
    subject_id: str
    provider_id: str | None = None
    model_id: str | None = None
    plan_or_tier: str | None = None
    commercial_use: str = "unknown"
    watermark_required: bool | None = None
    source_basis: str | None = None
    consent_reference: str | None = None
    evidence_urls: list[str] = Field(default_factory=list)
    verified_at: datetime | None = None
    publication_blocked: bool = True
    notes: list[str] = Field(default_factory=list)


class Approval(StrictModel):
    schema_version: int = SCHEMA_VERSION
    approval_id: str = Field(pattern=r"^APR-[0-9]{6}$")
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    subject_type: str
    subject_id: str
    decision: str
    actor: str
    reason: str | None = None
    created_at: datetime
