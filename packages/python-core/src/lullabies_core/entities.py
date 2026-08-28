from __future__ import annotations

from pydantic import Field

from .common import AuditFields, SCHEMA_VERSION, StrictModel


class World(StrictModel):
    schema_version: int = SCHEMA_VERSION
    world_id: str = Field(pattern=r"^WRL-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    description: str = ""
    style_profile_id: str | None = None
    canonical_reference_asset_ids: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    forbidden_mutations: list[str] = Field(default_factory=list)
    audit: AuditFields


class Location(StrictModel):
    schema_version: int = SCHEMA_VERSION
    location_id: str = Field(pattern=r"^LOC-[0-9]{6}$")
    world_id: str | None = Field(default=None, pattern=r"^WRL-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    description: str = ""
    canonical_reference_asset_ids: list[str] = Field(default_factory=list)
    environment_constraints: list[str] = Field(default_factory=list)
    audit: AuditFields


class Prop(StrictModel):
    schema_version: int = SCHEMA_VERSION
    prop_id: str = Field(pattern=r"^PRP-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    description: str = ""
    canonical_reference_asset_ids: list[str] = Field(default_factory=list)
    identity_constraints: list[str] = Field(default_factory=list)
    audit: AuditFields


class StyleProfile(StrictModel):
    schema_version: int = SCHEMA_VERSION
    style_profile_id: str = Field(pattern=r"^STY-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    treatment: list[str] = Field(default_factory=list)
    palette: list[str] = Field(default_factory=list)
    lighting_rules: list[str] = Field(default_factory=list)
    camera_rules: list[str] = Field(default_factory=list)
    texture_rules: list[str] = Field(default_factory=list)
    negative_constraints: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)
    audit: AuditFields


class VoiceProfile(StrictModel):
    schema_version: int = SCHEMA_VERSION
    voice_profile_id: str = Field(pattern=r"^VOC-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    presentation: str
    language: str = Field(min_length=2, max_length=32)
    timbre: str | None = None
    pace: str | None = None
    articulation: str | None = None
    emotion_defaults: list[str] = Field(default_factory=list)
    pronunciation_rules: list[str] = Field(default_factory=list)
    impersonation_prohibited: bool = True
    provider_voice_refs: dict[str, str] = Field(default_factory=dict)
    rights_record_id: str | None = None
    audit: AuditFields
