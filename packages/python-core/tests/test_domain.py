from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from lullabies_core import (
    Act,
    AudienceKind,
    AudienceProfile,
    CastAge,
    CastGender,
    CastProfile,
    CharacterLock,
    ContentFormat,
    CreativeProfile,
    LockScope,
    OutputProfile,
    Project,
    ProviderPolicyRef,
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


def make_project(project_id: str, duration: int, content_format: ContentFormat) -> Project:
    return Project(
        project_id=project_id,
        title="Contract fixture",
        audience=AudienceProfile(
            kind=AudienceKind.PRESCHOOL if duration <= 600 else AudienceKind.GENERAL,
            child_directed=duration <= 600,
            policy_profile="kids" if duration <= 600 else "general",
        ),
        cast=CastProfile(
            ages=[CastAge.CHILD] if duration <= 600 else [CastAge.ADULT, CastAge.MIXED],
            genders=[CastGender.MIXED],
            ai_may_decide=False,
        ),
        content_format=content_format,
        language="en",
        target_duration_seconds=duration,
        output=OutputProfile(aspect_ratio="16:9", fps=24, target_resolution_label="1080p"),
        creative=CreativeProfile(
            treatment=["cinematic"] if duration > 600 else ["3d-animation"],
            pacing_profile="cinematic-dynamic" if duration > 600 else "music-synced",
        ),
        provider_policy=ProviderPolicyRef(execution_mode="HYBRID_SMART"),
        audit=audit(),
    )


def test_two_minute_song_contract_validates() -> None:
    project = make_project("PRJ-000001", 120, ContentFormat.SONG)
    timeline = Timeline(
        timeline_id="TML-000001",
        project_id=project.project_id,
        duration_seconds=120,
        fps=24,
        act_ids=["ACT-000001"],
        audit=audit(),
    )
    act = Act(
        act_id="ACT-000001",
        project_id=project.project_id,
        order=1,
        title="Song",
        sequence_ids=["SEQ-000001"],
        target_duration_seconds=120,
        audit=audit(),
    )
    sequence = Sequence(
        sequence_id="SEQ-000001",
        act_id=act.act_id,
        order=1,
        title="Main sequence",
        scene_ids=["SCN-000001"],
        target_duration_seconds=120,
        audit=audit(),
    )
    scene = Scene(
        scene_id="SCN-000001",
        sequence_id=sequence.sequence_id,
        order=1,
        title="Song world",
        shot_ids=["SHT-000001", "SHT-000002"],
        target_duration_seconds=120,
        audit=audit(),
    )
    first = Shot(
        shot_id="SHT-000001",
        scene_id=scene.scene_id,
        order=1,
        time_range=TimeRange(start_seconds=0, duration_seconds=6),
        audit=audit(),
    )
    second = Shot(
        shot_id="SHT-000002",
        scene_id=scene.scene_id,
        order=2,
        time_range=TimeRange(start_seconds=6, duration_seconds=5.5),
        audit=audit(),
    )

    assert project.target_duration_seconds == 120
    assert timeline.duration_seconds == 120
    assert first.time_range.end_seconds == 6
    assert second.time_range.end_seconds == 11.5


def test_ninety_minute_movie_contract_validates() -> None:
    project = make_project("PRJ-000002", 5400, ContentFormat.MOVIE)
    timeline = Timeline(
        timeline_id="TML-000002",
        project_id=project.project_id,
        duration_seconds=5400,
        fps=24,
        act_ids=["ACT-000010", "ACT-000020", "ACT-000030"],
        audit=audit(),
    )

    assert project.content_format is ContentFormat.MOVIE
    assert timeline.duration_seconds == 5400
    assert len(timeline.act_ids) == 3


def test_project_rejects_more_than_three_hours() -> None:
    with pytest.raises(ValidationError):
        make_project("PRJ-000003", 10801, ContentFormat.MOVIE)


def test_locked_character_requires_version_pin() -> None:
    with pytest.raises(ValidationError):
        CharacterLock(scope=LockScope.PROJECT, project_id="PRJ-000001")


def test_look_lock_requires_look_pin() -> None:
    with pytest.raises(ValidationError):
        CharacterLock(
            scope=LockScope.LOOK,
            pinned_character_version_id="CHV-000001",
        )
