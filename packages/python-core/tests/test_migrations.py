from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"

EXPECTED_CORE_TABLES = {
    "rights_records",
    "style_profiles",
    "projects",
    "contents",
    "content_versions",
    "voice_profiles",
    "characters",
    "character_versions",
    "character_looks",
    "character_locks",
    "worlds",
    "locations",
    "props",
    "timelines",
    "timeline_tracks",
    "timeline_track_items",
    "acts",
    "sequences",
    "scenes",
    "shots",
    "takes",
    "assets",
    "storage_objects",
    "jobs",
    "job_dependencies",
    "job_commands",
    "generation_attempts",
    "generation_attempt_input_assets",
    "generation_attempt_qa_records",
    "qa_records",
    "take_qa_records",
    "cost_records",
    "approvals",
    "approval_requests",
    "legacy_content_imports",
    "project_characters",
    "project_worlds",
    "project_props",
    "content_version_characters",
    "content_version_worlds",
    "content_version_props",
    "scene_characters",
    "shot_characters",
    "shot_props",
    "shot_reference_assets",
    "character_version_reference_assets",
    "character_look_reference_assets",
    "world_reference_assets",
    "location_reference_assets",
    "prop_reference_assets",
    "style_reference_assets",
    "asset_parents",
    "timeline_marker_assets",
    "workflow_executions",
    "outbox_messages",
    "circuit_breakers",
    "provider_async_states",
    "provider_callback_events",
}

PROVIDER_ASYNC_TABLES = {"provider_async_states", "provider_callback_events"}
WP7_TABLES = {"job_commands"}
M03_WP1_TABLES = {"storage_objects"}


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_postgresql_migration_chain_is_reversible_and_deterministic() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    engine = create_engine(DATABASE_URL)

    try:
        command.upgrade(config, "head")

        db_inspector = inspect(engine)
        assert "core" in db_inspector.get_schema_names()
        assert set(db_inspector.get_table_names(schema="core")) == EXPECTED_CORE_TABLES
        job_columns = {column["name"] for column in db_inspector.get_columns("jobs", schema="core")}
        assert "operation_fingerprint" in job_columns
        command_columns = {
            column["name"] for column in db_inspector.get_columns("job_commands", schema="core")
        }
        assert {
            "command_type",
            "idempotency_key",
            "operation_fingerprint",
            "result",
            "occurred_at",
        }.issubset(command_columns)
        storage_columns = {
            column["name"] for column in db_inspector.get_columns("storage_objects", schema="core")
        }
        assert {
            "backend",
            "bucket",
            "object_key",
            "sha256",
            "mime_type",
            "size_bytes",
            "region",
            "etag",
            "version_id",
            "original_filename",
        }.issubset(storage_columns)
        approval_request_columns = {
            column["name"]
            for column in db_inspector.get_columns("approval_requests", schema="core")
        }
        assert {
            "request_fingerprint",
            "resolution_fingerprint",
            "resolved_job_revision",
            "resolved_job_status",
        }.issubset(approval_request_columns)
        provider_async_columns = {
            column["name"]
            for column in db_inspector.get_columns("provider_async_states", schema="core")
        }
        assert {
            "provider_generation_id",
            "next_poll_at",
            "deadline_at",
            "last_provider_event_at",
            "revision",
        }.issubset(provider_async_columns)
        callback_columns = {
            column["name"]
            for column in db_inspector.get_columns("provider_callback_events", schema="core")
        }
        assert "payload_sha256" in callback_columns
        assert "signature_scheme" in callback_columns
        assert "raw_payload" not in callback_columns
        assert "signature" not in callback_columns

        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            revision = result.scalar_one()
        assert revision == "20260829_0008"

        project_id = uuid4()
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.projects (
                        id, external_id, title, status, audience, "cast", content_format,
                        language, target_duration_seconds, output, creative, provider_policy,
                        created_at, updated_at
                    ) VALUES (
                        :id, 'PRJ-000901', 'Migration constraint fixture', 'draft',
                        '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                        '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, now(), now()
                    )
                    """
                ),
                {"id": project_id},
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.projects (
                        id, external_id, title, status, audience, "cast", content_format,
                        language, target_duration_seconds, output, creative, provider_policy,
                        created_at, updated_at
                    ) VALUES (
                        :id, 'PRJ-000901', 'Duplicate external id', 'draft',
                        '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                        '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, now(), now()
                    )
                    """
                ),
                {"id": uuid4()},
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.storage_objects (
                        id, external_id, project_id, backend, bucket, object_key,
                        sha256, mime_type, size_bytes, created_at, updated_at
                    ) VALUES (
                        :id, 'STO-000901', :project_id, 'filesystem', 'forbidden',
                        'source/PRJ-000901/STO-000901',
                        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                        'image/png', 1, now(), now()
                    )
                    """
                ),
                {"id": uuid4(), "project_id": project_id},
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.rights_records (
                        id, external_id, subject_type, subject_id,
                        commercial_use, publication_blocked
                    ) VALUES (
                        :id, 'RGT-000901', 'asset', 'AST-000901', 'unknown', false
                    )
                    """
                ),
                {"id": uuid4()},
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.contents (
                        id, external_id, status, created_at, updated_at
                    ) VALUES (
                        :id, 'CNT-000901', 'draft', now(), now()
                    )
                    """
                ),
                {"id": uuid4()},
            )

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.workflow_executions (
                        id, external_id, workflow_type, run_id, namespace, task_queue,
                        status, started_at, updated_at
                    ) VALUES (
                        :id, 'WFX-000901', 'SyntheticControlWorkflow', 'run-000901',
                        'default', 'aaf-control-v1', 'running', now(), now()
                    )
                    """
                ),
                {"id": uuid4()},
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO core.workflow_executions (
                        id, external_id, workflow_type, run_id, namespace, task_queue,
                        status, started_at, updated_at
                    ) VALUES (
                        :id, 'WFX-invalid', 'SyntheticControlWorkflow', 'run-000902',
                        'default', 'aaf-control-v1', 'running', now(), now()
                    )
                    """
                ),
                {"id": uuid4()},
            )

        command.upgrade(config, "head")
        assert set(inspect(engine).get_table_names(schema="core")) == EXPECTED_CORE_TABLES

        command.downgrade(config, "20260829_0007")
        m07_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_m03_tables = EXPECTED_CORE_TABLES - M03_WP1_TABLES
        assert m07_tables == pre_m03_tables

        command.downgrade(config, "20260829_0005")
        m05_tables = set(inspect(engine).get_table_names(schema="core"))
        m05_expected = pre_m03_tables - PROVIDER_ASYNC_TABLES - WP7_TABLES
        assert m05_tables == m05_expected
        assert "approval_requests" in m05_tables
        assert "circuit_breakers" in m05_tables

        command.downgrade(config, "20260829_0004")
        m04_tables = set(inspect(engine).get_table_names(schema="core"))
        m04_expected = m05_expected - {"approval_requests"}
        assert m04_tables == m04_expected
        assert "approval_requests" not in m04_tables
        assert "circuit_breakers" in m04_tables

        command.downgrade(config, "20260829_0003")
        m03_inspector = inspect(engine)
        m03_tables = set(m03_inspector.get_table_names(schema="core"))
        m03_expected = m04_expected - {"circuit_breakers"}
        assert m03_tables == m03_expected
        assert "circuit_breakers" not in m03_tables
        m03_job_columns = {
            column["name"] for column in m03_inspector.get_columns("jobs", schema="core")
        }
        assert "operation_fingerprint" in m03_job_columns
        assert "outbox_messages" in m03_tables
        assert "workflow_executions" in m03_tables

        command.downgrade(config, "20260829_0002")
        m02_inspector = inspect(engine)
        m02_tables = set(m02_inspector.get_table_names(schema="core"))
        m02_expected = m03_expected - {"outbox_messages"}
        assert m02_tables == m02_expected
        assert "outbox_messages" not in m02_tables
        m02_job_columns = {
            column["name"] for column in m02_inspector.get_columns("jobs", schema="core")
        }
        assert "operation_fingerprint" not in m02_job_columns
        assert "workflow_executions" in m02_tables

        command.downgrade(config, "20260829_0001")
        m01_tables = set(inspect(engine).get_table_names(schema="core"))
        m01_expected = m02_expected - {"workflow_executions"}
        assert m01_tables == m01_expected
        assert "workflow_executions" not in m01_tables

        command.upgrade(config, "head")
        assert set(inspect(engine).get_table_names(schema="core")) == EXPECTED_CORE_TABLES

        command.downgrade(config, "base")
        assert "core" not in inspect(engine).get_schema_names()

        command.upgrade(config, "head")
        assert set(inspect(engine).get_table_names(schema="core")) == EXPECTED_CORE_TABLES
    finally:
        command.downgrade(config, "base")
        engine.dispose()
