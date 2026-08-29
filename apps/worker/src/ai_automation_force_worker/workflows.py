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
SYNTHETIC_PROVIDER_ACTIVITY_TIMEOUT = timedelta(seconds=5)
SYNTHETIC_PROVIDER_TERMINAL = frozenset({"succeeded", "failed", "cancelled"})


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


@activity.defn
async def synthetic_provider_submit(job_key: str) -> str:
    """Return a fake external generation token without network access or spend."""

    normalized = job_key.strip()
    if not normalized:
        raise ApplicationError("job key is blank", type="SyntheticProviderInput", non_retryable=True)
    return f"fake-gen-{normalized}"


@activity.defn
async def synthetic_provider_poll(payload: dict[str, str | int]) -> str:
    """Return a fake provider observation for deterministic poll-path acceptance."""

    mode = str(payload["mode"])
    poll_index = int(payload["poll_index"])
    succeed_after = int(payload["succeed_after"])
    if mode == "unavailable":
        return "unavailable"
    if poll_index >= succeed_after:
        return "succeeded"
    return "running"


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
        except TimeoutError:
            await workflow.wait_condition(workflow.all_handlers_finished)
            return "expired"
        await workflow.wait_condition(workflow.all_handlers_finished)
        assert self._decision is not None
        return self._decision


@workflow.defn
class SyntheticProviderAsyncWorkflow:
    """Fake external async submit/poll/callback pattern with no provider network calls."""

    def __init__(self) -> None:
        self._generation_id: str | None = None
        self._terminal_status: str | None = None
        self._last_callback_order = -1
        self._seen_event_ids: set[str] = set()
        self._pending_callbacks: list[tuple[str, str, int, str]] = []

    def _apply_callbacks(self) -> None:
        if self._generation_id is None or self._terminal_status is not None:
            return
        for event_id, generation_id, event_order, status in self._pending_callbacks:
            if event_id in self._seen_event_ids:
                continue
            self._seen_event_ids.add(event_id)
            if generation_id != self._generation_id:
                continue
            if event_order <= self._last_callback_order:
                continue
            self._last_callback_order = event_order
            if status in SYNTHETIC_PROVIDER_TERMINAL:
                self._terminal_status = status
                return

    @workflow.signal
    def provider_callback(self, payload: dict[str, str | int]) -> None:
        event_id = str(payload["event_id"]).strip()
        generation_id = str(payload["generation_id"]).strip()
        status = str(payload["status"]).strip()
        event_order = int(payload["event_order"])
        if not event_id or not generation_id or not status:
            return
        self._pending_callbacks.append((event_id, generation_id, event_order, status))
        self._apply_callbacks()

    @workflow.run
    async def run(self, input: dict[str, str | int | float]) -> str:
        job_key = str(input["job_key"]).strip()
        mode = str(input["mode"]).strip()
        timeout_seconds = float(input["timeout_seconds"])
        poll_interval_seconds = float(input.get("poll_interval_seconds", 0.1))
        succeed_after = int(input.get("succeed_after", 2))
        if not job_key:
            raise ValueError("job_key must not be blank")
        if mode not in {"poll", "callback", "timeout", "unavailable"}:
            raise ValueError("unsupported synthetic provider mode")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if poll_interval_seconds <= 0:
            raise ValueError("poll_interval_seconds must be positive")
        if succeed_after < 1:
            raise ValueError("succeed_after must be at least 1")

        self._generation_id = await workflow.execute_activity(
            synthetic_provider_submit,
            job_key,
            start_to_close_timeout=SYNTHETIC_PROVIDER_ACTIVITY_TIMEOUT,
        )
        self._apply_callbacks()

        if mode == "callback":
            try:
                await workflow.wait_condition(
                    lambda: self._terminal_status is not None,
                    timeout=timedelta(seconds=timeout_seconds),
                )
            except TimeoutError:
                await workflow.wait_condition(workflow.all_handlers_finished)
                return "timed-out"
            await workflow.wait_condition(workflow.all_handlers_finished)
            assert self._terminal_status is not None
            return self._terminal_status

        deadline = workflow.now() + timedelta(seconds=timeout_seconds)
        poll_index = 0
        while workflow.now() < deadline:
            poll_index += 1
            status = await workflow.execute_activity(
                synthetic_provider_poll,
                {
                    "mode": mode,
                    "poll_index": poll_index,
                    "succeed_after": succeed_after,
                },
                start_to_close_timeout=SYNTHETIC_PROVIDER_ACTIVITY_TIMEOUT,
            )
            if status == "succeeded":
                return status
            if status == "unavailable":
                return status
            remaining = (deadline - workflow.now()).total_seconds()
            if remaining <= 0:
                break
            await workflow.sleep(min(poll_interval_seconds, remaining))
        return "timed-out"
