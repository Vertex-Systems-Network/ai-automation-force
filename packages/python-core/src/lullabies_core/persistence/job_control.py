from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import JobStatus
from ..job_control import (
    InvalidJobTransitionError,
    JobLeaseResult,
    JobSubmitResult,
    JobTransitionResult,
    assert_job_transition,
    operation_fingerprint,
)
from ..production import Job
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError


class JobIdempotencyConflictError(PersistenceConflictError):
    """An idempotency key was reused for different operation semantics."""


class JobVersionConflictError(PersistenceConflictError):
    """The caller attempted to mutate a stale job revision."""


class JobLeaseConflictError(PersistenceConflictError):
    """A job lease is active, expired, missing or owned by another worker."""


class JobStateConflictError(PersistenceConflictError):
    """The requested job lifecycle operation is invalid for the current state."""


class PostgresJobControlRepository:
    """Transactional M02 job lifecycle, idempotency and outbox boundary."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "jobs",
            "projects",
            "contents",
            "shots",
            "scenes",
            "sequences",
            "acts",
            "job_dependencies",
            "outbox_messages",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"job-control persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.jobs = metadata.tables["core.jobs"]
        self.projects = metadata.tables["core.projects"]
        self.contents = metadata.tables["core.contents"]
        self.shots = metadata.tables["core.shots"]
        self.scenes = metadata.tables["core.scenes"]
        self.sequences = metadata.tables["core.sequences"]
        self.acts = metadata.tables["core.acts"]
        self.dependencies = metadata.tables["core.job_dependencies"]
        self.outbox = metadata.tables["core.outbox_messages"]

    def submit(self, job: Job, operation: Mapping[str, Any]) -> JobSubmitResult:
        if job.status is not JobStatus.QUEUED:
            raise JobStateConflictError("new jobs must start in queued state")
        if job.attempt_ids or job.selected_attempt_id is not None:
            raise JobStateConflictError("new jobs cannot already reference generation attempts")
        if job.claimed_by is not None or job.lease_expires_at is not None:
            raise JobStateConflictError("new jobs cannot already hold a worker lease")

        fingerprint = operation_fingerprint(operation)
        try:
            with self.engine.begin() as connection:
                project = self._require_external(
                    connection,
                    self.projects,
                    job.project_id,
                    "project",
                )
                existing = self._row_by_idempotency(
                    connection,
                    project["id"],
                    job.idempotency_key,
                )
                if existing is not None:
                    if existing["operation_fingerprint"] == fingerprint:
                        return JobSubmitResult(
                            "reused",
                            str(existing["external_id"]),
                            fingerprint,
                            int(existing["revision"]),
                        )
                    raise JobIdempotencyConflictError(
                        "idempotency key is already bound to a different operation fingerprint"
                    )

                parent_internal = self._optional_job_in_project(
                    connection,
                    job.parent_job_id,
                    project["id"],
                    "parent job",
                )
                content_internal = self._optional_content_in_project(
                    connection,
                    job.content_id,
                    project["id"],
                )
                shot_internal = self._optional_shot_in_project(
                    connection,
                    job.shot_id,
                    project["id"],
                )
                dependency_internal = [
                    self._require_job_in_project(
                        connection,
                        value,
                        project["id"],
                        "dependency job",
                    )
                    for value in job.dependency_job_ids
                ]

                internal_id = uuid4()
                connection.execute(
                    insert(self.jobs).values(
                        id=internal_id,
                        external_id=job.job_id,
                        schema_version=job.schema_version,
                        project_id=project["id"],
                        job_type=job.job_type,
                        status=job.status.value,
                        priority=job.priority,
                        idempotency_key=job.idempotency_key,
                        operation_fingerprint=fingerprint,
                        parent_job_id=parent_internal,
                        shot_id=shot_internal,
                        content_id=content_internal,
                        selected_attempt_id=None,
                        retry_budget_remaining=job.retry_budget_remaining,
                        blocked_reason=job.blocked_reason,
                        claimed_by=None,
                        lease_expires_at=None,
                        created_at=job.audit.created_at,
                        updated_at=job.audit.updated_at,
                        created_by=job.audit.created_by,
                        revision=job.audit.revision,
                    )
                )
                for position, dependency_id in enumerate(dependency_internal):
                    connection.execute(
                        insert(self.dependencies).values(
                            job_id=internal_id,
                            dependency_job_id=dependency_id,
                            position=position,
                        )
                    )
                self._insert_outbox(
                    connection,
                    internal_id,
                    job.job_id,
                    job.audit.revision,
                    "job.created",
                    job.audit.created_at,
                    {
                        "job_id": job.job_id,
                        "project_id": job.project_id,
                        "status": job.status.value,
                        "revision": job.audit.revision,
                    },
                )
                return JobSubmitResult(
                    "created",
                    job.job_id,
                    fingerprint,
                    job.audit.revision,
                )
        except (JobIdempotencyConflictError, JobStateConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(f"database rejected job submission: {exc.orig}") from exc

    def claim(
        self,
        job_id: str,
        *,
        owner: str,
        now: datetime,
        lease_for: timedelta,
        expected_revision: int,
    ) -> JobLeaseResult:
        owner = owner.strip()
        if not owner:
            raise ValueError("lease owner must not be blank")
        if lease_for <= timedelta(0):
            raise ValueError("lease duration must be positive")

        with self.engine.begin() as connection:
            row = self._require_job_for_update(connection, job_id)
            self._require_revision(row, expected_revision)
            current = JobStatus(str(row["status"]))
            if current is not JobStatus.ELIGIBLE:
                raise JobStateConflictError(
                    f"job {job_id} cannot be claimed from {current.value}; eligible is required"
                )
            try:
                assert_job_transition(current, JobStatus.CLAIMED)
            except InvalidJobTransitionError as exc:
                raise JobStateConflictError(str(exc)) from exc

            new_revision = expected_revision + 1
            expires_at = now + lease_for
            self._cas_update(
                connection,
                row,
                expected_revision,
                {
                    "status": JobStatus.CLAIMED.value,
                    "claimed_by": owner,
                    "lease_expires_at": expires_at,
                    "updated_at": now,
                    "revision": new_revision,
                },
            )
            self._insert_outbox(
                connection,
                row["id"],
                job_id,
                new_revision,
                "job.claimed",
                now,
                {
                    "job_id": job_id,
                    "claimed_by": owner,
                    "lease_expires_at": expires_at.isoformat(),
                    "revision": new_revision,
                },
            )
            return JobLeaseResult(job_id, new_revision, owner, expires_at)

    def renew_lease(
        self,
        job_id: str,
        *,
        owner: str,
        now: datetime,
        lease_for: timedelta,
        expected_revision: int,
    ) -> JobLeaseResult:
        owner = owner.strip()
        if not owner:
            raise ValueError("lease owner must not be blank")
        if lease_for <= timedelta(0):
            raise ValueError("lease duration must be positive")

        with self.engine.begin() as connection:
            row = self._require_job_for_update(connection, job_id)
            self._require_revision(row, expected_revision)
            current = JobStatus(str(row["status"]))
            if current not in {JobStatus.CLAIMED, JobStatus.RUNNING}:
                raise JobLeaseConflictError(
                    f"job {job_id} has no renewable lease in state {current.value}"
                )
            if row["claimed_by"] != owner:
                raise JobLeaseConflictError(f"job {job_id} is leased by another owner")
            current_expiry = row["lease_expires_at"]
            if current_expiry is None or current_expiry <= now:
                raise JobLeaseConflictError(f"job {job_id} lease has expired")

            new_revision = expected_revision + 1
            expires_at = now + lease_for
            self._cas_update(
                connection,
                row,
                expected_revision,
                {
                    "lease_expires_at": expires_at,
                    "updated_at": now,
                    "revision": new_revision,
                },
            )
            return JobLeaseResult(job_id, new_revision, owner, expires_at)

    def recover_expired_lease(
        self,
        job_id: str,
        *,
        now: datetime,
        expected_revision: int,
    ) -> JobTransitionResult:
        with self.engine.begin() as connection:
            row = self._require_job_for_update(connection, job_id)
            self._require_revision(row, expected_revision)
            current = JobStatus(str(row["status"]))
            if current not in {JobStatus.CLAIMED, JobStatus.RUNNING}:
                raise JobLeaseConflictError(
                    f"job {job_id} is not in a lease-bearing state: {current.value}"
                )
            expiry = row["lease_expires_at"]
            if expiry is None or expiry > now:
                raise JobLeaseConflictError(f"job {job_id} lease is still active")

            new_revision = expected_revision + 1
            self._cas_update(
                connection,
                row,
                expected_revision,
                {
                    "status": JobStatus.ELIGIBLE.value,
                    "claimed_by": None,
                    "lease_expires_at": None,
                    "updated_at": now,
                    "revision": new_revision,
                },
            )
            self._insert_outbox(
                connection,
                row["id"],
                job_id,
                new_revision,
                "job.lease.expired",
                now,
                {
                    "job_id": job_id,
                    "previous_status": current.value,
                    "status": JobStatus.ELIGIBLE.value,
                    "revision": new_revision,
                },
            )
            return JobTransitionResult(
                job_id,
                current,
                JobStatus.ELIGIBLE,
                new_revision,
            )

    def transition(
        self,
        job_id: str,
        target: JobStatus,
        *,
        now: datetime,
        expected_revision: int,
        blocked_reason: str | None = None,
    ) -> JobTransitionResult:
        with self.engine.begin() as connection:
            row = self._require_job_for_update(connection, job_id)
            self._require_revision(row, expected_revision)
            current = JobStatus(str(row["status"]))
            try:
                assert_job_transition(current, target)
            except InvalidJobTransitionError as exc:
                raise JobStateConflictError(str(exc)) from exc

            blocking_states = {
                JobStatus.BLOCKED_BUDGET,
                JobStatus.BLOCKED_LICENSE,
                JobStatus.BLOCKED_CAPABILITY,
                JobStatus.MANUAL_HANDOFF,
            }
            normalized_reason = blocked_reason.strip() if blocked_reason is not None else None
            if target in blocking_states and not normalized_reason:
                raise JobStateConflictError(f"{target.value} requires a blocked_reason")
            if target is JobStatus.RUNNING:
                expiry = row["lease_expires_at"]
                if row["claimed_by"] is None or expiry is None or expiry <= now:
                    raise JobLeaseConflictError(
                        f"job {job_id} requires an active lease before entering running"
                    )

            new_revision = expected_revision + 1
            values: dict[str, Any] = {
                "status": target.value,
                "blocked_reason": normalized_reason if target in blocking_states else None,
                "updated_at": now,
                "revision": new_revision,
            }
            if target is not JobStatus.RUNNING:
                values["claimed_by"] = None
                values["lease_expires_at"] = None

            self._cas_update(connection, row, expected_revision, values)
            self._insert_outbox(
                connection,
                row["id"],
                job_id,
                new_revision,
                "job.status.changed",
                now,
                {
                    "job_id": job_id,
                    "previous_status": current.value,
                    "status": target.value,
                    "revision": new_revision,
                },
            )
            return JobTransitionResult(job_id, current, target, new_revision)

    def pending_outbox(self, *, limit: int = 100) -> list[RowMapping]:
        if limit < 1 or limit > 1000:
            raise ValueError("outbox limit must be between 1 and 1000")
        with self.engine.connect() as connection:
            return list(
                connection.execute(
                    select(self.outbox)
                    .where(self.outbox.c.published_at.is_(None))
                    .order_by(self.outbox.c.occurred_at, self.outbox.c.id)
                    .limit(limit)
                ).mappings()
            )

    def mark_outbox_published(self, message_id: UUID, *, published_at: datetime) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(
                update(self.outbox)
                .where(self.outbox.c.id == message_id, self.outbox.c.published_at.is_(None))
                .values(published_at=published_at)
            )
            return result.rowcount == 1

    def _row_by_idempotency(
        self,
        connection: Connection,
        project_id: UUID,
        idempotency_key: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.jobs)
            .where(
                self.jobs.c.project_id == project_id,
                self.jobs.c.idempotency_key == idempotency_key,
            )
            .with_for_update()
        ).mappings().one_or_none()

    def _require_job_for_update(self, connection: Connection, job_id: str) -> RowMapping:
        row = connection.execute(
            select(self.jobs)
            .where(self.jobs.c.external_id == job_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"job {job_id} was not found")
        return row

    @staticmethod
    def _require_revision(row: RowMapping, expected_revision: int) -> None:
        if int(row["revision"]) != expected_revision:
            raise JobVersionConflictError(
                f"stale job revision: expected {expected_revision}, current {row['revision']}"
            )

    def _cas_update(
        self,
        connection: Connection,
        row: RowMapping,
        expected_revision: int,
        values: dict[str, Any],
    ) -> None:
        result = connection.execute(
            update(self.jobs)
            .where(self.jobs.c.id == row["id"], self.jobs.c.revision == expected_revision)
            .values(**values)
        )
        if result.rowcount != 1:
            raise JobVersionConflictError("job revision changed during mutation")

    @staticmethod
    def _require_external(
        connection: Connection,
        table: Table,
        external_id: str,
        label: str,
    ) -> RowMapping:
        row = connection.execute(
            select(table).where(table.c.external_id == external_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing {label}:{external_id}")
        return row

    def _optional_job_in_project(
        self,
        connection: Connection,
        external_id: str | None,
        project_id: UUID,
        label: str,
    ) -> UUID | None:
        if external_id is None:
            return None
        return self._require_job_in_project(connection, external_id, project_id, label)

    def _require_job_in_project(
        self,
        connection: Connection,
        external_id: str,
        project_id: UUID,
        label: str,
    ) -> UUID:
        row = self._require_external(connection, self.jobs, external_id, label)
        if row["project_id"] != project_id:
            raise PersistenceReferenceError(f"{label} {external_id} belongs to another project")
        return row["id"]

    def _optional_content_in_project(
        self,
        connection: Connection,
        external_id: str | None,
        project_id: UUID,
    ) -> UUID | None:
        if external_id is None:
            return None
        row = self._require_external(connection, self.contents, external_id, "content")
        if row["project_id"] != project_id:
            raise PersistenceReferenceError(f"content {external_id} belongs to another project")
        return row["id"]

    def _optional_shot_in_project(
        self,
        connection: Connection,
        external_id: str | None,
        project_id: UUID,
    ) -> UUID | None:
        if external_id is None:
            return None
        row = connection.execute(
            select(self.shots.c.id, self.acts.c.project_id)
            .select_from(
                self.shots.join(self.scenes, self.shots.c.scene_id == self.scenes.c.id)
                .join(self.sequences, self.scenes.c.sequence_id == self.sequences.c.id)
                .join(self.acts, self.sequences.c.act_id == self.acts.c.id)
            )
            .where(self.shots.c.external_id == external_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing shot:{external_id}")
        if row["project_id"] != project_id:
            raise PersistenceReferenceError(f"shot {external_id} belongs to another project")
        return row["id"]

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
        dedupe_key = f"job:{job_external_id}:revision:{revision}:{event_type}"
        connection.execute(
            insert(self.outbox).values(
                id=uuid4(),
                job_id=job_internal_id,
                job_revision=revision,
                event_type=event_type,
                dedupe_key=dedupe_key,
                payload=payload,
                occurred_at=occurred_at,
                published_at=None,
            )
        )
