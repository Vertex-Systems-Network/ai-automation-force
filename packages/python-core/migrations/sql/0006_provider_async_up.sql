CREATE TABLE core.provider_async_states (
    attempt_id uuid PRIMARY KEY,
    provider_id text NOT NULL,
    provider_generation_id text NOT NULL,
    status text NOT NULL DEFAULT 'submitted',
    provider_status text NOT NULL DEFAULT 'submitted',
    submitted_at timestamptz NOT NULL,
    next_poll_at timestamptz,
    deadline_at timestamptz NOT NULL,
    poll_count integer NOT NULL DEFAULT 0,
    last_polled_at timestamptz,
    last_callback_at timestamptz,
    last_provider_event_at timestamptz,
    last_reconciled_at timestamptz NOT NULL,
    terminal_at timestamptz,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_provider_async_attempt FOREIGN KEY (attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT uq_provider_async_generation UNIQUE (provider_id, provider_generation_id),
    CONSTRAINT ck_provider_async_status CHECK (
        status IN ('submitted', 'running', 'succeeded', 'failed', 'timed-out', 'cancelled')
    ),
    CONSTRAINT ck_provider_async_provider_id CHECK (length(provider_id) BETWEEN 1 AND 120),
    CONSTRAINT ck_provider_async_generation_id CHECK (
        length(provider_generation_id) BETWEEN 1 AND 240
    ),
    CONSTRAINT ck_provider_async_provider_status CHECK (
        length(provider_status) BETWEEN 1 AND 120
    ),
    CONSTRAINT ck_provider_async_deadline CHECK (deadline_at > submitted_at),
    CONSTRAINT ck_provider_async_next_poll CHECK (
        next_poll_at IS NULL OR (next_poll_at >= submitted_at AND next_poll_at < deadline_at)
    ),
    CONSTRAINT ck_provider_async_poll_count CHECK (poll_count >= 0),
    CONSTRAINT ck_provider_async_revision CHECK (revision >= 1),
    CONSTRAINT ck_provider_async_reconcile_time CHECK (last_reconciled_at >= submitted_at),
    CONSTRAINT ck_provider_async_terminal CHECK (
        (status IN ('succeeded', 'failed', 'timed-out', 'cancelled') AND terminal_at IS NOT NULL)
        OR (status IN ('submitted', 'running') AND terminal_at IS NULL)
    )
);

CREATE INDEX idx_provider_async_poll_due
    ON core.provider_async_states (next_poll_at, attempt_id)
    WHERE status IN ('submitted', 'running') AND next_poll_at IS NOT NULL;

CREATE INDEX idx_provider_async_deadline
    ON core.provider_async_states (deadline_at, attempt_id)
    WHERE status IN ('submitted', 'running');

CREATE TABLE core.provider_callback_events (
    id uuid PRIMARY KEY,
    attempt_id uuid NOT NULL,
    provider_id text NOT NULL,
    event_id text NOT NULL,
    provider_generation_id text NOT NULL,
    payload_sha256 char(64) NOT NULL,
    signature_scheme text NOT NULL,
    provider_status text NOT NULL,
    normalized_status text NOT NULL,
    provider_event_at timestamptz NOT NULL,
    received_at timestamptz NOT NULL,
    processed_at timestamptz NOT NULL,
    stale boolean NOT NULL DEFAULT false,
    CONSTRAINT fk_provider_callback_attempt FOREIGN KEY (attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT uq_provider_callback_event UNIQUE (provider_id, event_id),
    CONSTRAINT ck_provider_callback_event_id CHECK (length(event_id) BETWEEN 3 AND 200),
    CONSTRAINT ck_provider_callback_provider_id CHECK (length(provider_id) BETWEEN 1 AND 120),
    CONSTRAINT ck_provider_callback_generation_id CHECK (
        length(provider_generation_id) BETWEEN 1 AND 240
    ),
    CONSTRAINT ck_provider_callback_sha CHECK (payload_sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_provider_callback_signature_scheme CHECK (
        length(signature_scheme) BETWEEN 3 AND 80
    ),
    CONSTRAINT ck_provider_callback_status CHECK (
        normalized_status IN ('submitted', 'running', 'succeeded', 'failed', 'timed-out', 'cancelled')
    ),
    CONSTRAINT ck_provider_callback_times CHECK (
        received_at >= provider_event_at AND processed_at >= received_at
    )
);

CREATE INDEX idx_provider_callback_attempt_time
    ON core.provider_callback_events (attempt_id, provider_event_at, id);
