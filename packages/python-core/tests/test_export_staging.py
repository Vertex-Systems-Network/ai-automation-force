from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from lullabies_core.common import AuditFields
from lullabies_core.export_staging import (
    EXPORT_STAGING_LIFECYCLE_CLASS,
    ExportStagingConflictError,
    prepare_export_staging,
)
from lullabies_core.persistence._db import PersistenceConflictError
from lullabies_core.persistence.export_staging import PostgresExportStagingRepository
from lullabies_core.persistence.storage_object import PostgresStorageObjectRepository
from lullabies_core.storage import (
    FilesystemStorageAdapter,
    StorageIntegrityError,
    StorageObject,
    build_object_key,
    storage_object_from_write,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def audit(at: datetime) -> AuditFields:
    return AuditFields(created_at=at, updated_at=at, created_by="export-staging-test")


def source_object(
    filesystem: FilesystemStorageAdapter,
    *,
    project_id: str = "PRJ-001601",
    storage_object_id: str = "STO-001601",
    data: bytes = b"canonical export source",
    at: datetime | None = None,
) -> StorageObject:
    created_at = at or datetime(2026, 9, 5, 9, 0, tzinfo=UTC)
    key = build_object_key("canonical/source", storage_object_id, project_id=project_id)
    write = filesystem.put_bytes(key, data, mime_type="video/mp4")
    return storage_object_from_write(
        storage_object_id,
        write,
        audit=audit(created_at),
        project_id=project_id,
        original_filename="source.mp4",
        lifecycle_class="canonical",
    )


def test_prepare_export_staging_copies_exact_bytes_to_private_deterministic_key(
    tmp_path: Path,
) -> None:
    filesystem = FilesystemStorageAdapter(tmp_path)
    created_at = datetime(2026, 9, 5, 9, 0, tzinfo=UTC)
    source = source_object(filesystem, at=created_at)

    prepared = prepare_export_staging(
        source=source,
        export_staging_id="EXS-001601",
        staging_storage_object_id="STO-001602",
        expires_at=created_at + timedelta(hours=4),
        audit=audit(created_at + timedelta(minutes=1)),
        storage=filesystem,
    )

    assert prepared.record.source_storage_object_id == source.storage_object_id
    assert prepared.record.source_sha256 == source.sha256
    assert prepared.record.staging_object_key == "exports/staging/PRJ-001601/STO-001602"
    assert prepared.storage_object.lifecycle_class == EXPORT_STAGING_LIFECYCLE_CLASS
    assert prepared.storage_object.sha256 == source.sha256
    assert filesystem.get_bytes(prepared.record.staging_object_key) == b"canonical export source"

    retried = prepare_export_staging(
        source=source,
        export_staging_id="EXS-001601",
        staging_storage_object_id="STO-001602",
        expires_at=created_at + timedelta(hours=4),
        audit=audit(created_at + timedelta(minutes=1)),
        storage=filesystem,
    )
    assert retried == prepared


def test_prepare_export_staging_fails_closed_when_source_bytes_drift(tmp_path: Path) -> None:
    filesystem = FilesystemStorageAdapter(tmp_path)
    source = source_object(filesystem)
    source_path = tmp_path / Path(*source.object_key.split("/"))
    source_path.write_bytes(b"tampered source")

    with pytest.raises(StorageIntegrityError, match="live SHA-256"):
        prepare_export_staging(
            source=source,
            export_staging_id="EXS-001603",
            staging_storage_object_id="STO-001603",
            expires_at=datetime(2026, 9, 5, 14, 0, tzinfo=UTC),
            audit=audit(datetime(2026, 9, 5, 10, 0, tzinfo=UTC)),
            storage=filesystem,
        )


def test_prepare_export_staging_rejects_projectless_source(tmp_path: Path) -> None:
    filesystem = FilesystemStorageAdapter(tmp_path)
    source = source_object(filesystem).model_copy(update={"project_id": None})

    with pytest.raises(ExportStagingConflictError, match="belong to a project"):
        prepare_export_staging(
            source=source,
            export_staging_id="EXS-001604",
            staging_storage_object_id="STO-001604",
            expires_at=datetime(2026, 9, 5, 14, 0, tzinfo=UTC),
            audit=audit(datetime(2026, 9, 5, 10, 0, tzinfo=UTC)),
            storage=filesystem,
        )


def _alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def _insert_project(engine: object, external_id: str) -> None:
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
            {"external_id": external_id, "title": f"Export fixture {external_id}"},
        )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_postgres_export_staging_persists_exact_provenance_and_reuse(tmp_path: Path) -> None:
    assert DATABASE_URL is not None
    config = _alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        project_id = "PRJ-001611"
        created_at = datetime(2026, 9, 5, 9, 0, tzinfo=UTC)
        _insert_project(engine, project_id)
        filesystem = FilesystemStorageAdapter(tmp_path)
        source = source_object(
            filesystem,
            project_id=project_id,
            storage_object_id="STO-001611",
            at=created_at,
        )
        PostgresStorageObjectRepository(engine).save(source)

        prepared = prepare_export_staging(
            source=source,
            export_staging_id="EXS-001611",
            staging_storage_object_id="STO-001612",
            expires_at=created_at + timedelta(hours=6),
            audit=audit(created_at + timedelta(minutes=1)),
            storage=filesystem,
        )
        repository = PostgresExportStagingRepository(engine)
        created = repository.save_prepared(prepared)
        assert created.action == "created"
        assert repository.load("EXS-001611") == prepared.record

        repeated = repository.save_prepared(prepared)
        assert repeated.action == "noop"

        conflicting = prepared.record.model_copy(
            update={"expires_at": prepared.record.expires_at + timedelta(hours=1)}
        )
        with pytest.raises(PersistenceConflictError, match="different data"):
            repository.save(conflicting)
    finally:
        command.downgrade(config, "base")
        engine.dispose()
