from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from .common import (
    SCHEMA_VERSION,
    ActId,
    AssetId,
    AttemptId,
    AuditFields,
    CanonicalStatus,
    CharacterId,
    LocationId,
    ProjectId,
    PropId,
    QARecordId,
    SceneId,
    SchemaVersion,
    SequenceId,
    ShotId,
    StrictModel,
    TakeId,
    TimelineId,
    TimeRange,
    TrackId,
)


class ContinuityState(StrictModel):
    character_states: dict[str, dict[str, str]] = Field(default_factory=dict)
    prop_states: dict[str, dict[str, str]] = Field(default_factory=dict)
    environment_state: dict[str, str] = Field(default_factory=dict)
    camera_state: dict[str, str] = Field(default_factory=dict)
    lighting_state: dict[str, str] = Field(default_factory=dict)
    motion_state: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class Take(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    take_id: TakeId
    shot_id: ShotId
    attempt_id: AttemptId | None = None
    asset_id: AssetId | None = None
    canonical_status: CanonicalStatus = CanonicalStatus.CANDIDATE
    continuity_score: Annotated[float | None, Field(ge=0, le=100)] = None
    qa_record_ids: list[QARecordId] = Field(default_factory=list)
    audit: AuditFields


class Shot(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    shot_id: ShotId
    scene_id: SceneId
    order: Annotated[int, Field(ge=1)]
    time_range: TimeRange
    purpose: str = ""
    action: str = ""
    character_ids: list[CharacterId] = Field(default_factory=list)
    location_id: LocationId | None = None
    prop_ids: list[PropId] = Field(default_factory=list)
    camera: dict[str, str] = Field(default_factory=dict)
    incoming_state: ContinuityState = Field(default_factory=ContinuityState)
    outgoing_state: ContinuityState = Field(default_factory=ContinuityState)
    first_frame_asset_id: AssetId | None = None
    end_frame_asset_id: AssetId | None = None
    reference_asset_ids: list[AssetId] = Field(default_factory=list)
    take_ids: list[TakeId] = Field(default_factory=list)
    selected_take_id: TakeId | None = None
    transition_in: str = "cut"
    transition_out: str = "cut"
    handles_seconds: Annotated[float, Field(ge=0, le=10)] = 0.0
    generation_notes: list[str] = Field(default_factory=list)
    audit: AuditFields

    @model_validator(mode="after")
    def validate_selected_take(self) -> Shot:
        if self.selected_take_id and self.selected_take_id not in self.take_ids:
            raise ValueError("selected_take_id must be present in take_ids")
        return self


class Scene(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    scene_id: SceneId
    sequence_id: SequenceId
    order: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    summary: str = ""
    location_id: LocationId | None = None
    character_ids: list[CharacterId] = Field(default_factory=list)
    shot_ids: list[ShotId] = Field(default_factory=list)
    target_duration_seconds: Annotated[float, Field(gt=0)]
    incoming_state: ContinuityState = Field(default_factory=ContinuityState)
    outgoing_state: ContinuityState = Field(default_factory=ContinuityState)
    audit: AuditFields


class Sequence(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    sequence_id: SequenceId
    act_id: ActId
    order: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    scene_ids: list[SceneId] = Field(default_factory=list)
    target_duration_seconds: Annotated[float, Field(gt=0)]
    audit: AuditFields


class Act(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    act_id: ActId
    project_id: ProjectId
    order: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    sequence_ids: list[SequenceId] = Field(default_factory=list)
    target_duration_seconds: Annotated[float, Field(gt=0)]
    audit: AuditFields


class TimelineTrack(StrictModel):
    track_id: TrackId
    kind: str = Field(min_length=1)
    name: str = Field(min_length=1)
    item_ids: list[str] = Field(default_factory=list)
    muted: bool = False
    locked: bool = False


class Timeline(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    timeline_id: TimelineId
    project_id: ProjectId
    version: Annotated[int, Field(ge=1)] = 1
    duration_seconds: Annotated[float, Field(ge=60, le=10800)]
    fps: Annotated[float, Field(gt=0, le=120)] = 24
    act_ids: list[ActId] = Field(default_factory=list)
    tracks: list[TimelineTrack] = Field(default_factory=list)
    marker_asset_ids: list[AssetId] = Field(default_factory=list)
    otio_asset_id: AssetId | None = None
    audit: AuditFields
