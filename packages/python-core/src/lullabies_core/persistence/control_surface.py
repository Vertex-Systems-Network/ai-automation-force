from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, and_, insert, or_, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import JobStatus
from ..control_surface import (
    JobCommandConflictError,
    JobCommandResult,
    JobCommandVersionConflictError,
    JobControlSnapshot,
    JobEventRecord,
    ProjectJobRecord,
)
from ..job_control import TERMINAL_JOB_STATUSES, assert_job_transition, operation_fingerprint
from ._db import PersistenceNotFoundError, PersistenceReferenceError

MutatingCommand = Literal["cancel", "retry"]


class PostgresControlSurfaceRepository:
    """Provider-neutral read/control boundary for the M02 job API and durable SSE feed."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "jobs",
            "projects",
            "shots",
            "contents",
            "job_dependencies",
            "outbox_messages",
            "workflow_executions",
            "job_commands",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                "control-surface persistence tables are not migrated: "
                + ", ".join(sorted(missing))
            )
        self.jobs = metadata.tables["core.jobs"]
        self.projects = metadata.tables["core.projects"]
        self.shots = metadata.tables["core.shots"]
        self.contents = metadata.tables["core.contents"]
        self.dependencies = metadata.tables["core.job_dependencies"]
        self.outbox = metadata.tables["core.outbox_messages"]
        self.workflows = metadata.tables["core.workflow_executions"]
        self.commands = metadata.tables["core.job_commands"]

    def load_job(self, job_id: str) -> JobControlSnapshot:
        with self.engine.connect() as connection:
            row = self._require_job(connection, job_id)
            return self._snapshot(connection, row)

    def load_job_checkpoint(
        self,
        job_id: str,
    ) -> tuple[JobControlSnapshot, JobEventRecord | None]:
        """Read a job plus an event high-water that cannot skip a newer job revision."""

        with self.engine.connect() as connection:
            row = self._require_job(connection, job_id)
            snapshot = self._snapshot(connection, row)
            event_row = connection.execute(
                select(self.outbox)
                .where(
                    self.outbox.c.job_id == row["id"],
                    self.outbox.c.job_revision <= int(row["revision"]),
                )
                .order_by(self.outbox.c.occurred_at.desc(), self.outbox.c.id.desc())
                .limit(1)
            ).mappings().one_or_none()
            event = self._event(job_id, event_row) if event_row is not None else None
            return snapshot, event

    def list_project_jobs(
        self,
        project_id: str,
        *,
        after: tuple[datetime, str] | None = None,
        limit: int = 50,
    ) -> list[ProjectJobRecord]:
        if limit < 1 or limit > 500:
            raise ValueError("project job limit must be between 1 and 500")
        with self.engine.connect() as connection:
            project_internal = connection.execute(
                select(self.projects.c.id).where(self.projects.c.external_id == project_id)
            ).scalar_one_or_none()
            if project_internal is None:
                raise PersistenceNotFoundError(f"project {project_id} was not found")
            statement = select(self.jobs).where(self.jobs.c.project_id == project_internal)
            if after is not None:
                after_time, after_job_id = after
                statement = statement.where(
                    or_(
                        self.jobs.c.created_at > after_time,
                        and_(
                            self.jobs.c.created_at == after_time,
                            self.jobs.c.external_id > after_job_id,
                        ),
                    )
                )
            rows = connection.execute(
                statement.order_by(self.jobs.c.created_at, self.jobs.c.external_id).limit(limit)
            ).mappings()
            return [
                ProjectJobRecord(
                    job_id=str(row["external_id"]),
                    status=JobStatus(str(row["status"])),
                    job_type=str(row["job_type"]),
                    priority=int(row["priority"]),
                    revision=int(row["revision"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

    def list_job_events(
        self,
        job_id: str,
        *,
        after: tuple[datetime, UUID] | None = None,
        limit: int = 100,
    ) -> list[JobEventRecord]:
        if limit < 1 or limit > 500:
            raise ValueError("event limit must be between 1 and 500")
        with self.engine.connect() as connection:
            job = self._require_job(connection, job_id)
            statement = select(self.outbox).where(self.outbox.c.job_id == job["id"])
            if after is not None:
                after_time, after_id = after
                statement = statement.where(
                    or_(
                        self.outbox.c.occurred_at > after_time,
                        and_(
                            self.outbox.c.occurred_at == after_time,
                            self.outbox.c.id > after_id,
                        ),
                    )
                )
            rows = connection.execute(
                statement.order_by(self.outbox.c.occurred_at, self.outbox.c.id).limit(limit)
            ).mappings()
            return [self._event(job_id, row) for row in rows]

    def cancel_job(
        self,
        job_id: str,
        *,
        idempotency_key: str,
        expected_revision: int,
        now: datetime,
    ) -> JobCommandResult:
        return self._mutate_job(
            job_id,
            command_type="cancel",
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
            now=now,
        )

    def retry_job(
        self,
        job_id: str,
        *,
        idempotency_key: str,
        expected_revision: int,
        now: datetime,
    ) -> JobCommandResult:
        return self._mutate_job(
            job_id,
            command_type="retry",
            idempotency_key=idempotency_key,
            expected_revision=expected_revision,
            now=now,
        )

    def load_start_command(
        self,
        job_id: str,
        *,
        idempotency_key: str,
        operation: Mapping[str, Any],
    ) -> JobCommandResult | None:
        """Return an existing semantically identical start before touching Temporal."""

        self._validate_idempotency_key(idempotency_key)
        fingerprint = self._command_fingerprint("start", job_id, operation)
        with self.engine.connect() as connection:
            job = self._require_job(connection, job_id)
            existing = self._command_by_key(connection, job["id"], idempotency_key)
            if existing is None:
                return None
            return self._reuse_command(existing, "start", fingerprint)

    def record_start(
        self,
        job_id: str,
        *,
        idempotency_key: str,
        workflow_execution_id: str,
        operation: Mapping[str, Any],
        now: datetime,
    ) -> JobCommandResult:
        self._validate_idempotency_key(idempotency_key)
        fingerprint = self._command_fingerprint("start", job_id, operation)
        try:
            with self.engine.begin() as connection:
                job = self._require_job_for_update(connection, job_id)
                existing = self._command_by_key(connection, job["id"], idempotency_key)
                if existing is not None:
                    return self._reuse_command(existing, "start", fingerprint)
                current = JobStatus(str(job["status"]))
                if current in TERMINAL_JOB_STATUSES:
                    raise JobCommandConflictError(
                        f"job {job_id} cannot start from terminal state {current.value}"
                    )
                result = JobCommandResult(
                    action="applied",
                    command_type="start",
                    job_id=job_id,
                    status=current,
                    revision=int(job["revision"]),
                    operation_fingerprint=fingerprint,
                    workflow_execution_id=workflow_execution_id,
                    occurred_at=now,
                )
                self._insert_command(connection, job["id"], idempotency_key, result)
                return result
        except IntegrityError as exc:
            raise JobCommandConflictError(f"database rejected start command: {exc.orig}") from exc

    def _mutate_job(
        self,
        job_id: str,
        *,
        command_type: MutatingCommand,
        idempotency_key: str,
        expected_revision: int,
        now: datetime,
    ) -> JobCommandResult:
        self._validate_idempotency_key(idempotency_key)
        if expected_revision < 1:
            raise ValueError("expected_revision must be at least 1")
        fingerprint = operation_fingerprint(
            {
                "command": command_type,
                "job_id": job_id,
                "expected_revision": expected_revision,
            }
        )
        try:
            with self.engine.begin() as connection:
                job = self._require_job_for_update(connection, job_id)
                existing = self._command_by_key(connection, job["id"], idempotency_key)
                if existing is not None:
                    return self._reuse_command(existing, command_type, fingerprint)

                current_revision = int(job["revision"])
                current = JobStatus(str(job["status"]))
                if command_type == "cancel" and current is JobStatus.CANCELLED:
                    result = JobCommandResult(
                        action="noop",
                        command_type="cancel",
                        job_id=job_id,
                        status=current,
                        revision=current_revision,
                        operation_fingerprint=fingerprint,
                        occurred_at=now,
                    )
                    self._insert_command(connection, job["id"], idempotency_key, result)
                    return result

                if current_revision != expected_revision:
                    message = (
                        f"stale job revision: expected {expected_revision}, "
                        f"current {current_revision}"
                    )
                    raise JobCommandVersionConflictError(message)

                if command_type == "cancel":
                    if current in TERMINAL_JOB_STATUSES:
                        raise JobCommandConflictError(
                            f"job {job_id} cannot cancel from terminal state {current.value}"
                        )
                    target = JobStatus.CANCELLED
                    assert_job_transition(current, target)
                    retry_budget = int(job["retry_budget_remaining"])
                    event_type = "job.status.changed"
                else:
                    if current is not JobStatus.RETRYABLE_FAILED:
                        raise JobCommandConflictError(
                            f"job {job_id} cannot retry from state {current.value}"
                        )
                    retry_budget = int(job["retry_budget_remaining"])
                    if retry_budget < 1:
                        raise JobCommandConflictError(f"job {job_id} retry budget is exhausted")
                    target = JobStatus.ELIGIBLE
                    assert_job_transition(current, target)
                    retry_budget -= 1
                    event_type = "job.retry.requested"

                new_revision = current_revision + 1
                update_result = connection.execute(
                    update(self.jobs)
                    .where(
                        self.jobs.c.id == job["id"],
                        self.jobs.c.revision == current_revision,
                    )
                    .values(
                        status=target.value,
                        retry_budget_remaining=retry_budget,
                        blocked_reason=None,
                        claimed_by=None,
                        lease_expires_at=None,
                        updated_at=now,
                        revision=new_revision,
                    )
                )
                if update_result.rowcount != 1:
                    raise JobCommandVersionConflictError(
                        "job revision changed during control command"
                    )
                self._insert_outbox(
                    connection,
                    job["id"],
                    job_id,
                    new_revision,
                    event_type,
                    now,
                    {
                        "job_id": job_id,
                        "previous_status": current.value,
                        "status": target.value,
                        "revision": new_revision,
                        "command": command_type,
                    },
                )
                result = JobCommandResult(
                    action="applied",
                    command_type=command_type,
                    job_id=job_id,
                    status=target,
                    revision=new_revision,
                    operation_fingerprint=fingerprint,
                    occurred_at=now,
                )
                self._insert_command(connection, job["id"], idempotency_key, result)
                return result
        except IntegrityError as exc:
            raise JobCommandConflictError(
                f"database rejected {command_type} command: {exc.orig}"
            ) from exc

    def _snapshot(self, connection: Connection, row: RowMapping) -> JobControlSnapshot:
        project_id = self._external_for_internal(connection, self.projects, row["project_id"])
        assert project_id is not None
        dependencies = list(
            connection.execute(
                select(self.jobs.c.external_id)
                .select_from(
                    self.dependencies.join(
                        self.jobs,
                        self.dependencies.c.dependency_job_id == self.jobs.c.id,
                    )
                )
                .where(self.dependencies.c.job_id == row["id"])
                .order_by(self.dependencies.c.position)
            ).scalars()
        )
        workflow_execution_id = connection.execute(
            select(self.workflows.c.external_id)
            .where(self.workflows.c.job_id == row["id"])
            .order_by(self.workflows.c.started_at.desc(), self.workflows.c.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        return JobControlSnapshot(
            job_id=str(row["external_id"]),
            project_id=project_id,
            job_type=str(row["job_type"]),
            status=JobStatus(str(row["status"])),
            priority=int(row["priority"]),
            idempotency_key=str(row["idempotency_key"]),
            operation_fingerprint=(
                str(row["operation_fingerprint"])
                if row["operation_fingerprint"] is not None
                else None
            ),
            parent_job_id=self._external_for_internal(connection, self.jobs, row["parent_job_id"]),
            dependency_job_ids=[str(value) for value in dependencies],
            shot_id=self._external_for_internal(connection, self.shots, row["shot_id"]),
            content_id=self._external_for_internal(connection, self.contents, row["content_id"]),
            retry_budget_remaining=int(row["retry_budget_remaining"]),
            blocked_reason=(str(row["blocked_reason"]) if row["blocked_reason"] else None),
            claimed_by=(str(row["claimed_by"]) if row["claimed_by"] else None),
            lease_expires_at=row["lease_expires_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            revision=int(row["revision"]),
            workflow_execution_id=(
                str(workflow_execution_id) if workflow_execution_id is not None else None
            ),
        )

    @staticmethod
    def _event(job_id: str, row: RowMapping) -> JobEventRecord:
        payload = row["payload"]
        if not isinstance(payload, dict):
            payload = dict(payload)
        return JobEventRecord(
            event_id=row["id"],
            job_id=job_id,
            job_revision=int(row["job_revision"]),
            event_type=str(row["event_type"]),
            payload=cast(dict[str, Any], payload),
            occurred_at=row["occurred_at"],
            published_at=row["published_at"],
        )

    def _require_job(self, connection: Connection, job_id: str) -> RowMapping:
        row = connection.execute(
            select(self.jobs).where(self.jobs.c.external_id == job_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"job {job_id} was not found")
        return row

    def _require_job_for_update(self, connection: Connection, job_id: str) -> RowMapping:
        row = connection.execute(
            select(self.jobs)
            .where(self.jobs.c.external_id == job_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"job {job_id} was not found")
        return row

    def _command_by_key(
        self,
        connection: Connection,
        job_internal_id: UUID,
        idempotency_key: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.commands).where(
                self.commands.c.job_id == job_internal_id,
                self.commands.c.idempotency_key == idempotency_key,
            )
        ).mappings().one_or_none()

    @staticmethod
    def _reuse_command(
        row: RowMapping,
        command_type: Literal["start", "cancel", "retry"],
        fingerprint: str,
    ) -> JobCommandResult:
        if row["command_type"] != command_type or row["operation_fingerprint"] != fingerprint:
            raise JobCommandConflictError(
                "idempotency key is already bound to different control-command semantics"
            )
        payload = row["result"]
        if not isinstance(payload, Mapping):
            raise JobCommandConflictError("persisted command result is malformed")
        restored = dict(payload)
        restored["action"] = "reused"
        restored["occurred_at"] = row["occurred_at"]
        return JobCommandResult.model_validate(restored)

    def _insert_command(
        self,
        connection: Connection,
        job_internal_id: UUID,
        idempotency_key: str,
        result: JobCommandResult,
    ) -> None:
        stored = result.model_dump(mode="json")
        stored.pop("action", None)
        stored.pop("occurred_at", None)
        connection.execute(
            insert(self.commands).values(
                id=uuid4(),
                job_id=job_internal_id,
                command_type=result.command_type,
                idempotency_key=idempotency_key,
                operation_fingerprint=result.operation_fingerprint,
                result=stored,
                occurred_at=result.occurred_at,
            )
        )

    def _insert_outbox(
        self,
        connection: Connection,
        job_internal_id: UUID,
        job_external_id: str,
        revision: int,
        event_type: str,
        occurred_at: datetime,
        payload: dict[str, Any],
    ) -> None:
        connection.execute(
            insert(self.outbox).values(
                id=uuid4(),
                job_id=job_internal_id,
                job_revision=revision,
                event_type=event_type,
                dedupe_key=f"job:{job_external_id}:revision:{revision}:{event_type}",
                payload=payload,
                occurred_at=occurred_at,
                published_at=None,
            )
        )

    @staticmethod
    def _command_fingerprint(
        command_type: Literal["start"],
        job_id: str,
        operation: Mapping[str, Any],
    ) -> str:
        return operation_fingerprint(
            {
                "command": command_type,
                "job_id": job_id,
                "operation": dict(operation),
            }
        )

    @staticmethod
    def _validate_idempotency_key(value: str) -> None:
        if not 8 <= len(value) <= 200:
            raise ValueError("idempotency key length must be between 8 and 200")
        if any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("idempotency key must not contain control characters")

    @staticmethod
    def _external_for_internal(
        connection: Connection,
        table: Any,
        internal_id: UUID | None,
    ) -> str | None:
        if internal_id is None:
            return None
        value = connection.execute(
            select(table.c.external_id).where(table.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(
                f"missing external identity for internal row {internal_id}"
            )
        return str(value)
