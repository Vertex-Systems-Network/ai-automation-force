CREATE TABLE core.workflow_executions (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    workflow_type text NOT NULL,
    run_id text NOT NULL UNIQUE,
    namespace text NOT NULL,
    task_queue text NOT NULL,
    project_id uuid,
    job_id uuid,
    status text NOT NULL DEFAULT 'running',
    started_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    closed_at timestamptz,
    CONSTRAINT fk_workflow_execution_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_workflow_execution_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT ck_workflow_execution_external_id CHECK (
        external_id ~ '^WFX-[0-9]{6,20}$'
    ),
    CONSTRAINT ck_workflow_execution_type CHECK (length(workflow_type) BETWEEN 1 AND 160),
    CONSTRAINT ck_workflow_execution_run_id CHECK (length(run_id) BETWEEN 1 AND 160),
    CONSTRAINT ck_workflow_execution_namespace CHECK (length(namespace) BETWEEN 1 AND 160),
    CONSTRAINT ck_workflow_execution_task_queue CHECK (length(task_queue) BETWEEN 1 AND 160),
    CONSTRAINT ck_workflow_execution_status CHECK (length(status) BETWEEN 1 AND 80),
    CONSTRAINT ck_workflow_execution_audit_time CHECK (updated_at >= started_at),
    CONSTRAINT ck_workflow_execution_closed_time CHECK (
        closed_at IS NULL OR closed_at >= started_at
    )
);

CREATE INDEX ix_workflow_executions_project
    ON core.workflow_executions(project_id);

CREATE INDEX ix_workflow_executions_job
    ON core.workflow_executions(job_id);

CREATE INDEX ix_workflow_executions_status
    ON core.workflow_executions(status);
