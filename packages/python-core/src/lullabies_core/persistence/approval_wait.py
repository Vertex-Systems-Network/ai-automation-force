from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..approval_wait import (
    ApprovalRequestResult,
    ApprovalRequestStatus,
    ApprovalResolutionResult,
    ApprovalWaitKind,
    ApprovalWaitRequest,
    expected_wait_status,
    expired_job_status,
    resolved_job_status,
)
from ..common import JobStatus
from ..job_control import InvalidJobTransitionError, assert_job_transition, operation_fingerprint
from ..production import Approval
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError


class ApprovalWaitConflictError(PersistenceConflictError):
    """Approval request identity, state, or captured job state is inconsistent."""


class ApprovalWaitVersionConflictError(ApprovalWaitConflictError):
    """Approval request or job changed after the caller observed it."""


class ApprovalWaitExpiredError(ApprovalWaitConflictError):
    """A resolution arrived after the approval request expiry boundary."""


class PostgresApprovalWaitRepository:
    """Atomic approval waits with stale-version and duplicate-resolution protection."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"approval_requests", "approvals", "jobs", "projects", "outbox_messages"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"approval-wait persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.requests = metadata.tables["core.approval_requests"]
        self.approvals = metadata.tables["core.approvals"]
        self.jobs = metadata.tables["core.jobs"]
        self.projects = metadata.tables["core.projects"]
        self.outbox = metadata.tables["core.outbox_messages"]

    def request(self, request: ApprovalWaitRequest) -> ApprovalRequestResult:
        required_status = expected_wait_status(request.wait_kind)
        fingerprint = request.request_fingerprint
        try:
            with self.engine.begin() as connection:
                project = self._require_external(
                    connection,
                    self.projects,
                    request.project_id,
                    "project",
                )
                job = self._require_job_for_update(connection, request.job_id)
                if job["project_id"] != project["id"]:
                    raise PersistenceReferenceError(
                        f"job {request.job_id} belongs to another project"
                    )
                self._require_job_snapshot(
                    job,
                    request.requested_job_revision,
                    required_status,
                )

                existing = connection.execute(
                    select(self.requests)
                    .where(
                        self.requests.c.job_id == job["id"],
                        self.requests.c.idempotency_key == request.idempotency_key,
                    )
                    .with_for_update()
                ).mappings().one_or_none()
                if existing is not None:
                    if existing["request_fingerprint"] != fingerprint:
                        raise ApprovalWaitConflictError(
                            "approval idempotency key is bound to different request semantics"
                        )
                    return ApprovalRequestResult(
                        "reused",
                        str(existing["external_id"]),
                        int(existing["revision"]),
                        int(existing["requested_job_revision"]),
                        ApprovalRequestStatus(str(existing["status"])),
                    )

                internal_id = uuid4()
                connection.execute(
                    insert(self.requests).values(
                        id=internal_id,
                        external_id=request.request_id,
                        project_id=project["id"],
                        job_id=job["id"],
                        wait_kind=request.wait_kind.value,
                        subject_type=request.subject_type,
                        subject_id=request.subject_id,
                        requested_job_status=required_status.value,
                        requested_job_revision=request.requested_job_revision,
                        requested_by=request.requested_by,
                        reason=request.reason,
                        idempotency_key=request.idempotency_key,
                        request_fingerprint=fingerprint,
                        status=ApprovalRequestStatus.PENDING.value,
                        expires_at=request.expires_at,
                        approval_id=None,
                        resolution_fingerprint=None,
                        resolved_job_revision=None,
                        resolved_job_status=None,
                        requested_at=request.requested_at,
                        closed_at=None,
                        updated_at=request.requested_at,
                        revision=1,
                    )
                )
                self._insert_outbox(
                    connection,
                    job["id"],
                    request.job_id,
                    request.requested_job_revision,
                    request.request_id,
                    1,
                    "approval.requested",
                    request.requested_at,
                    {
                        "request_id": request.request_id,
                        "job_id": request.job_id,
                        "wait_kind": request.wait_kind.value,
                        "status": ApprovalRequestStatus.PENDING.value,
                        "job_revision": request.requested_job_revision,
                    },
                )
                return ApprovalRequestResult(
                    "created",
                    request.request_id,
                    1,
                    request.requested_job_revision,
                    ApprovalRequestStatus.PENDING,
                )
        except (ApprovalWaitConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise ApprovalWaitConflictError(
                f"database rejected approval request: {exc.orig}"
            ) from exc

    def resolve(
        self,
        request_id: str,
        approval: Approval,
        *,
        expected_request_revision: int,
    ) -> ApprovalResolutionResult:
        fingerprint = operation_fingerprint(
            {
                "approval_id": approval.approval_id,
                "project_id": approval.project_id,
                "subject_type": approval.subject_type,
                "subject_id": approval.subject_id,
                "decision": approval.decision.value,
                "actor": approval.actor,
                "reason": approval.reason,
                "created_at": approval.created_at,
            }
        )
        try:
            with self.engine.begin() as connection:
                request = self._require_request_for_update(connection, request_id)
                status = ApprovalRequestStatus(str(request["status"]))
                if status is ApprovalRequestStatus.RESOLVED:
                    if request["resolution_fingerprint"] != fingerprint:
                        raise ApprovalWaitConflictError(
                            "approval request is already resolved with different semantics"
                        )
                    approval_row = self._require_approval_by_id(
                        connection,
                        request["approval_id"],
                    )
                    return ApprovalResolutionResult(
                        "reused",
                        request_id,
                        int(request["revision"]),
                        int(request["resolved_job_revision"]),
                        status,
                        JobStatus(str(request["resolved_job_status"])),
                        str(approval_row["external_id"]),
                    )
                if status is ApprovalRequestStatus.EXPIRED:
                    raise ApprovalWaitExpiredError(f"approval request {request_id} has expired")
                self._require_request_revision(request, expected_request_revision)
                if approval.created_at < request["requested_at"]:
                    raise ApprovalWaitConflictError("approval predates the request")
                expires_at = request["expires_at"]
                if expires_at is not None and approval.created_at >= expires_at:
                    raise ApprovalWaitExpiredError(
                        f"approval request {request_id} expired before resolution"
                    )
                self._require_approval_matches_request(request, approval)

                job = self._require_job_by_id_for_update(connection, request["job_id"])
                current_status = JobStatus(str(request["requested_job_status"]))
                self._require_job_snapshot(
                    job,
                    int(request["requested_job_revision"]),
                    current_status,
                )
                target = resolved_job_status(
                    ApprovalWaitKind(str(request["wait_kind"])),
                    approval.decision,
                )
                new_status = target or current_status
                if target is not None:
                    try:
                        assert_job_transition(current_status, target)
                    except InvalidJobTransitionError as exc:
                        raise ApprovalWaitConflictError(str(exc)) from exc
                new_job_revision = int(job["revision"]) + 1
                job_values: dict[str, Any] = {
                    "status": new_status.value,
                    "updated_at": approval.created_at,
                    "revision": new_job_revision,
                    "claimed_by": None,
                    "lease_expires_at": None,
                }
                if target is not None:
                    job_values["blocked_reason"] = None
                self._update_job(connection, job, job_values)

                approval_internal_id = uuid4()
                connection.execute(
                    insert(self.approvals).values(
                        id=approval_internal_id,
                        external_id=approval.approval_id,
                        schema_version=approval.schema_version,
                        project_id=request["project_id"],
                        subject_type=approval.subject_type,
                        subject_id=approval.subject_id,
                        decision=approval.decision.value,
                        actor=approval.actor,
                        reason=approval.reason,
                        created_at=approval.created_at,
                    )
                )

                new_request_revision = expected_request_revision + 1
                self._update_request(
                    connection,
                    request,
                    expected_request_revision,
                    {
                        "status": ApprovalRequestStatus.RESOLVED.value,
                        "approval_id": approval_internal_id,
                        "resolution_fingerprint": fingerprint,
                        "resolved_job_revision": new_job_revision,
                        "resolved_job_status": new_status.value,
                        "closed_at": approval.created_at,
                        "updated_at": approval.created_at,
                        "revision": new_request_revision,
                    },
                )
                self._insert_outbox(
                    connection,
                    job["id"],
                    str(job["external_id"]),
                    new_job_revision,
                    request_id,
                    new_request_revision,
                    "approval.resolved",
                    approval.created_at,
                    {
                        "request_id": request_id,
                        "approval_id": approval.approval_id,
                        "decision": approval.decision.value,
                        "job_id": str(job["external_id"]),
                        "job_status": new_status.value,
                        "job_revision": new_job_revision,
                    },
                )
                return ApprovalResolutionResult(
                    "resolved",
                    request_id,
                    new_request_revision,
                    new_job_revision,
                    ApprovalRequestStatus.RESOLVED,
                    new_status,
                    approval.approval_id,
                )
        except (
            ApprovalWaitConflictError,
            PersistenceNotFoundError,
            PersistenceReferenceError,
        ):
            raise
        except IntegrityError as exc:
            raise ApprovalWaitConflictError(
                f"database rejected approval resolution: {exc.orig}"
            ) from exc

    def expire(
        self,
        request_id: str,
        *,
        now: datetime,
        expected_request_revision: int,
    ) -> ApprovalResolutionResult:
        with self.engine.begin() as connection:
            request = self._require_request_for_update(connection, request_id)
            status = ApprovalRequestStatus(str(request["status"]))
            if status is ApprovalRequestStatus.EXPIRED:
                return ApprovalResolutionResult(
                    "expired",
                    request_id,
                    int(request["revision"]),
                    int(request["resolved_job_revision"]),
                    status,
                    JobStatus(str(request["resolved_job_status"])),
                )
            if status is ApprovalRequestStatus.RESOLVED:
                raise ApprovalWaitConflictError(f"approval request {request_id} is resolved")
            self._require_request_revision(request, expected_request_revision)
            expires_at = request["expires_at"]
            if expires_at is None or expires_at > now:
                raise ApprovalWaitConflictError(f"approval request {request_id} is not expired")

            job = self._require_job_by_id_for_update(connection, request["job_id"])
            current_status = JobStatus(str(request["requested_job_status"]))
            self._require_job_snapshot(
                job,
                int(request["requested_job_revision"]),
                current_status,
            )
            target = expired_job_status(ApprovalWaitKind(str(request["wait_kind"])))
            new_status = target or current_status
            if target is not None:
                try:
                    assert_job_transition(current_status, target)
                except InvalidJobTransitionError as exc:
                    raise ApprovalWaitConflictError(str(exc)) from exc
            new_job_revision = int(job["revision"]) + 1
            job_values: dict[str, Any] = {
                "status": new_status.value,
                "updated_at": now,
                "revision": new_job_revision,
                "claimed_by": None,
                "lease_expires_at": None,
            }
            if new_status is JobStatus.MANUAL_HANDOFF:
                job_values["blocked_reason"] = f"approval request {request_id} expired"
            self._update_job(connection, job, job_values)

            new_request_revision = expected_request_revision + 1
            self._update_request(
                connection,
                request,
                expected_request_revision,
                {
                    "status": ApprovalRequestStatus.EXPIRED.value,
                    "resolved_job_revision": new_job_revision,
                    "resolved_job_status": new_status.value,
                    "closed_at": now,
                    "updated_at": now,
                    "revision": new_request_revision,
                },
            )
            self._insert_outbox(
                connection,
                job["id"],
                str(job["external_id"]),
                new_job_revision,
                request_id,
                new_request_revision,
                "approval.expired",
                now,
                {
                    "request_id": request_id,
                    "job_id": str(job["external_id"]),
                    "job_status": new_status.value,
                    "job_revision": new_job_revision,
                },
            )
            return ApprovalResolutionResult(
                "expired",
                request_id,
                new_request_revision,
                new_job_revision,
                ApprovalRequestStatus.EXPIRED,
                new_status,
            )

    def load(self, request_id: str) -> RowMapping:
        with self.engine.connect() as connection:
            row = connection.execute(
                select(self.requests).where(self.requests.c.external_id == request_id)
            ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"approval request {request_id} was not found")
        return row

    def _require_request_for_update(self, connection: Connection, request_id: str) -> RowMapping:
        row = connection.execute(
            select(self.requests)
            .where(self.requests.c.external_id == request_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"approval request {request_id} was not found")
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

    def _require_job_by_id_for_update(self, connection: Connection, job_id: UUID) -> RowMapping:
        row = connection.execute(
            select(self.jobs).where(self.jobs.c.id == job_id).with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"approval request references missing job {job_id}")
        return row

    @staticmethod
    def _require_job_snapshot(row: RowMapping, revision: int, status: JobStatus) -> None:
        if int(row["revision"]) != revision:
            raise ApprovalWaitVersionConflictError(
                f"stale job revision: expected {revision}, current {row['revision']}"
            )
        current_status = JobStatus(str(row["status"]))
        if current_status is not status:
            raise ApprovalWaitVersionConflictError(
                f"stale job status: expected {status.value}, current {current_status.value}"
            )

    @staticmethod
    def _require_request_revision(row: RowMapping, expected_revision: int) -> None:
        if int(row["revision"]) != expected_revision:
            raise ApprovalWaitVersionConflictError(
                f"stale approval request revision: expected {expected_revision}, "
                f"current {row['revision']}"
            )

    @staticmethod
    def _require_approval_matches_request(request: RowMapping, approval: Approval) -> None:
        if approval.project_id != request["project_external_id"] if "project_external_id" in request else False:
            raise ApprovalWaitConflictError("approval belongs to another project")
        if approval.subject_type != request["subject_type"] or approval.subject_id != request["subject_id"]:
            raise ApprovalWaitConflictError("approval subject does not match the request")

    def _require_approval_by_id(self, connection: Connection, approval_id: UUID | None) -> RowMapping:
        if approval_id is None:
            raise PersistenceReferenceError("resolved request is missing approval identity")
        row = connection.execute(
            select(self.approvals).where(self.approvals.c.id == approval_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError("resolved request references missing approval")
        return row

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

    def _update_job(
        self,
        connection: Connection,
        row: RowMapping,
        values: dict[str, Any],
    ) -> None:
        result = connection.execute(
            update(self.jobs)
            .where(self.jobs.c.id == row["id"], self.jobs.c.revision == row["revision"])
            .values(**values)
        )
        if result.rowcount != 1:
            raise ApprovalWaitVersionConflictError("job changed during approval mutation")

    def _update_request(
        self,
        connection: Connection,
        row: RowMapping,
        expected_revision: int,
        values: dict[str, Any],
    ) -> None:
        result = connection.execute(
            update(self.requests)
            .where(
                self.requests.c.id == row["id"],
                self.requests.c.revision == expected_revision,
            )
            .values(**values)
        )
        if result.rowcount != 1:
            raise ApprovalWaitVersionConflictError(
                "approval request changed during mutation"
            )

    def _insert_outbox(
        self,
        connection: Connection,
        job_internal_id: UUID,
        job_external_id: str,
        job_revision: int,
        request_id: str,
        request_revision: int,
        event_type: str,
        occurred_at: datetime,
        payload: dict[str, Any],
    ) -> None:
        dedupe_key = f"approval:{request_id}:revision:{request_revision}:{event_type}"
        connection.execute(
            insert(self.outbox).values(
                id=uuid4(),
                job_id=job_internal_id,
                job_revision=job_revision,
                event_type=event_type,
                dedupe_key=dedupe_key,
                payload=payload,
                occurred_at=occurred_at,
                published_at=None,
            )
        )
