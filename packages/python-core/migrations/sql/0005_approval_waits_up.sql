CREATE TABLE core.approval_requests (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    project_id uuid NOT NULL,
    job_id uuid NOT NULL,
    wait_kind text NOT NULL,
    subject_type text NOT NULL,
    subject_id text NOT NULL,
    requested_job_status text NOT NULL,
    requested_job_revision integer NOT NULL,
    requested_by text NOT NULL,
    reason text,
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    status text NOT NULL DEFAULT 'pending',
    expires_at timestamptz,
    approval_id uuid UNIQUE,
    resolution_fingerprint char(64),
    resolved_job_revision integer,
    requested_at timestamptz NOT NULL,
    closed_at timestamptz,
    updated_at timestamptz NOT NULL,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_approval_request_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_approval_request_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT fk_approval_request_approval FOREIGN KEY (approval_id)
        REFERENCES core.approvals(id) ON DELETE RESTRICT,
    CONSTRAINT uq_approval_request_job_key UNIQUE (job_id, idempotency_key),
    CONSTRAINT ck_approval_request_external_id CHECK (external_id ~ '^AQR-[0-9]{6,20}$'),
    CONSTRAINT ck_approval_request_kind CHECK (
        wait_kind IN ('human-approval', 'budget', 'manual-handoff')
    ),
    CONSTRAINT ck_approval_request_wait_status CHECK (
        (wait_kind = 'human-approval' AND requested_job_status = 'waiting-human')
        OR (wait_kind = 'budget' AND requested_job_status = 'blocked-budget')
        OR (wait_kind = 'manual-handoff' AND requested_job_status = 'manual-handoff')
    ),
    CONSTRAINT ck_approval_request_status CHECK (status IN ('pending', 'resolved', 'expired')),
    CONSTRAINT ck_approval_request_job_revision CHECK (requested_job_revision >= 1),
    CONSTRAINT ck_approval_request_resolved_job_revision CHECK (
        resolved_job_revision IS NULL OR resolved_job_revision >= requested_job_revision
    ),
    CONSTRAINT ck_approval_request_idempotency CHECK (length(idempotency_key) BETWEEN 8 AND 200),
    CONSTRAINT ck_approval_request_fingerprint CHECK (
        request_fingerprint ~ '^[a-f0-9]{64}$'
    ),
    CONSTRAINT ck_approval_resolution_fingerprint CHECK (
        resolution_fingerprint IS NULL OR resolution_fingerprint ~ '^[a-f0-9]{64}$'
    ),
    CONSTRAINT ck_approval_request_expiry CHECK (
        expires_at IS NULL OR expires_at > requested_at
    ),
    CONSTRAINT ck_approval_request_time CHECK (updated_at >= requested_at),
    CONSTRAINT ck_approval_request_revision CHECK (revision >= 1),
    CONSTRAINT ck_approval_request_lifecycle CHECK (
        (status = 'pending' AND approval_id IS NULL AND resolution_fingerprint IS NULL
            AND resolved_job_revision IS NULL AND closed_at IS NULL)
        OR (status = 'resolved' AND approval_id IS NOT NULL AND resolution_fingerprint IS NOT NULL
            AND resolved_job_revision IS NOT NULL AND closed_at IS NOT NULL)
        OR (status = 'expired' AND approval_id IS NULL AND resolution_fingerprint IS NULL
            AND resolved_job_revision IS NOT NULL AND closed_at IS NOT NULL)
    )
);

CREATE UNIQUE INDEX uq_approval_request_job_pending
    ON core.approval_requests (job_id)
    WHERE status = 'pending';

CREATE INDEX idx_approval_request_expiry
    ON core.approval_requests (expires_at, id)
    WHERE status = 'pending' AND expires_at IS NOT NULL;
