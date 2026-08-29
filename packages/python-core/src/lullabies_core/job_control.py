from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel

from .common import JobStatus

TERMINAL_JOB_STATUSES = frozenset(
    {
        JobStatus.COMPLETED,
        JobStatus.PERMANENT_FAILED,
        JobStatus.CANCELLED,
    }
)

JOB_STATUS_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.ELIGIBLE, JobStatus.CANCELLED}),
    JobStatus.ELIGIBLE: frozenset(
        {
            JobStatus.CLAIMED,
            JobStatus.BLOCKED_BUDGET,
            JobStatus.BLOCKED_LICENSE,
            JobStatus.BLOCKED_CAPABILITY,
            JobStatus.MANUAL_HANDOFF,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.CLAIMED: frozenset(
        {
            JobStatus.RUNNING,
            JobStatus.ELIGIBLE,
            JobStatus.RETRYABLE_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.RUNNING: frozenset(
        {
            JobStatus.WAITING_PROVIDER,
            JobStatus.WAITING_QUOTA,
            JobStatus.WAITING_HUMAN,
            JobStatus.QA,
            JobStatus.COMPLETED,
            JobStatus.RETRYABLE_FAILED,
            JobStatus.BLOCKED_BUDGET,
            JobStatus.BLOCKED_LICENSE,
            JobStatus.BLOCKED_CAPABILITY,
            JobStatus.MANUAL_HANDOFF,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.WAITING_PROVIDER: frozenset(
        {
            JobStatus.RUNNING,
            JobStatus.RETRYABLE_FAILED,
            JobStatus.MANUAL_HANDOFF,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.WAITING_QUOTA: frozenset(
        {
            JobStatus.ELIGIBLE,
            JobStatus.MANUAL_HANDOFF,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.WAITING_HUMAN: frozenset(
        {
            JobStatus.ELIGIBLE,
            JobStatus.RUNNING,
            JobStatus.MANUAL_HANDOFF,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.QA: frozenset(
        {
            JobStatus.COMPLETED,
            JobStatus.RETRYABLE_FAILED,
            JobStatus.WAITING_HUMAN,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.RETRYABLE_FAILED: frozenset(
        {
            JobStatus.ELIGIBLE,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.BLOCKED_BUDGET: frozenset(
        {JobStatus.ELIGIBLE, JobStatus.MANUAL_HANDOFF, JobStatus.CANCELLED}
    ),
    JobStatus.BLOCKED_LICENSE: frozenset(
        {JobStatus.ELIGIBLE, JobStatus.MANUAL_HANDOFF, JobStatus.CANCELLED}
    ),
    JobStatus.BLOCKED_CAPABILITY: frozenset(
        {JobStatus.ELIGIBLE, JobStatus.MANUAL_HANDOFF, JobStatus.CANCELLED}
    ),
    JobStatus.MANUAL_HANDOFF: frozenset(
        {
            JobStatus.ELIGIBLE,
            JobStatus.RUNNING,
            JobStatus.COMPLETED,
            JobStatus.PERMANENT_FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.COMPLETED: frozenset(),
    JobStatus.PERMANENT_FAILED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}


class InvalidJobTransitionError(ValueError):
    pass


def assert_job_transition(current: JobStatus, target: JobStatus) -> None:
    if target not in JOB_STATUS_TRANSITIONS[current]:
        raise InvalidJobTransitionError(
            f"invalid job transition: {current.value} -> {target.value}"
        )


def _json_default(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"value of type {type(value).__name__} is not JSON fingerprintable")


def operation_fingerprint(operation: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        operation,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=_json_default,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


JobSubmitAction = Literal["created", "reused"]


@dataclass(frozen=True)
class JobSubmitResult:
    action: JobSubmitAction
    job_id: str
    operation_fingerprint: str
    revision: int


@dataclass(frozen=True)
class JobLeaseResult:
    job_id: str
    revision: int
    claimed_by: str
    lease_expires_at: datetime


@dataclass(frozen=True)
class JobTransitionResult:
    job_id: str
    previous_status: JobStatus
    status: JobStatus
    revision: int
