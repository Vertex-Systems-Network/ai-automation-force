from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .common import JobStatus


class FailureClass(StrEnum):
    TRANSIENT = "transient"
    RATE_LIMIT = "rate-limit"
    QUOTA_EXHAUSTED = "quota-exhausted"
    PROVIDER_UNAVAILABLE = "provider-unavailable"
    TIMEOUT = "timeout"
    INVALID_REQUEST = "invalid-request"
    AUTHENTICATION = "authentication"
    LICENSE = "license"
    BUDGET = "budget"
    MANUAL = "manual"
    CANCELLED = "cancelled"
    PERMANENT = "permanent"


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


@dataclass(frozen=True)
class RetryDecision:
    failure_class: FailureClass
    retryable: bool
    target_status: JobStatus
    counts_toward_circuit: bool
    manual_action_required: bool = False


RETRY_DECISIONS: dict[FailureClass, RetryDecision] = {
    FailureClass.TRANSIENT: RetryDecision(
        FailureClass.TRANSIENT,
        True,
        JobStatus.RETRYABLE_FAILED,
        True,
    ),
    FailureClass.RATE_LIMIT: RetryDecision(
        FailureClass.RATE_LIMIT,
        True,
        JobStatus.RETRYABLE_FAILED,
        True,
    ),
    FailureClass.QUOTA_EXHAUSTED: RetryDecision(
        FailureClass.QUOTA_EXHAUSTED,
        False,
        JobStatus.WAITING_QUOTA,
        False,
    ),
    FailureClass.PROVIDER_UNAVAILABLE: RetryDecision(
        FailureClass.PROVIDER_UNAVAILABLE,
        True,
        JobStatus.RETRYABLE_FAILED,
        True,
    ),
    FailureClass.TIMEOUT: RetryDecision(
        FailureClass.TIMEOUT,
        True,
        JobStatus.RETRYABLE_FAILED,
        True,
    ),
    FailureClass.INVALID_REQUEST: RetryDecision(
        FailureClass.INVALID_REQUEST,
        False,
        JobStatus.PERMANENT_FAILED,
        False,
    ),
    FailureClass.AUTHENTICATION: RetryDecision(
        FailureClass.AUTHENTICATION,
        False,
        JobStatus.MANUAL_HANDOFF,
        False,
        True,
    ),
    FailureClass.LICENSE: RetryDecision(
        FailureClass.LICENSE,
        False,
        JobStatus.BLOCKED_LICENSE,
        False,
        True,
    ),
    FailureClass.BUDGET: RetryDecision(
        FailureClass.BUDGET,
        False,
        JobStatus.BLOCKED_BUDGET,
        False,
        True,
    ),
    FailureClass.MANUAL: RetryDecision(
        FailureClass.MANUAL,
        False,
        JobStatus.MANUAL_HANDOFF,
        False,
        True,
    ),
    FailureClass.CANCELLED: RetryDecision(
        FailureClass.CANCELLED,
        False,
        JobStatus.CANCELLED,
        False,
    ),
    FailureClass.PERMANENT: RetryDecision(
        FailureClass.PERMANENT,
        False,
        JobStatus.PERMANENT_FAILED,
        False,
    ),
}


@dataclass(frozen=True)
class BackoffPolicy:
    initial_seconds: float = 1.0
    coefficient: float = 2.0
    maximum_seconds: float = 60.0
    maximum_attempts: int = 5

    def __post_init__(self) -> None:
        if self.initial_seconds <= 0:
            raise ValueError("initial_seconds must be positive")
        if self.coefficient < 1:
            raise ValueError("coefficient must be at least 1")
        if self.maximum_seconds < self.initial_seconds:
            raise ValueError("maximum_seconds must be >= initial_seconds")
        if self.maximum_attempts < 1:
            raise ValueError("maximum_attempts must be at least 1")

    def delay_seconds(self, retry_number: int) -> float:
        if retry_number < 1:
            raise ValueError("retry_number is 1-based")
        return min(
            self.maximum_seconds,
            self.initial_seconds * (self.coefficient ** (retry_number - 1)),
        )

    def can_retry(self, attempts_started: int) -> bool:
        if attempts_started < 0:
            raise ValueError("attempts_started must be non-negative")
        return attempts_started < self.maximum_attempts


@dataclass(frozen=True)
class DeadlinePolicy:
    schedule_to_close_seconds: int = 120
    start_to_close_seconds: int = 30
    heartbeat_seconds: int = 5

    def __post_init__(self) -> None:
        if self.schedule_to_close_seconds < 1:
            raise ValueError("schedule_to_close_seconds must be positive")
        if self.start_to_close_seconds < 1:
            raise ValueError("start_to_close_seconds must be positive")
        if self.heartbeat_seconds < 1:
            raise ValueError("heartbeat_seconds must be positive")
        if self.start_to_close_seconds > self.schedule_to_close_seconds:
            raise ValueError("start_to_close_seconds cannot exceed schedule_to_close_seconds")
        if self.heartbeat_seconds >= self.start_to_close_seconds:
            raise ValueError("heartbeat_seconds must be shorter than start_to_close_seconds")


@dataclass(frozen=True)
class CircuitBreakerPolicy:
    failure_threshold: int = 3
    open_seconds: int = 60
    probe_lease_seconds: int = 30

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if self.open_seconds < 1:
            raise ValueError("open_seconds must be positive")
        if self.probe_lease_seconds < 1:
            raise ValueError("probe_lease_seconds must be positive")


@dataclass(frozen=True)
class CircuitPermission:
    allowed: bool
    state: CircuitState
    revision: int
    retry_at: datetime | None = None
    probe_owner: str | None = None


@dataclass(frozen=True)
class CircuitRecordResult:
    state: CircuitState
    consecutive_failures: int
    revision: int
    next_probe_at: datetime | None = None


def retry_decision(failure_class: FailureClass) -> RetryDecision:
    return RETRY_DECISIONS[failure_class]
