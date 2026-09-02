from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from ai_automation_force_core import (
    AssetAccessClass,
    AssetLifecycleState,
    DeliveryResolutionError,
    PostgresAssetLifecycleRepository,
    PostgresDeliveryRepository,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"
NOW = datetime(2026, 9, 1, 21, 0, tzinfo=UTC)
DIGEST = "a" * 64


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def seed_deliverable(engine: object, *, suffix: str = "006401") -> tuple[str, str, str]:
    project_id = f"PRJ-{suffix}"
    asset_id = f"AST-{suffix}"
    storage_id = f"STO-{suffix}"
    rights_id = f"RGT-{suffix}"
    provenance_id = f"PRV-{suffix}"
    with engine.begin() as connection:  # type: ignore[attr-defined]
        connection.execute(
            text(
                """
                INSERT INTO core.projects (
                    id, external_id, title, status, audience, "cast", content_format,
                    language, target_duration_seconds, output, creative, provider_policy,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :project_id, 'Delivery fixture', 'draft',
                    '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                    '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, :now, :now
                )
                """
            ),
            {"project_id": project_id, "now": NOW},
        )
        connection.execute(
            text(
                """
                INSERT INTO core.rights_records (
                    id, external_id, subject_type, subject_id, commercial_use,
                    publication_blocked, verified_at
                ) VALUES (
                    gen_random_uuid(), :rights_id, 'asset', :asset_id,
                    'allowed', false, :now
                )
                """
            ),
            {"rights_id": rights_id, "asset_id": asset_id, "now": NOW},
        )
        connection.execute(
            text(
                """
                INSERT INTO core.assets (
                    id, external_id, project_id, kind, uri, sha256, mime_type,
                    size_bytes, rights_record_id, canonical_status,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :asset_id,
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    'image', :uri, :digest, 'image/png', 12,
                    (SELECT id FROM core.rights_records WHERE external_id = :rights_id),
                    'approved', :now, :now
                )
                """
            ),
            {
                "asset_id": asset_id,
                "project_id": project_id,
                "uri": f"s3://canonical-private/source/{project_id}/{storage_id}",
                "digest": DIGEST,
                "rights_id": rights_id,
                "now": NOW,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO core.storage_objects (
                    id, external_id, project_id, backend, bucket, object_key,
                    sha256, mime_type, size_bytes, region, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :storage_id,
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    's3', 'canonical-private', :object_key, :digest,
                    'image/png', 12, 'eu-central-1', :now, :now
                )
                """
            ),
            {
                "storage_id": storage_id,
                "project_id": project_id,
                "object_key": f"source/{project_id}/{storage_id}",
                "digest": DIGEST,
                "now": NOW,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO core.asset_provenance_records (
                    id, external_id, asset_id, project_id, storage_object_id,
                    source_kind, content_sha256, rights_record_id, created_at
                ) VALUES (
                    gen_random_uuid(), :provenance_id,
                    (SELECT id FROM core.assets WHERE external_id = :asset_id),
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    (SELECT id FROM core.storage_objects WHERE external_id = :storage_id),
                    'upload', :digest,
                    (SELECT id FROM core.rights_records WHERE external_id = :rights_id),
                    :provenance_at
                )
                """
            ),
            {
                "provenance_id": provenance_id,
                "asset_id": asset_id,
                "project_id": project_id,
                "storage_id": storage_id,
                "digest": DIGEST,
                "rights_id": rights_id,
                "provenance_at": NOW + timedelta(seconds=1),
            },
        )
    return project_id, asset_id, storage_id


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_delivery_resolution_defaults_private_and_public_requires_explicit_policy() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    try:
        project_id, asset_id, storage_id = seed_deliverable(engine)
        repository = PostgresDeliveryRepository(engine)

        resolved = repository.resolve(asset_id)
        assert resolved.access_class is AssetAccessClass.PRIVATE
        assert resolved.subject.project_id == project_id
        assert resolved.subject.storage_object_id == storage_id
        assert resolved.storage_object.bucket == "canonical-private"
        assert resolved.storage_object.region == "eu-central-1"

        public = repository.set_access_class(
            asset_id,
            AssetAccessClass.PUBLIC,
            now=NOW + timedelta(minutes=1),
        )
        assert public.action == "created"
        assert repository.resolve(asset_id).access_class is AssetAccessClass.PUBLIC

        replay = repository.set_access_class(
            asset_id,
            AssetAccessClass.PUBLIC,
            now=NOW + timedelta(minutes=2),
        )
        assert replay.action == "reused"
        assert replay.revision == 1

        private = repository.set_access_class(
            asset_id,
            AssetAccessClass.PRIVATE,
            now=NOW + timedelta(minutes=3),
        )
        assert private.action == "updated"
        assert private.revision == 2
        assert repository.resolve(asset_id).access_class is AssetAccessClass.PRIVATE
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_delivery_resolution_fails_closed_for_rights_or_provenance_ambiguity() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    try:
        project_id, asset_id, storage_id = seed_deliverable(engine, suffix="006410")
        repository = PostgresDeliveryRepository(engine)

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE core.rights_records
                    SET publication_blocked = true
                    WHERE external_id = 'RGT-006410'
                    """
                )
            )
        with pytest.raises(DeliveryResolutionError, match="publication-blocked"):
            repository.resolve(asset_id)

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE core.rights_records
                    SET publication_blocked = false
                    WHERE external_id = 'RGT-006410'
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO core.asset_provenance_records (
                        id, external_id, asset_id, project_id, storage_object_id,
                        source_kind, content_sha256, rights_record_id, created_at
                    ) VALUES (
                        gen_random_uuid(), 'PRV-006411',
                        (SELECT id FROM core.assets WHERE external_id = :asset_id),
                        (SELECT id FROM core.projects WHERE external_id = :project_id),
                        (SELECT id FROM core.storage_objects WHERE external_id = :storage_id),
                        'upload', :digest,
                        (SELECT id FROM core.rights_records WHERE external_id = 'RGT-006410'),
                        :created_at
                    )
                    """
                ),
                {
                    "asset_id": asset_id,
                    "project_id": project_id,
                    "storage_id": storage_id,
                    "digest": DIGEST,
                    "created_at": NOW + timedelta(seconds=2),
                },
            )
        with pytest.raises(DeliveryResolutionError, match="ambiguous"):
            repository.resolve(asset_id)
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_delivery_resolution_fails_closed_outside_deliverable_lifecycle_states() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    try:
        _, asset_id, _ = seed_deliverable(engine, suffix="006420")
        delivery = PostgresDeliveryRepository(engine)
        lifecycle = PostgresAssetLifecycleRepository(engine)

        assert delivery.resolve(asset_id).access_class is AssetAccessClass.PRIVATE

        requested = lifecycle.transition(
            asset_id,
            AssetLifecycleState.ARCHIVE_REQUESTED,
            operation_key="archive-request-6420",
            actor="wp7-test",
            occurred_at=NOW + timedelta(minutes=1),
            expected_revision=1,
        )
        assert delivery.resolve(asset_id).subject.asset_id == asset_id

        archiving = lifecycle.transition(
            asset_id,
            AssetLifecycleState.ARCHIVING,
            operation_key="archive-start-6420",
            actor="wp7-worker",
            occurred_at=NOW + timedelta(minutes=2),
            expected_revision=requested.snapshot.revision,
        )
        with pytest.raises(DeliveryResolutionError, match="lifecycle state archiving"):
            delivery.resolve(asset_id)
        with pytest.raises(DeliveryResolutionError, match="not deliverable"):
            delivery.set_access_class(
                asset_id,
                AssetAccessClass.PUBLIC,
                now=NOW + timedelta(minutes=3),
            )

        archived = lifecycle.transition(
            asset_id,
            AssetLifecycleState.ARCHIVED,
            operation_key="archive-complete-6420",
            actor="wp7-worker",
            occurred_at=NOW + timedelta(minutes=4),
            expected_revision=archiving.snapshot.revision,
        )
        with pytest.raises(DeliveryResolutionError, match="lifecycle state archived"):
            delivery.resolve(asset_id)

        restore_requested = lifecycle.transition(
            asset_id,
            AssetLifecycleState.RESTORE_REQUESTED,
            operation_key="restore-request-6420",
            actor="wp7-test",
            occurred_at=NOW + timedelta(minutes=5),
            expected_revision=archived.snapshot.revision,
        )
        restoring = lifecycle.transition(
            asset_id,
            AssetLifecycleState.RESTORING,
            operation_key="restore-start-6420",
            actor="wp7-worker",
            occurred_at=NOW + timedelta(minutes=6),
            expected_revision=restore_requested.snapshot.revision,
        )
        active = lifecycle.transition(
            asset_id,
            AssetLifecycleState.ACTIVE,
            operation_key="restore-complete-6420",
            actor="wp7-worker",
            occurred_at=NOW + timedelta(minutes=7),
            expected_revision=restoring.snapshot.revision,
        )
        public = delivery.set_access_class(
            asset_id,
            AssetAccessClass.PUBLIC,
            now=NOW + timedelta(minutes=8),
        )
        assert public.action == "created"
        assert delivery.resolve(asset_id).access_class is AssetAccessClass.PUBLIC

        pending = lifecycle.transition(
            asset_id,
            AssetLifecycleState.DELETION_PENDING,
            operation_key="delete-request-6420",
            actor="wp7-test",
            occurred_at=NOW + timedelta(minutes=9),
            expected_revision=active.snapshot.revision,
            recovery_until=NOW + timedelta(hours=1),
        )
        with pytest.raises(DeliveryResolutionError, match="lifecycle state deletion-pending"):
            delivery.resolve(asset_id)

        scheduled = lifecycle.transition(
            asset_id,
            AssetLifecycleState.HARD_DELETE_SCHEDULED,
            operation_key="hard-delete-schedule-6420",
            actor="wp7-worker",
            occurred_at=NOW + timedelta(hours=1),
            expected_revision=pending.snapshot.revision,
        )
        with pytest.raises(DeliveryResolutionError, match="hard-delete-scheduled"):
            delivery.resolve(asset_id)

        lifecycle.transition(
            asset_id,
            AssetLifecycleState.DELETED,
            operation_key="hard-delete-complete-6420",
            actor="wp7-worker",
            occurred_at=NOW + timedelta(hours=1, minutes=1),
            expected_revision=scheduled.snapshot.revision,
        )
        with pytest.raises(DeliveryResolutionError, match="lifecycle state deleted"):
            delivery.resolve(asset_id)
    finally:
        engine.dispose()
        command.downgrade(config, "base")
