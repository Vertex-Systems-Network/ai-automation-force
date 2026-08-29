ALTER TABLE core.jobs
    ADD COLUMN operation_fingerprint text;

ALTER TABLE core.jobs
    ADD CONSTRAINT ck_job_operation_fingerprint CHECK (
        operation_fingerprint IS NULL
        OR operation_fingerprint ~ '^[a-f0-9]{64}$'
    );

CREATE INDEX idx_jobs_runnable
    ON core.jobs (status, priority DESC, created_at, id)
    WHERE status IN ('queued', 'eligible', 'retryable-failed', 'claimed');

CREATE INDEX idx_jobs_lease_expiry
    ON core.jobs (lease_expires_at, id)
    WHERE lease_expires_at IS NOT NULL;

CREATE TABLE core.outbox_messages (
    id uuid PRIMARY KEY,
    job_id uuid NOT NULL,
    job_revision integer NOT NULL,
    event_type text NOT NULL,
    dedupe_key text NOT NULL UNIQUE,
    payload jsonb NOT NULL DEFAULT '{}',
    occurred_at timestamptz NOT NULL,
    published_at timestamptz,
    CONSTRAINT fk_outbox_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT ck_outbox_job_revision CHECK (job_revision >= 1),
    CONSTRAINT ck_outbox_event_type CHECK (length(event_type) BETWEEN 1 AND 160),
    CONSTRAINT ck_outbox_dedupe_key CHECK (length(dedupe_key) BETWEEN 8 AND 300),
    CONSTRAINT ck_outbox_publish_time CHECK (
        published_at IS NULL OR published_at >= occurred_at
    )
);

CREATE INDEX idx_outbox_pending
    ON core.outbox_messages (occurred_at, id)
    WHERE published_at IS NULL;
