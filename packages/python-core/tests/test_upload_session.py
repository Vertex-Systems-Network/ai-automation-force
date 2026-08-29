from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from ai_automation_force_core.upload_session import (
    DirectUploadGrant,
    UploadMode,
    UploadPart,
    UploadSession,
    UploadSessionStatus,
)
from ai_automation_force_core import AuditFields, StorageBackend


def make_session(*, mode: UploadMode = UploadMode.MULTIPART) -> UploadSession:
    now = datetime(2026, 8, 29, 16, 0, tzinfo=UTC)
    return UploadSession(
        upload_session_id="UPS-003001",
        project_id="PRJ-003001",
        storage_object_id="STO-003001",
        backend=StorageBackend.S3,
        bucket="aaf-private",
        object_key="uploads/quarantine/PRJ-003001/STO-003001",
        expected_size_bytes=10,
        expected_mime_type="video/mp4",
        original_filename="clip.mp4",
        mode=mode,
        part_size_bytes=5 if mode is UploadMode.MULTIPART else None,
        quota_reservation_id="quota-003001",
        creation_idempotency_key="create-003001",
        expires_at=now + timedelta(hours=1),
        audit=AuditFields(created_at=now, updated_at=now, created_by="wp2-test"),
    )


def test_single_and_multipart_contracts_fail_closed() -> None:
    single = make_session(mode=UploadMode.SINGLE)
    assert single.part_size_bytes is None

    with pytest.raises(ValidationError, match="single uploads must not define part_size_bytes"):
        UploadSession.model_validate(
            {**single.model_dump(), "part_size_bytes": 5}
        )

    multipart = make_session()
    with pytest.raises(ValidationError, match="multipart uploads require part_size_bytes"):
        UploadSession.model_validate(
            {**multipart.model_dump(), "part_size_bytes": None}
        )


def test_completed_multipart_requires_exact_recorded_bytes() -> None:
    session = make_session()
    first = UploadPart(
        part_number=1,
        size_bytes=5,
        etag="etag-1",
        recorded_at=session.audit.created_at + timedelta(minutes=1),
    )
    with pytest.raises(ValidationError, match="recorded multipart part bytes"):
        UploadSession.model_validate(
            {
                **session.model_dump(),
                "status": UploadSessionStatus.COMPLETED,
                "parts": [first.model_dump()],
                "observed_size_bytes": 10,
                "completed_at": session.audit.created_at + timedelta(minutes=2),
                "audit": {
                    **session.audit.model_dump(),
                    "updated_at": session.audit.created_at + timedelta(minutes=2),
                },
            }
        )


def test_upload_parts_must_be_unique_and_ordered() -> None:
    session = make_session()
    at = session.audit.created_at + timedelta(minutes=1)
    part = UploadPart(part_number=1, size_bytes=5, etag="one", recorded_at=at)
    with pytest.raises(ValidationError, match="part numbers must be unique"):
        UploadSession.model_validate(
            {**session.model_dump(), "parts": [part.model_dump(), part.model_dump()]}
        )

    part_two = UploadPart(part_number=2, size_bytes=5, etag="two", recorded_at=at)
    with pytest.raises(ValidationError, match="part-number order"):
        UploadSession.model_validate(
            {**session.model_dump(), "parts": [part_two.model_dump(), part.model_dump()]}
        )


def test_direct_upload_grant_does_not_mix_post_fields_with_put() -> None:
    now = datetime(2026, 8, 29, 16, 0, tzinfo=UTC)
    with pytest.raises(ValidationError, match="PUT upload grants must not carry form fields"):
        DirectUploadGrant(
            method="PUT",
            url="https://storage.example/upload",
            object_key="uploads/quarantine/PRJ-003001/STO-003001",
            content_type="video/mp4",
            max_size_bytes=10,
            expires_at=now + timedelta(minutes=5),
            form_fields={"key": "unexpected"},
        )
