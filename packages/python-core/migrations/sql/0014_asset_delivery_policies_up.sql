CREATE TABLE core.asset_delivery_policies (
    id uuid PRIMARY KEY,
    asset_id uuid NOT NULL UNIQUE,
    project_id uuid NOT NULL,
    access_class text NOT NULL DEFAULT 'private',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_asset_delivery_policy_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE CASCADE,
    CONSTRAINT fk_asset_delivery_policy_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT ck_asset_delivery_policy_access CHECK (
        access_class IN ('private', 'public')
    ),
    CONSTRAINT ck_asset_delivery_policy_revision CHECK (revision >= 1),
    CONSTRAINT ck_asset_delivery_policy_audit CHECK (updated_at >= created_at)
);

CREATE INDEX idx_asset_delivery_policies_project
    ON core.asset_delivery_policies (project_id, access_class, asset_id);
