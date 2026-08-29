from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    AuditFields,
    ProjectId,
    SchemaVersion,
    StorageObjectId,
    StrictModel,
    UploadSessionId,
)
from .storage import StorageBackend, validate_object_key


class UploadMode(StrEnum):
    SINGLE = "single"
    MULTIPART = "multipart"


class UploadSessionStatus(StrEnum):
    OPEN = "open"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    ABORTED = "aborted"
    EXPIRED = "expired"


class UploadSessionError(RuntimeError):
    """Base class for upload-session state failures."""


class UploadSessionConflictError(UploadSessionError):
    """An idempotency key, part identity, or terminal state conflicts with the request."""


class UploadSessionExpiredError(UploadSessionConflictError):
    """The upload session crossed its expiry boundary before the requested mutation."""


class UploadPart(StrictModel):
    part_number: int = Field(ge=1, le=10_000)
    size_bytes: int = Field(gt=0)
    etag: str | None = Field(default=None, min_length=1, max_length=512)
    checksum_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    recorded_at: AwareDatetime


class UploadSession(StrictModel):
    """Durable transfer state. Completion means uploaded, not quarantine/Asset acceptance."""

    schema_version: SchemaVersion = SCHEMA_VERSION
    upload_session_id: UploadSessionId
    project_id: ProjectId
    storage_object_id: StorageObjectId
    backend: StorageBackend
    bucket: str | None = Field(default=None, min_length=1, max_length=255)
    object_key: str = Field(min_length=1, max_length=1024)
    expected_size_bytes: int = Field(gt=0)
    expected_mime_type: str = Field(min_length=3, max_length=255)
    original_filename: str | None = Field(default=None, min_length=1, max_length=512)
    mode: UploadMode
    part_size_bytes: int | None = Field(default=None, gt=0)
    backend_upload_id: str | None = Field(default=None, min_length=1, max_length=2048)
    quota_reservation_id: str | None = Field(default=None, min_length=1, max_length=255)
    creation_idempotency_key: str = Field(min_length=8, max_length=200)
    expires_at: AwareDatetime
    status: UploadSessionStatus = UploadSessionStatus.OPEN
    parts: list[UploadPart] = Field(default_factory=list)
    observed_size_bytes: int | None = Field(default=None, ge=0)
    observed_etag: str | None = Field(default=None, min_length=1, max_length=512)
    observed_version_id: str | None = Field(default=None, min_length=1, max_length=1024)
    completed_at: AwareDatetime | None = None
    aborted_at: AwareDatetime | None = None
    audit: AuditFields

    @model_validator(mode="after")
    def validate_upload_contract(self) -> UploadSession:
        validate_object_key(self.object_key)
        if self.backend is StorageBackend.S3 and self.bucket is None:
            raise ValueError("S3 upload sessions require a bucket")
        if self.backend is StorageBackend.FILESYSTEM and self.bucket is not None:
            raise ValueError("filesystem upload sessions must not carry a bucket")
        if self.expires_at <= self.audit.created_at:
            raise ValueError("upload expiry must be after creation")
        if self.mode is UploadMode.SINGLE:
            if self.part_size_bytes is not None:
                raise ValueError("single uploads must not define part_size_bytes")
            if self.parts:
                raise ValueError("single uploads must not persist multipart parts")
            if self.backend_upload_id is not None:
                raise ValueError("single uploads must not carry a multipart backend upload id")
        else:
            if self.part_size_bytes is None:
                raise ValueError("multipart uploads require part_size_bytes")
            if self.part_size_bytes > self.expected_size_bytes:
                raise ValueError("part_size_bytes cannot exceed expected upload size")
        numbers = [part.part_number for part in self.parts]
        if len(numbers) != len(set(numbers)):
            raise ValueError("multipart part numbers must be unique")
        if numbers != sorted(numbers):
            raise ValueError("multipart parts must be stored in part-number order")
        if sum(part.size_bytes for part in self.parts) > self.expected_size_bytes:
            raise ValueError("recorded multipart bytes exceed expected upload size")
        if self.status is UploadSessionStatus.COMPLETED:
            if self.completed_at is None or self.observed_size_bytes is None:
                raise ValueError("completed uploads require completion time and observed size")
            if self.observed_size_bytes != self.expected_size_bytes:
                raise ValueError("completed upload size must match expected size")
            if self.mode is UploadMode.MULTIPART:
                if not self.parts:
                    raise ValueError("completed multipart uploads require recorded parts")
                if sum(part.size_bytes for part in self.parts) != self.expected_size_bytes:
                    raise ValueError("completed multipart part bytes must match expected size")
        elif self.completed_at is not None or self.observed_size_bytes is not None:
            raise ValueError("completion evidence is valid only for completed uploads")
        if self.status is UploadSessionStatus.ABORTED:
            if self.aborted_at is None:
                raise ValueError("aborted uploads require aborted_at")
        elif self.aborted_at is not None:
            raise ValueError("aborted_at is valid only for aborted uploads")
        if self.completed_at is not None and self.completed_at > self.audit.updated_at:
            raise ValueError("completed_at cannot exceed audit.updated_at")
        if self.aborted_at is not None and self.aborted_at > self.audit.updated_at:
            raise ValueError("aborted_at cannot exceed audit.updated_at")
        return self


class UploadMutationResult(StrictModel):
    action: Literal[
        "created",
        "reused",
        "bound",
        "recorded",
        "completed",
        "aborted",
        "expired",
    ]
    upload_session_id: UploadSessionId
    status: UploadSessionStatus
    revision: int = Field(ge=1)


class DirectUploadGrant(StrictModel):
    """Ephemeral exact-object transfer authorization; never canonical persistence."""

    method: Literal["PUT", "POST"]
    url: str = Field(min_length=1)
    object_key: str = Field(min_length=1, max_length=1024)
    content_type: str = Field(min_length=3, max_length=255)
    max_size_bytes: int = Field(gt=0)
    expires_at: AwareDatetime
    required_headers: dict[str, str] = Field(default_factory=dict)
    form_fields: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_key(self) -> DirectUploadGrant:
        validate_object_key(self.object_key)
        if self.method == "PUT" and self.form_fields:
            raise ValueError("PUT upload grants must not carry form fields")
        return self


class MultipartPartGrant(StrictModel):
    """Ephemeral authorization for exactly one persisted multipart upload part."""

    method: Literal["PUT"] = "PUT"
    url: str = Field(min_length=1)
    object_key: str = Field(min_length=1, max_length=1024)
    backend_upload_id: str = Field(min_length=1, max_length=2048)
    part_number: int = Field(ge=1, le=10_000)
    expires_at: AwareDatetime

    @model_validator(mode="after")
    def validate_key(self) -> MultipartPartGrant:
        validate_object_key(self.object_key)
        return self
