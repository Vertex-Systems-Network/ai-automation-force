from __future__ import annotations

import math

import pytest

from ai_automation_force_core import (
    JOB_STATUS_TRANSITIONS,
    TERMINAL_JOB_STATUSES,
    InvalidJobTransitionError,
    JobStatus,
    assert_job_transition,
    operation_fingerprint,
)


def test_operation_fingerprint_is_canonical_and_sensitive_to_semantics() -> None:
    left = operation_fingerprint({"shot": "SHT-000001", "options": {"quality": 2, "fps": 24}})
    reordered = operation_fingerprint(
        {"options": {"fps": 24, "quality": 2}, "shot": "SHT-000001"}
    )
    changed = operation_fingerprint({"shot": "SHT-000001", "options": {"quality": 3, "fps": 24}})

    assert left == reordered
    assert left != changed
    assert len(left) == 64
    assert all(character in "0123456789abcdef" for character in left)


def test_operation_fingerprint_rejects_non_json_numbers() -> None:
    with pytest.raises(ValueError):
        operation_fingerprint({"unsafe": math.nan})


def test_job_transition_matrix_covers_every_status_and_keeps_terminals_closed() -> None:
    assert set(JOB_STATUS_TRANSITIONS) == set(JobStatus)
    assert {
        JobStatus.COMPLETED,
        JobStatus.PERMANENT_FAILED,
        JobStatus.CANCELLED,
    } == TERMINAL_JOB_STATUSES
    for status in TERMINAL_JOB_STATUSES:
        assert JOB_STATUS_TRANSITIONS[status] == frozenset()

    assert_job_transition(JobStatus.QUEUED, JobStatus.ELIGIBLE)
    assert_job_transition(JobStatus.ELIGIBLE, JobStatus.CLAIMED)
    assert_job_transition(JobStatus.CLAIMED, JobStatus.RUNNING)
    assert_job_transition(JobStatus.RUNNING, JobStatus.QA)
    assert_job_transition(JobStatus.QA, JobStatus.COMPLETED)

    with pytest.raises(InvalidJobTransitionError, match="completed -> eligible"):
        assert_job_transition(JobStatus.COMPLETED, JobStatus.ELIGIBLE)
