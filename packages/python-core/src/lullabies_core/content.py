from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from .common import (
    AuditFields,
    SCHEMA_VERSION,
    SchemaVersion,
    StrictModel,
    TaxonomyValue,
    external_id_pattern,
)


class ContentObjective(StrictModel):
    primary: str = Field(min_length=1)
    entertainment: str | None = None
    learning: str | None = None
    emotional: str | None = None


class ContentVersion(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    content_version_id: str = Field(pattern=external_id_pattern("CTV"))
    content_id: str = Field(pattern=external_id_pattern("CNT"))
    version: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1, max_length=240)
    content_format: TaxonomyValue
    custom_content_format: str | None = None
    language: str = Field(min_length=2, max_length=32)
    target_duration_seconds: Annotated[int, Field(ge=60, le=10800)]
    objective: ContentObjective
    premise: str = ""
    hook: str = ""
    script_or_lyrics: str = Field(min_length=1)
    structure_map: list[str] = Field(default_factory=list)
    character_ids: list[str] = Field(default_factory=list)
    world_ids: list[str] = Field(default_factory=list)
    prop_ids: list[str] = Field(default_factory=list)
    pronunciation_notes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    originality_fingerprint: str | None = None
    audit: AuditFields

    @model_validator(mode="after")
    def validate_custom_format(self) -> "ContentVersion":
        if self.content_format == "custom" and not self.custom_content_format:
            raise ValueError("custom_content_format is required for custom content")
        if self.content_format != "custom" and self.custom_content_format:
            raise ValueError("custom_content_format is only valid for custom content")
        return self


class Content(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    content_id: str = Field(pattern=external_id_pattern("CNT"))
    active_version_id: str = Field(pattern=external_id_pattern("CTV"))
    project_id: str | None = Field(default=None, pattern=external_id_pattern("PRJ"))
    status: str = "draft"
    source_legacy_package_path: str | None = None
    audit: AuditFields
