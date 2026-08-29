from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    AuditFields,
    ProjectId,
    SchemaVersion,
    StorageObjectId,
    StrictModel,
    UploadSessionId,
    external_id_pattern,
)

QuarantineInspectionId = Annotated[str, Field(pattern=external_id_pattern("QIN"))]


class QuarantineStatus(StrEnum):
    PENDING = "pending"
    INSPECTING = "inspecting"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MediaProbeStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed-out"
    UNAVAILABLE = "unavailable"


class ThreatScanStatus(StrEnum):
    CLEAN = "clean"
    DETECTED = "detected"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


class QuarantineRejectionCode(StrEnum):
    SIZE_MISMATCH = "size-mismatch"
    SIZE_LIMIT_EXCEEDED = "size-limit-exceeded"
    UNSUPPORTED_MIME = "unsupported-mime"
    MAGIC_UNKNOWN = "magic-unknown"
    MIME_MISMATCH = "mime-mismatch"
    PROBE_REQUIRED = "probe-required"
    PROBE_FAILED = "probe-failed"
    PROBE_TIMED_OUT = "probe-timed-out"
    PROBE_UNAVAILABLE = "probe-unavailable"
    THREAT_DETECTED = "threat-detected"
    THREAT_SCAN_ERROR = "threat-scan-error"
    THREAT_SCAN_UNAVAILABLE = "threat-scan-unavailable"


class MediaSecurityPolicy(StrictModel):
    allowed_mime_types: tuple[str, ...]
    max_size_bytes: int = Field(gt=0)
    require_magic_match: bool = True
    probe_mime_prefixes: tuple[str, ...] = ("audio/", "video/")
    require_threat_scan: bool = True

    @model_validator(mode="after")
    def validate_policy(self) -> MediaSecurityPolicy:
        if not self.allowed_mime_types:
            raise ValueError("allowed_mime_types must not be empty")
        if len(self.allowed_mime_types) != len(set(self.allowed_mime_types)):
            raise ValueError("allowed_mime_types must be unique")
        for mime_type in self.allowed_mime_types:
            if "/" not in mime_type or mime_type != mime_type.strip().lower():
                raise ValueError("allowed MIME types must be normalized lower-case media types")
        if len(self.probe_mime_prefixes) != len(set(self.probe_mime_prefixes)):
            raise ValueError("probe_mime_prefixes must be unique")
        if any(not prefix.endswith("/") for prefix in self.probe_mime_prefixes):
            raise ValueError("probe MIME prefixes must end with '/'")
        return self

    def requires_probe(self, mime_type: str) -> bool:
        return any(mime_type.startswith(prefix) for prefix in self.probe_mime_prefixes)


class MediaProbeResult(StrictModel):
    status: MediaProbeStatus
    format_name: str | None = Field(default=None, min_length=1, max_length=160)
    duration_seconds: float | None = Field(default=None, ge=0)
    stream_count: int | None = Field(default=None, ge=0, le=10_000)
    error_code: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="after")
    def validate_probe_result(self) -> MediaProbeResult:
        if self.status is MediaProbeStatus.SUCCEEDED:
            if self.format_name is None or self.stream_count is None:
                raise ValueError("successful media probe requires format_name and stream_count")
            if self.error_code is not None:
                raise ValueError("successful media probe must not carry error_code")
        elif self.error_code is None:
            raise ValueError("failed media probe requires error_code")
        return self


class ThreatScanResult(StrictModel):
    status: ThreatScanStatus
    engine: str | None = Field(default=None, min_length=1, max_length=160)
    signature: str | None = Field(default=None, min_length=1, max_length=512)
    error_code: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="after")
    def validate_scan_result(self) -> ThreatScanResult:
        if self.status is ThreatScanStatus.CLEAN:
            if self.signature is not None or self.error_code is not None:
                raise ValueError("clean threat scan must not carry signature or error_code")
        elif self.status is ThreatScanStatus.DETECTED:
            if self.signature is None:
                raise ValueError("detected threat scan requires signature")
            if self.error_code is not None:
                raise ValueError("detected threat scan must not carry error_code")
        elif self.error_code is None:
            raise ValueError("unavailable/error threat scan requires error_code")
        return self


class QuarantineInspection(StrictModel):
    """Security decision for uploaded bytes before any canonical Asset promotion."""

    schema_version: SchemaVersion = SCHEMA_VERSION
    inspection_id: QuarantineInspectionId
    upload_session_id: UploadSessionId
    project_id: ProjectId
    storage_object_id: StorageObjectId
    claimed_mime_type: str = Field(min_length=3, max_length=255)
    detected_mime_type: str | None = Field(default=None, min_length=3, max_length=255)
    expected_size_bytes: int = Field(gt=0)
    observed_size_bytes: int = Field(ge=0)
    status: QuarantineStatus
    rejection_codes: tuple[QuarantineRejectionCode, ...] = ()
    probe: MediaProbeResult | None = None
    threat_scan: ThreatScanResult | None = None
    inspected_at: AwareDatetime | None = None
    audit: AuditFields

    @model_validator(mode="after")
    def validate_terminal_contract(self) -> QuarantineInspection:
        if len(self.rejection_codes) != len(set(self.rejection_codes)):
            raise ValueError("quarantine rejection codes must be unique")
        if self.status in {QuarantineStatus.PENDING, QuarantineStatus.INSPECTING}:
            if self.rejection_codes or self.inspected_at is not None:
                raise ValueError("non-terminal quarantine state cannot carry terminal evidence")
        elif self.inspected_at is None:
            raise ValueError("terminal quarantine state requires inspected_at")
        if self.status is QuarantineStatus.ACCEPTED and self.rejection_codes:
            raise ValueError("accepted quarantine inspection cannot carry rejection codes")
        if self.status is QuarantineStatus.REJECTED and not self.rejection_codes:
            raise ValueError("rejected quarantine inspection requires rejection codes")
        if self.inspected_at is not None and self.inspected_at > self.audit.updated_at:
            raise ValueError("inspected_at cannot exceed audit.updated_at")
        return self


def detect_magic_mime(prefix: bytes) -> str | None:
    """Detect a deliberately small allowlist of high-value media signatures."""

    if prefix.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if prefix.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if prefix.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(prefix) >= 12 and prefix[:4] == b"RIFF" and prefix[8:12] == b"WEBP":
        return "image/webp"
    if len(prefix) >= 12 and prefix[:4] == b"RIFF" and prefix[8:12] == b"WAVE":
        return "audio/wav"
    if prefix.startswith(b"fLaC"):
        return "audio/flac"
    if prefix.startswith(b"OggS"):
        return "audio/ogg"
    if prefix.startswith(b"ID3") or (
        len(prefix) >= 2 and prefix[0] == 0xFF and prefix[1] & 0xE0 == 0xE0
    ):
        return "audio/mpeg"
    if len(prefix) >= 12 and prefix[4:8] == b"ftyp":
        return "video/mp4"
    if prefix.startswith(b"\x1aE\xdf\xa3"):
        return "video/webm"
    if prefix.startswith(b"%PDF-"):
        return "application/pdf"
    return None


def evaluate_quarantine(
    *,
    policy: MediaSecurityPolicy,
    claimed_mime_type: str,
    expected_size_bytes: int,
    observed_size_bytes: int,
    detected_mime_type: str | None,
    probe: MediaProbeResult | None,
    threat_scan: ThreatScanResult | None,
) -> tuple[QuarantineStatus, tuple[QuarantineRejectionCode, ...]]:
    """Evaluate only supplied evidence; callers perform probe/scanner side effects externally."""

    claimed = claimed_mime_type.strip().lower()
    rejections: list[QuarantineRejectionCode] = []

    if observed_size_bytes != expected_size_bytes:
        rejections.append(QuarantineRejectionCode.SIZE_MISMATCH)
    if observed_size_bytes > policy.max_size_bytes:
        rejections.append(QuarantineRejectionCode.SIZE_LIMIT_EXCEEDED)
    if claimed not in policy.allowed_mime_types:
        rejections.append(QuarantineRejectionCode.UNSUPPORTED_MIME)
    if policy.require_magic_match:
        if detected_mime_type is None:
            rejections.append(QuarantineRejectionCode.MAGIC_UNKNOWN)
        elif detected_mime_type != claimed:
            rejections.append(QuarantineRejectionCode.MIME_MISMATCH)

    if policy.requires_probe(claimed):
        if probe is None:
            rejections.append(QuarantineRejectionCode.PROBE_REQUIRED)
        elif probe.status is MediaProbeStatus.FAILED:
            rejections.append(QuarantineRejectionCode.PROBE_FAILED)
        elif probe.status is MediaProbeStatus.TIMED_OUT:
            rejections.append(QuarantineRejectionCode.PROBE_TIMED_OUT)
        elif probe.status is MediaProbeStatus.UNAVAILABLE:
            rejections.append(QuarantineRejectionCode.PROBE_UNAVAILABLE)

    if policy.require_threat_scan:
        if threat_scan is None:
            rejections.append(QuarantineRejectionCode.THREAT_SCAN_UNAVAILABLE)
        elif threat_scan.status is ThreatScanStatus.DETECTED:
            rejections.append(QuarantineRejectionCode.THREAT_DETECTED)
        elif threat_scan.status is ThreatScanStatus.ERROR:
            rejections.append(QuarantineRejectionCode.THREAT_SCAN_ERROR)
        elif threat_scan.status is ThreatScanStatus.UNAVAILABLE:
            rejections.append(QuarantineRejectionCode.THREAT_SCAN_UNAVAILABLE)

    ordered = tuple(dict.fromkeys(rejections))
    if ordered:
        return QuarantineStatus.REJECTED, ordered
    return QuarantineStatus.ACCEPTED, ()
