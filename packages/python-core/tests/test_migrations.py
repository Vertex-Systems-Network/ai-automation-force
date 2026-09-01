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
    "asset_provenance_records",
    "derivative_records",
    "delivery_share_links",
    "asset_delivery_policies",
    "storage_objects",
    "upload_sessions",
    "upload_parts",
    "upload_session_commands",
    "quarantine_inspections",
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
M03_WP2_TABLES = {"upload_sessions", "upload_parts", "upload_session_commands"}
M03_WP3_TABLES = {"quarantine_inspections"}
M03_WP4_TABLES = {"asset_provenance_records"}
M03_WP5_TABLES = {"derivative_records"}
M03_WP6_SHARE_TABLES = {"delivery_share_links"}
M03_WP6_POLICY_TABLES = {"asset_delivery_policies"}


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
        upload_session_columns = {
            column["name"]
            for column in db_inspector.get_columns("upload_sessions", schema="core")
        }
        assert {
            "external_id",
            "storage_object_external_id",
            "object_key",
            "expected_size_bytes",
            "expected_mime_type",
            "mode",
            "part_size_bytes",
            "backend_upload_id",
            "quota_reservation_id",
            "creation_idempotency_key",
            "expires_at",
            "status",
            "revision",
        }.issubset(upload_session_columns)
        upload_part_columns = {
            column["name"] for column in db_inspector.get_columns("upload_parts", schema="core")
        }
        assert {
            "upload_session_id",
            "part_number",
            "size_bytes",
            "etag",
            "checksum_sha256",
            "recorded_at",
        }.issubset(upload_part_columns)
        upload_command_columns = {
            column["name"]
            for column in db_inspector.get_columns("upload_session_commands", schema="core")
        }
        assert {
            "command_type",
            "idempotency_key",
            "request_fingerprint",
            "result_status",
            "result_revision",
            "occurred_at",
        }.issubset(upload_command_columns)
        quarantine_columns = {
            column["name"]
            for column in db_inspector.get_columns("quarantine_inspections", schema="core")
        }
        assert {
            "external_id",
            "upload_session_id",
            "project_id",
            "storage_object_external_id",
            "policy",
            "claimed_mime_type",
            "detected_mime_type",
            "expected_size_bytes",
            "observed_size_bytes",
            "status",
            "rejection_codes",
            "probe",
            "threat_scan",
            "inspected_at",
            "revision",
        }.issubset(quarantine_columns)
        derivative_columns = {
            column["name"]
            for column in db_inspector.get_columns("derivative_records", schema="core")
        }
        assert {
            "external_id",
            "project_id",
            "source_asset_id",
            "output_asset_id",
            "output_storage_object_id",
            "job_id",
            "derivative_kind",
            "spec_json",
            "operation_fingerprint",
            "status",
            "created_at",
            "updated_at",
            "completed_at",
            "error_code",
            "revision",
        }.issubset(derivative_columns)
        share_link_columns = {
            column["name"]
            for column in db_inspector.get_columns("delivery_share_links", schema="core")
        }
        assert {
            "external_id",
            "project_id",
            "asset_id",
            "token_sha256",
            "allow_download",
            "allow_stream",
            "expires_at",
            "revoked_at",
            "max_uses",
            "use_count",
            "created_at",
            "updated_at",
            "revision",
        }.issubset(share_link_columns)
        assert "token" not in share_link_columns
        assert "raw_token" not in share_link_columns
        delivery_policy_columns = {
            column["name"]
            for column in db_inspector.get_columns("asset_delivery_policies", schema="core")
        }
        assert {
            "asset_id",
            "project_id",
            "access_class",
            "created_at",
            "updated_at",
            "revision",
        }.issubset(delivery_policy_columns)
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
        assert revision == "20260901_0014"

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

        command.downgrade(config, "20260901_0013")
        m13_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_wp6_policy_tables = EXPECTED_CORE_TABLES - M03_WP6_POLICY_TABLES
        assert m13_tables == pre_wp6_policy_tables

        command.downgrade(config, "20260831_0012")
        m12_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_wp6_tables = pre_wp6_policy_tables - M03_WP6_SHARE_TABLES
        assert m12_tables == pre_wp6_tables

        command.downgrade(config, "20260830_0011")
        m11_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_wp5_tables = pre_wp6_tables - M03_WP5_TABLES
        assert m11_tables == pre_wp5_tables

        command.downgrade(config, "20260829_0010")
        m10_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_wp4_tables = pre_wp5_tables - M03_WP4_TABLES
        assert m10_tables == pre_wp4_tables

        command.downgrade(config, "20260829_0009")
        m09_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_wp3_tables = pre_wp4_tables - M03_WP3_TABLES
        assert m09_tables == pre_wp3_tables

        command.downgrade(config, "20260829_0008")
        m08_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_wp2_tables = pre_wp3_tables - M03_WP2_TABLES
        assert m08_tables == pre_wp2_tables

        command.downgrade(config, "20260829_0007")
        m07_tables = set(inspect(engine).get_table_names(schema="core"))
        pre_m03_tables = pre_wp2_tables - M03_WP1_TABLES
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
