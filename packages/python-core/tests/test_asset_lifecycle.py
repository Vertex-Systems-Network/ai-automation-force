from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from lineage_fixtures import full_lineage_bundle
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ai_automation_force_core import (
    Asset,
    AssetKind,
    AssetLifecyclePersistenceConflictError,
    AssetLifecycleSnapshot,
    AssetLifecycleState,
    AssetLifecycleVersionConflictError,
    AssetProvenanceRecord,
    AssetProvenanceSource,
    CanonicalStatus,
    DeletionPropagationTargetKind,
    DeliveryMode,
    DerivativeKind,
    DerivativeRecord,
    DerivativeSpec,
    DerivativeStatus,
    InvalidAssetLifecycleTransitionError,
    InvalidDeletionPropagationError,
    Job,
    JobStatus,
    PostgresAssetLifecycleRepository,
    PostgresAssetProvenanceRepository,
    PostgresDerivativeRepository,
    PostgresProductionRepository,
    PostgresShareLinkRepository,
    PostgresStorageObjectRepository,
    ProductionLineageBundle,
    ShareLinkConstraint,
    StorageBackend,
    StorageObject,
    derivative_operation_fingerprint,
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


def propagation_bundle() -> tuple[ProductionLineageBundle, Asset, Asset, Job]:
    bundle = full_lineage_bundle()
    source = bundle.assets[1]
    assert source.asset_id == "AST-000501"
    assert source.project_id is not None
    proxy = Asset(
        asset_id="AST-000502",
        project_id=source.project_id,
        kind=AssetKind.VIDEO,
        uri="s3://fixture/derivatives/shot-500-proxy.mp4",
        sha256="c" * 64,
        mime_type="video/mp4",
        size_bytes=2048,
        duration_seconds=8,
        width=960,
        height=540,
        parent_asset_ids=[source.asset_id],
        canonical_status=CanonicalStatus.CANDIDATE,
        retention_class="project",
        audit=source.audit.model_copy(deep=True),
    )
    job = Job(
        job_id="JOB-000501",
        project_id=source.project_id,
        job_type="video-proxy-derivative",
        status=JobStatus.RUNNING,
        idempotency_key="fixture-derivative-job-000501",
        retry_budget_remaining=2,
        audit=source.audit.model_copy(deep=True),
    )
    candidate = bundle.model_copy(
        update={"assets": [*bundle.assets, proxy], "jobs": [*bundle.jobs, job]}
    )
    return ProductionLineageBundle.model_validate(candidate.model_dump()), source, proxy, job


def storage_for(asset: Asset, storage_id: str, lifecycle_class: str) -> StorageObject:
    assert asset.project_id is not None
    return StorageObject(
        storage_object_id=storage_id,
        project_id=asset.project_id,
        backend=StorageBackend.FILESYSTEM,
        object_key=f"{lifecycle_class}/{asset.project_id}/{storage_id}",
        sha256=asset.sha256,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        original_filename=f"{storage_id}.bin",
        lifecycle_class=lifecycle_class,
        audit=asset.audit.model_copy(deep=True),
    )


def provenance_for(asset: Asset, record_id: str, storage_id: str) -> AssetProvenanceRecord:
    assert asset.project_id is not None
    return AssetProvenanceRecord(
        provenance_record_id=record_id,
        asset_id=asset.asset_id,
        project_id=asset.project_id,
        storage_object_id=storage_id,
        source_kind=AssetProvenanceSource.UPLOAD,
        source_reference=f"upload:{record_id}",
        content_sha256=asset.sha256,
        rights_record_id=asset.rights_record_id,
        created_at=asset.audit.created_at,
    )


def schedule_hard_delete(
    repository: PostgresAssetLifecycleRepository,
    asset_id: str,
    *,
    base: datetime,
    suffix: str,
) -> AssetLifecycleSnapshot:
    pending = repository.transition(
        asset_id,
        AssetLifecycleState.DELETION_PENDING,
        operation_key=f"delete-request-{suffix}",
        actor="wp7-test",
        occurred_at=base,
        expected_revision=1,
        recovery_until=base + timedelta(hours=1),
    )
    scheduled = repository.transition(
        asset_id,
        AssetLifecycleState.HARD_DELETE_SCHEDULED,
        operation_key=f"hard-delete-schedule-{suffix}",
        actor="wp7-worker",
        occurred_at=base + timedelta(hours=1),
        expected_revision=pending.snapshot.revision,
    )
    return scheduled.snapshot


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


@pytest.mark.postgres
def test_deletion_propagation_plan_is_bounded_shared_safe_and_deterministic(
    migrated_engine: Engine,
) -> None:
    bundle, source, proxy, job = propagation_bundle()
    sibling = bundle.assets[0]
    assert sibling.asset_id == "AST-000500"
    PostgresProductionRepository(migrated_engine).save_bundle(bundle)

    storage_repository = PostgresStorageObjectRepository(migrated_engine)
    provenance_repository = PostgresAssetProvenanceRepository(migrated_engine)
    source_storage = storage_for(source, "STO-003040", "canonical")
    shared_storage = storage_for(source, "STO-003041", "canonical")
    proxy_storage = storage_for(proxy, "STO-003042", "derivative")
    for storage in (source_storage, shared_storage, proxy_storage):
        storage_repository.save(storage)
    provenance_repository.save(provenance_for(source, "PRV-003040", "STO-003040"))
    provenance_repository.save(provenance_for(source, "PRV-003041", "STO-003041"))
    with migrated_engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO core.asset_provenance_records (
                    id, external_id, asset_id, project_id, storage_object_id,
                    source_kind, content_sha256, created_at
                ) VALUES (
                    gen_random_uuid(), 'PRV-003042',
                    (SELECT id FROM core.assets WHERE external_id = :sibling_id),
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    (SELECT id FROM core.storage_objects WHERE external_id = 'STO-003041'),
                    'upload', :digest, :created_at
                )
                """
            ),
            {
                "sibling_id": sibling.asset_id,
                "project_id": source.project_id,
                "digest": shared_storage.sha256,
                "created_at": source.audit.created_at,
            },
        )

    created_at = source.audit.created_at + timedelta(seconds=1)
    derivative_repository = PostgresDerivativeRepository(migrated_engine)
    completed_spec = DerivativeSpec(
        kind=DerivativeKind.VIDEO_PROXY,
        width=960,
        height=540,
        mime_type="video/mp4",
    )
    open_spec = DerivativeSpec(
        kind=DerivativeKind.VIDEO_POSTER,
        width=1280,
        height=720,
        mime_type="image/png",
    )
    for record_id, spec in (("DRV-003040", completed_spec), ("DRV-003041", open_spec)):
        derivative_repository.create(
            DerivativeRecord(
                derivative_record_id=record_id,
                project_id=job.project_id,
                source_asset_id=source.asset_id,
                job_id=job.job_id,
                spec=spec,
                operation_fingerprint=derivative_operation_fingerprint(
                    project_id=job.project_id,
                    source_asset_id=source.asset_id,
                    spec=spec,
                ),
                created_at=created_at,
                updated_at=created_at,
            )
        )
    running = derivative_repository.transition(
        "DRV-003040",
        expected_revision=1,
        target_status=DerivativeStatus.RUNNING,
        updated_at=created_at + timedelta(seconds=1),
    )
    derivative_repository.transition(
        "DRV-003040",
        expected_revision=running.revision,
        target_status=DerivativeStatus.COMPLETED,
        updated_at=created_at + timedelta(seconds=2),
        completed_at=created_at + timedelta(seconds=2),
        output_asset_id=proxy.asset_id,
        output_storage_object_id=proxy_storage.storage_object_id,
    )

    share_links = PostgresShareLinkRepository(migrated_engine)
    for share_link_id, digest in (("SHL-003040-active", "d"), ("SHL-003040-revoked", "e")):
        share_links.create(
            ShareLinkConstraint(
                share_link_id=share_link_id,
                project_id=job.project_id,
                asset_id=source.asset_id,
                token_sha256=digest * 64,
                allowed_modes=[DeliveryMode.STREAM],
                expires_at=created_at + timedelta(days=2),
            ),
            created_at=created_at,
        )
    share_links.revoke("SHL-003040-revoked", revoked_at=created_at + timedelta(seconds=3))

    lifecycle = PostgresAssetLifecycleRepository(migrated_engine)
    base = created_at + timedelta(minutes=1)
    with pytest.raises(InvalidDeletionPropagationError, match="hard-delete-scheduled"):
        lifecycle.plan_deletion_propagation(source.asset_id, planned_at=base)

    scheduled = schedule_hard_delete(lifecycle, source.asset_id, base=base, suffix="3040")
    with pytest.raises(InvalidDeletionPropagationError, match="before hard deletion"):
        lifecycle.plan_deletion_propagation(
            source.asset_id,
            planned_at=scheduled.updated_at - timedelta(seconds=1),
        )

    plan = lifecycle.plan_deletion_propagation(
        source.asset_id,
        planned_at=scheduled.updated_at,
    )
    assert plan.asset_id == source.asset_id
    assert plan.project_id == source.project_id
    assert plan.lifecycle_revision == scheduled.revision
    assert [(target.kind, target.storage_object_id) for target in plan.storage_targets] == [
        (DeletionPropagationTargetKind.SOURCE_STORAGE_OBJECT, "STO-003040")
    ]
    source_target = plan.storage_targets[0]
    assert source_target.backend is StorageBackend.FILESYSTEM
    assert source_target.bucket is None
    assert source_target.object_key == source_storage.object_key
    assert source_target.sha256 == source.sha256
    assert source_target.derivative_record_id is None
    assert [
        (item.storage_object_id, item.retained_for_asset_ids)
        for item in plan.retained_shared_storage
    ] == [("STO-003041", [sibling.asset_id])]
    assert plan.share_link_ids == ["SHL-003040-active"]
    assert plan.open_derivative_record_ids == ["DRV-003041"]
    assert plan.derived_asset_ids == [proxy.asset_id]

    replanned = lifecycle.plan_deletion_propagation(
        source.asset_id,
        planned_at=scheduled.updated_at + timedelta(minutes=5),
    )
    assert replanned.planned_at != plan.planned_at
    assert replanned.fingerprint() == plan.fingerprint()

    proxy_scheduled = schedule_hard_delete(
        lifecycle,
        proxy.asset_id,
        base=base + timedelta(hours=2),
        suffix="3042",
    )
    proxy_plan = lifecycle.plan_deletion_propagation(
        proxy.asset_id,
        planned_at=proxy_scheduled.updated_at,
    )
    assert [
        (target.kind, target.storage_object_id, target.derivative_record_id)
        for target in proxy_plan.storage_targets
    ] == [
        (
            DeletionPropagationTargetKind.DERIVATIVE_STORAGE_OBJECT,
            "STO-003042",
            "DRV-003040",
        )
    ]
    assert proxy_plan.retained_shared_storage == []
    assert proxy_plan.share_link_ids == []
    assert proxy_plan.open_derivative_record_ids == []
    assert proxy_plan.derived_asset_ids == []
    assert proxy_plan.fingerprint() != plan.fingerprint()
