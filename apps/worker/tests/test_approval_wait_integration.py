from __future__ import annotations

import asyncio
import os

import pytest
from temporalio.worker import Replayer

from ai_automation_force_worker import (
    SyntheticApprovalWorkflow,
    WorkerSettings,
    build_worker,
    connect_temporal,
)

TEMPORAL_INTEGRATION = os.environ.get("AAF_TEMPORAL_INTEGRATION") == "1"


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_approval_wait_ignores_stale_and_duplicate_signals_and_replays() -> None:
    settings = WorkerSettings()

    async def scenario() -> tuple[str, object]:
        client = await connect_temporal(settings)
        worker = build_worker(client, settings)
        async with worker:
            handle = await client.start_workflow(
                SyntheticApprovalWorkflow.run,
                {"expected_revision": 7, "timeout_seconds": 2.0},
                id="WFX-000891-approval",
                task_queue=settings.task_queue,
            )
            await handle.signal(
                SyntheticApprovalWorkflow.resolve,
                {
                    "request_revision": 6,
                    "decision": "rejected",
                    "signal_key": "signal-stale",
                },
            )
            await handle.signal(
                SyntheticApprovalWorkflow.resolve,
                {
                    "request_revision": 7,
                    "decision": "approved",
                    "signal_key": "signal-valid",
                },
            )
            await handle.signal(
                SyntheticApprovalWorkflow.resolve,
                {
                    "request_revision": 7,
                    "decision": "rejected",
                    "signal_key": "signal-valid",
                },
            )
            result = await handle.result()
            history = await handle.fetch_history()
            return result, history

    result, history = asyncio.run(scenario())
    assert result == "approved"
    asyncio.run(Replayer(workflows=[SyntheticApprovalWorkflow]).replay_workflow(history))


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_approval_wait_expires_without_signal_and_replays() -> None:
    settings = WorkerSettings()

    async def scenario() -> tuple[str, object]:
        client = await connect_temporal(settings)
        worker = build_worker(client, settings)
        async with worker:
            handle = await client.start_workflow(
                SyntheticApprovalWorkflow.run,
                {"expected_revision": 1, "timeout_seconds": 1.0},
                id="WFX-000892-approval-expiry",
                task_queue=settings.task_queue,
            )
            result = await handle.result()
            history = await handle.fetch_history()
            return result, history

    result, history = asyncio.run(scenario())
    assert result == "expired"
    asyncio.run(Replayer(workflows=[SyntheticApprovalWorkflow]).replay_workflow(history))
