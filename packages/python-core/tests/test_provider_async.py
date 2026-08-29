from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ai_automation_force_core import (
    PROVIDER_ASYNC_TRANSITIONS,
    TERMINAL_PROVIDER_ASYNC_STATUSES,
    ProviderAsyncStatus,
    ProviderAsyncSubmission,
    ProviderAsyncTransitionError,
    ProviderCallbackEvent,
    SyntheticCallbackVerificationError,
    SyntheticHmacCallbackVerifier,
    assert_provider_async_transition,
    payload_sha256,
)


def test_provider_async_transition_matrix_closes_terminal_states() -> None:
    assert set(PROVIDER_ASYNC_TRANSITIONS) == set(ProviderAsyncStatus)
    assert_provider_async_transition(
        ProviderAsyncStatus.SUBMITTED,
        ProviderAsyncStatus.RUNNING,
    )
    assert_provider_async_transition(
        ProviderAsyncStatus.RUNNING,
        ProviderAsyncStatus.SUCCEEDED,
    )
    for status in TERMINAL_PROVIDER_ASYNC_STATUSES:
        assert PROVIDER_ASYNC_TRANSITIONS[status] == frozenset()
        with pytest.raises(ProviderAsyncTransitionError):
            assert_provider_async_transition(status, ProviderAsyncStatus.RUNNING)


def test_synthetic_callback_verification_is_constant_contract_and_time_bounded() -> None:
    verifier = SyntheticHmacCallbackVerifier(
        b"synthetic-test-secret-32-bytes!!",
        tolerance_seconds=60,
    )
    body = b'{"event_id":"evt-1","status":"succeeded"}'
    timestamp = 1_788_000_000
    signature = verifier.signature(body, timestamp)

    assert verifier.verify(
        body,
        timestamp=timestamp,
        signature=signature,
        now_timestamp=timestamp + 10,
    ) == payload_sha256(body)

    with pytest.raises(SyntheticCallbackVerificationError, match="invalid"):
        verifier.verify(
            body,
            timestamp=timestamp,
            signature="v1=deadbeef",
            now_timestamp=timestamp,
        )
    with pytest.raises(SyntheticCallbackVerificationError, match="stale"):
        verifier.verify(
            body,
            timestamp=timestamp,
            signature=signature,
            now_timestamp=timestamp + 61,
        )


def test_provider_async_submission_and_callback_validate_time_and_hash_boundaries() -> None:
    now = datetime(2026, 8, 29, 9, 0, tzinfo=UTC)
    ProviderAsyncSubmission(
        attempt_id="ATT-000001",
        provider_id="synthetic",
        provider_generation_id="fake-gen-1",
        submitted_at=now,
        next_poll_at=now + timedelta(seconds=1),
        deadline_at=now + timedelta(seconds=10),
    )
    ProviderCallbackEvent(
        event_id="evt-1",
        provider_id="synthetic",
        provider_generation_id="fake-gen-1",
        provider_status="complete",
        normalized_status=ProviderAsyncStatus.SUCCEEDED,
        provider_event_at=now,
        received_at=now + timedelta(seconds=1),
        payload_sha256="a" * 64,
    )

    with pytest.raises(ValueError, match="deadline"):
        ProviderAsyncSubmission(
            attempt_id="ATT-000001",
            provider_id="synthetic",
            provider_generation_id="fake-gen-1",
            submitted_at=now,
            deadline_at=now,
        )
    with pytest.raises(ValueError, match="SHA-256"):
        ProviderCallbackEvent(
            event_id="evt-1",
            provider_id="synthetic",
            provider_generation_id="fake-gen-1",
            provider_status="complete",
            normalized_status=ProviderAsyncStatus.SUCCEEDED,
            provider_event_at=now,
            received_at=now,
            payload_sha256="not-a-hash",
        )
