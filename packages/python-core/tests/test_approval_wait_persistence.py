from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, func, select, text

from ai_automation_force_core import (
    Approval,
    ApprovalDecision,
    ApprovalWaitConflictError,
    ApprovalWaitKind,
    ApprovalWaitRequest,
    ApprovalWaitVersionConflictError,
    JobStatus,
    PostgresApprovalWaitRepository,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def insert_project(engine: Engine, external_id: str) -> None:
    with engine.begin() as connection:
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
                    '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, :now, :now
                )
                """
            ),
            {
                "external_id": external_id,
                "title": f"Fixture {external_id}",
                "now": datetime(2026, 8, 29, 9, 0, tzinfo=UTC),
            },
        )


def insert_wait_job(
    engine: Engine,
    *,
    external_id: str,
    project_id: str,
    status: JobStatus,
    revision: int,
    now: datetime,
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO core.jobs (
                    id, external_id, project_id, job_type, status, priority,
                    idempotency_key, retry_budget_remaining, blocked_reason,
                    created_at, updated_at, revision
                )
                SELECT
                    gen_random_uuid(), :external_id, p.id, 'synthetic-approval', :status, 50,
                    :idempotency_key, 3, :blocked_reason, :now, :now, :revision
                FROM core.projects p
                WHERE p.external_id = :project_id
                """
            ),
            {
                "external_id": external_id,
                "project_id": project_id,
                "status": status.value,
                "idempotency_key": f"job-{external_id.lower()}",
                "blocked_reason": (
                    "approval required"
                    if status in {JobStatus.BLOCKED_BUDGET, JobStatus.MANUAL_HANDOFF}
                    else None
                ),
                "now": now,
                "revision": revision,
            },
        )


def approval_request(
    *,
    request_id: str,
    project_id: str,
    job_id: str,
    wait_kind: ApprovalWaitKind,
    job_revision: int,
    now: datetime,
    idempotency_key: str,
    expires_at: datetime | None = None,
    reason: str = "review required",
) -> ApprovalWaitRequest:
    return ApprovalWaitRequest(
        request_id=request_id,
        project_id=project_id,
        job_id=job_id,
        wait_kind=wait_kind,
        subject_type="job",
        subject_id=job_id,
        requested_job_revision=job_revision,
        requested_by="workflow",
        requested_at=now,
        idempotency_key=idempotency_key,
        expires_at=expires_at,
        reason=reason,
    )


def approval(
    *,
    approval_id: str,
    project_id: str,
    job_id: str,
    decision: ApprovalDecision,
    now: datetime,
) -> Approval:
    return Approval(
        approval_id=approval_id,
        project_id=project_id,
        subject_type="job",
        subject_id=job_id,
        decision=decision,
        actor="reviewer@example.invalid",
        reason="synthetic decision",
        created_at=now,
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_human_approval_wait_is_idempotent_atomic_and_outboxed() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime(2026, 8, 29, 9, 0, tzinfo=UTC)

    try:
        insert_project(engine, "PRJ-000950")
        insert_wait_job(
            engine,
            external_id="JOB-000950",
            project_id="PRJ-000950",
            status=JobStatus.WAITING_HUMAN,
            revision=5,
            now=now,
        )
        repository = PostgresApprovalWaitRepository(engine)
        request = approval_request(
            request_id="AQR-000950",
            project_id="PRJ-000950",
            job_id="JOB-000950",
            wait_kind=ApprovalWaitKind.HUMAN_APPROVAL,
            job_revision=5,
            now=now,
            idempotency_key="approval-000950",
            expires_at=now + timedelta(minutes=10),
        )

        created = repository.request(request)
        assert created.action == "created"
        assert created.request_revision == 1
        assert repository.request(request).action == "reused"

        changed = approval_request(
            request_id="AQR-000950",
            project_id="PRJ-000950",
            job_id="JOB-000950",
            wait_kind=ApprovalWaitKind.HUMAN_APPROVAL,
            job_revision=5,
            now=now,
            idempotency_key="approval-000950",
            expires_at=now + timedelta(minutes=10),
            reason="different semantics",
        )
        with pytest.raises(ApprovalWaitConflictError, match="different request semantics"):
            repository.request(changed)

        second_pending = approval_request(
            request_id="AQR-000951",
            project_id="PRJ-000950",
            job_id="JOB-000950",
            wait_kind=ApprovalWaitKind.HUMAN_APPROVAL,
            job_revision=5,
            now=now,
            idempotency_key="approval-000951",
            expires_at=now + timedelta(minutes=10),
        )
        with pytest.raises(ApprovalWaitConflictError, match="database rejected"):
            repository.request(second_pending)

        decision = approval(
            approval_id="APR-000950",
            project_id="PRJ-000950",
            job_id="JOB-000950",
            decision=ApprovalDecision.APPROVED,
            now=now + timedelta(minutes=1),
        )
        resolved = repository.resolve(
            request.request_id,
            decision,
            expected_request_revision=1,
        )
        assert resolved.action == "resolved"
        assert resolved.job_status is JobStatus.ELIGIBLE
        assert resolved.job_revision == 6
        assert resolved.request_revision == 2

        reused = repository.resolve(
            request.request_id,
            decision,
            expected_request_revision=1,
        )
        assert reused.action == "reused"
        assert reused.job_revision == 6
        assert reused.approval_id == decision.approval_id

        with engine.connect() as connection:
            job = connection.execute(
                text(
                    "SELECT status, revision, blocked_reason FROM core.jobs "
                    "WHERE external_id = 'JOB-000950'"
                )
            ).mappings().one()
            request_row = repository.load(request.request_id)
            approval_count = connection.execute(
                select(func.count()).select_from(repository.approvals)
            ).scalar_one()
            outbox_count = connection.execute(
                select(func.count())
                .select_from(repository.outbox)
                .where(repository.outbox.c.event_type.like("approval.%"))
            ).scalar_one()

        assert job["status"] == JobStatus.ELIGIBLE.value
        assert job["revision"] == 6
        assert job["blocked_reason"] is None
        assert request_row["status"] == "resolved"
        assert request_row["resolved_job_status"] == JobStatus.ELIGIBLE.value
        assert request_row["resolved_job_revision"] == 6
        assert approval_count == 1
        assert outbox_count == 2
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_approval_wait_rejects_stale_job_and_expires_idempotently() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime(2026, 8, 29, 10, 0, tzinfo=UTC)

    try:
        insert_project(engine, "PRJ-000952")
        insert_wait_job(
            engine,
            external_id="JOB-000952",
            project_id="PRJ-000952",
            status=JobStatus.WAITING_HUMAN,
            revision=3,
            now=now,
        )
        insert_wait_job(
            engine,
            external_id="JOB-000953",
            project_id="PRJ-000952",
            status=JobStatus.WAITING_HUMAN,
            revision=7,
            now=now,
        )
        repository = PostgresApprovalWaitRepository(engine)

        stale_request = approval_request(
            request_id="AQR-000952",
            project_id="PRJ-000952",
            job_id="JOB-000952",
            wait_kind=ApprovalWaitKind.HUMAN_APPROVAL,
            job_revision=3,
            now=now,
            idempotency_key="approval-000952",
            expires_at=now + timedelta(minutes=5),
        )
        repository.request(stale_request)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE core.jobs SET revision = 4, updated_at = :updated_at "
                    "WHERE external_id = 'JOB-000952'"
                ),
                {"updated_at": now + timedelta(seconds=1)},
            )

        with pytest.raises(ApprovalWaitVersionConflictError, match="stale job revision"):
            repository.resolve(
                stale_request.request_id,
                approval(
                    approval_id="APR-000952",
                    project_id="PRJ-000952",
                    job_id="JOB-000952",
                    decision=ApprovalDecision.APPROVED,
                    now=now + timedelta(minutes=1),
                ),
                expected_request_revision=1,
            )

        expiring = approval_request(
            request_id="AQR-000953",
            project_id="PRJ-000952",
            job_id="JOB-000953",
            wait_kind=ApprovalWaitKind.HUMAN_APPROVAL,
            job_revision=7,
            now=now,
            idempotency_key="approval-000953",
            expires_at=now + timedelta(minutes=1),
        )
        repository.request(expiring)
        expired = repository.expire(
            expiring.request_id,
            now=now + timedelta(minutes=2),
            expected_request_revision=1,
        )
        assert expired.action == "expired"
        assert expired.job_status is JobStatus.MANUAL_HANDOFF
        assert expired.job_revision == 8
        assert expired.request_revision == 2

        duplicate = repository.expire(
            expiring.request_id,
            now=now + timedelta(minutes=3),
            expected_request_revision=1,
        )
        assert duplicate.action == "expired"
        assert duplicate.job_revision == 8

        with engine.connect() as connection:
            job = connection.execute(
                text(
                    "SELECT status, revision, blocked_reason FROM core.jobs "
                    "WHERE external_id = 'JOB-000953'"
                )
            ).mappings().one()
        assert job["status"] == JobStatus.MANUAL_HANDOFF.value
        assert job["revision"] == 8
        assert "AQR-000953" in job["blocked_reason"]
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.parametrize(
    ("wait_kind", "job_status", "job_id", "request_id", "approval_id"),
    [
        (
            ApprovalWaitKind.BUDGET,
            JobStatus.BLOCKED_BUDGET,
            "JOB-000954",
            "AQR-000954",
            "APR-000954",
        ),
        (
            ApprovalWaitKind.MANUAL_HANDOFF,
            JobStatus.MANUAL_HANDOFF,
            "JOB-000955",
            "AQR-000955",
            "APR-000955",
        ),
    ],
)
@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_budget_and_manual_waits_resume_safely_when_approved(
    wait_kind: ApprovalWaitKind,
    job_status: JobStatus,
    job_id: str,
    request_id: str,
    approval_id: str,
) -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    now = datetime(2026, 8, 29, 11, 0, tzinfo=UTC)

    try:
        insert_project(engine, "PRJ-000954")
        insert_wait_job(
            engine,
            external_id=job_id,
            project_id="PRJ-000954",
            status=job_status,
            revision=2,
            now=now,
        )
        repository = PostgresApprovalWaitRepository(engine)
        request = approval_request(
            request_id=request_id,
            project_id="PRJ-000954",
            job_id=job_id,
            wait_kind=wait_kind,
            job_revision=2,
            now=now,
            idempotency_key=f"approval-{request_id.lower()}",
        )
        repository.request(request)
        result = repository.resolve(
            request_id,
            approval(
                approval_id=approval_id,
                project_id="PRJ-000954",
                job_id=job_id,
                decision=ApprovalDecision.APPROVED,
                now=now + timedelta(seconds=1),
            ),
            expected_request_revision=1,
        )
        assert result.job_status is JobStatus.ELIGIBLE
        assert result.job_revision == 3
    finally:
        engine.dispose()
        command.downgrade(config, "base")
