CREATE TABLE core.job_commands (
    id uuid PRIMARY KEY,
    job_id uuid NOT NULL,
    command_type text NOT NULL,
    idempotency_key text NOT NULL,
    operation_fingerprint text NOT NULL,
    result jsonb NOT NULL DEFAULT '{}',
    occurred_at timestamptz NOT NULL,
    CONSTRAINT fk_job_commands_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT uq_job_commands_idempotency UNIQUE (job_id, idempotency_key),
    CONSTRAINT ck_job_commands_type CHECK (length(command_type) BETWEEN 1 AND 80),
    CONSTRAINT ck_job_commands_idempotency_key CHECK (length(idempotency_key) BETWEEN 8 AND 200),
    CONSTRAINT ck_job_commands_fingerprint CHECK (operation_fingerprint ~ '^[a-f0-9]{64}$')
);

CREATE INDEX idx_job_commands_job_time
    ON core.job_commands (job_id, occurred_at, id);
