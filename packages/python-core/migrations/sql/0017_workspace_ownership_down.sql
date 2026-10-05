DROP INDEX IF EXISTS core.ix_voice_profiles_workspace;
DROP INDEX IF EXISTS core.ix_style_profiles_workspace;
DROP INDEX IF EXISTS core.ix_props_workspace;
DROP INDEX IF EXISTS core.ix_locations_workspace;
DROP INDEX IF EXISTS core.ix_worlds_workspace;
DROP INDEX IF EXISTS core.ix_characters_workspace;
DROP INDEX IF EXISTS core.ix_projects_workspace;

ALTER TABLE core.voice_profiles DROP CONSTRAINT IF EXISTS fk_voice_workspace;
ALTER TABLE core.style_profiles DROP CONSTRAINT IF EXISTS fk_style_workspace;
ALTER TABLE core.props DROP CONSTRAINT IF EXISTS fk_prop_workspace;
ALTER TABLE core.locations DROP CONSTRAINT IF EXISTS fk_location_workspace;
ALTER TABLE core.worlds DROP CONSTRAINT IF EXISTS fk_world_workspace;
ALTER TABLE core.characters DROP CONSTRAINT IF EXISTS fk_character_workspace;
ALTER TABLE core.projects DROP CONSTRAINT IF EXISTS fk_project_workspace;

ALTER TABLE core.voice_profiles DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE core.style_profiles DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE core.props DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE core.locations DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE core.worlds DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE core.characters DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE core.projects DROP COLUMN IF EXISTS workspace_id;

DROP TABLE IF EXISTS core.workspaces;
