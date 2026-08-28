from __future__ import annotations

import hashlib
import json
from typing import Annotated, Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from .common import AuditFields, ContentId, ContentVersionId, StrictModel
from .content import Content, ContentObjective, ContentVersion

LEGACY_CONTENT_MAPPING_VERSION = "legacy-content-v1-to-core-v1"

LegacyContentType = Literal[
    "song",
    "lullaby",
    "poem",
    "rhyme",
    "story",
    "bedtime-story",
    "educational-narration",
    "guided-imagination",
]
LegacyAgeBand = Literal[
    "baby-audio",
    "toddler",
    "preschool",
    "early-primary",
    "junior",
    "preteen",
]
LegacyStatus = Literal[
    "idea",
    "researched",
    "uniqueness-cleared",
    "drafted",
    "qa-passed",
    "audio-ready",
    "approved",
    "audio-generated",
    "video-planned",
    "video-generated",
    "publish-ready",
    "published",
    "analyzed",
]
LegacyAudioMode = Literal["speech", "music", "chant"]
LegacyProviderFamily = Literal["gemini-tts", "lyria"]
LegacyRenderStatus = Literal["not-rendered", "queued", "rendered", "qa-passed", "rejected"]
LegacyOriginalityDecision = Literal[
    "CLEAR",
    "CLEAR_WITH_DIFFERENTIATION",
    "REJECT_DUPLICATE",
    "REJECT_DERIVATIVE",
    "DEFER_PORTFOLIO_FATIGUE",
]
LegacyReconciliationAction = Literal["create", "noop", "conflict"]


class LegacyNestedModel(BaseModel):
    """Nested legacy objects preserve JSON Schema's default extra-field behavior."""

    model_config = ConfigDict(extra="allow")


class LegacyObjective(LegacyNestedModel):
    primary: str
    entertainment: str
    learning: str | None = None
    emotional: str | None = None


class LegacyCreative(LegacyNestedModel):
    premise: str
    hook: str
    creative_device: str
    characters: list[str] = Field(default_factory=list)
    setting: str | None = None
    topics: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class LegacyAudio(LegacyNestedModel):
    audio_mode: LegacyAudioMode
    provider_family: LegacyProviderFamily
    preferred_model: str
    female_voice_required: bool
    prompt_version: str
    selected_voice: str | None = None
    render_status: LegacyRenderStatus | None = None


class LegacyOriginality(LegacyNestedModel):
    decision: LegacyOriginalityDecision
    closest_prior_ids: list[str]
    notes: str = ""


class LegacyQA(LegacyNestedModel):
    all_mandatory_gates_passed: bool
    qa_file: str | None = None


class LegacyResearch(LegacyNestedModel):
    research_file: str | None = None
    source_count: Annotated[int | None, Field(ge=0)] = None


class LegacyFingerprints(LegacyNestedModel):
    title: str | None = None
    premise: str | None = None
    hook: str | None = None
    exact_text: str | None = None


class LegacyPaths(LegacyNestedModel):
    package: str
    content: str
    metadata: str
    audio_prompt: str
    qa: str
    research: str


class LegacyContentPackageV1(BaseModel):
    """Executable compatibility model for `schemas/content-package.schema.json` v1."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    content_id: Annotated[str, Field(pattern=r"^CNT-[0-9]{6}$")]
    run_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    normalized_title: str | None = None
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    content_type: LegacyContentType
    age_band: LegacyAgeBand
    language: str = Field(min_length=2)
    status: LegacyStatus
    target_duration_seconds: Annotated[int | None, Field(ge=1)] = None
    objective: LegacyObjective
    creative: LegacyCreative
    audio: LegacyAudio
    originality: LegacyOriginality
    qa: LegacyQA
    research: LegacyResearch | None = None
    fingerprints: LegacyFingerprints | None = None
    paths: LegacyPaths
    created_at: AwareDatetime
    approved_at: AwareDatetime | None = None


class LegacyContentImportReport(StrictModel):
    mapping_version: Literal["legacy-content-v1-to-core-v1"] = LEGACY_CONTENT_MAPPING_VERSION
    source_schema_version: Literal[1] = 1
    source_content_id: ContentId
    canonical_content_id: ContentId
    canonical_content_version_id: ContentVersionId
    source_fingerprint_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    import_key: str = Field(min_length=1)
    source_run_id: str
    source_package_path: str
    legacy_age_band: str
    legacy_content_type: str
    canonical_content_format: str
    legacy_audio_mode: str
    unmapped_character_names: list[str] = Field(default_factory=list)
    unmapped_setting: str | None = None
    warnings: list[str] = Field(default_factory=list)


class LegacyContentImportResult(StrictModel):
    content: Content
    content_version: ContentVersion
    report: LegacyContentImportReport


class LegacyContentReconciliation(StrictModel):
    """Pure persistence decision for an imported legacy content identity."""

    action: LegacyReconciliationAction
    canonical_content_id: ContentId
    canonical_content_version_id: ContentVersionId
    source_fingerprint_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    import_key: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    conflict_fields: list[str] = Field(default_factory=list)


class LegacyContentImportError(ValueError):
    """Recoverable legacy-to-canonical mapping failure with a stable machine code."""

    def __init__(self, code: str, message: str, field: str | None = None) -> None:
        self.code = code
        self.field = field
        detail = f"{code}: {message}"
        if field is not None:
            detail = f"{detail} [field={field}]"
        super().__init__(detail)


def import_legacy_content_package(
    payload: dict[str, Any],
    content_text: str,
) -> LegacyContentImportResult:
    """Map one legacy metadata package plus its resolved canonical text without I/O.

    The function never mutates `payload`, never reads paths from the package, and never
    writes persistence. Repeating the same inputs produces the same canonical IDs,
    source fingerprint and import key.
    """

    legacy = LegacyContentPackageV1.model_validate(payload)
    _validate_mapping_preconditions(legacy, content_text)

    content_version_id = _content_version_id(legacy.content_id)
    canonical_format = _canonical_content_format(legacy)
    source_fingerprint = _source_fingerprint(payload, content_text)
    updated_at = legacy.approved_at or legacy.created_at
    if updated_at < legacy.created_at:
        raise LegacyContentImportError(
            "LEGACY_APPROVAL_PRECEDES_CREATION",
            "approved_at cannot precede created_at",
            "approved_at",
        )

    audit = AuditFields(
        created_at=legacy.created_at,
        updated_at=updated_at,
        created_by=f"legacy-import:{legacy.run_id}",
    )
    content = Content(
        content_id=legacy.content_id,
        active_version_id=content_version_id,
        status=legacy.status,
        source_legacy_package_path=legacy.paths.package,
        audit=audit,
    )
    content_version = ContentVersion(
        content_version_id=content_version_id,
        content_id=legacy.content_id,
        version=1,
        title=legacy.title,
        content_format=canonical_format,
        language=legacy.language,
        target_duration_seconds=legacy.target_duration_seconds,
        objective=ContentObjective(
            primary=legacy.objective.primary,
            entertainment=legacy.objective.entertainment,
            learning=legacy.objective.learning,
            emotional=legacy.objective.emotional,
        ),
        premise=legacy.creative.premise,
        hook=legacy.creative.hook,
        script_or_lyrics=content_text,
        tags=_stable_unique([*legacy.creative.tags, *legacy.creative.topics]),
        originality_fingerprint=_originality_fingerprint(legacy, content_text),
        audit=audit.model_copy(deep=True),
    )

    warnings = _mapping_warnings(legacy)
    report = LegacyContentImportReport(
        source_content_id=legacy.content_id,
        canonical_content_id=content.content_id,
        canonical_content_version_id=content_version.content_version_id,
        source_fingerprint_sha256=source_fingerprint,
        import_key=(
            f"{LEGACY_CONTENT_MAPPING_VERSION}:{legacy.content_id}:{source_fingerprint}"
        ),
        source_run_id=legacy.run_id,
        source_package_path=legacy.paths.package,
        legacy_age_band=legacy.age_band,
        legacy_content_type=legacy.content_type,
        canonical_content_format=canonical_format,
        legacy_audio_mode=legacy.audio.audio_mode,
        unmapped_character_names=list(legacy.creative.characters),
        unmapped_setting=legacy.creative.setting,
        warnings=warnings,
    )
    return LegacyContentImportResult(
        content=content,
        content_version=content_version,
        report=report,
    )


def reconcile_legacy_content_import(
    imported: LegacyContentImportResult,
    *,
    existing_content: Content | None = None,
    existing_content_version: ContentVersion | None = None,
    existing_import_key: str | None = None,
) -> LegacyContentReconciliation:
    """Plan CREATE/NOOP/CONFLICT without performing persistence.

    WP5+ repositories may use this result inside a transaction. A repeated import of the
    same canonical records is a NOOP. Reusing the same stable CNT/CTV identity for changed
    source material or partial/mismatched canonical state is a CONFLICT, never an overwrite.
    """

    report = imported.report
    base = {
        "canonical_content_id": report.canonical_content_id,
        "canonical_content_version_id": report.canonical_content_version_id,
        "source_fingerprint_sha256": report.source_fingerprint_sha256,
        "import_key": report.import_key,
    }

    if existing_content is None and existing_content_version is None:
        return LegacyContentReconciliation(
            action="create",
            reason="canonical content identity is not persisted",
            **base,
        )

    if existing_content is None or existing_content_version is None:
        missing = "content" if existing_content is None else "content_version"
        return LegacyContentReconciliation(
            action="conflict",
            reason="canonical persistence state is partial and requires operator recovery",
            conflict_fields=[missing],
            **base,
        )

    conflicts: list[str] = []
    if existing_content.content_id != imported.content.content_id:
        conflicts.append("content.content_id")
    if existing_content_version.content_version_id != imported.content_version.content_version_id:
        conflicts.append("content_version.content_version_id")
    if existing_content_version.content_id != imported.content.content_id:
        conflicts.append("content_version.content_id")
    if existing_import_key is not None and existing_import_key != report.import_key:
        conflicts.append("import_key")

    if conflicts:
        return LegacyContentReconciliation(
            action="conflict",
            reason="stable legacy identity resolves to conflicting persisted identity or source",
            conflict_fields=conflicts,
            **base,
        )

    record_conflicts: list[str] = []
    if existing_content != imported.content:
        record_conflicts.append("content")
    if existing_content_version != imported.content_version:
        record_conflicts.append("content_version")
    if record_conflicts:
        return LegacyContentReconciliation(
            action="conflict",
            reason="stable legacy identity already exists with different canonical data",
            conflict_fields=record_conflicts,
            **base,
        )

    return LegacyContentReconciliation(
        action="noop",
        reason="same deterministic import is already represented canonically",
        **base,
    )


def _validate_mapping_preconditions(legacy: LegacyContentPackageV1, content_text: str) -> None:
    if legacy.target_duration_seconds is None:
        raise LegacyContentImportError(
            "LEGACY_DURATION_REQUIRED",
            "target_duration_seconds is optional in v1 metadata but required by the canonical model",
            "target_duration_seconds",
        )
    if not 60 <= legacy.target_duration_seconds <= 10800:
        raise LegacyContentImportError(
            "LEGACY_DURATION_OUT_OF_CANONICAL_RANGE",
            "target duration must be within the canonical 60..10800 second range",
            "target_duration_seconds",
        )
    if not content_text.strip():
        raise LegacyContentImportError(
            "LEGACY_CONTENT_TEXT_REQUIRED",
            "resolved content text is empty",
            "paths.content",
        )


def _content_version_id(content_id: str) -> str:
    return f"CTV-{content_id.removeprefix('CNT-')}"


def _canonical_content_format(legacy: LegacyContentPackageV1) -> str:
    if legacy.content_type != "lullaby":
        return legacy.content_type
    if legacy.audio.audio_mode == "speech":
        return "spoken-lullaby"
    return "sung-lullaby"


def _source_fingerprint(payload: dict[str, Any], content_text: str) -> str:
    try:
        metadata = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise LegacyContentImportError(
            "LEGACY_METADATA_NOT_CANONICAL_JSON",
            "metadata contains a value that cannot be deterministically serialized as JSON",
        ) from exc
    material = f"{metadata}\n---CONTENT---\n{content_text}".encode()
    return hashlib.sha256(material).hexdigest()


def _originality_fingerprint(legacy: LegacyContentPackageV1, content_text: str) -> str:
    if legacy.fingerprints is not None and legacy.fingerprints.exact_text:
        return legacy.fingerprints.exact_text
    return hashlib.sha256(content_text.encode()).hexdigest()


def _mapping_warnings(legacy: LegacyContentPackageV1) -> list[str]:
    warnings = [
        "legacy age_band remains source metadata; audience policy mapping belongs to project import",
        "legacy audio direction remains source metadata; audio production mapping is outside WP4",
    ]
    if legacy.creative.topics:
        warnings.append("legacy creative.topics were merged into canonical ContentVersion.tags")
    if legacy.creative.characters:
        warnings.append(
            "legacy free-text character names were not fabricated into canonical CHR-* references"
        )
    if legacy.creative.setting:
        warnings.append(
            "legacy free-text setting was not fabricated into canonical World/Location references"
        )
    return warnings


def _stable_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
