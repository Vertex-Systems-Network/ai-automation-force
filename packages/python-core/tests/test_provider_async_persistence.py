from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text

from ai_automation_force_core import (
    PersistenceNotFoundError,
    PostgresProviderAsyncRepository,
    ProviderAsyncConflictError,
    ProviderAsyncStatus,
    ProviderAsyncSubmission,
    ProviderAsyncVersionConflictError,
    ProviderCallbackConflictError,
    ProviderCallbackEvent,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def seed_attempt(engine: object, *, project_id: str, job_id: str, attempt_id: str) -> None:
    with engine.begin() as connection:  # type: ignore[attr-defined]
        project_uuid = uuid4()
        job_uuid = uuid4()
        connection.execute(
            text(
                """
                INSERT INTO core.projects (
                    id, external_id, title, status, audience, "cast", content_format,
                    language, target_duration_seconds, output, creative, provider_policy,
                    created_at, updated_at
                ) VALUES (
                    :id, :external_id, :title, 'draft', '{}'::jsonb, '{}'::jsonb,
                    'song', 'en', 120, '{}'::jsonb, '{}'::jsonb, '{}'::jsonb,
                    now(), now()
                )
                """
            ),
            {
                "id": project_uuid,
                "external_id": project_id,
                "title": f"Fixture {project_id}",
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO core.jobs (
                    id, external_id, project_id, job_type, status, idempotency_key,
                    created_at, updated_at
                ) VALUES (
                    :id, :external_id, :project_id, 'synthetic-provider', 'running',
                    :idempotency_key, now(), now()
                )
                """
            ),
            {
                "id": job_uuid,
                "external_id": job_id,
                "project_id": project_uuid,
                "idempotency_key": f"idem-{job_id.lower()}",
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO core.generation_attempts (
                    id, external_id, job_id, attempt_number, provider_id,
                    model_provider_id, model_id, capability, access_class,
                    request_project_id, request_constraints, requires_commercial_rights,
                    requires_character_continuity, request_idempotency_key,
                    started_at, status, currency
                ) VALUES (
                    gen_random_uuid(), :external_id, :job_id, 1, 'synthetic',
                    'synthetic', 'fake-async-v1', 'video', 'test', :project_id,
                    '{}'::jsonb, false, false, :request_idempotency_key,
                    now(), 'running', 'USD'
                )
                """
            ),
            {
                "external_id": attempt_id,
                "job_id": job_uuid,
                "project_id": project_uuid,
                "request_idempotency_key": f"idem-{attempt_id.lower()}",
            },
        )


def callback(
    *,
    event_id: str,
    generation_id: str,
    status: ProviderAsyncStatus,
    event_at: datetime,
    received_at: datetime,
    payload_hash: str,
) -> ProviderCallbackEvent:
    return ProviderCallbackEvent(
        event_id=event_id,
        provider_id="synthetic",
        provider_generation_id=generation_id,
        provider_status=status.value,
        normalized_status=status,
        provider_event_at=event_at,
        received_at=received_at,
        payload_sha256=payload_hash,
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_provider_async_polling_reconciles_canonical_attempt_and_closes_terminal_state() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        seed_attempt(
            engine,
            project_id="PRJ-001100",
            job_id="JOB-001100",
            attempt_id="ATT-001100",
        )
        repository = PostgresProviderAsyncRepository(engine)
        submission = ProviderAsyncSubmission(
            attempt_id="ATT-001100",
            provider_id="synthetic",
            provider_generation_id="fake-gen-poll-1",
            submitted_at=now,
            next_poll_at=now + timedelta(seconds=1),
            deadline_at=now + timedelta(seconds=20),
        )

        created = repository.register_submission(submission)
        assert created.status is ProviderAsyncStatus.SUBMITTED
        assert created.revision == 1
        reused = repository.register_submission(submission)
        assert reused.duplicate
        assert reused.revision == 1

        running = repository.record_poll(
            "ATT-001100",
            provider_status="processing",
            normalized_status=ProviderAsyncStatus.RUNNING,
            observed_at=now + timedelta(seconds=1),
            next_poll_at=now + timedelta(seconds=2),
            expected_revision=1,
        )
        assert running.status is ProviderAsyncStatus.RUNNING
        assert running.revision == 2

        with pytest.raises(ProviderAsyncVersionConflictError):
            repository.record_poll(
                "ATT-001100",
                provider_status="processing",
                normalized_status=ProviderAsyncStatus.RUNNING,
                observed_at=now + timedelta(seconds=2),
                next_poll_at=now + timedelta(seconds=3),
                expected_revision=1,
            )

        completed = repository.record_poll(
            "ATT-001100",
            provider_status="complete",
            normalized_status=ProviderAsyncStatus.SUCCEEDED,
            observed_at=now + timedelta(seconds=2),
            next_poll_at=None,
            expected_revision=2,
        )
        assert completed.status is ProviderAsyncStatus.SUCCEEDED
        assert completed.revision == 3

        stale = repository.record_poll(
            "ATT-001100",
            provider_status="complete",
            normalized_status=ProviderAsyncStatus.SUCCEEDED,
            observed_at=now + timedelta(seconds=3),
            next_poll_at=None,
            expected_revision=3,
        )
        assert stale.stale
        assert stale.status is ProviderAsyncStatus.SUCCEEDED
        assert stale.revision == 3

        with engine.connect() as connection:
            attempt = connection.execute(
                text(
                    """
                    SELECT provider_generation_id, status, normalized_error_code, finished_at
                    FROM core.generation_attempts
                    WHERE external_id = 'ATT-001100'
                    """
                )
            ).mappings().one()
            state = repository.load("ATT-001100")

        assert attempt["provider_generation_id"] == "fake-gen-poll-1"
        assert attempt["status"] == "succeeded"
        assert attempt["normalized_error_code"] is None
        assert attempt["finished_at"] is not None
        assert state["status"] == ProviderAsyncStatus.SUCCEEDED.value
        assert state["poll_count"] == 2
        assert state["next_poll_at"] is None
        assert state["terminal_at"] is not None
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_verified_callback_inbox_deduplicates_and_rejects_stale_or_conflicting_events() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        seed_attempt(
            engine,
            project_id="PRJ-001101",
            job_id="JOB-001101",
            attempt_id="ATT-001101",
        )
        repository = PostgresProviderAsyncRepository(engine)
        repository.register_submission(
            ProviderAsyncSubmission(
                attempt_id="ATT-001101",
                provider_id="synthetic",
                provider_generation_id="fake-gen-callback-1",
                submitted_at=now,
                next_poll_at=now + timedelta(seconds=2),
                deadline_at=now + timedelta(seconds=30),
            )
        )

        running_event = callback(
            event_id="evt-running-1",
            generation_id="fake-gen-callback-1",
            status=ProviderAsyncStatus.RUNNING,
            event_at=now + timedelta(seconds=2),
            received_at=now + timedelta(seconds=3),
            payload_hash="a" * 64,
        )
        running = repository.receive_callback(running_event)
        assert running.status is ProviderAsyncStatus.RUNNING
        assert running.revision == 2

        duplicate = repository.receive_callback(running_event)
        assert duplicate.duplicate
        assert duplicate.event_id == "evt-running-1"
        assert duplicate.revision == 2

        with pytest.raises(ProviderCallbackConflictError):
            repository.receive_callback(
                callback(
                    event_id="evt-running-1",
                    generation_id="fake-gen-callback-1",
                    status=ProviderAsyncStatus.RUNNING,
                    event_at=now + timedelta(seconds=2),
                    received_at=now + timedelta(seconds=4),
                    payload_hash="b" * 64,
                )
            )

        stale = repository.receive_callback(
            callback(
                event_id="evt-stale-1",
                generation_id="fake-gen-callback-1",
                status=ProviderAsyncStatus.SUBMITTED,
                event_at=now + timedelta(seconds=1),
                received_at=now + timedelta(seconds=4),
                payload_hash="c" * 64,
            )
        )
        assert stale.stale
        assert stale.revision == 2
        assert stale.status is ProviderAsyncStatus.RUNNING

        completed = repository.receive_callback(
            callback(
                event_id="evt-success-1",
                generation_id="fake-gen-callback-1",
                status=ProviderAsyncStatus.SUCCEEDED,
                event_at=now + timedelta(seconds=5),
                received_at=now + timedelta(seconds=6),
                payload_hash="d" * 64,
            )
        )
        assert completed.status is ProviderAsyncStatus.SUCCEEDED
        assert completed.revision == 3

        late = repository.receive_callback(
            callback(
                event_id="evt-late-1",
                generation_id="fake-gen-callback-1",
                status=ProviderAsyncStatus.RUNNING,
                event_at=now + timedelta(seconds=7),
                received_at=now + timedelta(seconds=8),
                payload_hash="e" * 64,
            )
        )
        assert late.stale
        assert late.status is ProviderAsyncStatus.SUCCEEDED
        assert late.revision == 3

        with pytest.raises(PersistenceNotFoundError):
            repository.receive_callback(
                callback(
                    event_id="evt-unknown-1",
                    generation_id="fake-gen-missing",
                    status=ProviderAsyncStatus.RUNNING,
                    event_at=now + timedelta(seconds=1),
                    received_at=now + timedelta(seconds=2),
                    payload_hash="f" * 64,
                )
            )

        with engine.connect() as connection:
            callback_count = connection.execute(
                select(func.count()).select_from(repository.callbacks)
            ).scalar_one()
            stale_count = connection.execute(
                select(func.count())
                .select_from(repository.callbacks)
                .where(repository.callbacks.c.stale.is_(True))
            ).scalar_one()
            attempt = connection.execute(
                text(
                    """
                    SELECT status, normalized_error_code, finished_at
                    FROM core.generation_attempts
                    WHERE external_id = 'ATT-001101'
                    """
                )
            ).mappings().one()

        assert callback_count == 4
        assert stale_count == 2
        assert attempt["status"] == "succeeded"
        assert attempt["normalized_error_code"] is None
        assert attempt["finished_at"] is not None
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_provider_timeout_is_deadline_guarded_and_reconciles_failure_once() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime.now(UTC)

    try:
        seed_attempt(
            engine,
            project_id="PRJ-001102",
            job_id="JOB-001102",
            attempt_id="ATT-001102",
        )
        repository = PostgresProviderAsyncRepository(engine)
        repository.register_submission(
            ProviderAsyncSubmission(
                attempt_id="ATT-001102",
                provider_id="synthetic",
                provider_generation_id="fake-gen-timeout-1",
                submitted_at=now,
                next_poll_at=now + timedelta(seconds=1),
                deadline_at=now + timedelta(seconds=5),
            )
        )

        with pytest.raises(ProviderAsyncConflictError, match="has not elapsed"):
            repository.mark_timeout(
                "ATT-001102",
                now=now + timedelta(seconds=4),
                expected_revision=1,
            )

        timed_out = repository.mark_timeout(
            "ATT-001102",
            now=now + timedelta(seconds=5),
            expected_revision=1,
        )
        assert timed_out.status is ProviderAsyncStatus.TIMED_OUT
        assert timed_out.revision == 2

        repeated = repository.mark_timeout(
            "ATT-001102",
            now=now + timedelta(seconds=6),
            expected_revision=2,
        )
        assert repeated.stale
        assert repeated.revision == 2

        with engine.connect() as connection:
            attempt = connection.execute(
                text(
                    """
                    SELECT status, normalized_error_code, finished_at
                    FROM core.generation_attempts
                    WHERE external_id = 'ATT-001102'
                    """
                )
            ).mappings().one()

        assert attempt["status"] == "failed"
        assert attempt["normalized_error_code"] == "provider_timeout"
        assert attempt["finished_at"] is not None
    finally:
        engine.dispose()
        command.downgrade(config, "base")
