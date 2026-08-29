from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..workflow_runtime import WorkflowExecutionRef
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

WorkflowPersistAction = Literal["created", "noop", "updated"]


@dataclass(frozen=True)
class WorkflowPersistResult:
    action: WorkflowPersistAction
    workflow_execution_id: str


class PostgresWorkflowExecutionRepository:
    """Persistence boundary for application-facing Temporal execution references."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"workflow_executions", "projects", "jobs"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"workflow persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.workflow_table = metadata.tables["core.workflow_executions"]
        self.project_table = metadata.tables["core.projects"]
        self.job_table = metadata.tables["core.jobs"]

    def save(self, execution: WorkflowExecutionRef) -> WorkflowPersistResult:
        try:
            with self.engine.begin() as connection:
                existing = self._row_by_external(connection, execution.workflow_execution_id)
                if existing is not None:
                    restored = self._from_row(connection, existing)
                    if restored == execution:
                        return WorkflowPersistResult("noop", execution.workflow_execution_id)
                    raise PersistenceConflictError(
                        f"workflow {execution.workflow_execution_id} already exists with different data"
                    )

                project_internal = self._optional_internal(
                    connection,
                    self.project_table,
                    execution.project_id,
                    "project",
                )
                job_internal = self._optional_internal(
                    connection,
                    self.job_table,
                    execution.job_id,
                    "job",
                )
                if job_internal is not None:
                    if project_internal is None:
                        raise PersistenceReferenceError("job-bound workflow requires project_id")
                    job_row = self._row_by_id(connection, self.job_table, job_internal)
                    if job_row is None or job_row["project_id"] != project_internal:
                        raise PersistenceReferenceError(
                            "workflow job_id does not belong to workflow project_id"
                        )

                connection.execute(
                    insert(self.workflow_table).values(
                        id=uuid4(),
                        external_id=execution.workflow_execution_id,
                        workflow_type=execution.workflow_type,
                        run_id=execution.run_id,
                        namespace=execution.namespace,
                        task_queue=execution.task_queue,
                        project_id=project_internal,
                        job_id=job_internal,
                        status=execution.status,
                        started_at=execution.started_at,
                        updated_at=execution.updated_at,
                        closed_at=execution.closed_at,
                    )
                )
        except (PersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database integrity rejected workflow {execution.workflow_execution_id}: {exc.orig}"
            ) from exc
        return WorkflowPersistResult("created", execution.workflow_execution_id)

    def load(self, workflow_execution_id: str) -> WorkflowExecutionRef:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, workflow_execution_id)
            if row is None:
                raise PersistenceNotFoundError(f"workflow {workflow_execution_id} was not found")
            return self._from_row(connection, row)

    def update_status(
        self,
        workflow_execution_id: str,
        *,
        status: str,
        updated_at: datetime,
        closed_at: datetime | None = None,
    ) -> WorkflowPersistResult:
        with self.engine.begin() as connection:
            row = self._row_by_external(connection, workflow_execution_id)
            if row is None:
                raise PersistenceNotFoundError(f"workflow {workflow_execution_id} was not found")
            candidate = self._from_row(connection, row).model_copy(
                update={"status": status, "updated_at": updated_at, "closed_at": closed_at},
            )
            candidate = WorkflowExecutionRef.model_validate(candidate.model_dump())
            connection.execute(
                update(self.workflow_table)
                .where(self.workflow_table.c.id == row["id"])
                .values(
                    status=candidate.status,
                    updated_at=candidate.updated_at,
                    closed_at=candidate.closed_at,
                )
            )
        return WorkflowPersistResult("updated", workflow_execution_id)

    def _from_row(self, connection: Connection, row: RowMapping) -> WorkflowExecutionRef:
        return WorkflowExecutionRef(
            workflow_execution_id=row["external_id"],
            workflow_type=row["workflow_type"],
            run_id=row["run_id"],
            namespace=row["namespace"],
            task_queue=row["task_queue"],
            project_id=self._external_for_internal(
                connection,
                self.project_table,
                row["project_id"],
            ),
            job_id=self._external_for_internal(connection, self.job_table, row["job_id"]),
            status=row["status"],
            started_at=row["started_at"],
            updated_at=row["updated_at"],
            closed_at=row["closed_at"],
        )

    def _row_by_external(self, connection: Connection, external_id: str) -> RowMapping | None:
        return connection.execute(
            select(self.workflow_table).where(self.workflow_table.c.external_id == external_id)
        ).mappings().one_or_none()

    @staticmethod
    def _row_by_id(connection: Connection, table: Table, internal_id: UUID) -> RowMapping | None:
        return connection.execute(select(table).where(table.c.id == internal_id)).mappings().one_or_none()

    @staticmethod
    def _optional_internal(
        connection: Connection,
        table: Table,
        external_id: str | None,
        label: str,
    ) -> UUID | None:
        if external_id is None:
            return None
        value = connection.execute(
            select(table.c.id).where(table.c.external_id == external_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing {label}:{external_id}")
        return value

    @staticmethod
    def _external_for_internal(
        connection: Connection,
        table: Table,
        internal_id: UUID | None,
    ) -> str | None:
        if internal_id is None:
            return None
        value: Any = connection.execute(
            select(table.c.external_id).where(table.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(f"missing external identity for internal row {internal_id}")
        return str(value)
