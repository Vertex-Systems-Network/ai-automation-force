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
    Asset,
    AssetKind,
    CanonicalStatus,
    DerivativeKind,
    DerivativePersistenceConflictError,
    DerivativeRecord,
    DerivativeSpec,
    DerivativeStatus,
    Job,
    JobStatus,
    PostgresDerivativeRepository,
    PostgresProductionRepository,
    PostgresStorageObjectRepository,
    ProductionLineageBundle,
    StorageBackend,
    StorageObject,
    derivative_operation_fingerprint,
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


def derivative_bundle() -> tuple[ProductionLineageBundle, Asset, Asset, Job]:
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
        update={
            "assets": [*bundle.assets, proxy],
            "jobs": [*bundle.jobs, job],
        }
    )
    validated = ProductionLineageBundle.model_validate(candidate.model_dump())
    return validated, source, proxy, job


def output_storage(
    proxy: Asset,
    storage_id: str = "STO-003020",
    sha256: str | None = None,
) -> StorageObject:
    assert proxy.project_id is not None
    return StorageObject(
        storage_object_id=storage_id,
        project_id=proxy.project_id,
        backend=StorageBackend.FILESYSTEM,
        object_key=f"derivatives/{proxy.project_id}/{storage_id}.mp4",
        sha256=sha256 or proxy.sha256,
        mime_type=proxy.mime_type,
        size_bytes=proxy.size_bytes,
        original_filename="shot-500-proxy.mp4",
        lifecycle_class="derivative",
        audit=proxy.audit.model_copy(deep=True),
    )


def proxy_spec() -> DerivativeSpec:
    return DerivativeSpec(
        kind=DerivativeKind.VIDEO_PROXY,
        width=960,
        height=540,
        mime_type="video/mp4",
        options={"video_codec": "h264", "profile": "proxy"},
    )


@pytest.mark.postgres
def test_derivative_persistence_is_idempotent_revisioned_and_lineage_safe(
    migrated_engine: Engine,
) -> None:
    bundle, source, proxy, job = derivative_bundle()
    PostgresProductionRepository(migrated_engine).save_bundle(bundle)
    storage = output_storage(proxy)
    PostgresStorageObjectRepository(migrated_engine).save(storage)

    spec = proxy_spec()
    created_at = source.audit.created_at + timedelta(seconds=1)
    fingerprint = derivative_operation_fingerprint(
        project_id=job.project_id,
        source_asset_id=source.asset_id,
        spec=spec,
    )
    record = DerivativeRecord(
        derivative_record_id="DRV-003020",
        project_id=job.project_id,
        source_asset_id=source.asset_id,
        job_id=job.job_id,
        spec=spec,
        operation_fingerprint=fingerprint,
        created_at=created_at,
        updated_at=created_at,
    )

    repository = PostgresDerivativeRepository(migrated_engine)
    first = repository.create(record)
    same_identity = repository.create(record)
    semantic_replay = repository.create(
        record.model_copy(update={"derivative_record_id": "DRV-003021"})
    )

    assert first.action == "created"
    assert same_identity.action == "reused"
    assert semantic_replay.action == "reused"
    assert semantic_replay.derivative_record_id == record.derivative_record_id
    assert semantic_replay.revision == 1

    running_at = created_at + timedelta(seconds=1)
    running = repository.transition(
        record.derivative_record_id,
        expected_revision=1,
        target_status=DerivativeStatus.RUNNING,
        updated_at=running_at,
    )
    assert running.action == "updated"
    assert running.status is DerivativeStatus.RUNNING
    assert running.revision == 2

    create_after_progress = repository.create(record)
    assert create_after_progress.action == "reused"
    assert create_after_progress.status is DerivativeStatus.RUNNING
    assert create_after_progress.revision == 2

    running_replay = repository.transition(
        record.derivative_record_id,
        expected_revision=1,
        target_status=DerivativeStatus.RUNNING,
        updated_at=running_at + timedelta(milliseconds=10),
    )
    assert running_replay.action == "noop"
    assert running_replay.revision == 2

    with pytest.raises(DerivativePersistenceConflictError, match="stale derivative revision"):
        repository.transition(
            record.derivative_record_id,
            expected_revision=1,
            target_status=DerivativeStatus.FAILED,
            updated_at=running_at + timedelta(seconds=1),
            error_code="stale-worker",
        )

    completed_at = running_at + timedelta(seconds=1)
    completed = repository.transition(
        record.derivative_record_id,
        expected_revision=2,
        target_status=DerivativeStatus.COMPLETED,
        updated_at=completed_at,
        completed_at=completed_at,
        output_asset_id=proxy.asset_id,
        output_storage_object_id=storage.storage_object_id,
    )
    assert completed.action == "updated"
    assert completed.status is DerivativeStatus.COMPLETED
    assert completed.revision == 3

    replay = repository.transition(
        record.derivative_record_id,
        expected_revision=2,
        target_status=DerivativeStatus.COMPLETED,
        updated_at=completed_at,
        completed_at=completed_at,
        output_asset_id=proxy.asset_id,
        output_storage_object_id=storage.storage_object_id,
    )
    assert replay.action == "noop"
    assert replay.revision == 3

    restored = repository.load(record.derivative_record_id)
    assert restored.status is DerivativeStatus.COMPLETED
    assert restored.output_asset_id == proxy.asset_id
    assert restored.output_storage_object_id == storage.storage_object_id
    assert restored.revision == 3


@pytest.mark.postgres
def test_derivative_completion_rejects_storage_hash_mismatch(
    migrated_engine: Engine,
) -> None:
    bundle, source, proxy, job = derivative_bundle()
    PostgresProductionRepository(migrated_engine).save_bundle(bundle)
    bad_storage = output_storage(proxy, storage_id="STO-003021", sha256="d" * 64)
    PostgresStorageObjectRepository(migrated_engine).save(bad_storage)

    spec = proxy_spec()
    created_at = source.audit.created_at + timedelta(seconds=1)
    record = DerivativeRecord(
        derivative_record_id="DRV-003030",
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
    repository = PostgresDerivativeRepository(migrated_engine)
    repository.create(record)
    running_at = created_at + timedelta(seconds=1)
    repository.transition(
        record.derivative_record_id,
        expected_revision=1,
        target_status=DerivativeStatus.RUNNING,
        updated_at=running_at,
    )

    completed_at = running_at + timedelta(seconds=1)
    with pytest.raises(
        DerivativePersistenceConflictError,
        match="storage hash does not match output asset",
    ):
        repository.transition(
            record.derivative_record_id,
            expected_revision=2,
            target_status=DerivativeStatus.COMPLETED,
            updated_at=completed_at,
            completed_at=completed_at,
            output_asset_id=proxy.asset_id,
            output_storage_object_id=bad_storage.storage_object_id,
        )
