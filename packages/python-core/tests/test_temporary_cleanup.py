from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from lullabies_core.storage import FilesystemStorageAdapter, StorageBackend
from lullabies_core.storage_s3 import S3StorageAdapter
from lullabies_core.temporary_cleanup import (
    AdapterTemporaryCleanupBackend,
    TemporaryCleanupBackendResult,
    TemporaryCleanupCandidate,
    TemporaryCleanupConflictError,
    TemporaryCleanupExecutor,
)
from lullabies_core.upload_session import UploadMode, UploadSessionStatus, build_upload_object_key


def candidate(
    *,
    status: UploadSessionStatus = UploadSessionStatus.EXPIRED,
    backend: StorageBackend = StorageBackend.FILESYSTEM,
    mode: UploadMode = UploadMode.SINGLE,
    bucket: str | None = None,
    backend_upload_id: str | None = None,
    terminal_at: datetime | None = None,
) -> TemporaryCleanupCandidate:
    project_id = "PRJ-000001"
    storage_object_id = "STO-000001"
    return TemporaryCleanupCandidate(
        upload_session_id="UPS-000001",
        project_id=project_id,
        storage_object_id=storage_object_id,
        backend=backend,
        bucket=bucket,
        object_key=build_upload_object_key(project_id, storage_object_id),
        mode=mode,
        backend_upload_id=backend_upload_id,
        status=status,
        terminal_at=terminal_at or datetime(2026, 9, 5, 8, 0, tzinfo=UTC),
        revision=3,
    )


@dataclass
class FakeRepository:
    current: TemporaryCleanupCandidate
    stale: bool = False
    observed_cutoff: datetime | None = None

    def revalidate(
        self,
        selected: TemporaryCleanupCandidate,
        *,
        cutoff: datetime,
    ) -> TemporaryCleanupCandidate:
        self.observed_cutoff = cutoff
        if self.stale or selected != self.current:
            raise TemporaryCleanupConflictError("stale cleanup candidate")
        return self.current


@dataclass
class FakeBackend:
    calls: list[str] = field(default_factory=list)

    def purge(self, selected: TemporaryCleanupCandidate) -> TemporaryCleanupBackendResult:
        self.calls.append(selected.upload_session_id)
        return TemporaryCleanupBackendResult(
            multipart_abort_attempted=(
                selected.mode is UploadMode.MULTIPART
                and selected.backend_upload_id is not None
            ),
            object_delete_attempted=True,
        )


def test_executor_requires_completed_grace_window() -> None:
    selected = candidate()
    repository = FakeRepository(selected)
    backend = FakeBackend()
    executor = TemporaryCleanupExecutor(repository=repository, backend=backend)

    with pytest.raises(TemporaryCleanupConflictError, match="grace window"):
        executor.execute(
            selected,
            now=datetime(2026, 9, 5, 8, 30, tzinfo=UTC),
            grace_period=timedelta(hours=1),
        )

    assert backend.calls == []
    assert repository.observed_cutoff == datetime(2026, 9, 5, 7, 30, tzinfo=UTC)


def test_executor_revalidates_exact_candidate_before_purge() -> None:
    selected = candidate()
    repository = FakeRepository(selected, stale=True)
    backend = FakeBackend()
    executor = TemporaryCleanupExecutor(repository=repository, backend=backend)

    with pytest.raises(TemporaryCleanupConflictError, match="stale cleanup candidate"):
        executor.execute(
            selected,
            now=datetime(2026, 9, 5, 10, 0, tzinfo=UTC),
            grace_period=timedelta(hours=1),
        )

    assert backend.calls == []


def test_executor_purges_terminal_candidate_after_grace() -> None:
    selected = candidate(status=UploadSessionStatus.ABORTED)
    repository = FakeRepository(selected)
    backend = FakeBackend()
    result = TemporaryCleanupExecutor(repository=repository, backend=backend).execute(
        selected,
        now=datetime(2026, 9, 5, 10, 0, tzinfo=UTC),
        grace_period=timedelta(hours=1),
    )

    assert backend.calls == ["UPS-000001"]
    assert result.status is UploadSessionStatus.ABORTED
    assert result.revision == 3
    assert result.object_delete_attempted is True


def test_candidate_rejects_nonterminal_and_noncanonical_targets() -> None:
    with pytest.raises(ValueError, match="aborted or expired"):
        candidate(status=UploadSessionStatus.COMPLETED)

    with pytest.raises(ValueError, match="canonical quarantine key"):
        TemporaryCleanupCandidate(
            upload_session_id="UPS-000001",
            project_id="PRJ-000001",
            storage_object_id="STO-000001",
            backend=StorageBackend.FILESYSTEM,
            bucket=None,
            object_key="uploads/quarantine/PRJ-000001/STO-999999",
            mode=UploadMode.SINGLE,
            backend_upload_id=None,
            status=UploadSessionStatus.EXPIRED,
            terminal_at=datetime(2026, 9, 5, 8, 0, tzinfo=UTC),
            revision=1,
        )


def test_filesystem_cleanup_is_idempotent(tmp_path: Path) -> None:
    selected = candidate()
    filesystem = FilesystemStorageAdapter(tmp_path)
    filesystem.put_bytes(selected.object_key, b"temporary", mime_type="application/octet-stream")
    backend = AdapterTemporaryCleanupBackend(filesystem=filesystem)

    first = backend.purge(selected)
    second = backend.purge(selected)

    assert first.object_delete_attempted is True
    assert second.object_delete_attempted is True
    assert not (tmp_path / Path(*selected.object_key.split("/"))).exists()


class FakeS3Client:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def abort_multipart_upload(self, **_: object) -> None:
        self.calls.append("abort")


class FakeS3:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.settings = SimpleNamespace(bucket="temp-bucket")
        self.client = FakeS3Client(self.calls)

    def delete(self, _: str) -> None:
        self.calls.append("delete")


def test_s3_multipart_aborts_before_quarantine_delete() -> None:
    selected = candidate(
        backend=StorageBackend.S3,
        bucket="temp-bucket",
        mode=UploadMode.MULTIPART,
        backend_upload_id="upload-123",
    )
    fake_s3 = FakeS3()
    backend = AdapterTemporaryCleanupBackend(s3=cast(S3StorageAdapter, fake_s3))

    result = backend.purge(selected)

    assert fake_s3.calls == ["abort", "delete"]
    assert result.multipart_abort_attempted is True
    assert result.object_delete_attempted is True
