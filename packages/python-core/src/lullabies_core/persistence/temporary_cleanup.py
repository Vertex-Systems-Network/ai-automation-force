from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import MetaData, and_, exists, func, or_, select
from sqlalchemy.engine import Connection, Engine, RowMapping

from ..storage import StorageBackend
from ..temporary_cleanup import (
    TemporaryCleanupCandidate,
    TemporaryCleanupConflictError,
    temporary_cleanup_cutoff,
)
from ..upload_session import UploadMode, UploadSessionStatus
from ._db import PersistenceNotFoundError, PersistenceReferenceError


class PostgresTemporaryCleanupRepository:
    """Read/revalidate bounded abandoned-upload cleanup targets without widening schema."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"upload_sessions", "storage_objects", "projects"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"temporary cleanup tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.uploads = metadata.tables["core.upload_sessions"]
        self.storage = metadata.tables["core.storage_objects"]
        self.projects = metadata.tables["core.projects"]

    def list_candidates(
        self,
        *,
        now: datetime,
        grace_period: timedelta,
        limit: int = 100,
    ) -> list[TemporaryCleanupCandidate]:
        if limit < 1 or limit > 1000:
            raise ValueError("temporary cleanup limit must be between 1 and 1000")
        cutoff = temporary_cleanup_cutoff(now=now, grace_period=grace_period)
        canonical_exists = exists(
            select(self.storage.c.id).where(
                or_(
                    self.storage.c.external_id == self.uploads.c.storage_object_external_id,
                    and_(
                        self.storage.c.backend == self.uploads.c.backend,
                        func.coalesce(self.storage.c.bucket, "")
                        == func.coalesce(self.uploads.c.bucket, ""),
                        self.storage.c.object_key == self.uploads.c.object_key,
                    ),
                )
            )
        )
        statement = (
            select(self.uploads, self.projects.c.external_id.label("project_external_id"))
            .join(self.projects, self.projects.c.id == self.uploads.c.project_id)
            .where(
                self.uploads.c.status.in_(
                    [UploadSessionStatus.ABORTED.value, UploadSessionStatus.EXPIRED.value]
                ),
                self.uploads.c.updated_at <= cutoff,
                ~canonical_exists,
            )
            .order_by(self.uploads.c.updated_at.asc(), self.uploads.c.id.asc())
            .limit(limit)
        )
        with self.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()
        return [self._candidate_from_row(row) for row in rows]

    def revalidate(
        self,
        candidate: TemporaryCleanupCandidate,
        *,
        cutoff: datetime,
    ) -> TemporaryCleanupCandidate:
        if cutoff.tzinfo is None or cutoff.utcoffset() is None:
            raise ValueError("temporary cleanup cutoff must be timezone-aware")
        with self.engine.begin() as connection:
            row = (
                connection.execute(
                    select(
                        self.uploads,
                        self.projects.c.external_id.label("project_external_id"),
                    )
                    .join(self.projects, self.projects.c.id == self.uploads.c.project_id)
                    .where(self.uploads.c.external_id == candidate.upload_session_id)
                    .with_for_update()
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise PersistenceNotFoundError(
                    f"upload session {candidate.upload_session_id} was not found"
                )
            current = self._candidate_from_row(row)
            if current != candidate:
                raise TemporaryCleanupConflictError(
                    "temporary cleanup candidate changed since it was selected"
                )
            if current.terminal_at > cutoff or row["updated_at"] > cutoff:
                raise TemporaryCleanupConflictError(
                    "temporary cleanup candidate has not completed the grace window"
                )
            if self._canonical_storage_exists(connection, row):
                raise TemporaryCleanupConflictError(
                    "temporary cleanup target is now represented by canonical storage metadata"
                )
            return current

    def _canonical_storage_exists(self, connection: Connection, row: RowMapping) -> bool:
        storage_id = connection.execute(
            select(self.storage.c.id)
            .where(
                or_(
                    self.storage.c.external_id == row["storage_object_external_id"],
                    and_(
                        self.storage.c.backend == row["backend"],
                        func.coalesce(self.storage.c.bucket, "")
                        == (row["bucket"] or ""),
                        self.storage.c.object_key == row["object_key"],
                    ),
                )
            )
            .limit(1)
        ).scalar_one_or_none()
        return storage_id is not None

    @staticmethod
    def _candidate_from_row(row: RowMapping) -> TemporaryCleanupCandidate:
        status = UploadSessionStatus(str(row["status"]))
        if status not in {UploadSessionStatus.ABORTED, UploadSessionStatus.EXPIRED}:
            raise TemporaryCleanupConflictError(
                f"upload session is not cleanup-terminal: {status.value}"
            )
        terminal_at = (
            row["aborted_at"]
            if status is UploadSessionStatus.ABORTED
            else row["updated_at"]
        )
        if terminal_at is None:
            raise TemporaryCleanupConflictError("terminal upload session is missing terminal time")
        return TemporaryCleanupCandidate(
            upload_session_id=str(row["external_id"]),
            project_id=str(row["project_external_id"]),
            storage_object_id=str(row["storage_object_external_id"]),
            backend=StorageBackend(str(row["backend"])),
            bucket=str(row["bucket"]) if row["bucket"] is not None else None,
            object_key=str(row["object_key"]),
            mode=UploadMode(str(row["mode"])),
            backend_upload_id=(
                str(row["backend_upload_id"])
                if row["backend_upload_id"] is not None
                else None
            ),
            status=status,
            terminal_at=terminal_at,
            revision=int(row["revision"]),
        )
