CREATE TABLE core.export_staging_objects (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    source_storage_object_id uuid NOT NULL,
    staging_storage_object_id uuid NOT NULL UNIQUE,
    source_sha256 char(64) NOT NULL,
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_export_staging_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_export_staging_source_storage FOREIGN KEY (source_storage_object_id)
        REFERENCES core.storage_objects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_export_staging_output_storage FOREIGN KEY (staging_storage_object_id)
        REFERENCES core.storage_objects(id) ON DELETE RESTRICT,
    CONSTRAINT ck_export_staging_external CHECK (external_id ~ '^EXS-[0-9]{6,20}$'),
    CONSTRAINT ck_export_staging_distinct_storage CHECK (
        source_storage_object_id <> staging_storage_object_id
    ),
    CONSTRAINT ck_export_staging_source_sha CHECK (source_sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_export_staging_expiry CHECK (expires_at > created_at),
    CONSTRAINT ck_export_staging_revision CHECK (revision >= 1),
    CONSTRAINT ck_export_staging_audit_time CHECK (updated_at >= created_at)
);

CREATE INDEX idx_export_staging_project_expiry
    ON core.export_staging_objects (project_id, expires_at, id);

CREATE INDEX idx_export_staging_source
    ON core.export_staging_objects (source_storage_object_id, created_at, id);
