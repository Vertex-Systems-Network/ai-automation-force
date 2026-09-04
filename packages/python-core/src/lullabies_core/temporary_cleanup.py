from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from botocore.exceptions import ClientError

from .storage import FilesystemStorageAdapter, StorageBackend
from .storage_s3 import S3StorageAdapter
from .upload_session import UploadMode, UploadSessionStatus, build_upload_object_key


class TemporaryCleanupError(RuntimeError):
    """Base class for fail-closed temporary cleanup failures."""


class TemporaryCleanupConflictError(TemporaryCleanupError):
    """The cleanup target is stale, unsafe, or no longer eligible."""


@dataclass(frozen=True)
class TemporaryCleanupCandidate:
    upload_session_id: str
    project_id: str
    storage_object_id: str
    backend: StorageBackend
    bucket: str | None
    object_key: str
    mode: UploadMode
    backend_upload_id: str | None
    status: UploadSessionStatus
    terminal_at: datetime
    revision: int

    def __post_init__(self) -> None:
        if self.status not in {UploadSessionStatus.ABORTED, UploadSessionStatus.EXPIRED}:
            raise ValueError("temporary cleanup accepts only aborted or expired upload sessions")
        if self.terminal_at.tzinfo is None or self.terminal_at.utcoffset() is None:
            raise ValueError("temporary cleanup terminal_at must be timezone-aware")
        if self.revision < 1:
            raise ValueError("temporary cleanup revision must be positive")
        expected_key = build_upload_object_key(self.project_id, self.storage_object_id)
        if self.object_key != expected_key:
            raise ValueError("temporary cleanup object_key is not the canonical quarantine key")
        if self.backend is StorageBackend.S3 and self.bucket is None:
            raise ValueError("S3 temporary cleanup candidates require a bucket")
        if self.backend is StorageBackend.FILESYSTEM and self.bucket is not None:
            raise ValueError("filesystem temporary cleanup candidates cannot carry a bucket")
        if self.mode is UploadMode.SINGLE and self.backend_upload_id is not None:
            raise ValueError("single-upload cleanup cannot carry a multipart UploadId")


@dataclass(frozen=True)
class TemporaryCleanupBackendResult:
    multipart_abort_attempted: bool
    object_delete_attempted: bool


@dataclass(frozen=True)
class TemporaryCleanupResult:
    upload_session_id: str
    status: UploadSessionStatus
    revision: int
    multipart_abort_attempted: bool
    object_delete_attempted: bool


class TemporaryCleanupRepository(Protocol):
    def revalidate(
        self,
        candidate: TemporaryCleanupCandidate,
        *,
        cutoff: datetime,
    ) -> TemporaryCleanupCandidate: ...


class TemporaryCleanupBackendExecutor(Protocol):
    def purge(self, candidate: TemporaryCleanupCandidate) -> TemporaryCleanupBackendResult: ...


def temporary_cleanup_cutoff(*, now: datetime, grace_period: timedelta) -> datetime:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("temporary cleanup now must be timezone-aware")
    if grace_period <= timedelta(0):
        raise ValueError("temporary cleanup grace_period must be positive")
    return now - grace_period


@dataclass
class AdapterTemporaryCleanupBackend:
    filesystem: FilesystemStorageAdapter | None = None
    s3: S3StorageAdapter | None = None

    def purge(self, candidate: TemporaryCleanupCandidate) -> TemporaryCleanupBackendResult:
        multipart_abort_attempted = False
        if candidate.backend is StorageBackend.FILESYSTEM:
            if self.filesystem is None:
                raise TemporaryCleanupConflictError(
                    "filesystem cleanup requested without a filesystem adapter"
                )
            if self.filesystem.backend is not StorageBackend.FILESYSTEM:
                raise TemporaryCleanupConflictError("filesystem cleanup adapter has wrong backend")
            self.filesystem.delete(candidate.object_key)
            return TemporaryCleanupBackendResult(
                multipart_abort_attempted=False,
                object_delete_attempted=True,
            )

        if self.s3 is None:
            raise TemporaryCleanupConflictError("S3 cleanup requested without an S3 adapter")
        if candidate.bucket != self.s3.settings.bucket:
            raise TemporaryCleanupConflictError(
                "S3 cleanup candidate bucket does not match the configured adapter"
            )
        if candidate.mode is UploadMode.MULTIPART and candidate.backend_upload_id is not None:
            multipart_abort_attempted = True
            try:
                self.s3.client.abort_multipart_upload(
                    Bucket=candidate.bucket,
                    Key=candidate.object_key,
                    UploadId=candidate.backend_upload_id,
                )
            except ClientError as exc:
                code = str((exc.response.get("Error") or {}).get("Code") or "")
                if code not in {"NoSuchUpload", "404"}:
                    raise
        self.s3.delete(candidate.object_key)
        return TemporaryCleanupBackendResult(
            multipart_abort_attempted=multipart_abort_attempted,
            object_delete_attempted=True,
        )


@dataclass
class TemporaryCleanupExecutor:
    repository: TemporaryCleanupRepository
    backend: TemporaryCleanupBackendExecutor

    def execute(
        self,
        candidate: TemporaryCleanupCandidate,
        *,
        now: datetime,
        grace_period: timedelta,
    ) -> TemporaryCleanupResult:
        cutoff = temporary_cleanup_cutoff(now=now, grace_period=grace_period)
        current = self.repository.revalidate(candidate, cutoff=cutoff)
        if current != candidate:
            raise TemporaryCleanupConflictError(
                "temporary cleanup candidate changed during revalidation"
            )
        if current.terminal_at > cutoff:
            raise TemporaryCleanupConflictError(
                "temporary cleanup candidate has not completed the grace window"
            )
        backend_result = self.backend.purge(current)
        return TemporaryCleanupResult(
            upload_session_id=current.upload_session_id,
            status=current.status,
            revision=current.revision,
            multipart_abort_attempted=backend_result.multipart_abort_attempted,
            object_delete_attempted=backend_result.object_delete_attempted,
        )
