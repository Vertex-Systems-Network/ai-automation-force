from __future__ import annotations

from datetime import UTC, datetime

import pytest
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
    TimeRange,
    Timeline,
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


def test_project_bundle_rejects_timeline_duration_mismatch() -> None:
    bundle = valid_bundle()
    data = bundle.model_dump()
    data["timeline"]["duration_seconds"] = 599
    with pytest.raises(ValidationError, match="timeline duration"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_missing_shot_reference() -> None:
    bundle = valid_bundle()
    data = bundle.model_dump()
    data["shots"] = data["shots"][:1]
    with pytest.raises(ValidationError, match="missing shots"):
        ProjectBundle.model_validate(data)


def test_project_bundle_rejects_duplicate_shot_order() -> None:
    bundle = valid_bundle()
    data = bundle.model_dump()
    data["shots"][1]["order"] = 1
    with pytest.raises(ValidationError, match="duplicate Shot order"):
        ProjectBundle.model_validate(data)
