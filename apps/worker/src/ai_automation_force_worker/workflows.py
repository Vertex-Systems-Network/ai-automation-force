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
