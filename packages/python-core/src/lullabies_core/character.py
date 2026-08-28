from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from .common import AuditFields, CanonicalStatus, LockScope, SCHEMA_VERSION, StrictModel


class CharacterLook(StrictModel):
    look_id: str = Field(pattern=r"^LOOK-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    wardrobe: list[str] = Field(default_factory=list)
    accessories: list[str] = Field(default_factory=list)
    hair: str | None = None
    eyes: str | None = None
    palette: list[str] = Field(default_factory=list)
    expression_defaults: list[str] = Field(default_factory=list)
    body_notes: list[str] = Field(default_factory=list)
    prohibited_mutations: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)


class CharacterVersion(StrictModel):
    schema_version: int = SCHEMA_VERSION
    character_version_id: str = Field(pattern=r"^CHV-[0-9]{6}$")
    character_id: str = Field(pattern=r"^CHR-[0-9]{6}$")
    version: Annotated[int, Field(ge=1)]
    display_name: str = Field(min_length=1, max_length=160)
    character_type: str = Field(min_length=1, max_length=80)
    species: str | None = None
    apparent_age: str | None = None
    gender_presentation: str | None = None
    personality_traits: list[str] = Field(default_factory=list)
    movement_style: str | None = None
    voice_profile_id: str | None = None
    looks: list[CharacterLook] = Field(default_factory=list)
    canonical_reference_asset_ids: list[str] = Field(default_factory=list)
    identity_constraints: list[str] = Field(default_factory=list)
    status: CanonicalStatus = CanonicalStatus.CANDIDATE
    audit: AuditFields


class CharacterLock(StrictModel):
    scope: LockScope
    pinned_character_version_id: str | None = Field(default=None, pattern=r"^CHV-[0-9]{6}$")
    pinned_look_id: str | None = Field(default=None, pattern=r"^LOOK-[0-9]{6}$")
    project_id: str | None = Field(default=None, pattern=r"^PRJ-[0-9]{6}$")
    scene_id: str | None = Field(default=None, pattern=r"^SCN-[0-9]{6}$")

    @model_validator(mode="after")
    def validate_scope_requirements(self) -> "CharacterLock":
        if self.scope != LockScope.UNLOCKED and self.pinned_character_version_id is None:
            raise ValueError("locked scopes require pinned_character_version_id")
        if self.scope == LockScope.PROJECT and self.project_id is None:
            raise ValueError("project lock requires project_id")
        if self.scope == LockScope.LOOK and self.pinned_look_id is None:
            raise ValueError("look lock requires pinned_look_id")
        if self.scope == LockScope.SCENE and self.scene_id is None:
            raise ValueError("scene lock requires scene_id")
        return self


class Character(StrictModel):
    schema_version: int = SCHEMA_VERSION
    character_id: str = Field(pattern=r"^CHR-[0-9]{6}$")
    name: str = Field(min_length=1, max_length=160)
    active_version_id: str = Field(pattern=r"^CHV-[0-9]{6}$")
    lock: CharacterLock
    reusable: bool = True
    rights_record_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    audit: AuditFields
