from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from botocore.exceptions import ClientError
from pydantic import ValidationError

from ai_automation_force_core import (
    AuditFields,
    FilesystemStorageAdapter,
    StorageBackend,
    StorageConflictError,
    StorageNotFoundError,
    StorageObject,
    build_object_key,
    sha256_bytes,
    storage_object_from_write,
    validate_object_key,
)
from ai_automation_force_core.storage_s3 import S3StorageAdapter, S3StorageSettings


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[str, dict[str, Any]] = {}
        self.race_bytes: bytes | None = None

    @staticmethod
    def _not_found(operation: str) -> ClientError:
        return ClientError(
            {
                "Error": {"Code": "NoSuchKey", "Message": "missing"},
                "ResponseMetadata": {"HTTPStatusCode": 404},
            },
            operation,
        )

    @staticmethod
    def _precondition(operation: str) -> ClientError:
        return ClientError(
            {
                "Error": {"Code": "PreconditionFailed", "Message": "exists"},
                "ResponseMetadata": {"HTTPStatusCode": 412},
            },
            operation,
        )

    def head_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        del Bucket
        try:
            row = self.objects[Key]
        except KeyError as exc:
            raise self._not_found("HeadObject") from exc
        return {
            "ContentLength": len(row["data"]),
            "ContentType": row["mime_type"],
            "Metadata": {"aaf-sha256": row["sha256"]},
            "ETag": f'"{row["etag"]}"',
            "VersionId": row["version_id"],
            "LastModified": datetime(2026, 8, 29, tzinfo=UTC),
        }

    def put_object(self, **kwargs: Any) -> dict[str, Any]:
        key = str(kwargs["Key"])
        data = bytes(kwargs["Body"])
        if self.race_bytes is not None:
            competing = self.race_bytes
            self.race_bytes = None
            self._store(key, competing, str(kwargs["ContentType"]))
            raise self._precondition("PutObject")
        if key in self.objects and kwargs.get("IfNoneMatch") == "*":
            raise self._precondition("PutObject")
        self._store(key, data, str(kwargs["ContentType"]))
        row = self.objects[key]
        assert kwargs["Metadata"] == {"aaf-sha256": sha256_bytes(data)}
        assert kwargs["IfNoneMatch"] == "*"
        return {"ETag": f'"{row["etag"]}"', "VersionId": row["version_id"]}

    def _store(self, key: str, data: bytes, mime_type: str) -> None:
        digest = sha256_bytes(data)
        self.objects[key] = {
            "data": data,
            "mime_type": mime_type,
            "sha256": digest,
            "etag": f"etag-{digest[:12]}",
            "version_id": f"version-{digest[:12]}",
        }

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        del Bucket
        try:
            row = self.objects[Key]
        except KeyError as exc:
            raise self._not_found("GetObject") from exc
        return {"Body": BytesIO(row["data"])}

    def delete_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        del Bucket
        self.objects.pop(Key, None)
        return {}


def test_object_key_is_opaque_deterministic_and_path_safe() -> None:
    assert build_object_key(
        "uploads/quarantine",
        "STO-000123",
        project_id="PRJ-000456",
    ) == "uploads/quarantine/PRJ-000456/STO-000123"

    for value in (
        "../escape",
        "safe/../escape",
        "/absolute",
        "trailing/",
        "double//slash",
        "windows\\path",
        " leading",
        "control\x00byte",
    ):
        with pytest.raises(ValueError):
            validate_object_key(value)

    with pytest.raises(ValueError):
        build_object_key("Uploaded Files", "STO-000123")
    with pytest.raises(ValueError):
        build_object_key("source", "STO-invalid")


def test_storage_object_enforces_backend_location_shape() -> None:
    now = datetime.now(UTC)
    audit = AuditFields(created_at=now, updated_at=now)
    digest = sha256_bytes(b"fixture")

    StorageObject(
        storage_object_id="STO-000101",
        backend=StorageBackend.FILESYSTEM,
        object_key="source/STO-000101",
        sha256=digest,
        mime_type="image/png",
        size_bytes=7,
        audit=audit,
    )
    StorageObject(
        storage_object_id="STO-000102",
        backend=StorageBackend.S3,
        bucket="private-media",
        object_key="source/STO-000102",
        sha256=digest,
        mime_type="image/png",
        size_bytes=7,
        audit=audit,
    )

    with pytest.raises(ValidationError):
        StorageObject(
            storage_object_id="STO-000103",
            backend=StorageBackend.S3,
            object_key="source/STO-000103",
            sha256=digest,
            mime_type="image/png",
            size_bytes=7,
            audit=audit,
        )


def test_filesystem_adapter_is_immutable_idempotent_and_root_contained(tmp_path: Path) -> None:
    adapter = FilesystemStorageAdapter(tmp_path / "objects")
    key = build_object_key("source", "STO-000201", project_id="PRJ-000201")
    payload = b"actual canonical bytes"

    created = adapter.put_bytes(key, payload, mime_type="application/octet-stream")
    assert created.sha256 == sha256_bytes(payload)
    assert created.size_bytes == len(payload)
    assert adapter.get_bytes(key) == payload

    reused = adapter.put_bytes(key, payload, mime_type="application/octet-stream")
    assert reused == created
    stat = adapter.stat(key)
    assert stat.sha256 == created.sha256
    assert stat.size_bytes == created.size_bytes
    assert stat.last_modified is not None
    assert stat.last_modified.utcoffset() is not None

    with pytest.raises(StorageConflictError):
        adapter.put_bytes(key, b"different", mime_type="application/octet-stream")

    canonical = storage_object_from_write(
        "STO-000201",
        created,
        project_id="PRJ-000201",
        original_filename="../../user-controlled-name.png",
        audit=AuditFields(
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    )
    assert canonical.object_key == key
    assert canonical.original_filename == "../../user-controlled-name.png"
    assert "user-controlled-name" not in canonical.object_key

    adapter.delete(key)
    adapter.delete(key)
    with pytest.raises(StorageNotFoundError):
        adapter.get_bytes(key)


def test_s3_settings_reject_embedded_credentials_and_make_http_explicit() -> None:
    with pytest.raises(ValueError, match="must not embed credentials"):
        S3StorageSettings(
            bucket="private-media",
            endpoint_url="https://user:pass@s3.example.test",
        )
    with pytest.raises(ValueError, match="verify_ssl=False"):
        S3StorageSettings(
            bucket="private-media",
            endpoint_url="http://127.0.0.1:9090",
        )

    settings = S3StorageSettings(
        bucket="private-media",
        endpoint_url="http://127.0.0.1:9090",
        verify_ssl=False,
        access_key_id="local-key",
        secret_access_key="local-secret",
    )
    assert "local-key" not in repr(settings)
    assert "local-secret" not in repr(settings)


def test_s3_adapter_uses_sha_metadata_and_never_treats_etag_as_content_hash() -> None:
    client = FakeS3Client()
    adapter = S3StorageAdapter(
        S3StorageSettings(bucket="private-media", region_name="test-region"),
        client=client,
    )
    key = "source/PRJ-000301/STO-000301"
    payload = b"s3 canonical bytes"

    created = adapter.put_bytes(key, payload, mime_type="video/mp4")
    assert created.sha256 == sha256_bytes(payload)
    assert created.etag is not None
    assert created.etag != created.sha256
    assert adapter.get_bytes(key) == payload
    assert adapter.stat(key).sha256 == created.sha256

    reused = adapter.put_bytes(key, payload, mime_type="video/mp4")
    assert reused.sha256 == created.sha256
    assert reused.etag == created.etag

    with pytest.raises(StorageConflictError):
        adapter.put_bytes(key, b"changed", mime_type="video/mp4")

    adapter.delete(key)
    with pytest.raises(StorageNotFoundError):
        adapter.stat(key)


def test_s3_conditional_put_reconciles_concurrent_writer_without_overwrite() -> None:
    key = "source/PRJ-000401/STO-000401"
    payload = b"intended"

    same_client = FakeS3Client()
    same_client.race_bytes = payload
    same_adapter = S3StorageAdapter(
        S3StorageSettings(bucket="private-media"),
        client=same_client,
    )
    reused = same_adapter.put_bytes(key, payload, mime_type="image/png")
    assert reused.sha256 == sha256_bytes(payload)

    conflict_client = FakeS3Client()
    conflict_client.race_bytes = b"competing"
    conflict_adapter = S3StorageAdapter(
        S3StorageSettings(bucket="private-media"),
        client=conflict_client,
    )
    with pytest.raises(StorageConflictError):
        conflict_adapter.put_bytes(key, payload, mime_type="image/png")
    assert conflict_client.objects[key]["data"] == b"competing"
