from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from botocore.exceptions import ClientError

from ai_automation_force_core import (
    AuditFields,
    S3UploadSessionAdapter,
    StorageBackend,
    UploadMode,
    UploadPart,
    UploadSession,
    UploadSessionConflictError,
    build_upload_object_key,
)
from ai_automation_force_core.storage_s3 import S3StorageAdapter, S3StorageSettings


def client_error(code: str, operation: str, *, status: int | None = None) -> ClientError:
    response: dict[str, Any] = {"Error": {"Code": code, "Message": code}}
    if status is not None:
        response["ResponseMetadata"] = {"HTTPStatusCode": status}
    return ClientError(response, operation)


class FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.object_exists = False
        self.complete_raises_no_such_upload = False
        self.final_size = 10

    def generate_presigned_post(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("generate_presigned_post", kwargs))
        return {
            "url": "https://storage.example/upload",
            "fields": {
                "key": str(kwargs["Key"]),
                "Content-Type": str(kwargs["Fields"]["Content-Type"]),
                "policy": "opaque-policy",
            },
        }

    def head_object(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("head_object", kwargs))
        if not self.object_exists:
            raise client_error("404", "HeadObject", status=404)
        return {
            "ContentLength": self.final_size,
            "ETag": '"final-etag"',
            "VersionId": "version-1",
        }

    def create_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("create_multipart_upload", kwargs))
        return {"UploadId": "backend-upload-1"}

    def generate_presigned_url(self, **kwargs: Any) -> str:
        self.calls.append(("generate_presigned_url", kwargs))
        return "https://storage.example/upload-part"

    def complete_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("complete_multipart_upload", kwargs))
        self.object_exists = True
        if self.complete_raises_no_such_upload:
            raise client_error("NoSuchUpload", "CompleteMultipartUpload", status=404)
        return {}

    def abort_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("abort_multipart_upload", kwargs))
        raise client_error("NoSuchUpload", "AbortMultipartUpload", status=404)


def make_session(*, mode: UploadMode) -> UploadSession:
    now = datetime(2026, 8, 29, 17, 0, tzinfo=UTC)
    return UploadSession(
        upload_session_id="UPS-003201",
        project_id="PRJ-003201",
        storage_object_id="STO-003201",
        backend=StorageBackend.S3,
        bucket="aaf-private",
        object_key=build_upload_object_key("PRJ-003201", "STO-003201"),
        expected_size_bytes=10,
        expected_mime_type="video/mp4",
        original_filename="clip.mp4",
        mode=mode,
        part_size_bytes=5 if mode is UploadMode.MULTIPART else None,
        creation_idempotency_key="create-003201",
        expires_at=now + timedelta(hours=1),
        audit=AuditFields(created_at=now, updated_at=now, created_by="wp2-s3-test"),
    )


def adapter(client: FakeS3Client) -> S3UploadSessionAdapter:
    storage = S3StorageAdapter(
        S3StorageSettings(bucket="aaf-private", region_name="us-east-1"),
        client=client,
    )
    return S3UploadSessionAdapter(storage)


def test_direct_grant_binds_exact_key_type_size_and_expiry_without_network() -> None:
    client = FakeS3Client()
    upload = adapter(client)
    session = make_session(mode=UploadMode.SINGLE)
    now = session.audit.created_at

    grant = upload.create_direct_grant(session, now=now, expires_in_seconds=600)

    assert grant.method == "POST"
    assert grant.object_key == session.object_key
    assert grant.content_type == session.expected_mime_type
    assert grant.max_size_bytes == session.expected_size_bytes
    assert grant.expires_at == now + timedelta(seconds=600)
    assert grant.form_fields["key"] == session.object_key

    name, kwargs = client.calls[-1]
    assert name == "generate_presigned_post"
    assert kwargs["Bucket"] == "aaf-private"
    assert kwargs["Key"] == session.object_key
    assert kwargs["Fields"] == {"Content-Type": "video/mp4"}
    assert {"Content-Type": "video/mp4"} in kwargs["Conditions"]
    assert ["content-length-range", 10, 10] in kwargs["Conditions"]
    assert kwargs["ExpiresIn"] == 600


def test_multipart_begin_and_part_grant_bind_backend_identity_exactly() -> None:
    client = FakeS3Client()
    upload = adapter(client)
    session = make_session(mode=UploadMode.MULTIPART)
    now = session.audit.created_at

    upload_id = upload.begin_multipart(session, now=now)
    assert upload_id == "backend-upload-1"
    create_call = next(call for call in client.calls if call[0] == "create_multipart_upload")
    assert create_call[1]["Bucket"] == "aaf-private"
    assert create_call[1]["Key"] == session.object_key
    assert create_call[1]["ContentType"] == "video/mp4"
    assert create_call[1]["Metadata"]["aaf-upload-session-id"] == session.upload_session_id

    bound = session.model_copy(update={"backend_upload_id": upload_id})
    part_grant = upload.create_part_grant(bound, 2, now=now, expires_in_seconds=120)
    assert part_grant.backend_upload_id == upload_id
    assert part_grant.part_number == 2
    presign_call = client.calls[-1]
    assert presign_call[0] == "generate_presigned_url"
    assert presign_call[1]["ClientMethod"] == "upload_part"
    assert presign_call[1]["Params"] == {
        "Bucket": "aaf-private",
        "Key": session.object_key,
        "UploadId": upload_id,
        "PartNumber": 2,
    }
    assert presign_call[1]["HttpMethod"] == "PUT"

    with pytest.raises(UploadSessionConflictError, match="part_number must be between"):
        upload.create_part_grant(bound, 3, now=now)


def test_multipart_begin_refuses_destructive_overwrite() -> None:
    client = FakeS3Client()
    client.object_exists = True
    upload = adapter(client)
    session = make_session(mode=UploadMode.MULTIPART)

    with pytest.raises(UploadSessionConflictError, match="refusing destructive overwrite"):
        upload.begin_multipart(session, now=session.audit.created_at)
    assert all(name != "create_multipart_upload" for name, _ in client.calls)


def test_complete_reconciles_lost_ack_and_verifies_final_size() -> None:
    client = FakeS3Client()
    client.complete_raises_no_such_upload = True
    upload = adapter(client)
    session = make_session(mode=UploadMode.MULTIPART)
    now = session.audit.created_at
    parts = [
        UploadPart(
            part_number=1,
            size_bytes=5,
            etag='"etag-1"',
            recorded_at=now + timedelta(minutes=1),
        ),
        UploadPart(
            part_number=2,
            size_bytes=5,
            etag='"etag-2"',
            recorded_at=now + timedelta(minutes=2),
        ),
    ]
    bound = session.model_copy(
        update={"backend_upload_id": "backend-upload-1", "parts": parts}
    )

    evidence = upload.complete_multipart(bound, now=now + timedelta(minutes=3))
    assert evidence.observed_size_bytes == 10
    assert evidence.observed_etag == "final-etag"
    assert evidence.observed_version_id == "version-1"

    complete_call = next(call for call in client.calls if call[0] == "complete_multipart_upload")
    assert complete_call[1]["MultipartUpload"] == {
        "Parts": [
            {"ETag": '"etag-1"', "PartNumber": 1},
            {"ETag": '"etag-2"', "PartNumber": 2},
        ]
    }

    client.final_size = 11
    with pytest.raises(UploadSessionConflictError, match="size does not match"):
        upload.complete_multipart(bound, now=now + timedelta(minutes=4))


def test_abort_no_such_upload_is_idempotent_and_expired_grants_fail_closed() -> None:
    client = FakeS3Client()
    upload = adapter(client)
    session = make_session(mode=UploadMode.MULTIPART).model_copy(
        update={"backend_upload_id": "backend-upload-1"}
    )
    now = session.audit.created_at

    upload.abort_multipart(session, now=now + timedelta(minutes=1))
    assert any(name == "abort_multipart_upload" for name, _ in client.calls)

    with pytest.raises(UploadSessionConflictError, match="expired"):
        upload.create_part_grant(
            session,
            1,
            now=session.expires_at,
        )
