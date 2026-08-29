CREATE TABLE core.quarantine_inspections (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    upload_session_id uuid NOT NULL,
    project_id uuid NOT NULL,
    storage_object_external_id text NOT NULL,
    claimed_mime_type text NOT NULL,
    detected_mime_type text,
    expected_size_bytes bigint NOT NULL,
    observed_size_bytes bigint NOT NULL DEFAULT 0,
    status text NOT NULL DEFAULT 'pending',
    rejection_codes jsonb NOT NULL DEFAULT '[]'::jsonb,
    probe jsonb,
    threat_scan jsonb,
    inspected_at timestamptz,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_quarantine_upload_session FOREIGN KEY (upload_session_id)
        REFERENCES core.upload_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_quarantine_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT uq_quarantine_upload_external UNIQUE (upload_session_id, external_id),
    CONSTRAINT ck_quarantine_external CHECK (external_id ~ '^QIN-[0-9]{6,20}$'),
    CONSTRAINT ck_quarantine_storage_external
        CHECK (storage_object_external_id ~ '^STO-[0-9]{6,20}$'),
    CONSTRAINT ck_quarantine_expected_size CHECK (expected_size_bytes > 0),
    CONSTRAINT ck_quarantine_observed_size CHECK (observed_size_bytes >= 0),
    CONSTRAINT ck_quarantine_status CHECK (
        status IN ('pending', 'inspecting', 'accepted', 'rejected')
    ),
    CONSTRAINT ck_quarantine_rejection_codes_array CHECK (
        jsonb_typeof(rejection_codes) = 'array'
    ),
    CONSTRAINT ck_quarantine_terminal CHECK (
        (
            status IN ('pending', 'inspecting')
            AND inspected_at IS NULL
            AND jsonb_array_length(rejection_codes) = 0
        )
        OR (
            status = 'accepted'
            AND inspected_at IS NOT NULL
            AND jsonb_array_length(rejection_codes) = 0
        )
        OR (
            status = 'rejected'
            AND inspected_at IS NOT NULL
            AND jsonb_array_length(rejection_codes) > 0
        )
    ),
    CONSTRAINT ck_quarantine_revision CHECK (revision >= 1),
    CONSTRAINT ck_quarantine_audit_time CHECK (updated_at >= created_at)
);

CREATE INDEX idx_quarantine_project_status
    ON core.quarantine_inspections (project_id, status, created_at, id);

CREATE INDEX idx_quarantine_upload_status
    ON core.quarantine_inspections (upload_session_id, status, id);
