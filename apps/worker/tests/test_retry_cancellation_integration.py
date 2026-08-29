from __future__ import annotations

import asyncio
import os

import pytest
from temporalio.client import WorkflowFailureError
from temporalio.exceptions import CancelledError
from temporalio.worker import Replayer

from ai_automation_force_worker import (
    SyntheticCancellationWorkflow,
    SyntheticRetryWorkflow,
    WorkerSettings,
    build_worker,
    connect_temporal,
)

TEMPORAL_INTEGRATION = os.environ.get("AAF_TEMPORAL_INTEGRATION") == "1"


def has_cancelled_cause(error: BaseException) -> bool:
    current: BaseException | None = error
    while current is not None:
        if isinstance(current, CancelledError):
            return True
        current = current.__cause__
    return False


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_retries_are_bounded_and_history_replays() -> None:
    settings = WorkerSettings()

    async def scenario() -> tuple[int, object]:
        client = await connect_temporal(settings)
        worker = build_worker(client, settings)
        async with worker:
            handle = await client.start_workflow(
                SyntheticRetryWorkflow.run,
                2,
                id="WFX-000881-retry",
                task_queue=settings.task_queue,
            )
            result = await handle.result()
            history = await handle.fetch_history()
            return result, history

    result, history = asyncio.run(scenario())
    assert result == 3
    asyncio.run(Replayer(workflows=[SyntheticRetryWorkflow]).replay_workflow(history))


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_workflow_cancel_propagates_to_heartbeat_activity_and_replays() -> None:
    settings = WorkerSettings()

    async def scenario() -> tuple[WorkflowFailureError, object]:
        client = await connect_temporal(settings)
        worker = build_worker(client, settings)
        async with worker:
            handle = await client.start_workflow(
                SyntheticCancellationWorkflow.run,
                "cancel-me",
                id="WFX-000882-cancel",
                task_queue=settings.task_queue,
            )
            await asyncio.sleep(0.25)
            await handle.cancel()
            try:
                await handle.result()
            except WorkflowFailureError as error:
                history = await handle.fetch_history()
                return error, history
            raise AssertionError("cancelled workflow unexpectedly completed")

    error, history = asyncio.run(scenario())
    assert has_cancelled_cause(error)
    assert any(
        event.HasField("activity_task_canceled_event_attributes") for event in history.events
    )
    asyncio.run(Replayer(workflows=[SyntheticCancellationWorkflow]).replay_workflow(history))
