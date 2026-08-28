from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Final, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION: Final = 1
SchemaVersion = Literal[1]
TaxonomyValue = Annotated[str, Field(min_length=1, max_length=160)]
NonNegativeDecimal = Annotated[Decimal, Field(ge=0)]


def external_id_pattern(prefix: str) -> str:
    """Return the stable external-ID pattern for a canonical entity.

    Six digits remain the minimum for backwards compatibility with repository fixtures,
    while allowing the namespace to scale without a later contract-breaking widening.
    Database primary keys remain a separate persistence concern.
    """

    return rf"^{prefix}-[0-9]{{6,20}}$"


ProjectId = Annotated[str, Field(pattern=external_id_pattern("PRJ"))]
ContentId = Annotated[str, Field(pattern=external_id_pattern("CNT"))]
ContentVersionId = Annotated[str, Field(pattern=external_id_pattern("CTV"))]
CharacterId = Annotated[str, Field(pattern=external_id_pattern("CHR"))]
CharacterVersionId = Annotated[str, Field(pattern=external_id_pattern("CHV"))]
LookId = Annotated[str, Field(pattern=external_id_pattern("LOOK"))]
WorldId = Annotated[str, Field(pattern=external_id_pattern("WRL"))]
LocationId = Annotated[str, Field(pattern=external_id_pattern("LOC"))]
PropId = Annotated[str, Field(pattern=external_id_pattern("PRP"))]
StyleProfileId = Annotated[str, Field(pattern=external_id_pattern("STY"))]
VoiceProfileId = Annotated[str, Field(pattern=external_id_pattern("VOC"))]
ActId = Annotated[str, Field(pattern=external_id_pattern("ACT"))]
SequenceId = Annotated[str, Field(pattern=external_id_pattern("SEQ"))]
SceneId = Annotated[str, Field(pattern=external_id_pattern("SCN"))]
ShotId = Annotated[str, Field(pattern=external_id_pattern("SHT"))]
TakeId = Annotated[str, Field(pattern=external_id_pattern("TAK"))]
TimelineId = Annotated[str, Field(pattern=external_id_pattern("TML"))]
TrackId = Annotated[str, Field(pattern=external_id_pattern("TRK"))]
AssetId = Annotated[str, Field(pattern=external_id_pattern("AST"))]
JobId = Annotated[str, Field(pattern=external_id_pattern("JOB"))]
AttemptId = Annotated[str, Field(pattern=external_id_pattern("ATT"))]
QARecordId = Annotated[str, Field(pattern=external_id_pattern("QAR"))]
CostRecordId = Annotated[str, Field(pattern=external_id_pattern("CST"))]
RightsRecordId = Annotated[str, Field(pattern=external_id_pattern("RGT"))]
ApprovalId = Annotated[str, Field(pattern=external_id_pattern("APR"))]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=False)


class AudienceKind(StrEnum):
    """Built-in audience taxonomy values.

    Registry-owned taxonomy fields accept strings so future configured values do not
    require a core-schema release. This enum is a convenience set for built-ins.
    """

    BABY = "baby"
    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    CHILD = "child"
    PRETEEN = "preteen"
    TEEN = "teen"
    FAMILY = "family"
    GENERAL = "general"
    ADULT = "adult"
    CUSTOM = "custom"


class CastAge(StrEnum):
    NONE = "none"
    BABY = "baby"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"
    MIXED = "mixed"
    NON_HUMAN = "non-human"
    CUSTOM = "custom"


class CastGender(StrEnum):
    NONE = "none"
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"
    UNSPECIFIED = "unspecified"
    NON_HUMAN = "non-human"
    CUSTOM = "custom"


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
    TRAILER_TEASER = "trailer-teaser"
    TRAILER = "trailer"
    TEASER = "teaser"
    SHORT_SOCIAL = "short-social"
    CUSTOM = "custom"


class ExecutionMode(StrEnum):
    FREE_ONLY = "FREE_ONLY"
    FREE_FIRST = "FREE_FIRST"
    HYBRID_SMART = "HYBRID_SMART"
    BUDGET_CAPPED = "BUDGET_CAPPED"
    QUALITY_FIRST = "QUALITY_FIRST"


class AttemptStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUEST_CHANGES = "request-changes"
    WAIVED = "waived"


class CommercialUseStatus(StrEnum):
    UNKNOWN = "unknown"
    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    PROHIBITED = "prohibited"


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
    created_at: AwareDatetime
    updated_at: AwareDatetime
    created_by: str | None = None
    revision: Annotated[int, Field(ge=1)] = 1

    @model_validator(mode="after")
    def validate_timestamp_order(self) -> AuditFields:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")
        return self
