from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urlsplit

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

from .storage import (
    StorageBackend,
    StorageBlobStat,
    StorageConflictError,
    StorageIntegrityError,
    StorageNotFoundError,
    StorageWriteResult,
    sha256_bytes,
    validate_object_key,
)

AddressingStyle = Literal["auto", "path", "virtual"]


@dataclass(frozen=True)
class S3StorageSettings:
    bucket: str
    region_name: str = "us-east-1"
    endpoint_url: str | None = None
    addressing_style: AddressingStyle = "auto"
    verify_ssl: bool = True
    access_key_id: str | None = field(default=None, repr=False)
    secret_access_key: str | None = field(default=None, repr=False)
    session_token: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.bucket.strip() or len(self.bucket) > 255:
            raise ValueError("bucket must be a non-empty storage bucket name")
        if not self.region_name.strip():
            raise ValueError("region_name must be non-empty")
        if (self.access_key_id is None) != (self.secret_access_key is None):
            raise ValueError("access_key_id and secret_access_key must be supplied together")
        if self.endpoint_url is not None:
            parsed = urlsplit(self.endpoint_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("endpoint_url must be an absolute HTTP(S) URL")
            if parsed.username is not None or parsed.password is not None:
                raise ValueError("endpoint_url must not embed credentials")
            if parsed.scheme == "http" and self.verify_ssl:
                # TLS verification is meaningless for HTTP; explicit local insecure mode is required.
                raise ValueError("HTTP endpoint_url requires verify_ssl=False explicitly")


class S3StorageAdapter:
    backend = StorageBackend.S3

    def __init__(
        self,
        settings: S3StorageSettings,
        *,
        client: BaseClient | None = None,
    ) -> None:
        self.settings = settings
        if client is None:
            session = boto3.session.Session(
                aws_access_key_id=settings.access_key_id,
                aws_secret_access_key=settings.secret_access_key,
                aws_session_token=settings.session_token,
                region_name=settings.region_name,
            )
            client = session.client(
                "s3",
                endpoint_url=settings.endpoint_url,
                verify=settings.verify_ssl,
                config=Config(
                    retries={"mode": "standard", "max_attempts": 3},
                    s3={"addressing_style": settings.addressing_style},
                ),
            )
        self.client = client

    @staticmethod
    def _etag(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if len(text) >= 2 and text[0] == text[-1] == '"':
            text = text[1:-1]
        return text or None

    @staticmethod
    def _is_not_found(exc: ClientError) -> bool:
        error = exc.response.get("Error", {})
        code = str(error.get("Code", ""))
        status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        return code in {"404", "NoSuchKey", "NotFound"} or status == 404

    def put_bytes(self, object_key: str, data: bytes, *, mime_type: str) -> StorageWriteResult:
        key = validate_object_key(object_key)
        if not mime_type or "/" not in mime_type:
            raise ValueError("mime_type must be a valid media type")
        digest = sha256_bytes(data)

        try:
            existing = self.stat(key)
        except StorageNotFoundError:
            existing = None
        if existing is not None:
            if existing.sha256 != digest or existing.size_bytes != len(data):
                raise StorageConflictError(f"object key {key} already stores different bytes")
            return StorageWriteResult(
                backend=self.backend,
                bucket=self.settings.bucket,
                object_key=key,
                sha256=digest,
                mime_type=existing.mime_type or mime_type,
                size_bytes=existing.size_bytes,
                region=self.settings.region_name,
                etag=existing.etag,
                version_id=existing.version_id,
            )

        response = self.client.put_object(
            Bucket=self.settings.bucket,
            Key=key,
            Body=data,
            ContentType=mime_type,
            Metadata={"aaf-sha256": digest},
        )
        return StorageWriteResult(
            backend=self.backend,
            bucket=self.settings.bucket,
            object_key=key,
            sha256=digest,
            mime_type=mime_type,
            size_bytes=len(data),
            region=self.settings.region_name,
            etag=self._etag(response.get("ETag")),
            version_id=(str(response["VersionId"]) if response.get("VersionId") else None),
        )

    def get_bytes(self, object_key: str) -> bytes:
        key = validate_object_key(object_key)
        try:
            response = self.client.get_object(Bucket=self.settings.bucket, Key=key)
        except ClientError as exc:
            if self._is_not_found(exc):
                raise StorageNotFoundError(f"object {key} was not found") from exc
            raise
        body = response["Body"]
        try:
            return bytes(body.read())
        finally:
            close = getattr(body, "close", None)
            if callable(close):
                close()

    def stat(self, object_key: str) -> StorageBlobStat:
        key = validate_object_key(object_key)
        try:
            response = self.client.head_object(Bucket=self.settings.bucket, Key=key)
        except ClientError as exc:
            if self._is_not_found(exc):
                raise StorageNotFoundError(f"object {key} was not found") from exc
            raise
        metadata = response.get("Metadata") or {}
        digest = metadata.get("aaf-sha256")
        if digest is not None and (len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest)):
            raise StorageIntegrityError(f"object {key} has malformed canonical SHA-256 metadata")
        return StorageBlobStat(
            backend=self.backend,
            bucket=self.settings.bucket,
            object_key=key,
            size_bytes=int(response["ContentLength"]),
            sha256=digest,
            mime_type=(str(response["ContentType"]) if response.get("ContentType") else None),
            region=self.settings.region_name,
            etag=self._etag(response.get("ETag")),
            version_id=(str(response["VersionId"]) if response.get("VersionId") else None),
            last_modified=response.get("LastModified"),
        )

    def delete(self, object_key: str) -> None:
        key = validate_object_key(object_key)
        self.client.delete_object(Bucket=self.settings.bucket, Key=key)
