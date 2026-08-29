from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from temporalio.worker import Replayer

from ai_automation_force_core import (
    PostgresWorkflowExecutionRepository,
    WorkflowExecutionRef,
)
from ai_automation_force_worker import (
    SyntheticControlWorkflow,
    WorkerSettings,
    build_worker,
    connect_temporal,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ROOT = Path(__file__).resolve().parents[3]
ALEMBIC_INI = ROOT / "packages" / "python-core" / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.mark.temporal
@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_real_temporal_workflow_replays_and_persists_run_reference() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    settings = WorkerSettings()

    async def scenario() -> tuple[str, str]:
        client = await connect_temporal(settings)
        worker = build_worker(client, settings)
        async with worker:
            handle = await client.start_workflow(
                SyntheticControlWorkflow.run,
                "wp2-foundation",
                id="WFX-000777",
                task_queue=settings.task_queue,
            )
            run_id = handle.result_run_id
            assert run_id is not None
            result = await handle.result()
            history = await handle.fetch_history()
            await Replayer(workflows=[SyntheticControlWorkflow]).replay_workflow(history)
            return result, run_id

    try:
        result, run_id = asyncio.run(scenario())
        assert result == "accepted:wp2-foundation"

        now = datetime.now(UTC)
        execution = WorkflowExecutionRef(
            workflow_execution_id="WFX-000777",
            workflow_type="SyntheticControlWorkflow",
            run_id=run_id,
            namespace=settings.temporal_namespace,
            task_queue=settings.task_queue,
            status="completed",
            started_at=now,
            updated_at=now,
            closed_at=now,
        )
        repository = PostgresWorkflowExecutionRepository(engine)
        assert repository.save(execution).action == "created"
        assert repository.load("WFX-000777") == execution
    finally:
        engine.dispose()
        command.downgrade(config, "base")
