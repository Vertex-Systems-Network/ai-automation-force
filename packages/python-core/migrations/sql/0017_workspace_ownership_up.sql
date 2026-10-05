CREATE TABLE core.workspaces (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    name text NOT NULL,
    slug text NOT NULL UNIQUE,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT ck_workspace_name CHECK (length(btrim(name)) > 0),
    CONSTRAINT ck_workspace_slug CHECK (length(btrim(slug)) > 0),
    CONSTRAINT ck_workspace_revision CHECK (revision >= 1),
    CONSTRAINT ck_workspace_audit_time CHECK (updated_at >= created_at)
);

INSERT INTO core.workspaces (
    id, external_id, name, slug, created_at, updated_at, created_by
)
VALUES (
    '00000000-0000-4000-8000-000000000017',
    'workspace-bootstrap-legacy',
    'Legacy Bootstrap Workspace',
    'legacy-bootstrap',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    '20261005_0017'
)
ON CONFLICT (external_id) DO NOTHING;

ALTER TABLE core.projects ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';
ALTER TABLE core.characters ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';
ALTER TABLE core.worlds ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';
ALTER TABLE core.locations ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';
ALTER TABLE core.props ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';
ALTER TABLE core.style_profiles ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';
ALTER TABLE core.voice_profiles ADD COLUMN workspace_id uuid DEFAULT '00000000-0000-4000-8000-000000000017';

UPDATE core.projects SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;
UPDATE core.characters SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;
UPDATE core.worlds SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;
UPDATE core.locations SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;
UPDATE core.props SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;
UPDATE core.style_profiles SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;
UPDATE core.voice_profiles SET workspace_id = '00000000-0000-4000-8000-000000000017' WHERE workspace_id IS NULL;

ALTER TABLE core.projects ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE core.characters ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE core.worlds ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE core.locations ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE core.props ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE core.style_profiles ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE core.voice_profiles ALTER COLUMN workspace_id SET NOT NULL;

ALTER TABLE core.projects ADD CONSTRAINT fk_project_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;
ALTER TABLE core.characters ADD CONSTRAINT fk_character_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;
ALTER TABLE core.worlds ADD CONSTRAINT fk_world_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;
ALTER TABLE core.locations ADD CONSTRAINT fk_location_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;
ALTER TABLE core.props ADD CONSTRAINT fk_prop_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;
ALTER TABLE core.style_profiles ADD CONSTRAINT fk_style_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;
ALTER TABLE core.voice_profiles ADD CONSTRAINT fk_voice_workspace
    FOREIGN KEY (workspace_id) REFERENCES core.workspaces(id) ON DELETE RESTRICT;

CREATE INDEX ix_projects_workspace ON core.projects(workspace_id);
CREATE INDEX ix_characters_workspace ON core.characters(workspace_id);
CREATE INDEX ix_worlds_workspace ON core.worlds(workspace_id);
CREATE INDEX ix_locations_workspace ON core.locations(workspace_id);
CREATE INDEX ix_props_workspace ON core.props(workspace_id);
CREATE INDEX ix_style_profiles_workspace ON core.style_profiles(workspace_id);
CREATE INDEX ix_voice_profiles_workspace ON core.voice_profiles(workspace_id);
