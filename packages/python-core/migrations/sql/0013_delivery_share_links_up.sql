CREATE TABLE core.delivery_share_links (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    token_sha256 char(64) NOT NULL UNIQUE,
    allow_download boolean NOT NULL DEFAULT false,
    allow_stream boolean NOT NULL DEFAULT false,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz,
    max_uses bigint,
    use_count bigint NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_delivery_share_link_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_delivery_share_link_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT ck_delivery_share_link_external CHECK (
        char_length(external_id) BETWEEN 8 AND 160
    ),
    CONSTRAINT ck_delivery_share_link_token CHECK (
        token_sha256 ~ '^[a-f0-9]{64}$'
    ),
    CONSTRAINT ck_delivery_share_link_modes CHECK (
        allow_download OR allow_stream
    ),
    CONSTRAINT ck_delivery_share_link_max_uses CHECK (
        max_uses IS NULL OR max_uses BETWEEN 1 AND 1000000
    ),
    CONSTRAINT ck_delivery_share_link_use_count CHECK (
        use_count >= 0 AND (max_uses IS NULL OR use_count <= max_uses)
    ),
    CONSTRAINT ck_delivery_share_link_expiry CHECK (
        expires_at > created_at
    ),
    CONSTRAINT ck_delivery_share_link_revocation CHECK (
        revoked_at IS NULL OR (revoked_at >= created_at AND revoked_at <= expires_at)
    ),
    CONSTRAINT ck_delivery_share_link_revision CHECK (revision >= 1),
    CONSTRAINT ck_delivery_share_link_audit_time CHECK (updated_at >= created_at)
);

CREATE INDEX idx_delivery_share_links_asset_expiry
    ON core.delivery_share_links (project_id, asset_id, expires_at, id);

CREATE INDEX idx_delivery_share_links_active
    ON core.delivery_share_links (expires_at, id)
    WHERE revoked_at IS NULL;
