from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from lineage_fixtures import full_lineage_bundle
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ai_automation_force_core import (
    AssetProvenanceRecord,
    AssetProvenanceSource,
    PersistenceConflictError,
    PersistenceReferenceError,
    PostgresAssetProvenanceRepository,
    PostgresProductionRepository,
    PostgresStorageObjectRepository,
    StorageBackend,
    StorageObject,
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


def generated_storage(bundle: object) -> StorageObject:
    typed_bundle = full_lineage_bundle() if bundle is None else bundle
    asset = typed_bundle.assets[1]  # type: ignore[attr-defined]
    assert asset.project_id is not None
    return StorageObject(
        storage_object_id="STO-003001",
        project_id=asset.project_id,
        backend=StorageBackend.FILESYSTEM,
        object_key=f"generated/{asset.project_id}/STO-003001",
        sha256=asset.sha256,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        original_filename="shot-500.mp4",
        lifecycle_class="canonical",
        audit=asset.audit.model_copy(deep=True),
    )


@pytest.mark.postgres
def test_asset_provenance_round_trip_is_append_only_and_integrity_safe(
    migrated_engine: Engine,
) -> None:
    bundle = full_lineage_bundle()
    production = PostgresProductionRepository(migrated_engine)
    production.save_bundle(bundle)

    asset = bundle.assets[1]
    assert asset.asset_id == "AST-000501"
    assert asset.project_id is not None
    assert asset.rights_record_id is not None

    storage = generated_storage(bundle)
    PostgresStorageObjectRepository(migrated_engine).save(storage)

    repository = PostgresAssetProvenanceRepository(migrated_engine)
    record = AssetProvenanceRecord(
        provenance_record_id="PRV-003001",
        asset_id=asset.asset_id,
        project_id=asset.project_id,
        storage_object_id=storage.storage_object_id,
        source_kind=AssetProvenanceSource.PROVIDER,
        source_reference="generation-attempt:ATT-000500",
        provider_reference="provider-generation:provider-job-500",
        content_sha256=asset.sha256,
        rights_record_id=asset.rights_record_id,
        created_at=asset.audit.created_at,
    )

    first = repository.save(record)
    restored = repository.load(record.provenance_record_id)
    second = repository.save(record)

    assert first.action == "created"
    assert second.action == "noop"
    assert restored == record

    conflicting_identity = record.model_copy(update={"provider_reference": "provider-generation:other"})
    with pytest.raises(PersistenceConflictError, match="already has different data"):
        repository.save(conflicting_identity)

    bad_hash = record.model_copy(
        update={
            "provenance_record_id": "PRV-003002",
            "content_sha256": "0" * 64,
        }
    )
    with pytest.raises(PersistenceConflictError, match="provenance hash"):
        repository.save(bad_hash)


@pytest.mark.postgres
def test_derived_provenance_requires_existing_canonical_parent(
    migrated_engine: Engine,
) -> None:
    bundle = full_lineage_bundle()
    PostgresProductionRepository(migrated_engine).save_bundle(bundle)
    repository = PostgresAssetProvenanceRepository(migrated_engine)

    generated = bundle.assets[1]
    assert generated.project_id is not None
    assert generated.rights_record_id is not None
    derived = AssetProvenanceRecord(
        provenance_record_id="PRV-003010",
        asset_id=generated.asset_id,
        project_id=generated.project_id,
        source_kind=AssetProvenanceSource.DERIVED,
        source_reference="asset-parent-graph",
        content_sha256=generated.sha256,
        rights_record_id=generated.rights_record_id,
        created_at=generated.audit.created_at,
    )
    assert repository.save(derived).action == "created"

    source = bundle.assets[0]
    assert source.project_id is not None
    parentless = AssetProvenanceRecord(
        provenance_record_id="PRV-003011",
        asset_id=source.asset_id,
        project_id=source.project_id,
        source_kind=AssetProvenanceSource.DERIVED,
        source_reference="invalid-parentless-derived-fixture",
        content_sha256=source.sha256,
        created_at=source.audit.created_at,
    )
    with pytest.raises(PersistenceReferenceError, match="existing parent"):
        repository.save(parentless)
