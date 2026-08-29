from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from ai_automation_force_core import JobStatus
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from ai_automation_force_api import Settings, create_app
from ai_automation_force_api.control import ControlService

DATABASE_URL = os.environ.get("DATABASE_URL")
TEMPORAL_INTEGRATION = os.environ.get("AAF_TEMPORAL_INTEGRATION") == "1"
ROOT = Path(__file__).resolve().parents[3]
ALEMBIC_INI = ROOT / "packages" / "python-core" / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def insert_project(external_id: str) -> None:
    assert DATABASE_URL is not None
    engine = create_engine(DATABASE_URL)
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
                        gen_random_uuid(), :external_id, :title, 'draft',
                        '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                        '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, now(), now()
                    )
                    """
                ),
                {"external_id": external_id, "title": f"API fixture {external_id}"},
            )
    finally:
        engine.dispose()


@pytest.mark.postgres
@pytest.mark.temporal
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_job_control_api_is_idempotent_paginated_streamable_and_temporal_linked() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    insert_project("PRJ-001200")
    app = create_app(
        Settings(
            environment="test",
            build_revision="wp7-integration",
            database_url=DATABASE_URL,
            sse_poll_interval_ms=25,
            sse_heartbeat_seconds=1,
        )
    )

    try:
        with TestClient(app) as client:
            body = {
                "project_id": "PRJ-001200",
                "job_type": "synthetic-cancellable",
                "idempotency_key": "api-create-001200",
                "priority": 70,
            }
            created = client.post("/api/v1/jobs", json=body)
            assert created.status_code == 201
            created_payload = created.json()
            assert created_payload["action"] == "created"
            job_id = created_payload["job"]["job_id"]
            first_cursor = created_payload["event_cursor"]
            assert first_cursor
            assert created_payload["job"]["status"] == "queued"
            assert created_payload["job"]["revision"] == 1

            reused_create = client.post("/api/v1/jobs", json=body)
            assert reused_create.status_code == 201
            assert reused_create.json()["action"] == "reused"
            assert reused_create.json()["job"]["job_id"] == job_id

            checkpoint = client.get(f"/api/v1/jobs/{job_id}")
            assert checkpoint.status_code == 200
            assert checkpoint.json()["event_cursor"] == first_cursor

            project_jobs = client.get("/api/v1/projects/PRJ-001200/jobs?limit=1")
            assert project_jobs.status_code == 200
            assert [item["job_id"] for item in project_jobs.json()["items"]] == [job_id]

            project_status = client.get("/api/v1/projects/PRJ-001200/status")
            assert project_status.status_code == 200
            assert project_status.json()["total_jobs"] == 1
            assert project_status.json()["job_status_counts"] == {"queued": 1}

            history = client.get(f"/api/v1/jobs/{job_id}/history")
            assert history.status_code == 200
            assert [item["event_type"] for item in history.json()["items"]] == ["job.created"]

            finite_stream = client.get(f"/api/v1/jobs/{job_id}/events?follow=false")
            assert finite_stream.status_code == 200
            assert finite_stream.headers["content-type"].startswith("text/event-stream")
            assert "event: job.created" in finite_stream.text
            assert "\"schema_version\":1" in finite_stream.text

            resumed_stream = client.get(
                f"/api/v1/jobs/{job_id}/events?follow=false",
                headers={"Last-Event-ID": first_cursor},
            )
            assert resumed_stream.status_code == 200
            assert resumed_stream.text == ""

            started = client.post(
                f"/api/v1/jobs/{job_id}/start",
                json={"idempotency_key": "api-start-001200", "expected_revision": 1},
            )
            assert started.status_code == 200
            start_command = started.json()["command"]
            assert start_command["action"] == "applied"
            assert start_command["status"] == "eligible"
            assert start_command["revision"] == 2
            workflow_id = start_command["workflow_execution_id"]
            assert workflow_id.startswith("WFX-")

            reused_start = client.post(
                f"/api/v1/jobs/{job_id}/start",
                json={"idempotency_key": "api-start-001200", "expected_revision": 1},
            )
            assert reused_start.status_code == 200
            assert reused_start.json()["command"]["action"] == "reused"
            assert reused_start.json()["command"]["workflow_execution_id"] == workflow_id

            workflow = client.get(f"/api/v1/workflows/{workflow_id}")
            assert workflow.status_code == 200
            assert workflow.json()["workflow"]["job_id"] == job_id
            assert workflow.json()["workflow"]["project_id"] == "PRJ-001200"

            after_start = client.get(f"/api/v1/jobs/{job_id}/history")
            assert [item["job_revision"] for item in after_start.json()["items"]] == [1, 2]
            assert after_start.json()["items"][-1]["payload"]["command"] == "start"

            status_after_start = client.get("/api/v1/projects/PRJ-001200/status")
            assert status_after_start.json()["job_status_counts"] == {"eligible": 1}
            assert status_after_start.json()["workflow_status_counts"] == {"running": 1}

            stale_cancel = client.post(
                f"/api/v1/jobs/{job_id}/cancel",
                json={"idempotency_key": "api-cancel-stale-001200", "expected_revision": 1},
            )
            assert stale_cancel.status_code == 409
            assert stale_cancel.json()["error"]["code"] == "STALE_REVISION"

            cancelled = client.post(
                f"/api/v1/jobs/{job_id}/cancel",
                json={"idempotency_key": "api-cancel-001200", "expected_revision": 2},
            )
            assert cancelled.status_code == 200
            assert cancelled.json()["command"]["status"] == "cancelled"
            assert cancelled.json()["command"]["revision"] == 3

            invalid_cursor = client.get(
                f"/api/v1/jobs/{job_id}/history",
                params={"cursor": "not-a-valid-cursor"},
            )
            assert invalid_cursor.status_code == 400
            assert invalid_cursor.json()["error"]["code"] == "INVALID_CONTROL_REQUEST"

            missing = client.get("/api/v1/jobs/JOB-999999")
            assert missing.status_code == 404
            assert missing.json()["error"]["code"] == "NOT_FOUND"
    finally:
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_retry_api_requeues_retryable_failure_once() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    insert_project("PRJ-001201")
    app = create_app(Settings(environment="test", database_url=DATABASE_URL))

    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/jobs",
                json={
                    "project_id": "PRJ-001201",
                    "job_type": "synthetic-control",
                    "idempotency_key": "api-create-001201",
                },
            )
            job_id = created.json()["job"]["job_id"]
            service = app.state.control_service
            assert isinstance(service, ControlService)
            now = datetime.now(UTC)
            service.jobs.transition(
                job_id,
                JobStatus.ELIGIBLE,
                now=now,
                expected_revision=1,
            )
            service.jobs.claim(
                job_id,
                owner="api-test-worker",
                now=now + timedelta(seconds=1),
                lease_for=timedelta(seconds=30),
                expected_revision=2,
            )
            service.jobs.transition(
                job_id,
                JobStatus.RUNNING,
                now=now + timedelta(seconds=2),
                expected_revision=3,
            )
            service.jobs.transition(
                job_id,
                JobStatus.RETRYABLE_FAILED,
                now=now + timedelta(seconds=3),
                expected_revision=4,
            )

            retried = client.post(
                f"/api/v1/jobs/{job_id}/retry",
                json={"idempotency_key": "api-retry-001201", "expected_revision": 5},
            )
            assert retried.status_code == 200
            assert retried.json()["command"]["action"] == "applied"
            assert retried.json()["command"]["status"] == "eligible"
            assert retried.json()["command"]["revision"] == 6

            reused = client.post(
                f"/api/v1/jobs/{job_id}/retry",
                json={"idempotency_key": "api-retry-001201", "expected_revision": 5},
            )
            assert reused.status_code == 200
            assert reused.json()["command"]["action"] == "reused"
            checkpoint = client.get(f"/api/v1/jobs/{job_id}").json()["job"]
            assert checkpoint["retry_budget_remaining"] == 2
    finally:
        command.downgrade(config, "base")
