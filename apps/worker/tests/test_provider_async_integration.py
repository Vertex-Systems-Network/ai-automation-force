from __future__ import annotations

import asyncio
import os

import pytest
from temporalio.worker import Replayer

from ai_automation_force_worker import (
    SyntheticProviderAsyncWorkflow,
    WorkerSettings,
    build_worker,
    connect_temporal,
)

TEMPORAL_INTEGRATION = os.environ.get("AAF_TEMPORAL_INTEGRATION") == "1"


async def run_provider_workflow(
    settings: WorkerSettings,
    *,
    workflow_id: str,
    payload: dict[str, str | int | float],
) -> tuple[str, object]:
    client = await connect_temporal(settings)
    worker = build_worker(client, settings)
    async with worker:
        handle = await client.start_workflow(
            SyntheticProviderAsyncWorkflow.run,
            payload,
            id=workflow_id,
            task_queue=settings.task_queue,
        )
        result = await handle.result()
        history = await handle.fetch_history()
        return result, history


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_fake_provider_poll_path_completes_and_replays() -> None:
    settings = WorkerSettings()
    result, history = asyncio.run(
        run_provider_workflow(
            settings,
            workflow_id="WFX-000901-provider-poll",
            payload={
                "job_key": "poll-1",
                "mode": "poll",
                "timeout_seconds": 2.0,
                "poll_interval_seconds": 0.05,
                "succeed_after": 2,
            },
        )
    )
    assert result == "succeeded"
    asyncio.run(Replayer(workflows=[SyntheticProviderAsyncWorkflow]).replay_workflow(history))


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_fake_provider_unavailable_path_is_normalized_and_replays() -> None:
    settings = WorkerSettings()
    result, history = asyncio.run(
        run_provider_workflow(
            settings,
            workflow_id="WFX-000902-provider-unavailable",
            payload={
                "job_key": "unavailable-1",
                "mode": "unavailable",
                "timeout_seconds": 2.0,
                "poll_interval_seconds": 0.05,
                "succeed_after": 2,
            },
        )
    )
    assert result == "unavailable"
    asyncio.run(Replayer(workflows=[SyntheticProviderAsyncWorkflow]).replay_workflow(history))


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_fake_provider_poll_deadline_times_out_and_replays() -> None:
    settings = WorkerSettings()
    result, history = asyncio.run(
        run_provider_workflow(
            settings,
            workflow_id="WFX-000903-provider-timeout",
            payload={
                "job_key": "timeout-1",
                "mode": "timeout",
                "timeout_seconds": 0.35,
                "poll_interval_seconds": 0.05,
                "succeed_after": 10_000,
            },
        )
    )
    assert result == "timed-out"
    asyncio.run(Replayer(workflows=[SyntheticProviderAsyncWorkflow]).replay_workflow(history))


@pytest.mark.temporal
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_temporal_fake_provider_callback_suppresses_wrong_stale_and_duplicate_events() -> None:
    settings = WorkerSettings()

    async def scenario() -> tuple[str, object]:
        client = await connect_temporal(settings)
        worker = build_worker(client, settings)
        async with worker:
            handle = await client.start_workflow(
                SyntheticProviderAsyncWorkflow.run,
                {
                    "job_key": "callback-1",
                    "mode": "callback",
                    "timeout_seconds": 2.0,
                    "poll_interval_seconds": 0.05,
                    "succeed_after": 2,
                },
                id="WFX-000904-provider-callback",
                task_queue=settings.task_queue,
            )
            await handle.signal(
                SyntheticProviderAsyncWorkflow.provider_callback,
                {
                    "event_id": "evt-wrong-generation",
                    "generation_id": "fake-gen-other",
                    "event_order": 1,
                    "status": "failed",
                },
            )
            await handle.signal(
                SyntheticProviderAsyncWorkflow.provider_callback,
                {
                    "event_id": "evt-running",
                    "generation_id": "fake-gen-callback-1",
                    "event_order": 2,
                    "status": "running",
                },
            )
            await handle.signal(
                SyntheticProviderAsyncWorkflow.provider_callback,
                {
                    "event_id": "evt-stale",
                    "generation_id": "fake-gen-callback-1",
                    "event_order": 1,
                    "status": "failed",
                },
            )
            await handle.signal(
                SyntheticProviderAsyncWorkflow.provider_callback,
                {
                    "event_id": "evt-running",
                    "generation_id": "fake-gen-callback-1",
                    "event_order": 3,
                    "status": "failed",
                },
            )
            await handle.signal(
                SyntheticProviderAsyncWorkflow.provider_callback,
                {
                    "event_id": "evt-success",
                    "generation_id": "fake-gen-callback-1",
                    "event_order": 3,
                    "status": "succeeded",
                },
            )
            result = await handle.result()
            history = await handle.fetch_history()
            return result, history

    result, history = asyncio.run(scenario())
    assert result == "succeeded"
    asyncio.run(Replayer(workflows=[SyntheticProviderAsyncWorkflow]).replay_workflow(history))
