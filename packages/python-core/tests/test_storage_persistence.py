from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from ai_automation_force_core import (
    AuditFields,
    PersistenceConflictError,
    PersistenceNotFoundError,
    PersistenceReferenceError,
    PostgresStorageObjectRepository,
    StorageBackend,
    StorageObject,
    sha256_bytes,
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
            {"external_id": external_id, "title": f"Storage fixture {external_id}"},
        )


def filesystem_object(
    storage_object_id: str,
    project_id: str,
    *,
    object_key: str,
    data: bytes = b"storage fixture",
) -> StorageObject:
    now = datetime.now(UTC)
    return StorageObject(
        storage_object_id=storage_object_id,
        project_id=project_id,
        backend=StorageBackend.FILESYSTEM,
        object_key=object_key,
        sha256=sha256_bytes(data),
        mime_type="application/octet-stream",
        size_bytes=len(data),
        original_filename="fixture.bin",
        audit=AuditFields(created_at=now, updated_at=now, created_by="wp1-test"),
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_storage_object_repository_round_trip_is_idempotent_and_reference_safe() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-002001")
        repository = PostgresStorageObjectRepository(engine)
        storage_object = filesystem_object(
            "STO-002001",
            "PRJ-002001",
            object_key="source/PRJ-002001/STO-002001",
        )

        created = repository.save(storage_object)
        assert created.action == "created"
        assert repository.load(storage_object.storage_object_id) == storage_object

        reused = repository.save(storage_object)
        assert reused.action == "noop"

        changed = storage_object.model_copy(update={"mime_type": "image/png"})
        with pytest.raises(PersistenceConflictError, match="different data"):
            repository.save(changed)

        with pytest.raises(PersistenceNotFoundError):
            repository.load("STO-009999")

        missing_project = filesystem_object(
            "STO-002002",
            "PRJ-009999",
            object_key="source/PRJ-009999/STO-002002",
        )
        with pytest.raises(PersistenceReferenceError, match="missing project"):
            repository.save(missing_project)
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_storage_physical_location_is_unique_across_stable_object_ids() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-002010")
        repository = PostgresStorageObjectRepository(engine)
        key = "source/PRJ-002010/STO-physical-location"
        first = filesystem_object("STO-002010", "PRJ-002010", object_key=key)
        second = filesystem_object("STO-002011", "PRJ-002010", object_key=key)

        assert repository.save(first).action == "created"
        with pytest.raises(PersistenceConflictError, match="database rejected"):
            repository.save(second)
    finally:
        engine.dispose()
        command.downgrade(config, "base")
