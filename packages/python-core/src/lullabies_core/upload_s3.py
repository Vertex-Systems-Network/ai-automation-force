from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import ceil
from typing import Any

from botocore.exceptions import ClientError

from .storage import StorageBackend
from .storage_s3 import S3StorageAdapter
from .upload_session import (
    DirectUploadGrant,
    MultipartPartGrant,
    UploadMode,
    UploadSession,
    UploadSessionConflictError,
    UploadSessionStatus,
)


@dataclass(frozen=True)
class S3UploadCompletionEvidence:
    observed_size_bytes: int
    observed_etag: str | None
    observed_version_id: str | None


class S3UploadSessionAdapter:
    """S3 transfer adapter. Ephemeral signed grants never enter canonical persistence."""

    def __init__(self, storage: S3StorageAdapter) -> None:
        self.storage = storage
        self.client = storage.client
        self.settings = storage.settings

    def create_direct_grant(
        self,
        session: UploadSession,
        *,
        now: datetime,
        expires_in_seconds: int = 900,
    ) -> DirectUploadGrant:
        self._require_session(session, UploadMode.SINGLE, now)
        seconds = self._bounded_expiry_seconds(session, now, expires_in_seconds)
        response: dict[str, Any] = self.client.generate_presigned_post(
            Bucket=self.settings.bucket,
            Key=session.object_key,
            Fields={"Content-Type": session.expected_mime_type},
            Conditions=[
                {"Content-Type": session.expected_mime_type},
                [
                    "content-length-range",
                    session.expected_size_bytes,
                    session.expected_size_bytes,
                ],
            ],
            ExpiresIn=seconds,
        )
        url = response.get("url")
        fields = response.get("fields")
        if not isinstance(url, str) or not url:
            raise UploadSessionConflictError("S3 presigned POST did not return a URL")
        if not isinstance(fields, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in fields.items()
        ):
            raise UploadSessionConflictError("S3 presigned POST returned invalid form fields")
        return DirectUploadGrant(
            method="POST",
            url=url,
            object_key=session.object_key,
            content_type=session.expected_mime_type,
            max_size_bytes=session.expected_size_bytes,
            expires_at=now + timedelta(seconds=seconds),
            form_fields={str(key): str(value) for key, value in fields.items()},
        )

    def begin_multipart(self, session: UploadSession, *, now: datetime) -> str:
        self._require_session(session, UploadMode.MULTIPART, now)
        if session.backend_upload_id is not None:
            return session.backend_upload_id
        try:
            self.client.head_object(Bucket=self.settings.bucket, Key=session.object_key)
        except ClientError as exc:
            if not self._is_not_found(exc):
                raise
        else:
            raise UploadSessionConflictError(
                "multipart destination already exists; refusing destructive overwrite"
            )
        response = self.client.create_multipart_upload(
            Bucket=self.settings.bucket,
            Key=session.object_key,
            ContentType=session.expected_mime_type,
            Metadata={
                "aaf-upload-session-id": session.upload_session_id,
                "aaf-storage-object-id": session.storage_object_id,
                "aaf-expected-size": str(session.expected_size_bytes),
            },
        )
        upload_id = response.get("UploadId")
        if not isinstance(upload_id, str) or not upload_id:
            raise UploadSessionConflictError("S3 did not return a multipart UploadId")
        return upload_id

    def create_part_grant(
        self,
        session: UploadSession,
        part_number: int,
        *,
        now: datetime,
        expires_in_seconds: int = 900,
    ) -> MultipartPartGrant:
        self._require_session(session, UploadMode.MULTIPART, now)
        if session.backend_upload_id is None:
            raise UploadSessionConflictError("multipart UploadId has not been durably bound")
        assert session.part_size_bytes is not None
        max_parts = ceil(session.expected_size_bytes / session.part_size_bytes)
        if part_number < 1 or part_number > max_parts:
            raise UploadSessionConflictError(
                f"part_number must be between 1 and {max_parts} for this session"
            )
        seconds = self._bounded_expiry_seconds(session, now, expires_in_seconds)
        url = self.client.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": self.settings.bucket,
                "Key": session.object_key,
                "UploadId": session.backend_upload_id,
                "PartNumber": part_number,
            },
            ExpiresIn=seconds,
            HttpMethod="PUT",
        )
        if not isinstance(url, str) or not url:
            raise UploadSessionConflictError("S3 did not return a multipart part URL")
        return MultipartPartGrant(
            url=url,
            object_key=session.object_key,
            backend_upload_id=session.backend_upload_id,
            part_number=part_number,
            expires_at=now + timedelta(seconds=seconds),
        )

    def complete_multipart(self, session: UploadSession, *, now: datetime) -> S3UploadCompletionEvidence:
        self._require_session(session, UploadMode.MULTIPART, now)
        if session.backend_upload_id is None:
            raise UploadSessionConflictError("multipart UploadId has not been durably bound")
        if not session.parts:
            raise UploadSessionConflictError("multipart upload has no recorded parts")
        if sum(part.size_bytes for part in session.parts) != session.expected_size_bytes:
            raise UploadSessionConflictError("multipart recorded bytes do not match expected size")
        if any(part.etag is None for part in session.parts):
            raise UploadSessionConflictError("every S3 multipart part requires an ETag")
        parts = [
            {"ETag": part.etag, "PartNumber": part.part_number}
            for part in session.parts
            if part.etag is not None
        ]
        try:
            self.client.complete_multipart_upload(
                Bucket=self.settings.bucket,
                Key=session.object_key,
                UploadId=session.backend_upload_id,
                MultipartUpload={"Parts": parts},
            )
        except ClientError as exc:
            if self._error_code(exc) != "NoSuchUpload":
                raise
            # A network loss after S3 accepted completion can make a retry see NoSuchUpload.
            # Exact destination ownership was established at session creation, so reconcile
            # against the final object instead of blindly creating a second multipart upload.
        return self._head_completion(session)

    def abort_multipart(self, session: UploadSession, *, now: datetime) -> None:
        self._require_session(session, UploadMode.MULTIPART, now, allow_terminal=True)
        if session.backend_upload_id is None:
            return
        try:
            self.client.abort_multipart_upload(
                Bucket=self.settings.bucket,
                Key=session.object_key,
                UploadId=session.backend_upload_id,
            )
        except ClientError as exc:
            if self._error_code(exc) != "NoSuchUpload":
                raise

    def _head_completion(self, session: UploadSession) -> S3UploadCompletionEvidence:
        response = self.client.head_object(Bucket=self.settings.bucket, Key=session.object_key)
        observed_size = int(response["ContentLength"])
        if observed_size != session.expected_size_bytes:
            raise UploadSessionConflictError(
                "S3 completed object size does not match upload-session expectation"
            )
        return S3UploadCompletionEvidence(
            observed_size_bytes=observed_size,
            observed_etag=self.storage._etag(response.get("ETag")),
            observed_version_id=(
                str(response["VersionId"]) if response.get("VersionId") else None
            ),
        )

    def _require_session(
        self,
        session: UploadSession,
        mode: UploadMode,
        now: datetime,
        *,
        allow_terminal: bool = False,
    ) -> None:
        if session.backend is not StorageBackend.S3:
            raise UploadSessionConflictError("S3 upload adapter requires an S3 session")
        if session.bucket != self.settings.bucket:
            raise UploadSessionConflictError("upload session bucket does not match adapter bucket")
        if session.mode is not mode:
            raise UploadSessionConflictError(f"upload session is not {mode.value} mode")
        if now >= session.expires_at:
            raise UploadSessionConflictError("upload session is expired")
        if not allow_terminal and session.status in {
            UploadSessionStatus.COMPLETED,
            UploadSessionStatus.ABORTED,
            UploadSessionStatus.EXPIRED,
        }:
            raise UploadSessionConflictError(
                f"upload session is terminal: {session.status.value}"
            )

    @staticmethod
    def _bounded_expiry_seconds(
        session: UploadSession,
        now: datetime,
        requested_seconds: int,
    ) -> int:
        if requested_seconds < 1 or requested_seconds > 3600:
            raise ValueError("signed upload expiry must be between 1 and 3600 seconds")
        remaining = int((session.expires_at - now).total_seconds())
        seconds = min(requested_seconds, remaining)
        if seconds < 1:
            raise UploadSessionConflictError("upload session expires before grant can be issued")
        return seconds

    @staticmethod
    def _error_code(exc: ClientError) -> str:
        return str(exc.response.get("Error", {}).get("Code", ""))

    @classmethod
    def _is_not_found(cls, exc: ClientError) -> bool:
        code = cls._error_code(exc)
        status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        return code in {"404", "NoSuchKey", "NotFound"} or status == 404
