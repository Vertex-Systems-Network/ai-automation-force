from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from lullabies_core.media_security import (
    MediaProbeResult,
    MediaProbeStatus,
    MediaSecurityPolicy,
    QuarantineInspection,
    QuarantineRejectionCode,
    QuarantineStatus,
    ThreatScanResult,
    ThreatScanStatus,
    detect_magic_mime,
    evaluate_quarantine,
)
from lullabies_core.common import AuditFields


@pytest.fixture
def policy() -> MediaSecurityPolicy:
    return MediaSecurityPolicy(
        allowed_mime_types=("image/png", "video/mp4"),
        max_size_bytes=20_000_000,
    )


def clean_scan() -> ThreatScanResult:
    return ThreatScanResult(status=ThreatScanStatus.CLEAN, engine="fake-scanner")


def successful_probe() -> MediaProbeResult:
    return MediaProbeResult(
        status=MediaProbeStatus.SUCCEEDED,
        format_name="mov,mp4,m4a,3gp,3g2,mj2",
        duration_seconds=4.2,
        stream_count=2,
    )


def test_magic_detection_uses_content_not_filename() -> None:
    assert detect_magic_mime(b"\x89PNG\r\n\x1a\nrest") == "image/png"
    assert detect_magic_mime(b"\x00\x00\x00\x18ftypisomrest") == "video/mp4"
    assert detect_magic_mime(b"<script>alert(1)</script>") is None


def test_matching_image_accepts_without_media_probe(policy: MediaSecurityPolicy) -> None:
    status, rejection_codes = evaluate_quarantine(
        policy=policy,
        claimed_mime_type="image/png",
        expected_size_bytes=12,
        observed_size_bytes=12,
        detected_mime_type="image/png",
        probe=None,
        threat_scan=clean_scan(),
    )

    assert status is QuarantineStatus.ACCEPTED
    assert rejection_codes == ()


def test_video_requires_probe_and_threat_scan(policy: MediaSecurityPolicy) -> None:
    status, rejection_codes = evaluate_quarantine(
        policy=policy,
        claimed_mime_type="video/mp4",
        expected_size_bytes=100,
        observed_size_bytes=100,
        detected_mime_type="video/mp4",
        probe=None,
        threat_scan=None,
    )

    assert status is QuarantineStatus.REJECTED
    assert rejection_codes == (
        QuarantineRejectionCode.PROBE_REQUIRED,
        QuarantineRejectionCode.THREAT_SCAN_UNAVAILABLE,
    )


def test_mime_spoof_size_mismatch_and_threat_detection_fail_closed(
    policy: MediaSecurityPolicy,
) -> None:
    status, rejection_codes = evaluate_quarantine(
        policy=policy,
        claimed_mime_type="video/mp4",
        expected_size_bytes=100,
        observed_size_bytes=101,
        detected_mime_type="image/png",
        probe=successful_probe(),
        threat_scan=ThreatScanResult(
            status=ThreatScanStatus.DETECTED,
            engine="fake-scanner",
            signature="EICAR-Test-Signature",
        ),
    )

    assert status is QuarantineStatus.REJECTED
    assert rejection_codes == (
        QuarantineRejectionCode.SIZE_MISMATCH,
        QuarantineRejectionCode.MIME_MISMATCH,
        QuarantineRejectionCode.THREAT_DETECTED,
    )


def test_probe_timeout_and_scanner_error_fail_closed(policy: MediaSecurityPolicy) -> None:
    status, rejection_codes = evaluate_quarantine(
        policy=policy,
        claimed_mime_type="video/mp4",
        expected_size_bytes=100,
        observed_size_bytes=100,
        detected_mime_type="video/mp4",
        probe=MediaProbeResult(
            status=MediaProbeStatus.TIMED_OUT,
            error_code="probe-timeout",
        ),
        threat_scan=ThreatScanResult(
            status=ThreatScanStatus.ERROR,
            engine="fake-scanner",
            error_code="scanner-failed",
        ),
    )

    assert status is QuarantineStatus.REJECTED
    assert rejection_codes == (
        QuarantineRejectionCode.PROBE_TIMED_OUT,
        QuarantineRejectionCode.THREAT_SCAN_ERROR,
    )


def test_terminal_inspection_contract_cannot_accept_with_rejections() -> None:
    now = datetime(2026, 8, 29, 18, 30, tzinfo=UTC)
    audit = AuditFields(created_at=now, updated_at=now)

    with pytest.raises(ValidationError, match="accepted quarantine inspection"):
        QuarantineInspection(
            inspection_id="QIN-003301",
            upload_session_id="UPS-003301",
            project_id="PRJ-003301",
            storage_object_id="STO-003301",
            claimed_mime_type="image/png",
            detected_mime_type="image/png",
            expected_size_bytes=12,
            observed_size_bytes=12,
            status=QuarantineStatus.ACCEPTED,
            rejection_codes=(QuarantineRejectionCode.MIME_MISMATCH,),
            inspected_at=now,
            audit=audit,
        )
