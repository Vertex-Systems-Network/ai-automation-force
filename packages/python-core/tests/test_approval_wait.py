from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ai_automation_force_core import (
    ApprovalDecision,
    ApprovalWaitKind,
    ApprovalWaitRequest,
    JobStatus,
    expected_wait_status,
    expired_job_status,
    resolved_job_status,
)


def test_approval_wait_state_matrix_is_explicit() -> None:
    assert expected_wait_status(ApprovalWaitKind.HUMAN_APPROVAL) is JobStatus.WAITING_HUMAN
    assert expected_wait_status(ApprovalWaitKind.BUDGET) is JobStatus.BLOCKED_BUDGET
    assert expected_wait_status(ApprovalWaitKind.MANUAL_HANDOFF) is JobStatus.MANUAL_HANDOFF

    for wait_kind in ApprovalWaitKind:
        assert resolved_job_status(wait_kind, ApprovalDecision.APPROVED) is JobStatus.ELIGIBLE
        assert resolved_job_status(wait_kind, ApprovalDecision.WAIVED) is JobStatus.ELIGIBLE
        assert resolved_job_status(wait_kind, ApprovalDecision.REQUEST_CHANGES) is None

    assert (
        resolved_job_status(ApprovalWaitKind.BUDGET, ApprovalDecision.REJECTED)
        is JobStatus.CANCELLED
    )
    assert (
        resolved_job_status(ApprovalWaitKind.HUMAN_APPROVAL, ApprovalDecision.REJECTED)
        is JobStatus.PERMANENT_FAILED
    )
    assert (
        resolved_job_status(ApprovalWaitKind.MANUAL_HANDOFF, ApprovalDecision.REJECTED)
        is JobStatus.PERMANENT_FAILED
    )

    assert expired_job_status(ApprovalWaitKind.HUMAN_APPROVAL) is JobStatus.MANUAL_HANDOFF
    assert expired_job_status(ApprovalWaitKind.BUDGET) is JobStatus.MANUAL_HANDOFF
    assert expired_job_status(ApprovalWaitKind.MANUAL_HANDOFF) is None


def test_approval_wait_request_fingerprint_is_stable_and_semantic() -> None:
    now = datetime(2026, 8, 29, 9, 0, tzinfo=UTC)
    request = ApprovalWaitRequest(
        request_id="AQR-000001",
        project_id="PRJ-000001",
        job_id="JOB-000001",
        wait_kind=ApprovalWaitKind.HUMAN_APPROVAL,
        subject_type="job",
        subject_id="JOB-000001",
        requested_job_revision=5,
        requested_by="workflow",
        requested_at=now,
        idempotency_key="approval-000001",
        expires_at=now + timedelta(minutes=10),
        reason="human review",
    )
    same = ApprovalWaitRequest(**request.__dict__)
    changed = ApprovalWaitRequest(
        **{**request.__dict__, "reason": "budget review"}
    )

    assert request.request_fingerprint == same.request_fingerprint
    assert request.request_fingerprint != changed.request_fingerprint
    assert len(request.request_fingerprint) == 64


def test_approval_wait_request_rejects_invalid_identity_and_expiry() -> None:
    now = datetime(2026, 8, 29, 9, 0, tzinfo=UTC)
    common = {
        "project_id": "PRJ-000001",
        "job_id": "JOB-000001",
        "wait_kind": ApprovalWaitKind.HUMAN_APPROVAL,
        "subject_type": "job",
        "subject_id": "JOB-000001",
        "requested_job_revision": 1,
        "requested_by": "workflow",
        "requested_at": now,
        "idempotency_key": "approval-000001",
    }

    with pytest.raises(ValueError, match="AQR"):
        ApprovalWaitRequest(request_id="APR-000001", **common)
    with pytest.raises(ValueError, match="later"):
        ApprovalWaitRequest(request_id="AQR-000001", expires_at=now, **common)
