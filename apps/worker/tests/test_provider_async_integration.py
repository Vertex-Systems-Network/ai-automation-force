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
RESULT_TIMEOUT_SECONDS = 5.0


def provider_payload(
    *,
    job_key: str,
    mode: str,
    timeout_ms: int,
    poll_interval_ms: int = 50,
    succeed_after: int = 2,
) -> dict[str, str | int]:
    """Build the single canonical fake-provider workflow input contract."""

    return {
        "job_key": job_key,
        "mode": mode,
        "timeout_ms": timeout_ms,
        "poll_interval_ms": poll_interval_ms,
        "succeed_after": succeed_after,
    }


async def run_provider_workflow(
    settings: WorkerSettings,
    *,
    workflow_id: str,
    payload: dict[str, str | int],
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
        result = await asyncio.wait_for(handle.result(), timeout=RESULT_TIMEOUT_SECONDS)
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
            payload=provider_payload(job_key="poll-1", mode="poll", timeout_ms=2_000),
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
            payload=provider_payload(
                job_key="unavailable-1",
                mode="unavailable",
                timeout_ms=2_000,
            ),
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
            payload=provider_payload(
                job_key="timeout-1",
                mode="timeout",
                timeout_ms=350,
                succeed_after=10_000,
            ),
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
                provider_payload(job_key="callback-1", mode="callback", timeout_ms=2_000),
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
            # An unknown high-order observation must not poison ordering for later valid events.
            await handle.signal(
                SyntheticProviderAsyncWorkflow.provider_callback,
                {
                    "event_id": "evt-unknown-status",
                    "generation_id": "fake-gen-callback-1",
                    "event_order": 100,
                    "status": "mystery-provider-state",
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
            # Same event ID with changed semantics is suppressed at the workflow layer;
            # durable payload-conflict evidence remains the persistence boundary's responsibility.
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
            result = await asyncio.wait_for(handle.result(), timeout=RESULT_TIMEOUT_SECONDS)
            history = await handle.fetch_history()
            return result, history

    result, history = asyncio.run(scenario())
    assert result == "succeeded"
    asyncio.run(Replayer(workflows=[SyntheticProviderAsyncWorkflow]).replay_workflow(history))
