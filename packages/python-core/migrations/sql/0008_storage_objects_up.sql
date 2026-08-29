CREATE TABLE core.storage_objects (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid,
    backend text NOT NULL,
    bucket text,
    object_key text NOT NULL,
    sha256 char(64) NOT NULL,
    mime_type text NOT NULL,
    size_bytes bigint NOT NULL,
    region text,
    etag text,
    version_id text,
    original_filename text,
    lifecycle_class text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_storage_object_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT ck_storage_object_backend CHECK (backend IN ('filesystem', 's3')),
    CONSTRAINT ck_storage_object_location CHECK (
        (backend = 's3' AND bucket IS NOT NULL)
        OR (backend = 'filesystem' AND bucket IS NULL)
    ),
    CONSTRAINT ck_storage_object_sha CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_storage_object_size CHECK (size_bytes >= 0),
    CONSTRAINT ck_storage_object_lifecycle_class CHECK (
        char_length(lifecycle_class) BETWEEN 1 AND 80
    ),
    CONSTRAINT ck_storage_object_revision CHECK (revision >= 1),
    CONSTRAINT ck_storage_object_audit_time CHECK (updated_at >= created_at)
);

CREATE UNIQUE INDEX uq_storage_objects_location
    ON core.storage_objects (backend, COALESCE(bucket, ''), object_key);

CREATE INDEX idx_storage_objects_project
    ON core.storage_objects (project_id, created_at, id);
