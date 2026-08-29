from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from ai_automation_force_core import (
    AuditFields,
    Job,
    JobCommandConflictError,
    JobCommandVersionConflictError,
    JobStatus,
    PostgresControlSurfaceRepository,
    PostgresJobControlRepository,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def insert_project(engine: object, external_id: str) -> None:
    with engine.begin() as connection:  # type: ignore[attr-defined]
        connection.execute(
            text(
                """
                INSERT INTO core.projects (
                    id, external_id, title, status, audience, "cast", content_format,
                    language, target_duration_seconds, output, creative, provider_policy,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :external_id, :title, 'draft',
                    '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                    '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, now(), now()
                )
                """
            ),
            {"external_id": external_id, "title": f"Fixture {external_id}"},
        )


def queued_job(job_id: str, project_id: str, key: str, now: datetime) -> Job:
    return Job(
        job_id=job_id,
        project_id=project_id,
        job_type="synthetic-control",
        idempotency_key=key,
        audit=AuditFields(created_at=now, updated_at=now, revision=1),
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_control_surface_reads_events_and_idempotently_cancels() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        insert_project(engine, "PRJ-001100")
        jobs = PostgresJobControlRepository(engine)
        control = PostgresControlSurfaceRepository(engine)
        job = queued_job("JOB-001100", "PRJ-001100", "create-001100", now)
        created = jobs.submit(job, {"kind": "synthetic-control", "value": "one"})
        assert created.action == "created"

        snapshot = control.load_job(job.job_id)
        assert snapshot.status is JobStatus.QUEUED
        assert snapshot.revision == 1
        assert snapshot.project_id == job.project_id
        assert snapshot.operation_fingerprint == created.operation_fingerprint

        events = control.list_job_events(job.job_id)
        assert [event.event_type for event in events] == ["job.created"]
        after = (events[0].occurred_at, events[0].event_id)
        assert control.list_job_events(job.job_id, after=after) == []

        applied = control.cancel_job(
            job.job_id,
            idempotency_key="cancel-001100",
            expected_revision=1,
            now=now + timedelta(seconds=1),
        )
        assert applied.action == "applied"
        assert applied.status is JobStatus.CANCELLED
        assert applied.revision == 2

        reused = control.cancel_job(
            job.job_id,
            idempotency_key="cancel-001100",
            expected_revision=1,
            now=now + timedelta(seconds=2),
        )
        assert reused.action == "reused"
        assert reused.revision == 2

        noop = control.cancel_job(
            job.job_id,
            idempotency_key="cancel-001100-new",
            expected_revision=1,
            now=now + timedelta(seconds=3),
        )
        assert noop.action == "noop"
        assert noop.revision == 2

        with pytest.raises(JobCommandConflictError, match="different control-command"):
            control.retry_job(
                job.job_id,
                idempotency_key="cancel-001100",
                expected_revision=1,
                now=now + timedelta(seconds=4),
            )

        all_events = control.list_job_events(job.job_id)
        assert [event.event_type for event in all_events] == [
            "job.created",
            "job.status.changed",
        ]
        page = control.list_project_jobs(job.project_id)
        assert len(page) == 1
        assert page[0].job_id == job.job_id
        assert page[0].status is JobStatus.CANCELLED
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_retry_command_decrements_budget_once_and_rejects_stale_or_wrong_state() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        insert_project(engine, "PRJ-001101")
        jobs = PostgresJobControlRepository(engine)
        control = PostgresControlSurfaceRepository(engine)
        job = queued_job("JOB-001101", "PRJ-001101", "create-001101", now)
        jobs.submit(job, {"kind": "synthetic-control", "value": "retry"})
        jobs.transition(
            job.job_id,
            JobStatus.ELIGIBLE,
            now=now + timedelta(seconds=1),
            expected_revision=1,
        )
        jobs.claim(
            job.job_id,
            owner="worker-wp7",
            now=now + timedelta(seconds=2),
            lease_for=timedelta(seconds=30),
            expected_revision=2,
        )
        jobs.transition(
            job.job_id,
            JobStatus.RUNNING,
            now=now + timedelta(seconds=3),
            expected_revision=3,
        )
        jobs.transition(
            job.job_id,
            JobStatus.RETRYABLE_FAILED,
            now=now + timedelta(seconds=4),
            expected_revision=4,
        )

        with pytest.raises(JobCommandVersionConflictError, match="stale"):
            control.retry_job(
                job.job_id,
                idempotency_key="retry-stale-001101",
                expected_revision=4,
                now=now + timedelta(seconds=5),
            )

        applied = control.retry_job(
            job.job_id,
            idempotency_key="retry-001101",
            expected_revision=5,
            now=now + timedelta(seconds=6),
        )
        assert applied.action == "applied"
        assert applied.status is JobStatus.ELIGIBLE
        assert applied.revision == 6
        snapshot = control.load_job(job.job_id)
        assert snapshot.retry_budget_remaining == 2

        reused = control.retry_job(
            job.job_id,
            idempotency_key="retry-001101",
            expected_revision=5,
            now=now + timedelta(seconds=7),
        )
        assert reused.action == "reused"
        assert control.load_job(job.job_id).retry_budget_remaining == 2

        with pytest.raises(JobCommandConflictError, match="cannot retry"):
            control.retry_job(
                job.job_id,
                idempotency_key="retry-again-001101",
                expected_revision=6,
                now=now + timedelta(seconds=8),
            )
    finally:
        engine.dispose()
        command.downgrade(config, "base")
