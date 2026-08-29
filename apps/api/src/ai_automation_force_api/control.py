from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from ai_automation_force_core import (
    AuditFields,
    Job,
    JobCommandConflictError,
    JobCommandResult,
    JobCommandVersionConflictError,
    JobControlSnapshot,
    JobEventRecord,
    JobIdempotencyConflictError,
    PersistenceConflictError,
    PersistenceNotFoundError,
    PersistenceReferenceError,
    PostgresControlSurfaceRepository,
    PostgresJobControlRepository,
    PostgresWorkflowExecutionRepository,
    ProjectControlStatus,
    ProjectJobRecord,
    WorkflowExecutionRef,
)
from fastapi import APIRouter, Header, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from temporalio.client import Client
from temporalio.common import WorkflowIDConflictPolicy, WorkflowIDReusePolicy

from .errors import APIError
from .settings import Settings

JobIdValue = Annotated[str, Field(pattern=r"^JOB-[0-9]{6,20}$")]
ProjectIdValue = Annotated[str, Field(pattern=r"^PRJ-[0-9]{6,20}$")]
WorkflowIdValue = Annotated[str, Field(pattern=r"^WFX-[0-9]{6,20}$")]
IdempotencyValue = Annotated[str, Field(min_length=8, max_length=200)]


class StrictAPIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class JobCreateRequest(StrictAPIModel):
    project_id: ProjectIdValue
    job_type: str = Field(min_length=1, max_length=120)
    idempotency_key: IdempotencyValue
    priority: int = Field(default=50, ge=0, le=100)
    parent_job_id: JobIdValue | None = None
    dependency_job_ids: list[JobIdValue] = Field(default_factory=list, max_length=500)
    shot_id: str | None = Field(default=None, pattern=r"^SHT-[0-9]{6,20}$")
    content_id: str | None = Field(default=None, pattern=r"^CNT-[0-9]{6,20}$")
    retry_budget_remaining: int = Field(default=3, ge=0, le=100)


class JobCreateResponse(StrictAPIModel):
    action: Literal["created", "reused"]
    job: JobControlSnapshot
    event_cursor: str | None = None


class JobCheckpointResponse(StrictAPIModel):
    job: JobControlSnapshot
    event_cursor: str | None = None


class JobCommandRequest(StrictAPIModel):
    idempotency_key: IdempotencyValue
    expected_revision: int = Field(ge=1)


class JobCommandResponse(StrictAPIModel):
    command: JobCommandResult


class ProjectJobsResponse(StrictAPIModel):
    items: list[ProjectJobRecord]
    next_cursor: str | None = None


class JobEventsResponse(StrictAPIModel):
    items: list[JobEventRecord]
    next_cursor: str | None = None


class WorkflowResponse(StrictAPIModel):
    workflow: WorkflowExecutionRef


class SSEEventEnvelope(StrictAPIModel):
    schema_version: Literal[1] = 1
    event: JobEventRecord


class ControlDependencyError(RuntimeError):
    """The durable control service cannot currently reach a required dependency."""


def _numeric_external_id(prefix: str) -> str:
    number = uuid4().int % (10**20)
    return f"{prefix}-{number:020d}"


def _workflow_id(job_id: str, revision: int) -> str:
    digest = hashlib.sha256(f"{job_id}:{revision}".encode()).digest()
    number = int.from_bytes(digest[:8], "big") % (10**20)
    return f"WFX-{number:020d}"


def encode_cursor(at: datetime, stable_id: str) -> str:
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("cursor time must be timezone-aware")
    raw = json.dumps(
        {"at": at.isoformat(), "id": stable_id},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_cursor(value: str, *, uuid_id: bool) -> tuple[datetime, UUID | str]:
    if not 1 <= len(value) <= 512:
        raise ValueError("cursor length is invalid")
    try:
        padding = "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(value + padding))
        if not isinstance(payload, dict) or set(payload) != {"at", "id"}:
            raise ValueError("cursor shape is invalid")
        at = datetime.fromisoformat(str(payload["at"]))
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("cursor time must be timezone-aware")
        stable_id = str(payload["id"])
        return at, UUID(stable_id) if uuid_id else stable_id
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("cursor is invalid") from exc


def event_cursor(event: JobEventRecord) -> str:
    return encode_cursor(event.occurred_at, str(event.event_id))


class ControlService:
    def __init__(self, settings: Settings) -> None:
        if settings.database_url is None:
            raise ValueError("DATABASE_URL is required for the job control surface")
        self.settings = settings
        self.engine: Engine = create_engine(
            settings.database_url.get_secret_value(),
            pool_pre_ping=True,
        )
        self.jobs = PostgresJobControlRepository(self.engine)
        self.control = PostgresControlSurfaceRepository(self.engine)
        self.workflows = PostgresWorkflowExecutionRepository(self.engine)
        self._temporal_client: Client | None = None

    def close(self) -> None:
        self.engine.dispose()

    async def temporal_client(self) -> Client:
        if self._temporal_client is None:
            try:
                self._temporal_client = await Client.connect(
                    self.settings.temporal_target,
                    namespace=self.settings.temporal_namespace,
                )
            except Exception as exc:  # normalized at the API boundary, never leaked
                raise ControlDependencyError("Temporal is unavailable") from exc
        return self._temporal_client

    def create_job(self, request: JobCreateRequest) -> JobCreateResponse:
        now = datetime.now(UTC)
        operation = request.model_dump(mode="json")
        job = Job(
            job_id=_numeric_external_id("JOB"),
            project_id=request.project_id,
            job_type=request.job_type,
            priority=request.priority,
            idempotency_key=request.idempotency_key,
            parent_job_id=request.parent_job_id,
            dependency_job_ids=request.dependency_job_ids,
            shot_id=request.shot_id,
            content_id=request.content_id,
            retry_budget_remaining=request.retry_budget_remaining,
            audit=AuditFields(
                created_at=now,
                updated_at=now,
                created_by=self.settings.internal_dev_identity or self.settings.service_name,
                revision=1,
            ),
        )
        result = self.jobs.submit(job, operation)
        snapshot, high_water = self.control.load_job_checkpoint(result.job_id)
        return JobCreateResponse(
            action=result.action,
            job=snapshot,
            event_cursor=event_cursor(high_water) if high_water else None,
        )

    def checkpoint(self, job_id: str) -> JobCheckpointResponse:
        snapshot, high_water = self.control.load_job_checkpoint(job_id)
        return JobCheckpointResponse(
            job=snapshot,
            event_cursor=event_cursor(high_water) if high_water else None,
        )

    def project_jobs(
        self,
        project_id: str,
        *,
        cursor: str | None,
        limit: int,
    ) -> ProjectJobsResponse:
        after: tuple[datetime, str] | None = None
        if cursor:
            at, stable_id = decode_cursor(cursor, uuid_id=False)
            after = (at, str(stable_id))
        rows = self.control.list_project_jobs(project_id, after=after, limit=limit + 1)
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor(last.created_at, last.job_id)
        return ProjectJobsResponse(items=items, next_cursor=next_cursor)

    def project_status(self, project_id: str) -> ProjectControlStatus:
        return self.control.project_status(project_id)

    def events(
        self,
        job_id: str,
        *,
        cursor: str | None,
        limit: int,
    ) -> JobEventsResponse:
        after: tuple[datetime, UUID] | None = None
        if cursor:
            at, stable_id = decode_cursor(cursor, uuid_id=True)
            assert isinstance(stable_id, UUID)
            after = (at, stable_id)
        rows = self.control.list_job_events(job_id, after=after, limit=limit + 1)
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = event_cursor(items[-1]) if has_more and items else None
        return JobEventsResponse(items=items, next_cursor=next_cursor)

    def _existing_workflow(
        self,
        workflow_execution_id: str,
        *,
        workflow_type: str,
        project_id: str,
        job_id: str,
    ) -> WorkflowExecutionRef | None:
        try:
            existing = self.workflows.load(workflow_execution_id)
        except PersistenceNotFoundError:
            return None
        if (
            existing.workflow_type != workflow_type
            or existing.project_id != project_id
            or existing.job_id != job_id
            or existing.namespace != self.settings.temporal_namespace
            or existing.task_queue != self.settings.temporal_task_queue
        ):
            raise JobCommandConflictError(
                f"workflow {workflow_execution_id} is bound to different execution semantics"
            )
        return existing

    async def start_job(self, job_id: str, request: JobCommandRequest) -> JobCommandResult:
        operation: dict[str, Any] = {
            "expected_revision": request.expected_revision,
            "workflow_kind": "synthetic-job-control",
        }
        existing_command = self.control.load_start_command(
            job_id,
            idempotency_key=request.idempotency_key,
            operation=operation,
        )
        if existing_command is not None:
            return existing_command

        snapshot = self.control.load_job(job_id)
        if snapshot.revision != request.expected_revision:
            raise JobCommandVersionConflictError(
                f"stale job revision: expected {request.expected_revision}, "
                f"current {snapshot.revision}"
            )
        workflow_execution_id = _workflow_id(job_id, request.expected_revision)
        workflow_type = (
            "SyntheticCancellationWorkflow"
            if snapshot.job_type == "synthetic-cancellable"
            else "SyntheticControlWorkflow"
        )
        workflow_ref = self._existing_workflow(
            workflow_execution_id,
            workflow_type=workflow_type,
            project_id=snapshot.project_id,
            job_id=job_id,
        )
        if workflow_ref is None:
            client = await self.temporal_client()
            try:
                handle = await client.start_workflow(
                    workflow_type,
                    job_id,
                    id=workflow_execution_id,
                    task_queue=self.settings.temporal_task_queue,
                    id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
                    id_conflict_policy=WorkflowIDConflictPolicy.USE_EXISTING,
                )
            except Exception as exc:
                raise ControlDependencyError("Temporal workflow start failed") from exc
            run_id = handle.result_run_id
            if not run_id:
                raise ControlDependencyError("Temporal did not return a workflow run ID")
            now = datetime.now(UTC)
            workflow_ref = WorkflowExecutionRef(
                workflow_execution_id=workflow_execution_id,
                workflow_type=workflow_type,
                run_id=run_id,
                namespace=self.settings.temporal_namespace,
                task_queue=self.settings.temporal_task_queue,
                project_id=snapshot.project_id,
                job_id=job_id,
                status="running",
                started_at=now,
                updated_at=now,
            )
            self.workflows.save(workflow_ref)
        now = datetime.now(UTC)
        return self.control.record_start(
            job_id,
            idempotency_key=request.idempotency_key,
            expected_revision=request.expected_revision,
            workflow_execution_id=workflow_ref.workflow_execution_id,
            operation=operation,
            now=now,
        )

    async def cancel_job(self, job_id: str, request: JobCommandRequest) -> JobCommandResult:
        result = self.control.cancel_job(
            job_id,
            idempotency_key=request.idempotency_key,
            expected_revision=request.expected_revision,
            now=datetime.now(UTC),
        )
        snapshot = self.control.load_job(job_id)
        if snapshot.workflow_execution_id is not None:
            client = await self.temporal_client()
            try:
                handle = client.get_workflow_handle(snapshot.workflow_execution_id)
                await handle.cancel()
            except Exception as exc:
                raise ControlDependencyError("Temporal workflow cancellation failed") from exc
        return result

    def retry_job(self, job_id: str, request: JobCommandRequest) -> JobCommandResult:
        return self.control.retry_job(
            job_id,
            idempotency_key=request.idempotency_key,
            expected_revision=request.expected_revision,
            now=datetime.now(UTC),
        )

    def workflow(self, workflow_execution_id: str) -> WorkflowExecutionRef:
        return self.workflows.load(workflow_execution_id)

    async def stream_events(
        self,
        request: Request,
        job_id: str,
        *,
        last_event_id: str | None,
        follow: bool,
    ) -> AsyncIterator[str]:
        cursor = last_event_id
        heartbeat_deadline = asyncio.get_running_loop().time() + self.settings.sse_heartbeat_seconds
        while not await request.is_disconnected():
            page = self.events(job_id, cursor=cursor, limit=100)
            if page.items:
                for item in page.items:
                    cursor = event_cursor(item)
                    envelope = SSEEventEnvelope(event=item)
                    data = envelope.model_dump_json()
                    yield f"id: {cursor}\nevent: {item.event_type}\ndata: {data}\n\n"
                heartbeat_deadline = (
                    asyncio.get_running_loop().time() + self.settings.sse_heartbeat_seconds
                )
                continue
            if not follow:
                return
            now = asyncio.get_running_loop().time()
            if now >= heartbeat_deadline:
                yield ": keepalive\n\n"
                heartbeat_deadline = now + self.settings.sse_heartbeat_seconds
            await asyncio.sleep(self.settings.sse_poll_interval_ms / 1000)


def _service(request: Request) -> ControlService:
    service = getattr(request.app.state, "control_service", None)
    if not isinstance(service, ControlService):
        raise APIError(
            "CONTROL_SURFACE_UNAVAILABLE",
            "job control surface is not configured",
            status_code=503,
        )
    return service


def _translate_error(exc: Exception) -> APIError:
    if isinstance(exc, PersistenceNotFoundError):
        return APIError("NOT_FOUND", str(exc), status_code=404)
    if isinstance(exc, JobCommandVersionConflictError):
        return APIError("STALE_REVISION", str(exc), status_code=409)
    if isinstance(
        exc,
        (
            JobIdempotencyConflictError,
            JobCommandConflictError,
            PersistenceConflictError,
            PersistenceReferenceError,
        ),
    ):
        return APIError("CONTROL_CONFLICT", str(exc), status_code=409)
    if isinstance(exc, ControlDependencyError):
        return APIError("DEPENDENCY_UNAVAILABLE", str(exc), status_code=503)
    if isinstance(exc, ValueError):
        return APIError("INVALID_CONTROL_REQUEST", str(exc), status_code=400)
    return APIError("CONTROL_FAILURE", "control operation failed", status_code=500)


def control_router() -> APIRouter:
    router = APIRouter(tags=["jobs"])

    @router.post("/jobs", response_model=JobCreateResponse, status_code=201)
    async def create_job(request: Request, body: JobCreateRequest) -> JobCreateResponse:
        try:
            return _service(request).create_job(body)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.get("/jobs/{job_id}", response_model=JobCheckpointResponse)
    async def get_job(request: Request, job_id: JobIdValue) -> JobCheckpointResponse:
        try:
            return _service(request).checkpoint(job_id)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.get("/projects/{project_id}/jobs", response_model=ProjectJobsResponse)
    async def list_project_jobs(
        request: Request,
        project_id: ProjectIdValue,
        cursor: str | None = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 50,
    ) -> ProjectJobsResponse:
        try:
            return _service(request).project_jobs(project_id, cursor=cursor, limit=limit)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.get("/projects/{project_id}/status", response_model=ProjectControlStatus)
    async def get_project_status(
        request: Request,
        project_id: ProjectIdValue,
    ) -> ProjectControlStatus:
        try:
            return _service(request).project_status(project_id)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.get("/jobs/{job_id}/history", response_model=JobEventsResponse)
    async def job_history(
        request: Request,
        job_id: JobIdValue,
        cursor: str | None = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 100,
    ) -> JobEventsResponse:
        try:
            return _service(request).events(job_id, cursor=cursor, limit=limit)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.post("/jobs/{job_id}/start", response_model=JobCommandResponse)
    async def start_job(
        request: Request,
        job_id: JobIdValue,
        body: JobCommandRequest,
    ) -> JobCommandResponse:
        try:
            result = await _service(request).start_job(job_id, body)
            return JobCommandResponse(command=result)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.post("/jobs/{job_id}/cancel", response_model=JobCommandResponse)
    async def cancel_job(
        request: Request,
        job_id: JobIdValue,
        body: JobCommandRequest,
    ) -> JobCommandResponse:
        try:
            result = await _service(request).cancel_job(job_id, body)
            return JobCommandResponse(command=result)
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.post("/jobs/{job_id}/retry", response_model=JobCommandResponse)
    async def retry_job(
        request: Request,
        job_id: JobIdValue,
        body: JobCommandRequest,
    ) -> JobCommandResponse:
        try:
            return JobCommandResponse(command=_service(request).retry_job(job_id, body))
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.get("/workflows/{workflow_execution_id}", response_model=WorkflowResponse)
    async def get_workflow(
        request: Request,
        workflow_execution_id: WorkflowIdValue,
    ) -> WorkflowResponse:
        try:
            return WorkflowResponse(workflow=_service(request).workflow(workflow_execution_id))
        except Exception as exc:
            raise _translate_error(exc) from exc

    @router.get("/jobs/{job_id}/events")
    async def job_events(
        request: Request,
        job_id: JobIdValue,
        last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
        follow: bool = True,
    ) -> StreamingResponse:
        service = _service(request)
        try:
            service.checkpoint(job_id)
            if last_event_id:
                decode_cursor(last_event_id, uuid_id=True)
        except Exception as exc:
            raise _translate_error(exc) from exc
        return StreamingResponse(
            service.stream_events(
                request,
                job_id,
                last_event_id=last_event_id,
                follow=follow,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return router
