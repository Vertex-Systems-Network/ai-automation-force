from __future__ import annotations

import asyncio
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

SYNTHETIC_ACTIVITY_START_TO_CLOSE = timedelta(seconds=10)
SYNTHETIC_RETRY_SCHEDULE_TO_CLOSE = timedelta(seconds=10)
SYNTHETIC_RETRY_START_TO_CLOSE = timedelta(seconds=2)
SYNTHETIC_CANCEL_START_TO_CLOSE = timedelta(seconds=30)
SYNTHETIC_CANCEL_HEARTBEAT = timedelta(seconds=1)


@activity.defn
async def synthetic_echo(value: str) -> str:
    """Spend-free Activity proving the external-side-effect boundary."""

    return f"accepted:{value}"


@activity.defn
async def synthetic_flaky(fail_attempts: int) -> int:
    """Fail deterministically by Activity attempt so Temporal owns retries."""

    attempt = activity.info().attempt
    if attempt <= fail_attempts:
        raise ApplicationError(
            f"synthetic transient failure on attempt {attempt}",
            type="SyntheticTransient",
        )
    return attempt


@activity.defn
async def synthetic_cancellable(label: str) -> None:
    """Heartbeat until Temporal cancellation is delivered to the Activity task."""

    while True:
        activity.heartbeat(label)
        await asyncio.sleep(0.05)


@workflow.defn
class SyntheticControlWorkflow:
    """Minimal deterministic workflow used only to prove M02 durability plumbing."""

    @workflow.run
    async def run(self, value: str) -> str:
        return await workflow.execute_activity(
            synthetic_echo,
            value,
            start_to_close_timeout=SYNTHETIC_ACTIVITY_START_TO_CLOSE,
        )


@workflow.defn
class SyntheticRetryWorkflow:
    """Spend-free workflow proving bounded Temporal Activity retry behavior."""

    @workflow.run
    async def run(self, fail_attempts: int) -> int:
        return await workflow.execute_activity(
            synthetic_flaky,
            fail_attempts,
            schedule_to_close_timeout=SYNTHETIC_RETRY_SCHEDULE_TO_CLOSE,
            start_to_close_timeout=SYNTHETIC_RETRY_START_TO_CLOSE,
            retry_policy=RetryPolicy(
                initial_interval=timedelta(milliseconds=100),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(milliseconds=400),
                maximum_attempts=4,
                non_retryable_error_types=["SyntheticPermanent"],
            ),
        )


@workflow.defn
class SyntheticCancellationWorkflow:
    """Proves workflow cancellation propagates to a heartbeat-enabled Activity."""

    @workflow.run
    async def run(self, label: str) -> None:
        await workflow.execute_activity(
            synthetic_cancellable,
            label,
            start_to_close_timeout=SYNTHETIC_CANCEL_START_TO_CLOSE,
            heartbeat_timeout=SYNTHETIC_CANCEL_HEARTBEAT,
            cancellation_type=workflow.ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
        )


@workflow.defn
class SyntheticApprovalWorkflow:
    """Spend-free signal wait proving stale, duplicate and expiry-safe resume behavior."""

    def __init__(self) -> None:
        self._expected_revision: int | None = None
        self._decision: str | None = None
        self._pending_signals: list[tuple[int, str]] = []
        self._seen_signal_keys: set[str] = set()

    def _apply_pending(self) -> None:
        if self._expected_revision is None or self._decision is not None:
            return
        for request_revision, decision in self._pending_signals:
            if request_revision == self._expected_revision:
                self._decision = decision
                return

    @workflow.signal
    def resolve(self, payload: dict[str, str | int]) -> None:
        signal_key = str(payload["signal_key"]).strip()
        if not signal_key or signal_key in self._seen_signal_keys:
            return
        self._seen_signal_keys.add(signal_key)
        request_revision = int(payload["request_revision"])
        decision = str(payload["decision"]).strip()
        if not decision:
            return
        self._pending_signals.append((request_revision, decision))
        self._apply_pending()

    @workflow.run
    async def run(self, input: dict[str, int | float]) -> str:
        self._expected_revision = int(input["expected_revision"])
        timeout_seconds = float(input["timeout_seconds"])
        if self._expected_revision < 1:
            raise ValueError("expected_revision must be at least 1")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._apply_pending()
        try:
            await workflow.wait_condition(
                lambda: self._decision is not None,
                timeout=timedelta(seconds=timeout_seconds),
            )
        except asyncio.TimeoutError:
            await workflow.wait_condition(workflow.all_handlers_finished)
            return "expired"
        await workflow.wait_condition(workflow.all_handlers_finished)
        assert self._decision is not None
        return self._decision
