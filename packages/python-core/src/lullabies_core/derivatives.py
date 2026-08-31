from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Annotated, Any

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    AssetId,
    JobId,
    ProjectId,
    SchemaVersion,
    StorageObjectId,
    StrictModel,
    external_id_pattern,
)

DerivativeRecordId = Annotated[str, Field(pattern=external_id_pattern("DRV"))]


class DerivativeKind(StrEnum):
    THUMBNAIL = "thumbnail"
    IMAGE_PREVIEW = "image-preview"
    AUDIO_WAVEFORM = "audio-waveform"
    AUDIO_PREVIEW = "audio-preview"
    VIDEO_PROXY = "video-proxy"
    VIDEO_POSTER = "video-poster"


class DerivativeStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DerivativeSpec(StrictModel):
    kind: DerivativeKind
    width: Annotated[int | None, Field(gt=0)] = None
    height: Annotated[int | None, Field(gt=0)] = None
    max_duration_seconds: Annotated[float | None, Field(gt=0)] = None
    mime_type: str = Field(min_length=3, max_length=120)
    options: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_shape(self) -> DerivativeSpec:
        image_like = {
            DerivativeKind.THUMBNAIL,
            DerivativeKind.IMAGE_PREVIEW,
            DerivativeKind.VIDEO_POSTER,
        }
        if self.kind in image_like and (self.width is None or self.height is None):
            raise ValueError(f"{self.kind.value} requires width and height")
        if self.kind is DerivativeKind.AUDIO_WAVEFORM and self.max_duration_seconds is not None:
            raise ValueError("audio-waveform does not accept max_duration_seconds")
        return self

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)


class DerivativeRecord(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    derivative_record_id: DerivativeRecordId
    project_id: ProjectId
    source_asset_id: AssetId
    output_asset_id: AssetId | None = None
    output_storage_object_id: StorageObjectId | None = None
    job_id: JobId
    spec: DerivativeSpec
    operation_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    status: DerivativeStatus = DerivativeStatus.PLANNED
    created_at: AwareDatetime
    completed_at: AwareDatetime | None = None
    error_code: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="after")
    def validate_terminal_state(self) -> DerivativeRecord:
        if self.completed_at is not None and self.completed_at < self.created_at:
            raise ValueError("completed_at cannot precede created_at")
        if self.status is DerivativeStatus.COMPLETED:
            if self.completed_at is None:
                raise ValueError("completed derivative requires completed_at")
            if self.output_asset_id is None or self.output_storage_object_id is None:
                raise ValueError("completed derivative requires output asset and storage object")
        elif self.output_asset_id is not None or self.output_storage_object_id is not None:
            raise ValueError("non-completed derivative cannot publish output identities")
        return self


def derivative_operation_fingerprint(
    *,
    project_id: str,
    source_asset_id: str,
    spec: DerivativeSpec,
) -> str:
    """Stable semantic identity for one source asset + derivative specification.

    Runtime timestamps, worker identity and output IDs are intentionally excluded so a
    retried request resolves to the same operation fingerprint.
    """

    payload = {
        "project_id": project_id,
        "source_asset_id": source_asset_id,
        "spec": spec.canonical_payload(),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
