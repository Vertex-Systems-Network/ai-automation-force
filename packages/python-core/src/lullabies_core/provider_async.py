from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ProviderAsyncStatus(StrEnum):
    SUBMITTED = "submitted"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed-out"
    CANCELLED = "cancelled"


TERMINAL_PROVIDER_ASYNC_STATUSES = frozenset(
    {
        ProviderAsyncStatus.SUCCEEDED,
        ProviderAsyncStatus.FAILED,
        ProviderAsyncStatus.TIMED_OUT,
        ProviderAsyncStatus.CANCELLED,
    }
)

PROVIDER_ASYNC_TRANSITIONS: dict[ProviderAsyncStatus, frozenset[ProviderAsyncStatus]] = {
    ProviderAsyncStatus.SUBMITTED: frozenset(
        {
            ProviderAsyncStatus.RUNNING,
            ProviderAsyncStatus.SUCCEEDED,
            ProviderAsyncStatus.FAILED,
            ProviderAsyncStatus.TIMED_OUT,
            ProviderAsyncStatus.CANCELLED,
        }
    ),
    ProviderAsyncStatus.RUNNING: frozenset(
        {
            ProviderAsyncStatus.SUCCEEDED,
            ProviderAsyncStatus.FAILED,
            ProviderAsyncStatus.TIMED_OUT,
            ProviderAsyncStatus.CANCELLED,
        }
    ),
    ProviderAsyncStatus.SUCCEEDED: frozenset(),
    ProviderAsyncStatus.FAILED: frozenset(),
    ProviderAsyncStatus.TIMED_OUT: frozenset(),
    ProviderAsyncStatus.CANCELLED: frozenset(),
}


class ProviderAsyncTransitionError(ValueError):
    pass


class SyntheticCallbackVerificationError(ValueError):
    pass


def assert_provider_async_transition(
    current: ProviderAsyncStatus,
    target: ProviderAsyncStatus,
) -> None:
    if target not in PROVIDER_ASYNC_TRANSITIONS[current]:
        raise ProviderAsyncTransitionError(
            f"invalid provider async transition: {current.value} -> {target.value}"
        )


def payload_sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


class SyntheticHmacCallbackVerifier:
    """Test-only callback verifier defining the later signed-webhook abstraction."""

    def __init__(self, secret: bytes, *, tolerance_seconds: int = 300) -> None:
        if len(secret) < 16:
            raise ValueError("synthetic callback secret must be at least 16 bytes")
        if tolerance_seconds < 1 or tolerance_seconds > 3600:
            raise ValueError("callback tolerance must be between 1 and 3600 seconds")
        self._secret = secret
        self._tolerance_seconds = tolerance_seconds

    def signature(self, body: bytes, timestamp: int) -> str:
        digest = hmac.new(
            self._secret,
            str(timestamp).encode("ascii") + b"." + body,
            hashlib.sha256,
        ).hexdigest()
        return f"v1={digest}"

    def verify(
        self,
        body: bytes,
        *,
        timestamp: int,
        signature: str,
        now_timestamp: int,
    ) -> str:
        if abs(now_timestamp - timestamp) > self._tolerance_seconds:
            raise SyntheticCallbackVerificationError("synthetic callback timestamp is stale")
        expected = self.signature(body, timestamp)
        if not hmac.compare_digest(expected, signature):
            raise SyntheticCallbackVerificationError("synthetic callback signature is invalid")
        return payload_sha256(body)


@dataclass(frozen=True)
class ProviderCallbackEvent:
    event_id: str
    provider_id: str
    provider_generation_id: str
    provider_status: str
    normalized_status: ProviderAsyncStatus
    provider_event_at: datetime
    received_at: datetime
    payload_sha256: str

    def __post_init__(self) -> None:
        if not 3 <= len(self.event_id) <= 200:
            raise ValueError("event_id length must be between 3 and 200")
        if not 1 <= len(self.provider_id) <= 120:
            raise ValueError("provider_id length must be between 1 and 120")
        if not 1 <= len(self.provider_generation_id) <= 240:
            raise ValueError("provider_generation_id length must be between 1 and 240")
        if not 1 <= len(self.provider_status) <= 120:
            raise ValueError("provider_status length must be between 1 and 120")
        if len(self.payload_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.payload_sha256
        ):
            raise ValueError("payload_sha256 must be lowercase SHA-256 hex")
        if self.received_at < self.provider_event_at:
            raise ValueError("received_at cannot precede provider_event_at")


@dataclass(frozen=True)
class ProviderAsyncSubmission:
    attempt_id: str
    provider_id: str
    provider_generation_id: str
    submitted_at: datetime
    deadline_at: datetime
    next_poll_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.attempt_id.startswith("ATT-"):
            raise ValueError("attempt_id must use the ATT namespace")
        if not self.provider_id.strip() or not self.provider_generation_id.strip():
            raise ValueError("provider identity must not be blank")
        if self.deadline_at <= self.submitted_at:
            raise ValueError("deadline_at must be later than submitted_at")
        if self.next_poll_at is not None and not (
            self.submitted_at <= self.next_poll_at < self.deadline_at
        ):
            raise ValueError("next_poll_at must be within the provider deadline")


@dataclass(frozen=True)
class ProviderAsyncResult:
    attempt_id: str
    status: ProviderAsyncStatus
    revision: int
    stale: bool = False
    duplicate: bool = False
    event_id: str | None = None
