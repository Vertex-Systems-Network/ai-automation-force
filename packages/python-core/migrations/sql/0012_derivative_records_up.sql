CREATE TABLE core.derivative_records (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    source_asset_id uuid NOT NULL,
    output_asset_id uuid,
    output_storage_object_id uuid,
    job_id uuid NOT NULL,
    derivative_kind text NOT NULL,
    spec_json jsonb NOT NULL,
    operation_fingerprint text NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    completed_at timestamptz,
    error_code text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_derivative_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_derivative_source_asset FOREIGN KEY (source_asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT fk_derivative_output_asset FOREIGN KEY (output_asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT fk_derivative_output_storage FOREIGN KEY (output_storage_object_id)
        REFERENCES core.storage_objects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_derivative_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT ck_derivative_external CHECK (external_id ~ '^DRV-[0-9]{6,20}$'),
    CONSTRAINT ck_derivative_fingerprint CHECK (operation_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_derivative_revision CHECK (revision >= 1),
    CONSTRAINT ck_derivative_kind CHECK (
        derivative_kind IN (
            'thumbnail', 'image-preview', 'audio-waveform',
            'audio-preview', 'video-proxy', 'video-poster'
        )
    ),
    CONSTRAINT ck_derivative_status CHECK (
        status IN ('planned', 'running', 'completed', 'failed', 'cancelled')
    ),
    CONSTRAINT ck_derivative_completion CHECK (
        (status = 'completed' AND completed_at IS NOT NULL
            AND output_asset_id IS NOT NULL AND output_storage_object_id IS NOT NULL)
        OR
        (status <> 'completed' AND completed_at IS NULL
            AND output_asset_id IS NULL AND output_storage_object_id IS NULL)
    ),
    CONSTRAINT ck_derivative_error CHECK (
        (status = 'failed' AND error_code IS NOT NULL)
        OR (status <> 'failed' AND error_code IS NULL)
    ),
    CONSTRAINT ck_derivative_chronology CHECK (
        updated_at >= created_at
        AND (completed_at IS NULL OR completed_at >= created_at)
    ),
    CONSTRAINT ck_derivative_distinct_output CHECK (
        output_asset_id IS NULL OR output_asset_id <> source_asset_id
    ),
    CONSTRAINT uq_derivative_operation UNIQUE (
        project_id, source_asset_id, operation_fingerprint
    )
);

CREATE INDEX idx_derivative_source_status
    ON core.derivative_records (source_asset_id, status, updated_at, id);

CREATE INDEX idx_derivative_job
    ON core.derivative_records (job_id);

CREATE INDEX idx_derivative_output_asset
    ON core.derivative_records (output_asset_id)
    WHERE output_asset_id IS NOT NULL;
