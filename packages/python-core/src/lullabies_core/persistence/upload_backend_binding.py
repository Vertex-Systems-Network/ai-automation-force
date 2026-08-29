from __future__ import annotations

from datetime import datetime

from sqlalchemy import MetaData, select, update
from sqlalchemy.engine import Engine

from ..upload_session import UploadMode, UploadMutationResult, UploadSessionStatus
from ._db import PersistenceNotFoundError, PersistenceReferenceError
from .upload_session import UploadPersistenceConflictError


class PostgresUploadBackendBindingRepository:
    """Atomic binding of an opaque multipart backend UploadId after session reservation."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        key = "core.upload_sessions"
        if key not in metadata.tables:
            raise PersistenceReferenceError("upload_sessions table is not migrated")
        self.sessions = metadata.tables[key]

    def bind(
        self,
        upload_session_id: str,
        backend_upload_id: str,
        *,
        now: datetime,
    ) -> UploadMutationResult:
        if not backend_upload_id or len(backend_upload_id) > 2048:
            raise ValueError("backend_upload_id must contain 1..2048 characters")
        with self.engine.begin() as connection:
            row = connection.execute(
                select(self.sessions)
                .where(self.sessions.c.external_id == upload_session_id)
                .with_for_update()
            ).mappings().one_or_none()
            if row is None:
                raise PersistenceNotFoundError(
                    f"upload session {upload_session_id} was not found"
                )
            status = UploadSessionStatus(str(row["status"]))
            if status in {
                UploadSessionStatus.COMPLETED,
                UploadSessionStatus.ABORTED,
                UploadSessionStatus.EXPIRED,
            }:
                raise UploadPersistenceConflictError(
                    f"cannot bind backend upload id while session is {status.value}"
                )
            if now >= row["expires_at"]:
                revision = int(row["revision"]) + 1
                connection.execute(
                    update(self.sessions)
                    .where(self.sessions.c.id == row["id"])
                    .values(
                        status=UploadSessionStatus.EXPIRED.value,
                        updated_at=now,
                        revision=revision,
                    )
                )
                return UploadMutationResult(
                    action="expired",
                    upload_session_id=upload_session_id,
                    status=UploadSessionStatus.EXPIRED,
                    revision=revision,
                )
            if UploadMode(str(row["mode"])) is not UploadMode.MULTIPART:
                raise UploadPersistenceConflictError(
                    "single upload cannot bind a multipart backend upload id"
                )
            existing = row["backend_upload_id"]
            if existing is not None:
                if str(existing) != backend_upload_id:
                    raise UploadPersistenceConflictError(
                        "multipart session is already bound to a different backend upload id"
                    )
                return UploadMutationResult(
                    action="reused",
                    upload_session_id=upload_session_id,
                    status=status,
                    revision=int(row["revision"]),
                )
            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.sessions)
                .where(self.sessions.c.id == row["id"])
                .values(
                    backend_upload_id=backend_upload_id,
                    updated_at=now,
                    revision=revision,
                )
            )
            return UploadMutationResult(
                action="bound",
                upload_session_id=upload_session_id,
                status=status,
                revision=revision,
            )
