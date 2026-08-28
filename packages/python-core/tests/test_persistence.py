from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from lineage_fixtures import full_lineage_bundle
from pydantic import ValidationError
from sqlalchemy import MetaData, create_engine, func, select
from sqlalchemy.engine import Engine

from lullabies_core import (
    Act,
    PersistenceConflictError,
    PersistenceError,
    PersistenceNotFoundError,
    PostgresProductionRepository,
    ProductionLineageBundle,
    Scene,
    Sequence,
    Shot,
    TimeRange,
    World,
    import_legacy_content_package,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"
FIXTURES = Path(__file__).parent / "fixtures"


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


def long_form_bundle() -> ProductionLineageBundle:
    data = full_lineage_bundle().model_dump()
    data["project_bundle"]["project"]["target_duration_seconds"] = 5400
    data["project_bundle"]["timeline"]["duration_seconds"] = 5400
    data["content_version"]["target_duration_seconds"] = 5400

    first_act = data["project_bundle"]["acts"][0]
    first_sequence = data["project_bundle"]["sequences"][0]
    first_scene = data["project_bundle"]["scenes"][0]
    first_act["target_duration_seconds"] = 2700
    first_sequence["target_duration_seconds"] = 2700
    first_scene["target_duration_seconds"] = 2700

    audit = first_act["audit"]
    second_act = Act(
        act_id="ACT-000501",
        project_id="PRJ-000500",
        order=2,
        title="Second half",
        sequence_ids=["SEQ-000501"],
        target_duration_seconds=2700,
        audit=audit,
    )
    second_sequence = Sequence(
        sequence_id="SEQ-000501",
        act_id=second_act.act_id,
        order=1,
        title="Long-form continuation",
        scene_ids=["SCN-000501"],
        target_duration_seconds=2700,
        audit=audit,
    )
    second_scene = Scene(
        scene_id="SCN-000501",
        sequence_id=second_sequence.sequence_id,
        order=1,
        title="Second-half scene",
        character_ids=["CHR-000500"],
        shot_ids=["SHT-000501"],
        target_duration_seconds=2700,
        audit=audit,
    )
    second_shot = Shot(
        shot_id="SHT-000501",
        scene_id=second_scene.scene_id,
        order=1,
        time_range=TimeRange(start_seconds=2700, duration_seconds=8),
        purpose="Prove long-form hierarchy ordering",
        action="Mira continues the story in the second half.",
        character_ids=["CHR-000500"],
        audit=audit,
    )

    data["project_bundle"]["timeline"]["act_ids"] = ["ACT-000500", "ACT-000501"]
    data["project_bundle"]["acts"].append(second_act.model_dump())
    data["project_bundle"]["sequences"].append(second_sequence.model_dump())
    data["project_bundle"]["scenes"].append(second_scene.model_dump())
    data["project_bundle"]["shots"].append(second_shot.model_dump())
    return ProductionLineageBundle.model_validate(data)


def assert_same_bundle(
    expected: ProductionLineageBundle,
    actual: ProductionLineageBundle,
) -> None:
    assert actual.model_dump(mode="python") == expected.model_dump(mode="python")


@pytest.mark.postgres
def test_two_minute_production_bundle_round_trips_and_retry_is_noop(
    migrated_engine: Engine,
) -> None:
    repository = PostgresProductionRepository(migrated_engine)
    bundle = full_lineage_bundle()

    first = repository.save_bundle(bundle)
    restored = repository.load_bundle(bundle.project_bundle.project.project_id)
    second = repository.save_bundle(bundle)

    assert first.action == "created"
    assert second.action == "noop"
    assert_same_bundle(bundle, restored)
    assert restored.attempts[0].paid_cost == bundle.attempts[0].paid_cost
    assert restored.cost_records[0].paid_cost == bundle.cost_records[0].paid_cost
    assert restored.cost_records[0].free_credits_used == bundle.cost_records[0].free_credits_used
    assert restored.project_bundle.shots[0].selected_take_id == "TAK-000500"
    character = restored.project_bundle.characters[0]
    assert character.active_version_id == "CHV-000501"
    assert character.lock.pinned_character_version_id == "CHV-000500"
    assert restored.rights_records[0].publication_blocked is True


@pytest.mark.postgres
def test_ninety_minute_project_preserves_hierarchy_order(
    migrated_engine: Engine,
) -> None:
    repository = PostgresProductionRepository(migrated_engine)
    bundle = long_form_bundle()

    repository.save_bundle(bundle)
    restored = repository.load_bundle(bundle.project_bundle.project.project_id)

    assert_same_bundle(bundle, restored)
    assert restored.project_bundle.project.target_duration_seconds == 5400
    assert restored.project_bundle.timeline.duration_seconds == 5400
    assert restored.project_bundle.timeline.act_ids == ["ACT-000500", "ACT-000501"]
    assert [item.order for item in restored.project_bundle.acts] == [1, 2]
    assert restored.project_bundle.acts[1].sequence_ids == ["SEQ-000501"]
    assert restored.project_bundle.sequences[1].scene_ids == ["SCN-000501"]
    assert restored.project_bundle.scenes[1].shot_ids == ["SHT-000501"]


@pytest.mark.postgres
def test_changed_retry_conflicts_without_overwriting_canonical_project(
    migrated_engine: Engine,
) -> None:
    repository = PostgresProductionRepository(migrated_engine)
    bundle = full_lineage_bundle()
    repository.save_bundle(bundle)

    changed = bundle.model_copy(deep=True)
    changed.project_bundle.project.title = "Changed after canonical insert"

    with pytest.raises(PersistenceConflictError, match="different canonical data"):
        repository.save_bundle(changed)

    restored = repository.load_bundle(bundle.project_bundle.project.project_id)
    assert restored.project_bundle.project.title == bundle.project_bundle.project.title


@pytest.mark.postgres
def test_failed_reference_rolls_back_whole_aggregate(migrated_engine: Engine) -> None:
    repository = PostgresProductionRepository(migrated_engine)
    bundle = full_lineage_bundle().model_copy(deep=True)
    bundle.project_bundle.project.world_ids = ["WRL-000900"]
    bundle.project_bundle.worlds = [
        World(
            world_id="WRL-000900",
            name="Rollback world",
            style_profile_id="STY-999999",
            audit=bundle.project_bundle.project.audit.model_copy(deep=True),
        )
    ]
    bundle = ProductionLineageBundle.model_validate(bundle.model_dump())

    with pytest.raises(PersistenceError):
        repository.save_bundle(bundle)

    with pytest.raises(PersistenceNotFoundError):
        repository.load_bundle(bundle.project_bundle.project.project_id)


@pytest.mark.postgres
def test_legacy_import_create_then_noop_without_duplicate_rows(
    migrated_engine: Engine,
) -> None:
    repository = PostgresProductionRepository(migrated_engine)
    payload_path = FIXTURES / "legacy-content-package-v1.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    content_text = (FIXTURES / "legacy-content-v1.md").read_text(encoding="utf-8")
    imported = import_legacy_content_package(payload, content_text)
    imported_at = imported.content.audit.updated_at

    first = repository.import_legacy_content(imported, imported_at=imported_at)
    second = repository.import_legacy_content(imported, imported_at=imported_at)

    assert first.action == "create"
    assert second.action == "noop"

    metadata = MetaData()
    metadata.reflect(bind=migrated_engine, schema="core")
    with migrated_engine.connect() as connection:
        content_count = connection.execute(
            select(func.count()).select_from(metadata.tables["core.contents"])
        ).scalar_one()
        version_count = connection.execute(
            select(func.count()).select_from(metadata.tables["core.content_versions"])
        ).scalar_one()
        ledger_count = connection.execute(
            select(func.count()).select_from(metadata.tables["core.legacy_content_imports"])
        ).scalar_one()

    assert content_count == 1
    assert version_count == 1
    assert ledger_count == 1


def test_long_form_fixture_is_valid_domain_data() -> None:
    try:
        bundle = long_form_bundle()
    except ValidationError as exc:  # pragma: no cover - diagnostic assertion
        pytest.fail(str(exc))
    assert bundle.project_bundle.timeline.duration_seconds == 5400
