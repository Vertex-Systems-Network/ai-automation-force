from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest
from temporalio.worker import Replayer

from ai_automation_force_worker import (
    SyntheticRecoveryWorkflow,
    WorkerSettings,
    build_worker,
    connect_temporal,
)

TEMPORAL_INTEGRATION = os.environ.get("AAF_TEMPORAL_INTEGRATION") == "1"


async def wait_for_approval_barrier(handle: Any) -> dict[str, Any]:
    for _ in range(200):
        progress = await handle.query(SyntheticRecoveryWorkflow.progress)
        if progress["waiting_for_approval"] and progress["completed_count"] == 50:
            return dict(progress)
        await asyncio.sleep(0.05)
    raise AssertionError("recovery workflow did not reach the 50-shot approval barrier")


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_100_shot_workflow_survives_worker_restart_retries_approval_and_replays() -> None:
    settings = WorkerSettings()
    expected_retries = list(range(0, 100, 10))

    async def scenario() -> tuple[dict[str, Any], object, int]:
        client = await connect_temporal(settings)
        worker_one = build_worker(client, settings)
        async with worker_one:
            handle = await client.start_workflow(
                SyntheticRecoveryWorkflow.run,
                {
                    "project_key": "wp8-100-shot",
                    "shot_count": 100,
                    "fail_first_indexes": expected_retries,
                    "approval_after": 50,
                    "expected_approval_revision": 7,
                },
                id="WFX-009800-recovery",
                task_queue=settings.task_queue,
            )
            barrier = await wait_for_approval_barrier(handle)
            assert barrier == {
                "project_key": "wp8-100-shot",
                "shot_count": 100,
                "completed_count": 50,
                "waiting_for_approval": True,
                "approval_received": False,
            }

        # No worker is polling here. Signals are accepted by Temporal and delivered after restart.
        await handle.signal(
            SyntheticRecoveryWorkflow.approve,
            {
                "request_revision": 6,
                "decision": "approved",
                "signal_key": "wp8-stale",
            },
        )
        await handle.signal(
            SyntheticRecoveryWorkflow.approve,
            {
                "request_revision": 7,
                "decision": "approved",
                "signal_key": "wp8-valid",
            },
        )
        await handle.signal(
            SyntheticRecoveryWorkflow.approve,
            {
                "request_revision": 7,
                "decision": "rejected",
                "signal_key": "wp8-valid",
            },
        )

        worker_two = build_worker(client, settings)
        async with worker_two:
            result = await asyncio.wait_for(handle.result(), timeout=30.0)
            history = await handle.fetch_history()
        return dict(result), history, len(history.events)

    result, history, retained_event_count = asyncio.run(scenario())

    assert result["project_key"] == "wp8-100-shot"
    assert result["shot_count"] == 100
    assert result["completed_count"] == 100
    assert len(result["terminal_keys"]) == 100
    assert len(set(result["terminal_keys"])) == 100
    assert result["retried_shots"] == expected_retries
    assert result["continue_as_new_suggested"] is False
    assert result["history_length"] <= retained_event_count
    assert retained_event_count - result["history_length"] <= 5
    assert retained_event_count < 4096

    asyncio.run(Replayer(workflows=[SyntheticRecoveryWorkflow]).replay_workflow(history))
