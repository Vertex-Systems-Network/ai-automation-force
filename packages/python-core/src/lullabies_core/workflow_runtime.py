from __future__ import annotations

from typing import Annotated

from pydantic import AwareDatetime, Field, model_validator

from .common import JobId, ProjectId, StrictModel, external_id_pattern

WorkflowExecutionId = Annotated[str, Field(pattern=external_id_pattern("WFX"))]


class WorkflowExecutionRef(StrictModel):
    """Application-facing reference to one Temporal workflow run.

    Temporal event history remains owned by Temporal. This record stores only the
    stable application identity and the run reference required to inspect/reconcile it.
    """

    workflow_execution_id: WorkflowExecutionId
    workflow_type: str = Field(min_length=1, max_length=160)
    run_id: str = Field(min_length=1, max_length=160)
    namespace: str = Field(min_length=1, max_length=160)
    task_queue: str = Field(min_length=1, max_length=160)
    project_id: ProjectId | None = None
    job_id: JobId | None = None
    status: str = Field(default="running", min_length=1, max_length=80)
    started_at: AwareDatetime
    updated_at: AwareDatetime
    closed_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_shape_and_chronology(self) -> WorkflowExecutionRef:
        if self.job_id is not None and self.project_id is None:
            raise ValueError("job-bound workflow requires project_id")
        if self.updated_at < self.started_at:
            raise ValueError("updated_at cannot precede started_at")
        if self.closed_at is not None and self.closed_at < self.started_at:
            raise ValueError("closed_at cannot precede started_at")
        return self
