CREATE TABLE core.asset_lifecycle_states (
    id uuid PRIMARY KEY,
    asset_id uuid NOT NULL UNIQUE,
    project_id uuid NOT NULL,
    state text NOT NULL DEFAULT 'active',
    recovery_state text,
    recovery_until timestamptz,
    updated_at timestamptz NOT NULL,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_asset_lifecycle_state_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE CASCADE,
    CONSTRAINT fk_asset_lifecycle_state_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT ck_asset_lifecycle_state_value CHECK (
        state IN (
            'active',
            'archive-requested',
            'archiving',
            'archived',
            'archive-failed',
            'restore-requested',
            'restoring',
            'restore-failed',
            'deletion-pending',
            'hard-delete-scheduled',
            'deleted'
        )
    ),
    CONSTRAINT ck_asset_lifecycle_recovery_state CHECK (
        recovery_state IS NULL OR recovery_state IN (
            'active', 'archived', 'archive-failed', 'restore-failed'
        )
    ),
    CONSTRAINT ck_asset_lifecycle_recovery_window CHECK (
        (
            state = 'deletion-pending'
            AND recovery_state IS NOT NULL
            AND recovery_until IS NOT NULL
            AND recovery_until > updated_at
        ) OR (
            state <> 'deletion-pending'
            AND recovery_state IS NULL
            AND recovery_until IS NULL
        )
    ),
    CONSTRAINT ck_asset_lifecycle_revision CHECK (revision >= 1)
);

CREATE INDEX idx_asset_lifecycle_states_project_state
    ON core.asset_lifecycle_states (project_id, state, updated_at, id);

CREATE TABLE core.asset_lifecycle_events (
    id uuid PRIMARY KEY,
    asset_external_id text NOT NULL,
    project_external_id text NOT NULL,
    from_state text NOT NULL,
    to_state text NOT NULL,
    operation_key text NOT NULL,
    actor text NOT NULL,
    reason text,
    recovery_state text,
    recovery_until timestamptz,
    occurred_at timestamptz NOT NULL,
    revision integer NOT NULL,
    CONSTRAINT ck_asset_lifecycle_event_asset CHECK (
        asset_external_id ~ '^AST-[0-9]{6,20}$'
    ),
    CONSTRAINT ck_asset_lifecycle_event_project CHECK (
        project_external_id ~ '^PRJ-[0-9]{6,20}$'
    ),
    CONSTRAINT ck_asset_lifecycle_event_from_state CHECK (
        from_state IN (
            'active',
            'archive-requested',
            'archiving',
            'archived',
            'archive-failed',
            'restore-requested',
            'restoring',
            'restore-failed',
            'deletion-pending',
            'hard-delete-scheduled',
            'deleted'
        )
    ),
    CONSTRAINT ck_asset_lifecycle_event_to_state CHECK (
        to_state IN (
            'active',
            'archive-requested',
            'archiving',
            'archived',
            'archive-failed',
            'restore-requested',
            'restoring',
            'restore-failed',
            'deletion-pending',
            'hard-delete-scheduled',
            'deleted'
        )
    ),
    CONSTRAINT ck_asset_lifecycle_event_changes_state CHECK (from_state <> to_state),
    CONSTRAINT ck_asset_lifecycle_event_operation CHECK (
        char_length(operation_key) BETWEEN 8 AND 200
    ),
    CONSTRAINT ck_asset_lifecycle_event_actor CHECK (
        char_length(actor) BETWEEN 1 AND 200
    ),
    CONSTRAINT ck_asset_lifecycle_event_reason CHECK (
        reason IS NULL OR char_length(reason) BETWEEN 1 AND 2000
    ),
    CONSTRAINT ck_asset_lifecycle_event_recovery_state CHECK (
        recovery_state IS NULL OR recovery_state IN (
            'active', 'archived', 'archive-failed', 'restore-failed'
        )
    ),
    CONSTRAINT ck_asset_lifecycle_event_recovery_window CHECK (
        (
            to_state = 'deletion-pending'
            AND recovery_state IS NOT NULL
            AND recovery_until IS NOT NULL
            AND recovery_until > occurred_at
        ) OR (
            to_state <> 'deletion-pending'
            AND recovery_state IS NULL
            AND recovery_until IS NULL
        )
    ),
    CONSTRAINT ck_asset_lifecycle_event_revision CHECK (revision >= 2),
    CONSTRAINT uq_asset_lifecycle_event_operation UNIQUE (
        asset_external_id, operation_key
    )
);

CREATE INDEX idx_asset_lifecycle_events_asset_time
    ON core.asset_lifecycle_events (asset_external_id, occurred_at, id);

CREATE INDEX idx_asset_lifecycle_events_project_time
    ON core.asset_lifecycle_events (project_external_id, occurred_at, id);
