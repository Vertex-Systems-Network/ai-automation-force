from __future__ import annotations

import hashlib
import mimetypes
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Protocol

from pydantic import AwareDatetime, Field, model_validator

from .common import AuditFields, ProjectId, StrictModel, external_id_pattern

StorageObjectId = Annotated[str, Field(pattern=external_id_pattern("STO"))]
_NAMESPACE_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}(?:/[a-z0-9][a-z0-9-]{0,63})*$")
_MAX_KEY_UTF8_BYTES = 1024


class StorageBackend(StrEnum):
    FILESYSTEM = "filesystem"
    S3 = "s3"


class StorageError(RuntimeError):
    """Base class for storage-adapter failures."""


class StorageNotFoundError(StorageError):
    """The requested object does not exist."""


class StorageConflictError(StorageError):
    """A stable object key is already bound to different bytes or metadata."""


class StorageIntegrityError(StorageError):
    """Stored bytes do not satisfy the canonical integrity contract."""


class StorageObject(StrictModel):
    """Canonical physical-object metadata, separate from business Asset identity."""

    storage_object_id: StorageObjectId
    project_id: ProjectId | None = None
    backend: StorageBackend
    bucket: str | None = Field(default=None, min_length=1, max_length=255)
    object_key: str = Field(min_length=1, max_length=1024)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    mime_type: str = Field(min_length=3, max_length=255)
    size_bytes: int = Field(ge=0)
    region: str | None = Field(default=None, min_length=1, max_length=160)
    etag: str | None = Field(default=None, min_length=1, max_length=512)
    version_id: str | None = Field(default=None, min_length=1, max_length=1024)
    original_filename: str | None = Field(default=None, min_length=1, max_length=512)
    audit: AuditFields

    @model_validator(mode="after")
    def validate_location(self) -> StorageObject:
        validate_object_key(self.object_key)
        if self.backend is StorageBackend.S3 and self.bucket is None:
            raise ValueError("S3 storage objects require a bucket")
        if self.backend is StorageBackend.FILESYSTEM and self.bucket is not None:
            raise ValueError("filesystem storage objects must not carry a bucket")
        return self


class StorageWriteResult(StrictModel):
    backend: StorageBackend
    bucket: str | None = None
    object_key: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    mime_type: str = Field(min_length=3, max_length=255)
    size_bytes: int = Field(ge=0)
    region: str | None = None
    etag: str | None = None
    version_id: str | None = None


class StorageBlobStat(StrictModel):
    backend: StorageBackend
    bucket: str | None = None
    object_key: str
    size_bytes: int = Field(ge=0)
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    mime_type: str | None = None
    region: str | None = None
    etag: str | None = None
    version_id: str | None = None
    last_modified: AwareDatetime | None = None


class StorageAdapter(Protocol):
    backend: StorageBackend

    def put_bytes(self, object_key: str, data: bytes, *, mime_type: str) -> StorageWriteResult: ...

    def get_bytes(self, object_key: str) -> bytes: ...

    def stat(self, object_key: str) -> StorageBlobStat: ...

    def delete(self, object_key: str) -> None: ...


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_object_key(value: str) -> str:
    """Validate one canonical S3-style key without converting it into a host path."""

    if value != value.strip() or not value:
        raise ValueError("object key must be non-empty and must not contain edge whitespace")
    if value.startswith("/") or value.endswith("/"):
        raise ValueError("object key must not start or end with a slash")
    if "\\" in value:
        raise ValueError("object key must use forward slashes only")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError("object key must not contain control characters")
    if len(value.encode("utf-8")) > _MAX_KEY_UTF8_BYTES:
        raise ValueError("object key exceeds the 1024-byte UTF-8 limit")
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ValueError("object key contains an unsafe path segment")
    return value


def build_object_key(
    namespace: str,
    storage_object_id: str,
    *,
    project_id: str | None = None,
) -> str:
    """Build an opaque canonical key; filenames never participate in physical paths."""

    if not _NAMESPACE_RE.fullmatch(namespace):
        raise ValueError("namespace must be lower-case slash-separated opaque segments")
    if re.fullmatch(external_id_pattern("STO"), storage_object_id) is None:
        raise ValueError("storage_object_id is invalid")
    parts = [namespace]
    if project_id is not None:
        if re.fullmatch(external_id_pattern("PRJ"), project_id) is None:
            raise ValueError("project_id is invalid")
        parts.append(project_id)
    parts.append(storage_object_id)
    return validate_object_key("/".join(parts))


def storage_object_from_write(
    storage_object_id: str,
    result: StorageWriteResult,
    *,
    audit: AuditFields,
    project_id: str | None = None,
    original_filename: str | None = None,
) -> StorageObject:
    return StorageObject(
        storage_object_id=storage_object_id,
        project_id=project_id,
        backend=result.backend,
        bucket=result.bucket,
        object_key=result.object_key,
        sha256=result.sha256,
        mime_type=result.mime_type,
        size_bytes=result.size_bytes,
        region=result.region,
        etag=result.etag,
        version_id=result.version_id,
        original_filename=original_filename,
        audit=audit,
    )


@dataclass(frozen=True)
class FilesystemStorageAdapter:
    root: Path
    backend: StorageBackend = StorageBackend.FILESYSTEM

    def __post_init__(self) -> None:
        resolved = self.root.expanduser().resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        object.__setattr__(self, "root", resolved)

    def _path(self, object_key: str) -> Path:
        key = validate_object_key(object_key)
        candidate = (self.root / Path(*key.split("/"))).resolve(strict=False)
        if not candidate.is_relative_to(self.root):
            raise StorageIntegrityError("object key escaped the configured storage root")
        return candidate

    def put_bytes(self, object_key: str, data: bytes, *, mime_type: str) -> StorageWriteResult:
        if not mime_type or "/" not in mime_type:
            raise ValueError("mime_type must be a valid media type")
        path = self._path(object_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = sha256_bytes(data)

        if path.exists():
            existing = path.read_bytes()
            if existing != data:
                raise StorageConflictError(f"object key {object_key} already stores different bytes")
        else:
            descriptor, temporary_name = tempfile.mkstemp(prefix=".aaf-write-", dir=path.parent)
            temporary_path = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                try:
                    os.link(temporary_path, path)
                except FileExistsError:
                    existing = path.read_bytes()
                    if existing != data:
                        raise StorageConflictError(
                            f"object key {object_key} raced with different bytes"
                        )
            finally:
                temporary_path.unlink(missing_ok=True)

        return StorageWriteResult(
            backend=self.backend,
            object_key=object_key,
            sha256=digest,
            mime_type=mime_type,
            size_bytes=len(data),
        )

    def get_bytes(self, object_key: str) -> bytes:
        path = self._path(object_key)
        try:
            return path.read_bytes()
        except FileNotFoundError as exc:
            raise StorageNotFoundError(f"object {object_key} was not found") from exc

    def stat(self, object_key: str) -> StorageBlobStat:
        path = self._path(object_key)
        try:
            data = path.read_bytes()
            details = path.stat()
        except FileNotFoundError as exc:
            raise StorageNotFoundError(f"object {object_key} was not found") from exc
        guessed_type, _ = mimetypes.guess_type(object_key)
        return StorageBlobStat(
            backend=self.backend,
            object_key=object_key,
            size_bytes=len(data),
            sha256=sha256_bytes(data),
            mime_type=guessed_type,
            last_modified=datetime.fromtimestamp(details.st_mtime, tz=UTC),
        )

    def delete(self, object_key: str) -> None:
        path = self._path(object_key)
        try:
            path.unlink()
        except FileNotFoundError:
            return
        current = path.parent
        while current != self.root:
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent
