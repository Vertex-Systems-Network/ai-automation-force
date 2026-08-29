from __future__ import annotations

import pytest

from ai_automation_force_core import (
    BackoffPolicy,
    CircuitBreakerPolicy,
    DeadlinePolicy,
    FailureClass,
    JobStatus,
    retry_decision,
)


def test_backoff_is_bounded_and_attempt_budget_is_explicit() -> None:
    policy = BackoffPolicy(
        initial_seconds=2,
        coefficient=2,
        maximum_seconds=10,
        maximum_attempts=4,
    )
    assert [policy.delay_seconds(value) for value in range(1, 6)] == [2, 4, 8, 10, 10]
    assert policy.can_retry(0)
    assert policy.can_retry(3)
    assert not policy.can_retry(4)

    with pytest.raises(ValueError, match="1-based"):
        policy.delay_seconds(0)


def test_failure_classes_normalize_retry_manual_and_terminal_outcomes() -> None:
    transient = retry_decision(FailureClass.TRANSIENT)
    assert transient.retryable
    assert transient.target_status is JobStatus.RETRYABLE_FAILED
    assert transient.counts_toward_circuit

    quota = retry_decision(FailureClass.QUOTA_EXHAUSTED)
    assert not quota.retryable
    assert quota.target_status is JobStatus.WAITING_QUOTA
    assert not quota.manual_action_required

    authentication = retry_decision(FailureClass.AUTHENTICATION)
    assert authentication.target_status is JobStatus.MANUAL_HANDOFF
    assert authentication.manual_action_required

    assert retry_decision(FailureClass.LICENSE).target_status is JobStatus.BLOCKED_LICENSE
    assert retry_decision(FailureClass.BUDGET).target_status is JobStatus.BLOCKED_BUDGET
    assert retry_decision(FailureClass.CANCELLED).target_status is JobStatus.CANCELLED
    assert retry_decision(FailureClass.PERMANENT).target_status is JobStatus.PERMANENT_FAILED


def test_deadline_and_circuit_policies_reject_unsafe_values() -> None:
    DeadlinePolicy(schedule_to_close_seconds=30, start_to_close_seconds=10, heartbeat_seconds=2)
    CircuitBreakerPolicy(failure_threshold=3, open_seconds=60, probe_lease_seconds=10)

    with pytest.raises(ValueError, match="shorter"):
        DeadlinePolicy(
            schedule_to_close_seconds=30,
            start_to_close_seconds=10,
            heartbeat_seconds=10,
        )
    with pytest.raises(ValueError, match="failure_threshold"):
        CircuitBreakerPolicy(failure_threshold=0)
