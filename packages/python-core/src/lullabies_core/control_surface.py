from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import AwareDatetime, Field

from .common import JobStatus, StrictModel


class JobControlSnapshot(StrictModel):
    job_id: str = Field(pattern=r"^JOB-[0-9]{6,20}$")
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6,20}$")
    job_type: str = Field(min_length=1, max_length=120)
    status: JobStatus
    priority: int = Field(ge=0, le=100)
    idempotency_key: str = Field(min_length=8, max_length=200)
    operation_fingerprint: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    parent_job_id: str | None = None
    dependency_job_ids: list[str] = Field(default_factory=list)
    shot_id: str | None = None
    content_id: str | None = None
    retry_budget_remaining: int = Field(ge=0)
    blocked_reason: str | None = None
    claimed_by: str | None = None
    lease_expires_at: AwareDatetime | None = None
    created_at: AwareDatetime
    updated_at: AwareDatetime
    revision: int = Field(ge=1)
    workflow_execution_id: str | None = Field(default=None, pattern=r"^WFX-[0-9]{6,20}$")


class JobEventRecord(StrictModel):
    event_id: UUID
    job_id: str = Field(pattern=r"^JOB-[0-9]{6,20}$")
    job_revision: int = Field(ge=1)
    event_type: str = Field(min_length=1, max_length=160)
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: AwareDatetime
    published_at: AwareDatetime | None = None


class ProjectJobRecord(StrictModel):
    job_id: str = Field(pattern=r"^JOB-[0-9]{6,20}$")
    status: JobStatus
    job_type: str
    priority: int
    revision: int = Field(ge=1)
    created_at: AwareDatetime
    updated_at: AwareDatetime


class ProjectControlStatus(StrictModel):
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6,20}$")
    total_jobs: int = Field(ge=0)
    job_status_counts: dict[str, int] = Field(default_factory=dict)
    workflow_status_counts: dict[str, int] = Field(default_factory=dict)
    latest_job_updated_at: AwareDatetime | None = None


class JobCommandResult(StrictModel):
    action: Literal["applied", "reused", "noop"]
    command_type: Literal["start", "cancel", "retry"]
    job_id: str = Field(pattern=r"^JOB-[0-9]{6,20}$")
    status: JobStatus
    revision: int = Field(ge=1)
    operation_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    workflow_execution_id: str | None = Field(default=None, pattern=r"^WFX-[0-9]{6,20}$")
    occurred_at: AwareDatetime


class JobCommandConflictError(RuntimeError):
    """A control command conflicts with persisted idempotency or job state."""


class JobCommandVersionConflictError(JobCommandConflictError):
    """The caller supplied a stale expected job revision."""


def control_cursor_key(occurred_at: datetime, event_id: UUID) -> tuple[datetime, UUID]:
    """Return the stable total-order key used by durable event pagination/SSE replay."""

    return occurred_at, event_id
