from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=False)


class AudienceKind(StrEnum):
    BABY = "baby"
    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    CHILD = "child"
    PRETEEN = "preteen"
    TEEN = "teen"
    FAMILY = "family"
    GENERAL = "general"
    ADULT = "adult"


class CastAge(StrEnum):
    BABY = "baby"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"
    MIXED = "mixed"
    NON_HUMAN = "non-human"


class CastGender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"
    UNSPECIFIED = "unspecified"
    NON_HUMAN = "non-human"


class ContentFormat(StrEnum):
    SONG = "song"
    SUNG_LULLABY = "sung-lullaby"
    SPOKEN_LULLABY = "spoken-lullaby"
    POEM = "poem"
    RHYME = "rhyme"
    STORY = "story"
    BEDTIME_STORY = "bedtime-story"
    GUIDED_IMAGINATION = "guided-imagination"
    EDUCATIONAL = "educational-video"
    EXPLAINER = "explainer"
    MUSIC_VIDEO = "music-video"
    DIALOGUE_SCENE = "dialogue-scene"
    SHORT_FILM = "short-film"
    EPISODE = "episode"
    SERIES_EPISODE = "series-episode"
    MOVIE = "movie"
    DOCUMENTARY = "documentary"
    CINEMATIC_SEQUENCE = "cinematic-sequence"
    COMPILATION = "compilation"
    TRAILER = "trailer"
    TEASER = "teaser"
    SHORT_SOCIAL = "short-social"
    CUSTOM = "custom"


class LockScope(StrEnum):
    GLOBAL = "global"
    PROJECT = "project"
    LOOK = "look"
    SCENE = "scene"
    UNLOCKED = "unlocked"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    PLANNING = "planning"
    PRODUCTION = "production"
    QA = "qa"
    PUBLISH_READY = "publish-ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class JobStatus(StrEnum):
    QUEUED = "queued"
    ELIGIBLE = "eligible"
    CLAIMED = "claimed"
    RUNNING = "running"
    WAITING_PROVIDER = "waiting-provider"
    WAITING_QUOTA = "waiting-quota"
    WAITING_HUMAN = "waiting-human"
    QA = "qa"
    COMPLETED = "completed"
    RETRYABLE_FAILED = "retryable-failed"
    BLOCKED_BUDGET = "blocked-budget"
    BLOCKED_LICENSE = "blocked-license"
    BLOCKED_CAPABILITY = "blocked-capability"
    MANUAL_HANDOFF = "manual-handoff"
    PERMANENT_FAILED = "permanent-failed"
    CANCELLED = "cancelled"


class AssetKind(StrEnum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SUBTITLE = "subtitle"
    DOCUMENT = "document"
    TIMELINE = "timeline"
    MANIFEST = "manifest"
    OTHER = "other"


class CanonicalStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class TimeRange(StrictModel):
    start_seconds: Annotated[float, Field(ge=0)]
    duration_seconds: Annotated[float, Field(gt=0)]

    @property
    def end_seconds(self) -> float:
        return self.start_seconds + self.duration_seconds


class AuditFields(StrictModel):
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    revision: Annotated[int, Field(ge=1)] = 1
