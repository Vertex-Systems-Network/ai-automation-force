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
    JobStatus,
    PostgresJobControlRepository,
    operation_fingerprint,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def test_100_shot_operations_have_unique_order_independent_fingerprints() -> None:
    operations = [
        {
            "project_id": "PRJ-009800",
            "shot_id": f"SHT-{index + 1:06d}",
            "operation": "synthetic-recovery-shot",
            "shot_index": index,
        }
        for index in range(100)
    ]
    fingerprints = [operation_fingerprint(operation) for operation in operations]

    assert len(fingerprints) == 100
    assert len(set(fingerprints)) == 100

    for operation, fingerprint in zip(operations, fingerprints, strict=True):
        reordered = {
            "shot_index": operation["shot_index"],
            "operation": operation["operation"],
            "shot_id": operation["shot_id"],
            "project_id": operation["project_id"],
        }
        assert operation_fingerprint(reordered) == fingerprint


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_100_jobs_enqueue_reuse_and_complete_without_duplicate_terminal_events() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    repository = PostgresJobControlRepository(engine)
    started_at = datetime.now(UTC)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.projects (
                        id, external_id, title, status, audience, "cast", content_format,
                        language, target_duration_seconds, output, creative, provider_policy,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), 'PRJ-009801', 'WP8 100-shot persistence', 'draft',
                        '{}'::jsonb, '{}'::jsonb, 'short-film', 'en', 120,
                        '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, now(), now()
                    )
                    """
                )
            )

        for index in range(100):
            now = started_at + timedelta(milliseconds=index)
            job_id = f"JOB-{980100 + index:06d}"
            idempotency_key = f"wp8-shot-{index:03d}-create"
            job = Job(
                job_id=job_id,
                project_id="PRJ-009801",
                job_type="synthetic-recovery-shot",
                idempotency_key=idempotency_key,
                retry_budget_remaining=3,
                audit=AuditFields(created_at=now, updated_at=now, revision=1),
            )
            operation = {
                "project_id": "PRJ-009801",
                "shot_index": index,
                "operation": "synthetic-recovery-shot",
            }
            created = repository.submit(job, operation)
            assert created.action == "created"
            reused = repository.submit(
                job,
                {
                    "operation": "synthetic-recovery-shot",
                    "shot_index": index,
                    "project_id": "PRJ-009801",
                },
            )
            assert reused.action == "reused"
            assert reused.operation_fingerprint == created.operation_fingerprint

            eligible_at = now + timedelta(seconds=1)
            repository.transition(
                job_id,
                JobStatus.ELIGIBLE,
                now=eligible_at,
                expected_revision=1,
            )
            repository.claim(
                job_id,
                owner=f"wp8-worker-{index % 4}",
                now=eligible_at + timedelta(seconds=1),
                lease_for=timedelta(seconds=30),
                expected_revision=2,
            )
            repository.transition(
                job_id,
                JobStatus.RUNNING,
                now=eligible_at + timedelta(seconds=2),
                expected_revision=3,
            )
            completed = repository.transition(
                job_id,
                JobStatus.COMPLETED,
                now=eligible_at + timedelta(seconds=3),
                expected_revision=4,
            )
            assert completed.revision == 5

        with engine.connect() as connection:
            job_count = connection.execute(
                text("SELECT count(*) FROM core.jobs WHERE project_id = (SELECT id FROM core.projects WHERE external_id = 'PRJ-009801')")
            ).scalar_one()
            completed_count = connection.execute(
                text(
                    """
                    SELECT count(*)
                    FROM core.jobs
                    WHERE project_id = (
                        SELECT id FROM core.projects WHERE external_id = 'PRJ-009801'
                    ) AND status = 'completed'
                    """
                )
            ).scalar_one()
            terminal_event_count = connection.execute(
                text(
                    """
                    SELECT count(*)
                    FROM core.outbox_messages AS event
                    JOIN core.jobs AS job ON job.id = event.job_id
                    JOIN core.projects AS project ON project.id = job.project_id
                    WHERE project.external_id = 'PRJ-009801'
                      AND event.event_type = 'job.status.changed'
                      AND event.payload ->> 'status' = 'completed'
                    """
                )
            ).scalar_one()

        assert job_count == 100
        assert completed_count == 100
        assert terminal_event_count == 100
    finally:
        engine.dispose()
        command.downgrade(config, "base")
