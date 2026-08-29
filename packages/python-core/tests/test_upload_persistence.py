from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from ai_automation_force_core import (
    AuditFields,
    PersistenceReferenceError,
    PostgresUploadSessionRepository,
    StorageBackend,
    UploadMode,
    UploadPart,
    UploadPersistenceConflictError,
    UploadSession,
    UploadSessionStatus,
    build_upload_object_key,
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
            {"external_id": external_id, "title": f"Upload fixture {external_id}"},
        )


def multipart_session(
    upload_session_id: str,
    project_id: str,
    storage_object_id: str,
    *,
    created_at: datetime,
    expires_at: datetime | None = None,
    idempotency_key: str | None = None,
) -> UploadSession:
    return UploadSession(
        upload_session_id=upload_session_id,
        project_id=project_id,
        storage_object_id=storage_object_id,
        backend=StorageBackend.S3,
        bucket="aaf-private",
        object_key=build_upload_object_key(project_id, storage_object_id),
        expected_size_bytes=10,
        expected_mime_type="video/mp4",
        original_filename="clip.mp4",
        mode=UploadMode.MULTIPART,
        part_size_bytes=5,
        quota_reservation_id=f"quota-{upload_session_id}",
        creation_idempotency_key=idempotency_key or f"create-{upload_session_id}",
        expires_at=expires_at or created_at + timedelta(hours=1),
        audit=AuditFields(
            created_at=created_at,
            updated_at=created_at,
            created_by="wp2-persistence-test",
        ),
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_multipart_upload_resumes_across_reload_and_terminal_complete_is_idempotent() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-003101")
        repository = PostgresUploadSessionRepository(engine)
        started = datetime(2026, 8, 29, 17, 0, tzinfo=UTC)
        session = multipart_session(
            "UPS-003101",
            "PRJ-003101",
            "STO-003101",
            created_at=started,
        )

        created = repository.create(session)
        assert created.action == "created"
        assert created.status is UploadSessionStatus.OPEN

        bound = repository.bind_backend_upload_id(
            session.upload_session_id,
            "backend-upload-003101",
            now=started + timedelta(seconds=1),
        )
        assert bound.action == "bound"

        # A retried create request after multipart initialization must still resolve to
        # the original session; backend UploadId is mutable transfer state, not creation semantics.
        retried_create = repository.create(session)
        assert retried_create.action == "reused"
        assert retried_create.upload_session_id == session.upload_session_id

        reloaded = repository.load(session.upload_session_id)
        assert reloaded.backend_upload_id == "backend-upload-003101"
        assert reloaded.parts == []

        first = UploadPart(
            part_number=1,
            size_bytes=5,
            etag='"etag-1"',
            checksum_sha256="a" * 64,
            recorded_at=started + timedelta(minutes=1),
        )
        first_result = repository.record_part(
            session.upload_session_id,
            first,
            now=started + timedelta(minutes=1),
        )
        assert first_result.action == "recorded"

        # Simulate process restart: reload durable state, then receive the same backend
        # part observation at a later local observation time. Semantic part identity is
        # number/size/ETag/checksum, not the observation timestamp.
        after_restart = repository.load(session.upload_session_id)
        assert [part.part_number for part in after_restart.parts] == [1]
        repeated_first = first.model_copy(
            update={"recorded_at": started + timedelta(minutes=2)}
        )
        replayed_part = repository.record_part(
            session.upload_session_id,
            repeated_first,
            now=started + timedelta(minutes=2),
        )
        assert replayed_part.action == "reused"

        second = UploadPart(
            part_number=2,
            size_bytes=5,
            etag='"etag-2"',
            checksum_sha256="b" * 64,
            recorded_at=started + timedelta(minutes=3),
        )
        assert (
            repository.record_part(
                session.upload_session_id,
                second,
                now=started + timedelta(minutes=3),
            ).action
            == "recorded"
        )

        completed_at = started + timedelta(minutes=4)
        completed = repository.complete(
            session.upload_session_id,
            idempotency_key="complete-003101",
            observed_size_bytes=10,
            observed_etag='"final-etag"',
            observed_version_id="version-1",
            completed_at=completed_at,
        )
        assert completed.action == "completed"
        assert completed.status is UploadSessionStatus.COMPLETED

        replayed_complete = repository.complete(
            session.upload_session_id,
            idempotency_key="complete-003101",
            observed_size_bytes=10,
            observed_etag='"final-etag"',
            observed_version_id="version-1",
            completed_at=completed_at,
        )
        assert replayed_complete.action == "reused"
        assert replayed_complete.revision == completed.revision

        with pytest.raises(
            UploadPersistenceConflictError,
            match="idempotency key is bound to different request semantics",
        ):
            repository.complete(
                session.upload_session_id,
                idempotency_key="complete-003101",
                observed_size_bytes=10,
                observed_etag='"changed-etag"',
                observed_version_id="version-1",
                completed_at=completed_at,
            )

        with pytest.raises(
            UploadPersistenceConflictError,
            match="completed upload cannot be aborted",
        ):
            repository.abort(
                session.upload_session_id,
                idempotency_key="abort-after-complete",
                aborted_at=completed_at + timedelta(seconds=1),
            )

        restored = repository.load(session.upload_session_id)
        assert restored.status is UploadSessionStatus.COMPLETED
        assert restored.observed_size_bytes == 10
        assert [part.part_number for part in restored.parts] == [1, 2]

        # WP2 completion is transfer completion only. Canonical Asset promotion belongs
        # to WP3/WP4 and therefore must not be an implicit side effect here.
        with engine.connect() as connection:
            asset_count = connection.execute(text("SELECT count(*) FROM core.assets")).scalar_one()
        assert asset_count == 0
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_upload_conflicts_abort_idempotency_and_expiry_fail_closed() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-003110")
        repository = PostgresUploadSessionRepository(engine)
        started = datetime(2026, 8, 29, 17, 10, tzinfo=UTC)
        session = multipart_session(
            "UPS-003110",
            "PRJ-003110",
            "STO-003110",
            created_at=started,
        )
        assert repository.create(session).action == "created"

        changed_creation = session.model_copy(
            update={"expected_mime_type": "video/webm"}
        )
        with pytest.raises(
            UploadPersistenceConflictError,
            match="creation idempotency key is bound to different semantics",
        ):
            repository.create(changed_creation)

        part = UploadPart(
            part_number=1,
            size_bytes=5,
            etag='"etag-1"',
            recorded_at=started + timedelta(seconds=5),
        )
        with pytest.raises(UploadPersistenceConflictError, match="durably bound"):
            repository.record_part(
                session.upload_session_id,
                part,
                now=started + timedelta(seconds=5),
            )

        assert (
            repository.bind_backend_upload_id(
                session.upload_session_id,
                "backend-upload-003110",
                now=started + timedelta(seconds=6),
            ).action
            == "bound"
        )
        assert (
            repository.bind_backend_upload_id(
                session.upload_session_id,
                "backend-upload-003110",
                now=started + timedelta(seconds=7),
            ).action
            == "reused"
        )
        with pytest.raises(UploadPersistenceConflictError, match="different backend UploadId"):
            repository.bind_backend_upload_id(
                session.upload_session_id,
                "backend-upload-conflict",
                now=started + timedelta(seconds=8),
            )

        aborted_at = started + timedelta(minutes=1)
        aborted = repository.abort(
            session.upload_session_id,
            idempotency_key="abort-003110",
            aborted_at=aborted_at,
        )
        assert aborted.action == "aborted"
        replayed_abort = repository.abort(
            session.upload_session_id,
            idempotency_key="abort-003110",
            aborted_at=aborted_at,
        )
        assert replayed_abort.action == "reused"
        with pytest.raises(
            UploadPersistenceConflictError,
            match="aborted upload cannot be completed",
        ):
            repository.complete(
                session.upload_session_id,
                idempotency_key="complete-aborted",
                observed_size_bytes=10,
                completed_at=aborted_at + timedelta(seconds=1),
            )

        expired = multipart_session(
            "UPS-003111",
            "PRJ-003110",
            "STO-003111",
            created_at=started,
            expires_at=started + timedelta(seconds=30),
            idempotency_key="create-003111",
        )
        assert repository.create(expired).action == "created"
        expiry_result = repository.bind_backend_upload_id(
            expired.upload_session_id,
            "backend-upload-expired",
            now=started + timedelta(seconds=31),
        )
        assert expiry_result.action == "expired"
        assert repository.load(expired.upload_session_id).status is UploadSessionStatus.EXPIRED

        complete_expired = repository.complete(
            expired.upload_session_id,
            idempotency_key="complete-expired",
            observed_size_bytes=10,
            completed_at=started + timedelta(seconds=32),
        )
        assert complete_expired.status is UploadSessionStatus.EXPIRED
        assert repository.load(expired.upload_session_id).status is UploadSessionStatus.EXPIRED
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_upload_persistence_rejects_unknown_schema_version() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-003120")
        repository = PostgresUploadSessionRepository(engine)
        started = datetime(2026, 8, 29, 17, 20, tzinfo=UTC)
        session = multipart_session(
            "UPS-003120",
            "PRJ-003120",
            "STO-003120",
            created_at=started,
        )
        repository.create(session)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE core.upload_sessions SET schema_version = 2 "
                    "WHERE external_id = 'UPS-003120'"
                )
            )
        with pytest.raises(
            PersistenceReferenceError,
            match="unsupported upload session schema version",
        ):
            repository.load(session.upload_session_id)
    finally:
        engine.dispose()
        command.downgrade(config, "base")
