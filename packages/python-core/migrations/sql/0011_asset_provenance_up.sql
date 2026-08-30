CREATE TABLE core.asset_provenance_records (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    asset_id uuid NOT NULL,
    project_id uuid,
    storage_object_id uuid,
    source_kind text NOT NULL,
    source_reference text,
    import_reference text,
    provider_reference text,
    content_sha256 text NOT NULL,
    rights_record_id uuid,
    created_at timestamptz NOT NULL,
    CONSTRAINT fk_asset_provenance_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asset_provenance_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asset_provenance_storage FOREIGN KEY (storage_object_id)
        REFERENCES core.storage_objects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asset_provenance_rights FOREIGN KEY (rights_record_id)
        REFERENCES core.rights_records(id) ON DELETE RESTRICT,
    CONSTRAINT ck_asset_provenance_external CHECK (external_id ~ '^PRV-[0-9]{6,20}$'),
    CONSTRAINT ck_asset_provenance_source_kind CHECK (
        source_kind IN ('upload', 'import', 'provider', 'derived')
    ),
    CONSTRAINT ck_asset_provenance_sha256 CHECK (content_sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_asset_provenance_upload_evidence CHECK (
        source_kind <> 'upload' OR storage_object_id IS NOT NULL
    ),
    CONSTRAINT ck_asset_provenance_import_evidence CHECK (
        source_kind <> 'import' OR import_reference IS NOT NULL
    ),
    CONSTRAINT ck_asset_provenance_provider_evidence CHECK (
        source_kind <> 'provider' OR provider_reference IS NOT NULL
    )
);

CREATE INDEX idx_asset_provenance_asset_created
    ON core.asset_provenance_records (asset_id, created_at, id);

CREATE INDEX idx_asset_provenance_storage
    ON core.asset_provenance_records (storage_object_id)
    WHERE storage_object_id IS NOT NULL;
