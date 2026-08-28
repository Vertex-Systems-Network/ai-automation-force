from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from .common import (
    AudienceKind,
    AuditFields,
    CastAge,
    CastGender,
    ContentFormat,
    ProjectStatus,
    SCHEMA_VERSION,
    StrictModel,
)


class AudienceProfile(StrictModel):
    kind: AudienceKind
    age_min_years: Annotated[float | None, Field(ge=0)] = None
    age_max_years: Annotated[float | None, Field(ge=0)] = None
    child_directed: bool = False
    family_co_viewing: bool = False
    policy_profile: str = "general"

    @model_validator(mode="after")
    def validate_age_range(self) -> "AudienceProfile":
        if (
            self.age_min_years is not None
            and self.age_max_years is not None
            and self.age_min_years > self.age_max_years
        ):
            raise ValueError("age_min_years cannot exceed age_max_years")
        return self


class CastProfile(StrictModel):
    ages: list[CastAge] = Field(default_factory=list)
    genders: list[CastGender] = Field(default_factory=list)
    human_count_target: Annotated[int | None, Field(ge=0)] = None
    non_human_count_target: Annotated[int | None, Field(ge=0)] = None
    ai_may_decide: bool = True


class OutputProfile(StrictModel):
    aspect_ratio: str = "16:9"
    width: Annotated[int | None, Field(gt=0)] = None
    height: Annotated[int | None, Field(gt=0)] = None
    fps: Annotated[float, Field(gt=0, le=120)] = 24
    target_resolution_label: str = "1080p"
    master_container: str = "mp4"
    generate_vertical_derivative: bool = False


class CreativeProfile(StrictModel):
    treatment: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    visual_style_id: str | None = None
    pacing_profile: str = "balanced"
    camera_profile: str | None = None
    transition_profile: str | None = None


class ProviderPolicyRef(StrictModel):
    execution_mode: str = "HYBRID_SMART"
    budget_policy_id: str | None = None
    allow_manual_free_handoff: bool = True
    preferred_provider_ids: list[str] = Field(default_factory=list)
    blocked_provider_ids: list[str] = Field(default_factory=list)


class Project(StrictModel):
    schema_version: int = SCHEMA_VERSION
    project_id: str = Field(pattern=r"^PRJ-[0-9]{6}$")
    title: str = Field(min_length=1, max_length=240)
    status: ProjectStatus = ProjectStatus.DRAFT
    audience: AudienceProfile
    cast: CastProfile
    content_format: ContentFormat
    custom_content_format: str | None = None
    language: str = Field(min_length=2, max_length=32)
    target_duration_seconds: Annotated[int, Field(ge=60, le=10800)]
    output: OutputProfile = Field(default_factory=OutputProfile)
    creative: CreativeProfile = Field(default_factory=CreativeProfile)
    provider_policy: ProviderPolicyRef = Field(default_factory=ProviderPolicyRef)
    character_ids: list[str] = Field(default_factory=list)
    world_ids: list[str] = Field(default_factory=list)
    prop_ids: list[str] = Field(default_factory=list)
    content_id: str | None = None
    active_timeline_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    audit: AuditFields

    @model_validator(mode="after")
    def validate_custom_format(self) -> "Project":
        if self.content_format == ContentFormat.CUSTOM and not self.custom_content_format:
            raise ValueError("custom_content_format is required when content_format=custom")
        if self.content_format != ContentFormat.CUSTOM and self.custom_content_format:
            raise ValueError("custom_content_format is only valid when content_format=custom")
        return self
