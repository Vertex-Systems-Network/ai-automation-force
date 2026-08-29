CREATE TABLE core.circuit_breakers (
    id uuid PRIMARY KEY,
    circuit_key text NOT NULL UNIQUE,
    state text NOT NULL DEFAULT 'closed',
    consecutive_failures integer NOT NULL DEFAULT 0,
    failure_threshold integer NOT NULL,
    opened_at timestamptz,
    next_probe_at timestamptz,
    probe_owner text,
    probe_lease_expires_at timestamptz,
    last_failure_class text,
    updated_at timestamptz NOT NULL,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT ck_circuit_key CHECK (length(circuit_key) BETWEEN 3 AND 240),
    CONSTRAINT ck_circuit_state CHECK (state IN ('closed', 'open', 'half-open')),
    CONSTRAINT ck_circuit_failures CHECK (consecutive_failures >= 0),
    CONSTRAINT ck_circuit_threshold CHECK (failure_threshold >= 1),
    CONSTRAINT ck_circuit_revision CHECK (revision >= 1),
    CONSTRAINT ck_circuit_open_times CHECK (
        state <> 'open' OR (opened_at IS NOT NULL AND next_probe_at IS NOT NULL)
    ),
    CONSTRAINT ck_circuit_probe_lease CHECK (
        state <> 'half-open'
        OR (probe_owner IS NOT NULL AND probe_lease_expires_at IS NOT NULL)
    )
);

CREATE INDEX idx_circuit_breakers_probe
    ON core.circuit_breakers (next_probe_at, circuit_key)
    WHERE state = 'open';
