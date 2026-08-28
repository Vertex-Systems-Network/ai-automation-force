from __future__ import annotations

from datetime import UTC, datetime

import pytest
from lineage_fixtures import full_lineage_bundle
from pydantic import ValidationError

from lullabies_core import (
    Act,
    AudienceKind,
    AudienceProfile,
    CastProfile,
    ContentFormat,
    Project,
    ProjectBundle,
    Scene,
    Sequence,
    Shot,
    Timeline,
    TimeRange,
)
from lullabies_core.common import AuditFields


def audit() -> AuditFields:
    now = datetime.now(UTC)
    return AuditFields(created_at=now, updated_at=now)


def valid_bundle() -> ProjectBundle:
    project = Project(
        project_id="PRJ-000100",
        title="Aggregate fixture",
        audience=AudienceProfile(kind=AudienceKind.GENERAL),
        cast=CastProfile(),
        content_format=ContentFormat.MOVIE,
        language="en",
        target_duration_seconds=600,
        audit=audit(),
    )
    timeline = Timeline(
        timeline_id="TML-000100",
        project_id=project.project_id,
        duration_seconds=600,
        act_ids=["ACT-000100"],
        audit=audit(),
    )
    act = Act(
        act_id="ACT-000100",
        project_id=project.project_id,
        order=1,
        title="Act 1",
        sequence_ids=["SEQ-000100"],
        target_duration_seconds=600,
        audit=audit(),
    )
    sequence = Sequence(
        sequence_id="SEQ-000100",
        act_id=act.act_id,
        order=1,
        title="Sequence 1",
        scene_ids=["SCN-000100"],
        target_duration_seconds=600,
        audit=audit(),
    )
    scene = Scene(
        scene_id="SCN-000100",
        sequence_id=sequence.sequence_id,
        order=1,
        title="Scene 1",
        shot_ids=["SHT-000100", "SHT-000101"],
        target_duration_seconds=600,
        audit=audit(),
    )
    shots = [
        Shot(
            shot_id="SHT-000100",
            scene_id=scene.scene_id,
            order=1,
            time_range=TimeRange(start_seconds=0, duration_seconds=6),
            audit=audit(),
        ),
        Shot(
            shot_id="SHT-000101",
            scene_id=scene.scene_id,
            order=2,
            time_range=TimeRange(start_seconds=6, duration_seconds=6),
            audit=audit(),
        ),
    ]
    return ProjectBundle(
        project=project,
        timeline=timeline,
        acts=[act],
        sequences=[sequence],
        scenes=[scene],
        shots=shots,
    )


def test_project_bundle_validates_cross_entity_graph() -> None:
    bundle = valid_bundle()
    assert bundle.project.project_id == bundle.timeline.project_id
    assert len(bundle.shots) == 2


def test_two_minute_lineage_project_remains_valid() -> None:
    project_bundle = full_lineage_bundle().project_bundle
    assert project_bundle.project.target_duration_seconds == 120
    assert ProjectBundle.model_validate(project_bundle.model_dump()) == project_bundle


def test_ninety_minute_project_remains_valid() -> None:
    data = valid_bundle().model_dump()
    data["project"]["target_duration_seconds"] = 5400
    data["timeline"]["duration_seconds"] = 5400
    data["acts"][0]["target_duration_seconds"] = 5400
    data["sequences"][0]["target_duration_seconds"] = 5400
    data["scenes"][0]["target_duration_seconds"] = 5400

    bundle = ProjectBundle.model_validate(data)
    assert bundle.timeline.duration_seconds == 5400


def test_project_bundle_rejects_timeline_duration_mismatch() -> None:
    bundle = valid_bundle()
    data = bundle.model_dump()
    data["timeline"]["duration_seconds"] = 599
    with pytest.raises(ValidationError, match="timeline duration"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_wrong_active_timeline() -> None:
    data = full_lineage_bundle().project_bundle.model_dump()
    data["project"]["active_timeline_id"] = "TML-999999"

    with pytest.raises(ValidationError, match="active_timeline_id"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_missing_shot_reference() -> None:
    bundle = valid_bundle()
    data = bundle.model_dump()
    data["shots"] = data["shots"][:1]
    with pytest.raises(ValidationError, match="missing shots"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_orphan_shot_parent() -> None:
    data = valid_bundle().model_dump()
    data["scenes"][0]["shot_ids"] = ["SHT-000100"]
    data["shots"][1]["scene_id"] = "SCN-999999"

    with pytest.raises(ValidationError, match="missing parent scene"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_duplicate_shot_order() -> None:
    bundle = valid_bundle()
    data = bundle.model_dump()
    data["shots"][1]["order"] = 1
    with pytest.raises(ValidationError, match="duplicate Shot order"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_duplicate_membership_reference() -> None:
    data = valid_bundle().model_dump()
    data["timeline"]["act_ids"].append("ACT-000100")

    with pytest.raises(ValidationError, match="duplicate references in timeline.act_ids"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_duplicate_track_id() -> None:
    data = valid_bundle().model_dump()
    data["timeline"]["tracks"] = [
        {"track_id": "TRK-000100", "kind": "video", "name": "Primary"},
        {"track_id": "TRK-000100", "kind": "audio", "name": "Music"},
    ]

    with pytest.raises(ValidationError, match="duplicate TimelineTrack IDs"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_primary_edit_overlap() -> None:
    data = valid_bundle().model_dump()
    data["shots"][1]["time_range"]["start_seconds"] = 5

    with pytest.raises(ValidationError, match="primary edit shots overlap"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_cross_scene_time_reversal() -> None:
    data = valid_bundle().model_dump()
    scene_two = dict(data["scenes"][0])
    scene_two["scene_id"] = "SCN-000101"
    scene_two["order"] = 2
    scene_two["title"] = "Scene 2"
    scene_two["shot_ids"] = ["SHT-000101"]
    data["scenes"][0]["shot_ids"] = ["SHT-000100"]
    data["scenes"].append(scene_two)
    data["sequences"][0]["scene_ids"] = ["SCN-000100", "SCN-000101"]
    data["shots"][1]["scene_id"] = "SCN-000101"
    data["shots"][0]["time_range"]["start_seconds"] = 6
    data["shots"][1]["time_range"]["start_seconds"] = 0

    with pytest.raises(ValidationError, match="moves backwards across hierarchy"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_character_used_but_not_declared_by_project() -> None:
    data = full_lineage_bundle().project_bundle.model_dump()
    data["project"]["character_ids"] = []

    with pytest.raises(ValidationError, match="uses undeclared characters"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_character_used_but_not_declared_by_scene() -> None:
    data = full_lineage_bundle().project_bundle.model_dump()
    data["scenes"][0]["character_ids"] = []

    with pytest.raises(ValidationError, match="not declared by scene"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_duplicate_character_version_number() -> None:
    data = full_lineage_bundle().project_bundle.model_dump()
    data["character_versions"][1]["version"] = 1

    with pytest.raises(ValidationError, match="duplicate version number"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_invalid_pinned_look() -> None:
    data = full_lineage_bundle().project_bundle.model_dump()
    data["characters"][0]["lock"] = {
        "scope": "look",
        "pinned_character_version_id": "CHV-000500",
        "pinned_look_id": "LOOK-999999",
        "project_id": None,
        "scene_id": None,
    }

    with pytest.raises(ValidationError, match="lock look is not in pinned version"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_scene_lock_where_character_is_absent() -> None:
    data = full_lineage_bundle().project_bundle.model_dump()
    data["characters"][0]["lock"] = {
        "scope": "scene",
        "pinned_character_version_id": "CHV-000500",
        "pinned_look_id": None,
        "project_id": None,
        "scene_id": "SCN-000500",
    }
    data["scenes"][0]["character_ids"] = []
    data["shots"][0]["character_ids"] = []

    with pytest.raises(ValidationError, match="character is not declared"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_used_location_from_undeclared_world() -> None:
    data = valid_bundle().model_dump()
    data["worlds"] = [
        {
            "world_id": "WRL-000100",
            "name": "Fixture world",
            "audit": audit().model_dump(),
        }
    ]
    data["locations"] = [
        {
            "location_id": "LOC-000100",
            "world_id": "WRL-000100",
            "name": "Fixture location",
            "audit": audit().model_dump(),
        }
    ]
    data["scenes"][0]["location_id"] = "LOC-000100"

    with pytest.raises(ValidationError, match="undeclared world"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_shot_location_different_from_scene() -> None:
    data = valid_bundle().model_dump()
    data["locations"] = [
        {"location_id": "LOC-000100", "name": "A", "audit": audit().model_dump()},
        {"location_id": "LOC-000101", "name": "B", "audit": audit().model_dump()},
    ]
    data["scenes"][0]["location_id"] = "LOC-000100"
    data["shots"][0]["location_id"] = "LOC-000101"

    with pytest.raises(ValidationError, match="differs from its continuous scene location"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_used_prop_not_declared_by_project() -> None:
    data = valid_bundle().model_dump()
    data["props"] = [
        {"prop_id": "PRP-000100", "name": "Star wand", "audit": audit().model_dump()}
    ]
    data["shots"][0]["prop_ids"] = ["PRP-000100"]

    with pytest.raises(ValidationError, match="uses undeclared props"):
        ProjectBundle.model_validate(data)
