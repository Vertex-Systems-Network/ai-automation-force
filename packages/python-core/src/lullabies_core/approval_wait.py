from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal

from .common import ApprovalDecision, JobStatus
from .job_control import operation_fingerprint


class ApprovalWaitKind(StrEnum):
    HUMAN_APPROVAL = "human-approval"
    BUDGET = "budget"
    MANUAL_HANDOFF = "manual-handoff"


class ApprovalRequestStatus(StrEnum):
    PENDING = "pending"
    RESOLVED = "resolved"
    EXPIRED = "expired"


WAIT_JOB_STATUS: dict[ApprovalWaitKind, JobStatus] = {
    ApprovalWaitKind.HUMAN_APPROVAL: JobStatus.WAITING_HUMAN,
    ApprovalWaitKind.BUDGET: JobStatus.BLOCKED_BUDGET,
    ApprovalWaitKind.MANUAL_HANDOFF: JobStatus.MANUAL_HANDOFF,
}


def expected_wait_status(wait_kind: ApprovalWaitKind) -> JobStatus:
    return WAIT_JOB_STATUS[wait_kind]


def resolved_job_status(
    wait_kind: ApprovalWaitKind,
    decision: ApprovalDecision,
) -> JobStatus | None:
    if decision in {ApprovalDecision.APPROVED, ApprovalDecision.WAIVED}:
        return JobStatus.ELIGIBLE
    if decision is ApprovalDecision.REQUEST_CHANGES:
        return None
    if wait_kind is ApprovalWaitKind.BUDGET:
        return JobStatus.CANCELLED
    return JobStatus.PERMANENT_FAILED


def expired_job_status(wait_kind: ApprovalWaitKind) -> JobStatus | None:
    if wait_kind is ApprovalWaitKind.MANUAL_HANDOFF:
        return None
    return JobStatus.MANUAL_HANDOFF


@dataclass(frozen=True)
class ApprovalWaitRequest:
    request_id: str
    project_id: str
    job_id: str
    wait_kind: ApprovalWaitKind
    subject_type: str
    subject_id: str
    requested_job_revision: int
    requested_by: str
    requested_at: datetime
    idempotency_key: str
    expires_at: datetime | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not self.request_id.startswith("AQR-") or not self.request_id[4:].isdigit():
            raise ValueError("request_id must use the AQR numeric namespace")
        if len(self.request_id[4:]) < 6 or len(self.request_id[4:]) > 20:
            raise ValueError("request_id numeric component must contain 6 to 20 digits")
        if self.requested_job_revision < 1:
            raise ValueError("requested_job_revision must be at least 1")
        if not self.subject_type.strip() or not self.subject_id.strip():
            raise ValueError("approval subject must not be blank")
        if not self.requested_by.strip():
            raise ValueError("requested_by must not be blank")
        if len(self.idempotency_key) < 8 or len(self.idempotency_key) > 200:
            raise ValueError("idempotency_key length must be between 8 and 200")
        if self.expires_at is not None and self.expires_at <= self.requested_at:
            raise ValueError("expires_at must be later than requested_at")

    @property
    def request_fingerprint(self) -> str:
        return operation_fingerprint(
            {
                "project_id": self.project_id,
                "job_id": self.job_id,
                "wait_kind": self.wait_kind.value,
                "subject_type": self.subject_type,
                "subject_id": self.subject_id,
                "requested_job_revision": self.requested_job_revision,
                "requested_by": self.requested_by,
                "requested_at": self.requested_at,
                "expires_at": self.expires_at,
                "reason": self.reason,
            }
        )


ApprovalRequestAction = Literal["created", "reused"]
ApprovalResolutionAction = Literal["resolved", "reused", "expired"]


@dataclass(frozen=True)
class ApprovalRequestResult:
    action: ApprovalRequestAction
    request_id: str
    request_revision: int
    job_revision: int
    status: ApprovalRequestStatus


@dataclass(frozen=True)
class ApprovalResolutionResult:
    action: ApprovalResolutionAction
    request_id: str
    request_revision: int
    job_revision: int
    request_status: ApprovalRequestStatus
    job_status: JobStatus
    approval_id: str | None = None
