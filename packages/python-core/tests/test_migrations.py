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
    "jobs",
    "job_dependencies",
    "generation_attempts",
    "generation_attempt_input_assets",
    "generation_attempt_qa_records",
    "qa_records",
    "take_qa_records",
    "cost_records",
    "approvals",
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
}


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_initial_postgresql_migration_is_reversible_and_deterministic() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    engine = create_engine(DATABASE_URL)

    try:
        command.upgrade(config, "head")

        db_inspector = inspect(engine)
        assert "core" in db_inspector.get_schema_names()
        assert set(db_inspector.get_table_names(schema="core")) == EXPECTED_CORE_TABLES

        with engine.connect() as connection:
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert revision == "20260829_0001"

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

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
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

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
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

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
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

        # Applying head twice must be a no-op rather than replaying schema DDL.
        command.upgrade(config, "head")
        assert set(inspect(engine).get_table_names(schema="core")) == EXPECTED_CORE_TABLES

        command.downgrade(config, "base")
        assert "core" not in inspect(engine).get_schema_names()

        # A clean re-upgrade after rollback proves the initial migration is repeatable.
        command.upgrade(config, "head")
        assert set(inspect(engine).get_table_names(schema="core")) == EXPECTED_CORE_TABLES
    finally:
        command.downgrade(config, "base")
        engine.dispose()
