CREATE TABLE core.upload_sessions (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    storage_object_external_id text NOT NULL,
    backend text NOT NULL,
    bucket text,
    object_key text NOT NULL,
    expected_size_bytes bigint NOT NULL,
    expected_mime_type text NOT NULL,
    original_filename text,
    mode text NOT NULL,
    part_size_bytes bigint,
    backend_upload_id text,
    quota_reservation_id text,
    creation_idempotency_key text NOT NULL,
    expires_at timestamptz NOT NULL,
    status text NOT NULL DEFAULT 'open',
    observed_size_bytes bigint,
    observed_etag text,
    observed_version_id text,
    completed_at timestamptz,
    aborted_at timestamptz,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_upload_session_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT uq_upload_session_project_idempotency
        UNIQUE (project_id, creation_idempotency_key),
    CONSTRAINT ck_upload_session_external CHECK (external_id ~ '^UPS-[0-9]{6,20}$'),
    CONSTRAINT ck_upload_storage_object_external
        CHECK (storage_object_external_id ~ '^STO-[0-9]{6,20}$'),
    CONSTRAINT ck_upload_backend CHECK (backend IN ('filesystem', 's3')),
    CONSTRAINT ck_upload_location CHECK (
        (backend = 's3' AND bucket IS NOT NULL)
        OR (backend = 'filesystem' AND bucket IS NULL)
    ),
    CONSTRAINT ck_upload_expected_size CHECK (expected_size_bytes > 0),
    CONSTRAINT ck_upload_mode CHECK (mode IN ('single', 'multipart')),
    CONSTRAINT ck_upload_part_size CHECK (
        (mode = 'single' AND part_size_bytes IS NULL AND backend_upload_id IS NULL)
        OR (
            mode = 'multipart'
            AND part_size_bytes IS NOT NULL
            AND part_size_bytes > 0
            AND part_size_bytes <= expected_size_bytes
        )
    ),
    CONSTRAINT ck_upload_status CHECK (
        status IN ('open', 'uploading', 'completed', 'aborted', 'expired')
    ),
    CONSTRAINT ck_upload_completion CHECK (
        (status = 'completed' AND completed_at IS NOT NULL
            AND observed_size_bytes = expected_size_bytes)
        OR (status <> 'completed' AND completed_at IS NULL AND observed_size_bytes IS NULL)
    ),
    CONSTRAINT ck_upload_abort CHECK (
        (status = 'aborted' AND aborted_at IS NOT NULL)
        OR (status <> 'aborted' AND aborted_at IS NULL)
    ),
    CONSTRAINT ck_upload_expiry CHECK (expires_at > created_at),
    CONSTRAINT ck_upload_revision CHECK (revision >= 1),
    CONSTRAINT ck_upload_audit_time CHECK (updated_at >= created_at)
);

CREATE UNIQUE INDEX uq_upload_sessions_location
    ON core.upload_sessions (backend, COALESCE(bucket, ''), object_key);

CREATE INDEX idx_upload_sessions_project_status
    ON core.upload_sessions (project_id, status, expires_at, id);

CREATE TABLE core.upload_parts (
    id uuid PRIMARY KEY,
    upload_session_id uuid NOT NULL,
    part_number integer NOT NULL,
    size_bytes bigint NOT NULL,
    etag text,
    checksum_sha256 char(64),
    recorded_at timestamptz NOT NULL,
    CONSTRAINT fk_upload_part_session FOREIGN KEY (upload_session_id)
        REFERENCES core.upload_sessions(id) ON DELETE CASCADE,
    CONSTRAINT uq_upload_part_number UNIQUE (upload_session_id, part_number),
    CONSTRAINT ck_upload_part_number CHECK (part_number BETWEEN 1 AND 10000),
    CONSTRAINT ck_upload_part_size CHECK (size_bytes > 0),
    CONSTRAINT ck_upload_part_checksum CHECK (
        checksum_sha256 IS NULL OR checksum_sha256 ~ '^[a-f0-9]{64}$'
    )
);

CREATE INDEX idx_upload_parts_session
    ON core.upload_parts (upload_session_id, part_number);

CREATE TABLE core.upload_session_commands (
    id uuid PRIMARY KEY,
    upload_session_id uuid NOT NULL,
    command_type text NOT NULL,
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    result_status text NOT NULL,
    result_revision integer NOT NULL,
    occurred_at timestamptz NOT NULL,
    CONSTRAINT fk_upload_command_session FOREIGN KEY (upload_session_id)
        REFERENCES core.upload_sessions(id) ON DELETE CASCADE,
    CONSTRAINT uq_upload_command_idempotency
        UNIQUE (upload_session_id, command_type, idempotency_key),
    CONSTRAINT ck_upload_command_type CHECK (command_type IN ('complete', 'abort')),
    CONSTRAINT ck_upload_command_fingerprint CHECK (
        request_fingerprint ~ '^[a-f0-9]{64}$'
    ),
    CONSTRAINT ck_upload_command_status CHECK (
        result_status IN ('completed', 'aborted', 'expired')
    ),
    CONSTRAINT ck_upload_command_revision CHECK (result_revision >= 1)
);
