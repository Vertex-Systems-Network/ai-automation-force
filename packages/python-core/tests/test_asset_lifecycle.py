from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from lineage_fixtures import full_lineage_bundle
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ai_automation_force_core import (
    AssetLifecyclePersistenceConflictError,
    AssetLifecycleSnapshot,
    AssetLifecycleState,
    AssetLifecycleVersionConflictError,
    InvalidAssetLifecycleTransitionError,
    PostgresAssetLifecycleRepository,
    PostgresProductionRepository,
    plan_asset_lifecycle_transition,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.fixture
def migrated_engine() -> Iterator[Engine]:
    if DATABASE_URL is None:
        pytest.skip("DATABASE_URL is not configured")
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    try:
        yield engine
    finally:
        engine.dispose()
        command.downgrade(config, "base")


def test_lifecycle_contract_preserves_recovery_state_and_window() -> None:
    bundle = full_lineage_bundle()
    asset = bundle.assets[1]
    assert asset.project_id is not None
    now = asset.audit.created_at + timedelta(minutes=1)
    current = AssetLifecycleSnapshot(
        asset_id=asset.asset_id,
        project_id=asset.project_id,
        updated_at=asset.audit.created_at,
    )

    deletion = plan_asset_lifecycle_transition(
        current,
        AssetLifecycleState.DELETION_PENDING,
        occurred_at=now,
        recovery_until=now + timedelta(hours=1),
    )
    assert deletion.recovery_state is AssetLifecycleState.ACTIVE

    pending = current.model_copy(
        update={
            "state": AssetLifecycleState.DELETION_PENDING,
            "recovery_state": deletion.recovery_state,
            "recovery_until": deletion.recovery_until,
            "updated_at": now,
            "revision": 2,
        }
    )
    with pytest.raises(InvalidAssetLifecycleTransitionError, match="recovery window closes"):
        plan_asset_lifecycle_transition(
            pending,
            AssetLifecycleState.HARD_DELETE_SCHEDULED,
            occurred_at=now + timedelta(minutes=30),
        )
    recovered = plan_asset_lifecycle_transition(
        pending,
        AssetLifecycleState.ACTIVE,
        occurred_at=now + timedelta(minutes=45),
    )
    assert recovered.to_state is AssetLifecycleState.ACTIVE
    assert recovered.recovery_state is None


@pytest.mark.postgres
def test_lifecycle_repository_archive_restore_is_versioned_and_idempotent(
    migrated_engine: Engine,
) -> None:
    bundle = full_lineage_bundle()
    PostgresProductionRepository(migrated_engine).save_bundle(bundle)
    asset = bundle.assets[1]
    assert asset.project_id is not None
    base = asset.audit.created_at + timedelta(minutes=1)
    repository = PostgresAssetLifecycleRepository(migrated_engine)

    initial = repository.load(asset.asset_id)
    assert initial.state is AssetLifecycleState.ACTIVE
    assert initial.revision == 1

    requested = repository.transition(
        asset.asset_id,
        AssetLifecycleState.ARCHIVE_REQUESTED,
        operation_key="archive-request-0001",
        actor="wp7-test",
        occurred_at=base,
        expected_revision=1,
    )
    replay = repository.transition(
        asset.asset_id,
        AssetLifecycleState.ARCHIVE_REQUESTED,
        operation_key="archive-request-0001",
        actor="wp7-test",
        occurred_at=base,
        expected_revision=1,
    )
    assert requested.action == "transitioned"
    assert replay.action == "reused"
    assert replay.snapshot == requested.snapshot

    with pytest.raises(
        AssetLifecyclePersistenceConflictError,
        match="different mutation semantics",
    ):
        repository.transition(
            asset.asset_id,
            AssetLifecycleState.ACTIVE,
            operation_key="archive-request-0001",
            actor="wp7-test",
            occurred_at=base,
            expected_revision=2,
        )

    with pytest.raises(AssetLifecycleVersionConflictError, match="revision is 2"):
        repository.transition(
            asset.asset_id,
            AssetLifecycleState.ARCHIVING,
            operation_key="archive-start-0001",
            actor="wp7-worker",
            occurred_at=base + timedelta(minutes=1),
            expected_revision=1,
        )

    archiving = repository.transition(
        asset.asset_id,
        AssetLifecycleState.ARCHIVING,
        operation_key="archive-start-0002",
        actor="wp7-worker",
        occurred_at=base + timedelta(minutes=1),
        expected_revision=2,
    )
    archived = repository.transition(
        asset.asset_id,
        AssetLifecycleState.ARCHIVED,
        operation_key="archive-complete-0001",
        actor="wp7-worker",
        occurred_at=base + timedelta(minutes=2),
        expected_revision=archiving.snapshot.revision,
    )
    restore_requested = repository.transition(
        asset.asset_id,
        AssetLifecycleState.RESTORE_REQUESTED,
        operation_key="restore-request-0001",
        actor="wp7-test",
        occurred_at=base + timedelta(minutes=3),
        expected_revision=archived.snapshot.revision,
    )
    restoring = repository.transition(
        asset.asset_id,
        AssetLifecycleState.RESTORING,
        operation_key="restore-start-0001",
        actor="wp7-worker",
        occurred_at=base + timedelta(minutes=4),
        expected_revision=restore_requested.snapshot.revision,
    )
    active = repository.transition(
        asset.asset_id,
        AssetLifecycleState.ACTIVE,
        operation_key="restore-complete-0001",
        actor="wp7-worker",
        occurred_at=base + timedelta(minutes=5),
        expected_revision=restoring.snapshot.revision,
    )

    assert active.snapshot.state is AssetLifecycleState.ACTIVE
    assert active.snapshot.revision == 7
    history = repository.history(asset.asset_id)
    assert [event.to_state for event in history] == [
        AssetLifecycleState.ARCHIVE_REQUESTED,
        AssetLifecycleState.ARCHIVING,
        AssetLifecycleState.ARCHIVED,
        AssetLifecycleState.RESTORE_REQUESTED,
        AssetLifecycleState.RESTORING,
        AssetLifecycleState.ACTIVE,
    ]


@pytest.mark.postgres
def test_lifecycle_repository_soft_delete_recovery_and_hard_delete_schedule(
    migrated_engine: Engine,
) -> None:
    bundle = full_lineage_bundle()
    PostgresProductionRepository(migrated_engine).save_bundle(bundle)
    asset = bundle.assets[1]
    base = asset.audit.created_at + timedelta(minutes=1)
    repository = PostgresAssetLifecycleRepository(migrated_engine)

    pending = repository.transition(
        asset.asset_id,
        AssetLifecycleState.DELETION_PENDING,
        operation_key="delete-request-0001",
        actor="wp7-test",
        occurred_at=base,
        expected_revision=1,
        reason="user requested project cleanup",
        recovery_until=base + timedelta(hours=1),
    )
    assert pending.snapshot.recovery_state is AssetLifecycleState.ACTIVE

    with pytest.raises(
        InvalidAssetLifecycleTransitionError,
        match="recovery window closes",
    ):
        repository.transition(
            asset.asset_id,
            AssetLifecycleState.HARD_DELETE_SCHEDULED,
            operation_key="hard-delete-early-0001",
            actor="wp7-worker",
            occurred_at=base + timedelta(minutes=30),
            expected_revision=2,
        )

    recovered = repository.transition(
        asset.asset_id,
        AssetLifecycleState.ACTIVE,
        operation_key="delete-recover-0001",
        actor="wp7-test",
        occurred_at=base + timedelta(minutes=45),
        expected_revision=2,
    )
    assert recovered.snapshot.recovery_state is None

    pending_again = repository.transition(
        asset.asset_id,
        AssetLifecycleState.DELETION_PENDING,
        operation_key="delete-request-0002",
        actor="wp7-test",
        occurred_at=base + timedelta(hours=2),
        expected_revision=3,
        recovery_until=base + timedelta(hours=3),
    )
    scheduled = repository.transition(
        asset.asset_id,
        AssetLifecycleState.HARD_DELETE_SCHEDULED,
        operation_key="hard-delete-schedule-0001",
        actor="wp7-worker",
        occurred_at=base + timedelta(hours=3),
        expected_revision=pending_again.snapshot.revision,
    )
    deleted = repository.transition(
        asset.asset_id,
        AssetLifecycleState.DELETED,
        operation_key="hard-delete-complete-0001",
        actor="wp7-worker",
        occurred_at=base + timedelta(hours=3, minutes=1),
        expected_revision=scheduled.snapshot.revision,
    )

    assert deleted.snapshot.state is AssetLifecycleState.DELETED
    assert deleted.snapshot.revision == 6
    assert len(repository.history(asset.asset_id)) == 5
    with pytest.raises(InvalidAssetLifecycleTransitionError, match="cannot transition"):
        repository.transition(
            asset.asset_id,
            AssetLifecycleState.ACTIVE,
            operation_key="deleted-recover-0001",
            actor="wp7-test",
            occurred_at=base + timedelta(hours=4),
            expected_revision=6,
        )
