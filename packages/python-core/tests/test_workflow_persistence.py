from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from lineage_fixtures import full_lineage_bundle
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from lullabies_core import (
    PersistenceConflictError,
    PersistenceReferenceError,
    PostgresProductionRepository,
    PostgresWorkflowExecutionRepository,
    WorkflowExecutionRef,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"
NOW = datetime(2026, 8, 29, 13, 0, tzinfo=UTC)


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.fixture
def migrated_engine() -> Iterator[Engine]:
    if DATABASE_URL is None:
        pytest.skip("DATABASE_URL is not configured")
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    try:
        yield engine
    finally:
        engine.dispose()
        command.downgrade(config, "base")


def workflow_ref() -> WorkflowExecutionRef:
    return WorkflowExecutionRef(
        workflow_execution_id="WFX-000500",
        workflow_type="SyntheticControlWorkflow",
        run_id="temporal-run-000500",
        namespace="default",
        task_queue="aaf-control-v1",
        project_id="PRJ-000500",
        job_id="JOB-000500",
        status="running",
        started_at=NOW,
        updated_at=NOW,
    )


@pytest.mark.postgres
def test_workflow_reference_round_trip_and_status_update(migrated_engine: Engine) -> None:
    PostgresProductionRepository(migrated_engine).save_bundle(full_lineage_bundle())
    repository = PostgresWorkflowExecutionRepository(migrated_engine)
    execution = workflow_ref()

    first = repository.save(execution)
    second = repository.save(execution.model_copy(deep=True))
    restored = repository.load(execution.workflow_execution_id)
    completed_at = NOW + timedelta(seconds=2)
    updated = repository.update_status(
        execution.workflow_execution_id,
        status="completed",
        updated_at=completed_at,
        closed_at=completed_at,
    )
    completed = repository.load(execution.workflow_execution_id)

    assert first.action == "created"
    assert second.action == "noop"
    assert restored == execution
    assert updated.action == "updated"
    assert completed.status == "completed"
    assert completed.closed_at == completed_at
    assert completed.project_id == "PRJ-000500"
    assert completed.job_id == "JOB-000500"


@pytest.mark.postgres
def test_changed_workflow_identity_conflicts(migrated_engine: Engine) -> None:
    PostgresProductionRepository(migrated_engine).save_bundle(full_lineage_bundle())
    repository = PostgresWorkflowExecutionRepository(migrated_engine)
    execution = workflow_ref()
    repository.save(execution)

    changed = execution.model_copy(update={"task_queue": "different-queue"})
    with pytest.raises(PersistenceConflictError, match="different data"):
        repository.save(changed)


@pytest.mark.postgres
def test_workflow_reference_rejects_missing_owner(migrated_engine: Engine) -> None:
    repository = PostgresWorkflowExecutionRepository(migrated_engine)
    execution = workflow_ref().model_copy(update={"job_id": None})

    with pytest.raises(PersistenceReferenceError, match="missing project"):
        repository.save(execution)


def test_job_bound_workflow_requires_project() -> None:
    with pytest.raises(ValidationError, match="project_id"):
        WorkflowExecutionRef(
            workflow_execution_id="WFX-000501",
            workflow_type="SyntheticControlWorkflow",
            run_id="temporal-run-000501",
            namespace="default",
            task_queue="aaf-control-v1",
            job_id="JOB-000500",
            started_at=NOW,
            updated_at=NOW,
        )
