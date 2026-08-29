from __future__ import annotations

import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from ai_automation_force_api import Settings, create_app

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
                {"external_id": external_id, "title": f"Restart fixture {external_id}"},
            )
    finally:
        engine.dispose()


@pytest.mark.postgres
@pytest.mark.temporal
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
@pytest.mark.skipif(not TEMPORAL_INTEGRATION, reason="AAF_TEMPORAL_INTEGRATION=1 is required")
def test_api_restart_does_not_own_or_lose_temporal_workflow_reference() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    insert_project("PRJ-001280")
    settings = Settings(
        environment="test",
        build_revision="wp8-api-restart",
        database_url=DATABASE_URL,
    )

    try:
        first_app = create_app(settings)
        with TestClient(first_app) as first_client:
            created = first_client.post(
                "/api/v1/jobs",
                json={
                    "project_id": "PRJ-001280",
                    "job_type": "synthetic-cancellable",
                    "idempotency_key": "wp8-create-restart",
                },
            )
            assert created.status_code == 201
            job_id = created.json()["job"]["job_id"]
            started = first_client.post(
                f"/api/v1/jobs/{job_id}/start",
                json={
                    "idempotency_key": "wp8-start-restart",
                    "expected_revision": 1,
                },
            )
            assert started.status_code == 200
            workflow_id = started.json()["command"]["workflow_execution_id"]
            assert workflow_id

        # The first API lifespan is fully closed here; durable state must remain external.
        second_app = create_app(settings)
        with TestClient(second_app) as second_client:
            checkpoint = second_client.get(f"/api/v1/jobs/{job_id}")
            assert checkpoint.status_code == 200
            assert checkpoint.json()["job"]["workflow_execution_id"] == workflow_id
            assert checkpoint.json()["job"]["status"] == "eligible"

            workflow = second_client.get(f"/api/v1/workflows/{workflow_id}")
            assert workflow.status_code == 200
            assert workflow.json()["workflow"]["job_id"] == job_id
            assert workflow.json()["workflow"]["project_id"] == "PRJ-001280"

            cancelled = second_client.post(
                f"/api/v1/jobs/{job_id}/cancel",
                json={
                    "idempotency_key": "wp8-cancel-restart",
                    "expected_revision": 2,
                },
            )
            assert cancelled.status_code == 200
            assert cancelled.json()["command"]["status"] == "cancelled"
            assert cancelled.json()["command"]["revision"] == 3
    finally:
        command.downgrade(config, "base")
