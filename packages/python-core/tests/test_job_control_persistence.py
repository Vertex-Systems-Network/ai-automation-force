from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text

from ai_automation_force_core import (
    AuditFields,
    Job,
    JobIdempotencyConflictError,
    JobLeaseConflictError,
    JobStateConflictError,
    JobStatus,
    JobVersionConflictError,
    PersistenceReferenceError,
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


def queued_job(
    *,
    job_id: str,
    project_id: str,
    idempotency_key: str,
    now: datetime,
    dependency_job_ids: list[str] | None = None,
) -> Job:
    return Job(
        job_id=job_id,
        project_id=project_id,
        job_type="synthetic-render",
        idempotency_key=idempotency_key,
        dependency_job_ids=dependency_job_ids or [],
        audit=AuditFields(created_at=now, updated_at=now, revision=1),
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_job_control_is_idempotent_versioned_leased_and_outboxed() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        insert_project(engine, "PRJ-000930")
        repository = PostgresJobControlRepository(engine)
        job = queued_job(
            job_id="JOB-000930",
            project_id="PRJ-000930",
            idempotency_key="idem-000930",
            now=now,
        )
        operation = {"mode": "synthetic", "shot_count": 3}

        created = repository.submit(job, operation)
        assert created.action == "created"
        assert created.revision == 1

        reused = repository.submit(job, {"shot_count": 3, "mode": "synthetic"})
        assert reused.action == "reused"
        assert reused.job_id == job.job_id
        assert reused.operation_fingerprint == created.operation_fingerprint

        with pytest.raises(JobIdempotencyConflictError):
            repository.submit(job, {"mode": "synthetic", "shot_count": 4})

        eligible = repository.transition(
            job.job_id,
            JobStatus.ELIGIBLE,
            now=now + timedelta(seconds=1),
            expected_revision=1,
        )
        assert eligible.revision == 2

        with pytest.raises(JobVersionConflictError):
            repository.transition(
                job.job_id,
                JobStatus.CANCELLED,
                now=now + timedelta(seconds=2),
                expected_revision=1,
            )

        first_claim = repository.claim(
            job.job_id,
            owner="worker-a",
            now=now + timedelta(seconds=2),
            lease_for=timedelta(seconds=30),
            expected_revision=2,
        )
        assert first_claim.revision == 3

        running = repository.transition(
            job.job_id,
            JobStatus.RUNNING,
            now=now + timedelta(seconds=3),
            expected_revision=3,
        )
        assert running.revision == 4

        renewed = repository.renew_lease(
            job.job_id,
            owner="worker-a",
            now=now + timedelta(seconds=4),
            lease_for=timedelta(seconds=30),
            expected_revision=4,
        )
        assert renewed.revision == 5

        with pytest.raises(JobLeaseConflictError):
            repository.renew_lease(
                job.job_id,
                owner="worker-b",
                now=now + timedelta(seconds=5),
                lease_for=timedelta(seconds=30),
                expected_revision=5,
            )

        recovered = repository.recover_expired_lease(
            job.job_id,
            now=now + timedelta(seconds=40),
            expected_revision=5,
        )
        assert recovered.status is JobStatus.ELIGIBLE
        assert recovered.revision == 6

        second_claim = repository.claim(
            job.job_id,
            owner="worker-b",
            now=now + timedelta(seconds=41),
            lease_for=timedelta(seconds=30),
            expected_revision=6,
        )
        assert second_claim.revision == 7

        repository.transition(
            job.job_id,
            JobStatus.RUNNING,
            now=now + timedelta(seconds=42),
            expected_revision=7,
        )
        completed = repository.transition(
            job.job_id,
            JobStatus.COMPLETED,
            now=now + timedelta(seconds=43),
            expected_revision=8,
        )
        assert completed.revision == 9

        with pytest.raises(JobStateConflictError):
            repository.transition(
                job.job_id,
                JobStatus.ELIGIBLE,
                now=now + timedelta(seconds=44),
                expected_revision=9,
            )

        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT status, revision, claimed_by, lease_expires_at,
                           operation_fingerprint
                    FROM core.jobs
                    WHERE external_id = 'JOB-000930'
                    """
                )
            ).mappings().one()
            outbox_count = connection.execute(
                select(func.count()).select_from(repository.outbox)
            ).scalar_one()

        assert row["status"] == JobStatus.COMPLETED.value
        assert row["revision"] == 9
        assert row["claimed_by"] is None
        assert row["lease_expires_at"] is None
        assert row["operation_fingerprint"] == created.operation_fingerprint
        assert outbox_count == 8

        pending = repository.pending_outbox()
        assert len(pending) == 8
        assert pending[0]["event_type"] == "job.created"
        first_message_id = pending[0]["id"]
        assert repository.mark_outbox_published(
            first_message_id,
            published_at=now + timedelta(seconds=50),
        )
        assert not repository.mark_outbox_published(
            first_message_id,
            published_at=now + timedelta(seconds=51),
        )
        assert len(repository.pending_outbox()) == 7
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_job_control_rejects_cross_project_dependency() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        insert_project(engine, "PRJ-000931")
        insert_project(engine, "PRJ-000932")
        repository = PostgresJobControlRepository(engine)

        foreign_job = queued_job(
            job_id="JOB-000931",
            project_id="PRJ-000932",
            idempotency_key="idem-000931",
            now=now,
        )
        assert repository.submit(foreign_job, {"kind": "foreign"}).action == "created"

        dependent = queued_job(
            job_id="JOB-000932",
            project_id="PRJ-000931",
            idempotency_key="idem-000932",
            dependency_job_ids=[foreign_job.job_id],
            now=now,
        )
        with pytest.raises(PersistenceReferenceError, match="another project"):
            repository.submit(dependent, {"kind": "dependent"})
    finally:
        engine.dispose()
        command.downgrade(config, "base")
