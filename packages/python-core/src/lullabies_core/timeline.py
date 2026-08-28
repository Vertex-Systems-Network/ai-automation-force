from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from .common import AuditFields, CanonicalStatus, SCHEMA_VERSION, StrictModel, TimeRange


class ContinuityState(StrictModel):
    character_states: dict[str, dict[str, str]] = Field(default_factory=dict)
    prop_states: dict[str, dict[str, str]] = Field(default_factory=dict)
    environment_state: dict[str, str] = Field(default_factory=dict)
    camera_state: dict[str, str] = Field(default_factory=dict)
    lighting_state: dict[str, str] = Field(default_factory=dict)
    motion_state: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class Take(StrictModel):
    schema_version: int = SCHEMA_VERSION
    take_id: str = Field(pattern=r"^TAK-[0-9]{6}$")
    shot_id: str = Field(pattern=r"^SHT-[0-9]{6}$")
    attempt_id: str | None = Field(default=None, pattern=r"^ATT-[0-9]{6}$")
    asset_id: str | None = Field(default=None, pattern=r"^AST-[0-9]{6}$")
    canonical_status: CanonicalStatus = CanonicalStatus.CANDIDATE
    continuity_score: Annotated[float | None, Field(ge=0, le=100)] = None
    qa_record_ids: list[str] = Field(default_factory=list)
    audit: AuditFields


class Shot(StrictModel):
    schema_version: int = SCHEMA_VERSION
    shot_id: str = Field(pattern=r"^SHT-[0-9]{6}$")
    scene_id: str = Field(pattern=r"^SCN-[0-9]{6}$")
    order: Annotated[int, Field(ge=1)]
    time_range: TimeRange
    purpose: str = ""
    action: str = ""
    character_ids: list[str] = Field(default_factory=list)
    location_id: str | None = Field(default=None, pattern=r"^LOC-[0-9]{6}$")
    prop_ids: list[str] = Field(default_factory=list)
    camera: dict[str, str] = Field(default_factory=dict)
    incoming_state: ContinuityState = Field(default_factory=ContinuityState)
    outgoing_state: ContinuityState = Field(default_factory=ContinuityState)
    first_frame_asset_id: str | None = Field(default=None, pattern=r"^AST-[0-9]{6}$")
    end_frame_asset_id: str | None = Field(default=None, pattern=r"^AST-[0-9]{6}$")
    reference_asset_ids: list[str] = Field(default_factory=list)
    take_ids: list[str] = Field(default_factory=list)
    selected_take_id: str | None = Field(default=None, pattern=r"^TAK-[0-9]{6}$")
    transition_in: str = "cut"
    transition_out: str = "cut"
    handles_seconds: Annotated[float, Field(ge=0, le=10)] = 0.0
    generation_notes: list[str] = Field(default_factory=list)
    audit: AuditFields

    @model_validator(mode="after")
    def validate_selected_take(self) -> "Shot":
        if self.selected_take_id and self.selected_take_id not in self.take_ids:
            raise ValueError("selected_take_id must be present in take_ids")
        return self


class Scene(StrictModel):
    schema_version: int = SCHEMA_VERSION
    scene_id: str = Field(pattern=r"^SCN-[0-9]{6}$")
    sequence_id: str = Field(pattern=r"^SEQ-[0-9]{6}$")
    order: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    summary: str = ""
    location_id: str | None = Field(default=None, pattern=r"^LOC-[0-9]{6}$")
    character_ids: list[str] = Field(default_factory=list)
    shot_ids: list[str] = Field(default_factory=list)
    target_duration_seconds: Annotated[float, Field(gt=0)]
    incoming_state: ContinuityState = Field(default_factory=ContinuityState)
    outgoing_state: ContinuityState = Field(default_factory=ContinuityState)
    audit: AuditFields


class Sequence(StrictModel):
    schema_version: int = SCHEMA_VERSION
    sequence_id: str = Field(pattern=r"^SEQ-[0-9]{6}$")
    act_id: str = Field(pattern=r"^ACT-[0-9]{6}$")
    order: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    scene_ids: list[str] = Field(default_factory=list)
    target_duration_seconds: Annotated[float, Field(gt=0)]
    audit: AuditFields


class Act(StrictModel):
    schema_version: int = SCHEMA_VERSION
    act_id: str = Field(pattern=r"^ACT-[0-9]{6}$")
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    order: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    sequence_ids: list[str] = Field(default_factory=list)
    target_duration_seconds: Annotated[float, Field(gt=0)]
    audit: AuditFields


class TimelineTrack(StrictModel):
    track_id: str = Field(pattern=r"^TRK-[0-9]{6}$")
    kind: str = Field(min_length=1)
    name: str = Field(min_length=1)
    item_ids: list[str] = Field(default_factory=list)
    muted: bool = False
    locked: bool = False


class Timeline(StrictModel):
    schema_version: int = SCHEMA_VERSION
    timeline_id: str = Field(pattern=r"^TML-[0-9]{6}$")
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    version: Annotated[int, Field(ge=1)] = 1
    duration_seconds: Annotated[float, Field(ge=60, le=10800)]
    fps: Annotated[float, Field(gt=0, le=120)] = 24
    act_ids: list[str] = Field(default_factory=list)
    tracks: list[TimelineTrack] = Field(default_factory=list)
    marker_asset_ids: list[str] = Field(default_factory=list)
    otio_asset_id: str | None = Field(default=None, pattern=r"^AST-[0-9]{6}$")
    audit: AuditFields
