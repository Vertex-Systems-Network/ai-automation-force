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
    MediaSecurityPolicy,
    PostgresQuarantineInspectionRepository,
    PostgresUploadSessionRepository,
    QuarantineInspection,
    QuarantinePersistenceConflictError,
    QuarantineRejectionCode,
    QuarantineStatus,
    StorageBackend,
    ThreatScanResult,
    ThreatScanStatus,
    UploadMode,
    UploadSession,
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
            {"external_id": external_id, "title": f"Quarantine fixture {external_id}"},
        )


def upload_session(
    upload_session_id: str,
    project_id: str,
    storage_object_id: str,
    *,
    now: datetime,
) -> UploadSession:
    return UploadSession(
        upload_session_id=upload_session_id,
        project_id=project_id,
        storage_object_id=storage_object_id,
        backend=StorageBackend.S3,
        bucket="aaf-private",
        object_key=build_upload_object_key(project_id, storage_object_id),
        expected_size_bytes=12,
        expected_mime_type="image/png",
        original_filename="fixture.png",
        mode=UploadMode.SINGLE,
        creation_idempotency_key=f"create-{upload_session_id}",
        expires_at=now + timedelta(hours=1),
        audit=AuditFields(created_at=now, updated_at=now, created_by="wp3-test"),
    )


def policy() -> MediaSecurityPolicy:
    return MediaSecurityPolicy(
        allowed_mime_types=("image/png",),
        max_size_bytes=1_000_000,
    )


def pending_inspection(
    inspection_id: str,
    session: UploadSession,
    *,
    now: datetime,
) -> QuarantineInspection:
    return QuarantineInspection(
        inspection_id=inspection_id,
        upload_session_id=session.upload_session_id,
        project_id=session.project_id,
        storage_object_id=session.storage_object_id,
        policy=policy(),
        claimed_mime_type=session.expected_mime_type,
        expected_size_bytes=session.expected_size_bytes,
        observed_size_bytes=0,
        status=QuarantineStatus.PENDING,
        audit=AuditFields(created_at=now, updated_at=now, created_by="wp3-test"),
    )


def accepted_inspection(
    base: QuarantineInspection,
    *,
    inspected_at: datetime,
) -> QuarantineInspection:
    return QuarantineInspection(
        **{
            **base.model_dump(mode="python"),
            "detected_mime_type": "image/png",
            "observed_size_bytes": 12,
            "status": QuarantineStatus.ACCEPTED,
            "threat_scan": ThreatScanResult(
                status=ThreatScanStatus.CLEAN,
                engine="fake-scanner",
            ),
            "inspected_at": inspected_at,
            "audit": AuditFields(
                created_at=base.audit.created_at,
                updated_at=inspected_at,
                created_by=base.audit.created_by,
                revision=base.audit.revision,
            ),
        }
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_completed_upload_can_be_inspected_and_terminal_acceptance_is_idempotent() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-003401")
        started = datetime(2026, 8, 29, 19, 0, tzinfo=UTC)
        session = upload_session(
            "UPS-003401",
            "PRJ-003401",
            "STO-003401",
            now=started,
        )
        uploads = PostgresUploadSessionRepository(engine)
        uploads.create(session)
        uploads.complete(
            session.upload_session_id,
            idempotency_key="complete-003401",
            observed_size_bytes=12,
            observed_etag="etag-003401",
            completed_at=started + timedelta(minutes=1),
        )

        repository = PostgresQuarantineInspectionRepository(engine)
        pending = pending_inspection("QIN-003401", session, now=started + timedelta(minutes=2))
        assert repository.create(pending).action == "created"
        assert repository.create(pending).action == "reused"
        assert repository.mark_inspecting(
            pending.inspection_id,
            now=started + timedelta(minutes=3),
        ).action == "inspecting"

        terminal = accepted_inspection(
            pending,
            inspected_at=started + timedelta(minutes=4),
        )
        accepted = repository.finalize(terminal)
        assert accepted.action == "accepted"
        assert accepted.status is QuarantineStatus.ACCEPTED

        replay = accepted_inspection(
            pending,
            inspected_at=started + timedelta(minutes=5),
        )
        replayed = repository.finalize(replay)
        assert replayed.action == "reused"
        assert replayed.revision == accepted.revision

        restored = repository.load(pending.inspection_id)
        assert restored.status is QuarantineStatus.ACCEPTED
        assert restored.detected_mime_type == "image/png"
        assert restored.threat_scan is not None
        assert restored.threat_scan.status is ThreatScanStatus.CLEAN

        with engine.connect() as connection:
            asset_count = connection.execute(text("SELECT count(*) FROM core.assets")).scalar_one()
        assert asset_count == 0
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_open_upload_cannot_enter_quarantine_and_rejected_decision_is_immutable() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        insert_project(engine, "PRJ-003410")
        started = datetime(2026, 8, 29, 19, 10, tzinfo=UTC)
        session = upload_session(
            "UPS-003410",
            "PRJ-003410",
            "STO-003410",
            now=started,
        )
        uploads = PostgresUploadSessionRepository(engine)
        uploads.create(session)
        repository = PostgresQuarantineInspectionRepository(engine)
        pending = pending_inspection("QIN-003410", session, now=started + timedelta(minutes=1))

        with pytest.raises(
            QuarantinePersistenceConflictError,
            match="requires a completed upload session",
        ):
            repository.create(pending)

        uploads.complete(
            session.upload_session_id,
            idempotency_key="complete-003410",
            observed_size_bytes=12,
            completed_at=started + timedelta(minutes=2),
        )
        repository.create(pending)
        repository.mark_inspecting(
            pending.inspection_id,
            now=started + timedelta(minutes=3),
        )

        rejected_at = started + timedelta(minutes=4)
        rejected = QuarantineInspection(
            **{
                **pending.model_dump(mode="python"),
                "detected_mime_type": None,
                "observed_size_bytes": 12,
                "status": QuarantineStatus.REJECTED,
                "rejection_codes": (
                    QuarantineRejectionCode.MAGIC_UNKNOWN,
                    QuarantineRejectionCode.THREAT_SCAN_UNAVAILABLE,
                ),
                "inspected_at": rejected_at,
                "audit": AuditFields(
                    created_at=pending.audit.created_at,
                    updated_at=rejected_at,
                    created_by=pending.audit.created_by,
                ),
            }
        )
        assert repository.finalize(rejected).action == "rejected"

        accepted = accepted_inspection(
            pending,
            inspected_at=started + timedelta(minutes=5),
        )
        with pytest.raises(
            QuarantinePersistenceConflictError,
            match="already terminal with different evidence",
        ):
            repository.finalize(accepted)
    finally:
        engine.dispose()
        command.downgrade(config, "base")
