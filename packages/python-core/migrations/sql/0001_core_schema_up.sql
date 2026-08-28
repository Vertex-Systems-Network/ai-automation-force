CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE core.rights_records (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    subject_type text NOT NULL,
    subject_id text NOT NULL,
    provider_id text,
    model_provider_id text,
    model_id text,
    plan_or_tier text,
    commercial_use text NOT NULL DEFAULT 'unknown',
    watermark_required boolean,
    source_basis text,
    consent_reference text,
    evidence_urls text[] NOT NULL DEFAULT '{}',
    verified_at timestamptz,
    publication_blocked boolean NOT NULL DEFAULT true,
    notes text[] NOT NULL DEFAULT '{}',
    CONSTRAINT ck_rights_fail_closed CHECK (publication_blocked OR commercial_use = 'allowed')
);

CREATE TABLE core.style_profiles (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    name text NOT NULL,
    treatment text[] NOT NULL DEFAULT '{}',
    palette text[] NOT NULL DEFAULT '{}',
    lighting_rules text[] NOT NULL DEFAULT '{}',
    camera_rules text[] NOT NULL DEFAULT '{}',
    texture_rules text[] NOT NULL DEFAULT '{}',
    negative_constraints text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT ck_style_revision CHECK (revision >= 1),
    CONSTRAINT ck_style_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.projects (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    title text NOT NULL,
    status text NOT NULL DEFAULT 'draft',
    audience jsonb NOT NULL,
    cast jsonb NOT NULL,
    content_format text NOT NULL,
    custom_content_format text,
    language text NOT NULL,
    target_duration_seconds integer NOT NULL,
    output jsonb NOT NULL,
    creative jsonb NOT NULL,
    provider_policy jsonb NOT NULL,
    content_id uuid,
    active_timeline_id uuid,
    tags text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT ck_project_duration CHECK (target_duration_seconds BETWEEN 60 AND 10800),
    CONSTRAINT ck_project_custom_format CHECK (
        (content_format = 'custom' AND custom_content_format IS NOT NULL)
        OR (content_format <> 'custom' AND custom_content_format IS NULL)
    ),
    CONSTRAINT ck_project_revision CHECK (revision >= 1),
    CONSTRAINT ck_project_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.contents (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    active_version_id uuid,
    project_id uuid,
    status text NOT NULL DEFAULT 'draft',
    source_legacy_package_path text,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT uq_contents_id_project UNIQUE (id, project_id),
    CONSTRAINT fk_contents_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT ck_content_revision CHECK (revision >= 1),
    CONSTRAINT ck_content_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.content_versions (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    content_id uuid NOT NULL,
    version integer NOT NULL,
    title text NOT NULL,
    content_format text NOT NULL,
    custom_content_format text,
    language text NOT NULL,
    target_duration_seconds integer NOT NULL,
    objective jsonb NOT NULL,
    premise text NOT NULL DEFAULT '',
    hook text NOT NULL DEFAULT '',
    script_or_lyrics text NOT NULL,
    structure_map text[] NOT NULL DEFAULT '{}',
    pronunciation_notes text[] NOT NULL DEFAULT '{}',
    tags text[] NOT NULL DEFAULT '{}',
    originality_fingerprint text,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_content_versions_content FOREIGN KEY (content_id)
        REFERENCES core.contents(id) ON DELETE RESTRICT,
    CONSTRAINT uq_content_versions_owner_version UNIQUE (content_id, version),
    CONSTRAINT uq_content_versions_id_owner UNIQUE (id, content_id),
    CONSTRAINT ck_content_version_version CHECK (version >= 1),
    CONSTRAINT ck_content_version_duration CHECK (target_duration_seconds BETWEEN 60 AND 10800),
    CONSTRAINT ck_content_version_custom_format CHECK (
        (content_format = 'custom' AND custom_content_format IS NOT NULL)
        OR (content_format <> 'custom' AND custom_content_format IS NULL)
    ),
    CONSTRAINT ck_content_version_revision CHECK (revision >= 1),
    CONSTRAINT ck_content_version_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.voice_profiles (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    name text NOT NULL,
    presentation text NOT NULL,
    language text NOT NULL,
    timbre text,
    pace text,
    articulation text,
    emotion_defaults text[] NOT NULL DEFAULT '{}',
    pronunciation_rules text[] NOT NULL DEFAULT '{}',
    impersonation_prohibited boolean NOT NULL DEFAULT true,
    provider_voice_refs jsonb NOT NULL DEFAULT '{}',
    rights_record_id uuid,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_voice_rights FOREIGN KEY (rights_record_id)
        REFERENCES core.rights_records(id) ON DELETE RESTRICT,
    CONSTRAINT ck_voice_revision CHECK (revision >= 1),
    CONSTRAINT ck_voice_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.characters (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    name text NOT NULL,
    active_version_id uuid NOT NULL,
    reusable boolean NOT NULL DEFAULT true,
    rights_record_id uuid,
    tags text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_character_rights FOREIGN KEY (rights_record_id)
        REFERENCES core.rights_records(id) ON DELETE RESTRICT,
    CONSTRAINT ck_character_revision CHECK (revision >= 1),
    CONSTRAINT ck_character_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.character_versions (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    character_id uuid NOT NULL,
    version integer NOT NULL,
    display_name text NOT NULL,
    character_type text NOT NULL,
    species text,
    apparent_age text,
    gender_presentation text,
    personality_traits text[] NOT NULL DEFAULT '{}',
    movement_style text,
    voice_profile_id uuid,
    identity_constraints text[] NOT NULL DEFAULT '{}',
    status text NOT NULL DEFAULT 'candidate',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_character_version_owner FOREIGN KEY (character_id)
        REFERENCES core.characters(id) ON DELETE RESTRICT,
    CONSTRAINT fk_character_version_voice FOREIGN KEY (voice_profile_id)
        REFERENCES core.voice_profiles(id) ON DELETE RESTRICT,
    CONSTRAINT uq_character_versions_owner_version UNIQUE (character_id, version),
    CONSTRAINT uq_character_versions_id_owner UNIQUE (id, character_id),
    CONSTRAINT ck_character_version_version CHECK (version >= 1),
    CONSTRAINT ck_character_version_revision CHECK (revision >= 1),
    CONSTRAINT ck_character_version_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.character_looks (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    character_version_id uuid NOT NULL,
    position integer NOT NULL,
    name text NOT NULL,
    wardrobe text[] NOT NULL DEFAULT '{}',
    accessories text[] NOT NULL DEFAULT '{}',
    hair text,
    eyes text,
    palette text[] NOT NULL DEFAULT '{}',
    expression_defaults text[] NOT NULL DEFAULT '{}',
    body_notes text[] NOT NULL DEFAULT '{}',
    prohibited_mutations text[] NOT NULL DEFAULT '{}',
    CONSTRAINT fk_character_look_version FOREIGN KEY (character_version_id)
        REFERENCES core.character_versions(id) ON DELETE RESTRICT,
    CONSTRAINT uq_character_look_position UNIQUE (character_version_id, position),
    CONSTRAINT uq_character_look_id_version UNIQUE (id, character_version_id),
    CONSTRAINT ck_character_look_position CHECK (position >= 0)
);

CREATE TABLE core.worlds (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    style_profile_id uuid,
    rules text[] NOT NULL DEFAULT '{}',
    forbidden_mutations text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_world_style FOREIGN KEY (style_profile_id)
        REFERENCES core.style_profiles(id) ON DELETE RESTRICT,
    CONSTRAINT ck_world_revision CHECK (revision >= 1),
    CONSTRAINT ck_world_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.locations (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    world_id uuid,
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    environment_constraints text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_location_world FOREIGN KEY (world_id)
        REFERENCES core.worlds(id) ON DELETE RESTRICT,
    CONSTRAINT ck_location_revision CHECK (revision >= 1),
    CONSTRAINT ck_location_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.props (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    name text NOT NULL,
    description text NOT NULL DEFAULT '',
    identity_constraints text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT ck_prop_revision CHECK (revision >= 1),
    CONSTRAINT ck_prop_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.timelines (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    version integer NOT NULL,
    duration_seconds numeric(12,3) NOT NULL,
    fps numeric(8,3) NOT NULL DEFAULT 24,
    otio_asset_id uuid,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_timeline_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT uq_timeline_owner_version UNIQUE (project_id, version),
    CONSTRAINT uq_timeline_id_project UNIQUE (id, project_id),
    CONSTRAINT ck_timeline_version CHECK (version >= 1),
    CONSTRAINT ck_timeline_duration CHECK (duration_seconds BETWEEN 60 AND 10800),
    CONSTRAINT ck_timeline_fps CHECK (fps > 0 AND fps <= 120),
    CONSTRAINT ck_timeline_revision CHECK (revision >= 1),
    CONSTRAINT ck_timeline_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.timeline_tracks (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    timeline_id uuid NOT NULL,
    position integer NOT NULL,
    kind text NOT NULL,
    name text NOT NULL,
    muted boolean NOT NULL DEFAULT false,
    locked boolean NOT NULL DEFAULT false,
    CONSTRAINT fk_timeline_track_owner FOREIGN KEY (timeline_id)
        REFERENCES core.timelines(id) ON DELETE RESTRICT,
    CONSTRAINT uq_timeline_track_position UNIQUE (timeline_id, position),
    CONSTRAINT ck_timeline_track_position CHECK (position >= 0)
);

CREATE TABLE core.acts (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    timeline_id uuid NOT NULL,
    "order" integer NOT NULL,
    title text NOT NULL,
    target_duration_seconds numeric(12,3) NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_act_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_act_timeline_owner FOREIGN KEY (timeline_id, project_id)
        REFERENCES core.timelines(id, project_id) ON DELETE RESTRICT,
    CONSTRAINT uq_act_timeline_order UNIQUE (timeline_id, "order"),
    CONSTRAINT ck_act_order CHECK ("order" >= 1),
    CONSTRAINT ck_act_duration CHECK (target_duration_seconds > 0),
    CONSTRAINT ck_act_revision CHECK (revision >= 1),
    CONSTRAINT ck_act_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.sequences (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    act_id uuid NOT NULL,
    "order" integer NOT NULL,
    title text NOT NULL,
    target_duration_seconds numeric(12,3) NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_sequence_act FOREIGN KEY (act_id)
        REFERENCES core.acts(id) ON DELETE RESTRICT,
    CONSTRAINT uq_sequence_act_order UNIQUE (act_id, "order"),
    CONSTRAINT ck_sequence_order CHECK ("order" >= 1),
    CONSTRAINT ck_sequence_duration CHECK (target_duration_seconds > 0),
    CONSTRAINT ck_sequence_revision CHECK (revision >= 1),
    CONSTRAINT ck_sequence_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.scenes (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    sequence_id uuid NOT NULL,
    "order" integer NOT NULL,
    title text NOT NULL,
    summary text NOT NULL DEFAULT '',
    location_id uuid,
    target_duration_seconds numeric(12,3) NOT NULL,
    incoming_state jsonb NOT NULL DEFAULT '{}',
    outgoing_state jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_scene_sequence FOREIGN KEY (sequence_id)
        REFERENCES core.sequences(id) ON DELETE RESTRICT,
    CONSTRAINT fk_scene_location FOREIGN KEY (location_id)
        REFERENCES core.locations(id) ON DELETE RESTRICT,
    CONSTRAINT uq_scene_sequence_order UNIQUE (sequence_id, "order"),
    CONSTRAINT ck_scene_order CHECK ("order" >= 1),
    CONSTRAINT ck_scene_duration CHECK (target_duration_seconds > 0),
    CONSTRAINT ck_scene_revision CHECK (revision >= 1),
    CONSTRAINT ck_scene_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.shots (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    scene_id uuid NOT NULL,
    "order" integer NOT NULL,
    start_seconds numeric(12,3) NOT NULL,
    duration_seconds numeric(12,3) NOT NULL,
    purpose text NOT NULL DEFAULT '',
    action text NOT NULL DEFAULT '',
    location_id uuid,
    camera jsonb NOT NULL DEFAULT '{}',
    incoming_state jsonb NOT NULL DEFAULT '{}',
    outgoing_state jsonb NOT NULL DEFAULT '{}',
    first_frame_asset_id uuid,
    end_frame_asset_id uuid,
    selected_take_id uuid,
    transition_in text NOT NULL DEFAULT 'cut',
    transition_out text NOT NULL DEFAULT 'cut',
    handles_seconds numeric(8,3) NOT NULL DEFAULT 0,
    generation_notes text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_shot_scene FOREIGN KEY (scene_id)
        REFERENCES core.scenes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_shot_location FOREIGN KEY (location_id)
        REFERENCES core.locations(id) ON DELETE RESTRICT,
    CONSTRAINT uq_shot_scene_order UNIQUE (scene_id, "order"),
    CONSTRAINT ck_shot_order CHECK ("order" >= 1),
    CONSTRAINT ck_shot_start CHECK (start_seconds >= 0),
    CONSTRAINT ck_shot_duration CHECK (duration_seconds > 0),
    CONSTRAINT ck_shot_handles CHECK (handles_seconds BETWEEN 0 AND 10),
    CONSTRAINT ck_shot_revision CHECK (revision >= 1),
    CONSTRAINT ck_shot_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.jobs (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    job_type text NOT NULL,
    status text NOT NULL DEFAULT 'queued',
    priority integer NOT NULL DEFAULT 50,
    idempotency_key text NOT NULL,
    parent_job_id uuid,
    shot_id uuid,
    content_id uuid,
    selected_attempt_id uuid,
    retry_budget_remaining integer NOT NULL DEFAULT 3,
    blocked_reason text,
    claimed_by text,
    lease_expires_at timestamptz,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_job_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_job_parent FOREIGN KEY (parent_job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT fk_job_shot FOREIGN KEY (shot_id)
        REFERENCES core.shots(id) ON DELETE RESTRICT,
    CONSTRAINT fk_job_content FOREIGN KEY (content_id)
        REFERENCES core.contents(id) ON DELETE RESTRICT,
    CONSTRAINT uq_job_project_idempotency UNIQUE (project_id, idempotency_key),
    CONSTRAINT uq_job_id_project UNIQUE (id, project_id),
    CONSTRAINT ck_job_priority CHECK (priority BETWEEN 0 AND 100),
    CONSTRAINT ck_job_retry_budget CHECK (retry_budget_remaining >= 0),
    CONSTRAINT ck_job_revision CHECK (revision >= 1),
    CONSTRAINT ck_job_audit_time CHECK (updated_at >= created_at),
    CONSTRAINT ck_job_no_self_parent CHECK (parent_job_id IS NULL OR parent_job_id <> id)
);

CREATE TABLE core.generation_attempts (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    job_id uuid NOT NULL,
    attempt_number integer NOT NULL,
    provider_id text NOT NULL,
    model_provider_id text NOT NULL,
    model_id text NOT NULL,
    capability text NOT NULL,
    access_class text NOT NULL,
    registry_verified_at timestamptz,
    request_project_id uuid NOT NULL,
    request_shot_id uuid,
    request_content_id uuid,
    prompt_id text,
    prompt_version text,
    request_constraints jsonb NOT NULL DEFAULT '{}',
    target_duration_seconds numeric(12,3),
    requires_commercial_rights boolean NOT NULL DEFAULT true,
    requires_character_continuity boolean NOT NULL DEFAULT false,
    request_idempotency_key text NOT NULL,
    provider_generation_id text,
    started_at timestamptz NOT NULL,
    finished_at timestamptz,
    status text NOT NULL DEFAULT 'running',
    normalized_error_code text,
    error_detail text,
    free_credits_used numeric(24,8),
    paid_cost numeric(24,8),
    currency char(3) NOT NULL DEFAULT 'USD',
    CONSTRAINT fk_attempt_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT fk_attempt_project FOREIGN KEY (request_project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_attempt_shot FOREIGN KEY (request_shot_id)
        REFERENCES core.shots(id) ON DELETE RESTRICT,
    CONSTRAINT fk_attempt_content FOREIGN KEY (request_content_id)
        REFERENCES core.contents(id) ON DELETE RESTRICT,
    CONSTRAINT uq_attempt_job_number UNIQUE (job_id, attempt_number),
    CONSTRAINT uq_attempt_id_job UNIQUE (id, job_id),
    CONSTRAINT ck_attempt_number CHECK (attempt_number >= 1),
    CONSTRAINT ck_attempt_duration CHECK (target_duration_seconds IS NULL OR target_duration_seconds > 0),
    CONSTRAINT ck_attempt_finished CHECK (finished_at IS NULL OR finished_at >= started_at),
    CONSTRAINT ck_attempt_free_credits CHECK (free_credits_used IS NULL OR free_credits_used >= 0),
    CONSTRAINT ck_attempt_paid_cost CHECK (paid_cost IS NULL OR paid_cost >= 0)
);

CREATE TABLE core.assets (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid,
    kind text NOT NULL,
    uri text NOT NULL,
    sha256 char(64) NOT NULL,
    mime_type text NOT NULL,
    size_bytes bigint NOT NULL,
    duration_seconds numeric(12,3),
    width integer,
    height integer,
    provider_id text,
    model_provider_id text,
    provider_model_id text,
    generation_attempt_id uuid,
    generation_output_position integer,
    rights_record_id uuid,
    canonical_status text NOT NULL DEFAULT 'candidate',
    retention_class text NOT NULL DEFAULT 'project',
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_asset_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asset_attempt FOREIGN KEY (generation_attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asset_rights FOREIGN KEY (rights_record_id)
        REFERENCES core.rights_records(id) ON DELETE RESTRICT,
    CONSTRAINT uq_asset_attempt_output UNIQUE (generation_attempt_id, generation_output_position),
    CONSTRAINT ck_asset_sha CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_asset_size CHECK (size_bytes >= 0),
    CONSTRAINT ck_asset_duration CHECK (duration_seconds IS NULL OR duration_seconds > 0),
    CONSTRAINT ck_asset_width CHECK (width IS NULL OR width > 0),
    CONSTRAINT ck_asset_height CHECK (height IS NULL OR height > 0),
    CONSTRAINT ck_asset_output_position CHECK (
        generation_output_position IS NULL OR generation_output_position >= 0
    ),
    CONSTRAINT ck_asset_output_owner CHECK (
        generation_output_position IS NULL OR generation_attempt_id IS NOT NULL
    ),
    CONSTRAINT ck_asset_revision CHECK (revision >= 1),
    CONSTRAINT ck_asset_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.takes (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    shot_id uuid NOT NULL,
    position integer NOT NULL,
    attempt_id uuid,
    asset_id uuid,
    canonical_status text NOT NULL DEFAULT 'candidate',
    continuity_score numeric(6,3),
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    created_by text,
    revision integer NOT NULL DEFAULT 1,
    CONSTRAINT fk_take_shot FOREIGN KEY (shot_id)
        REFERENCES core.shots(id) ON DELETE RESTRICT,
    CONSTRAINT fk_take_attempt FOREIGN KEY (attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_take_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_take_shot_position UNIQUE (shot_id, position),
    CONSTRAINT uq_take_id_shot UNIQUE (id, shot_id),
    CONSTRAINT ck_take_position CHECK (position >= 0),
    CONSTRAINT ck_take_continuity CHECK (
        continuity_score IS NULL OR continuity_score BETWEEN 0 AND 100
    ),
    CONSTRAINT ck_take_revision CHECK (revision >= 1),
    CONSTRAINT ck_take_audit_time CHECK (updated_at >= created_at)
);

CREATE TABLE core.qa_records (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    subject_type text NOT NULL,
    subject_id text NOT NULL,
    gate text NOT NULL,
    passed boolean NOT NULL,
    critical boolean NOT NULL DEFAULT false,
    score numeric(6,3),
    findings text[] NOT NULL DEFAULT '{}',
    reviewer text,
    created_at timestamptz NOT NULL,
    CONSTRAINT ck_qa_score CHECK (score IS NULL OR score BETWEEN 0 AND 100)
);

CREATE TABLE core.cost_records (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    job_id uuid,
    attempt_id uuid,
    provider_id text NOT NULL,
    model_provider_id text NOT NULL,
    model_id text NOT NULL,
    free_credits_used numeric(24,8) NOT NULL DEFAULT 0,
    paid_cost numeric(24,8) NOT NULL DEFAULT 0,
    currency char(3) NOT NULL DEFAULT 'USD',
    estimated boolean NOT NULL DEFAULT false,
    recorded_at timestamptz NOT NULL,
    CONSTRAINT fk_cost_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_cost_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT fk_cost_attempt FOREIGN KEY (attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT ck_cost_free_credits CHECK (free_credits_used >= 0),
    CONSTRAINT ck_cost_paid CHECK (paid_cost >= 0),
    CONSTRAINT ck_cost_actual_attempt CHECK (estimated OR attempt_id IS NOT NULL)
);

CREATE TABLE core.approvals (
    id uuid PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    schema_version smallint NOT NULL DEFAULT 1,
    project_id uuid NOT NULL,
    subject_type text NOT NULL,
    subject_id text NOT NULL,
    decision text NOT NULL,
    actor text NOT NULL,
    reason text,
    created_at timestamptz NOT NULL,
    CONSTRAINT fk_approval_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT
);

CREATE TABLE core.character_locks (
    id uuid PRIMARY KEY,
    character_id uuid NOT NULL UNIQUE,
    scope text NOT NULL,
    pinned_character_version_id uuid,
    pinned_look_id uuid,
    project_id uuid,
    scene_id uuid,
    CONSTRAINT fk_character_lock_owner FOREIGN KEY (character_id)
        REFERENCES core.characters(id) ON DELETE RESTRICT,
    CONSTRAINT fk_character_lock_version_owner FOREIGN KEY (
        pinned_character_version_id, character_id
    ) REFERENCES core.character_versions(id, character_id)
        ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_character_lock_look_version FOREIGN KEY (
        pinned_look_id, pinned_character_version_id
    ) REFERENCES core.character_looks(id, character_version_id)
        ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_character_lock_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_character_lock_scene FOREIGN KEY (scene_id)
        REFERENCES core.scenes(id) ON DELETE RESTRICT,
    CONSTRAINT ck_character_lock_scope CHECK (
        (scope = 'unlocked' AND pinned_character_version_id IS NULL)
        OR (scope <> 'unlocked' AND pinned_character_version_id IS NOT NULL)
    ),
    CONSTRAINT ck_character_lock_project CHECK (
        scope <> 'project' OR project_id IS NOT NULL
    ),
    CONSTRAINT ck_character_lock_look CHECK (
        scope <> 'look' OR pinned_look_id IS NOT NULL
    ),
    CONSTRAINT ck_character_lock_scene CHECK (
        scope <> 'scene' OR scene_id IS NOT NULL
    )
);

CREATE TABLE core.legacy_content_imports (
    id uuid PRIMARY KEY,
    mapping_version text NOT NULL,
    source_schema_version integer NOT NULL,
    source_content_external_id text NOT NULL,
    source_fingerprint_sha256 char(64) NOT NULL,
    import_key text NOT NULL UNIQUE,
    source_run_id text NOT NULL,
    source_package_path text NOT NULL,
    content_id uuid NOT NULL,
    content_version_id uuid NOT NULL,
    imported_at timestamptz NOT NULL,
    CONSTRAINT fk_legacy_import_content FOREIGN KEY (content_id)
        REFERENCES core.contents(id) ON DELETE RESTRICT,
    CONSTRAINT fk_legacy_import_version FOREIGN KEY (content_version_id)
        REFERENCES core.content_versions(id) ON DELETE RESTRICT,
    CONSTRAINT uq_legacy_import_source UNIQUE (
        mapping_version, source_content_external_id, source_fingerprint_sha256
    ),
    CONSTRAINT ck_legacy_import_sha CHECK (source_fingerprint_sha256 ~ '^[a-f0-9]{64}$')
);

CREATE TABLE core.project_characters (
    project_id uuid NOT NULL,
    character_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (project_id, character_id),
    CONSTRAINT fk_project_character_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_project_character_character FOREIGN KEY (character_id)
        REFERENCES core.characters(id) ON DELETE RESTRICT,
    CONSTRAINT uq_project_character_position UNIQUE (project_id, position),
    CONSTRAINT ck_project_character_position CHECK (position >= 0)
);

CREATE TABLE core.project_worlds (
    project_id uuid NOT NULL,
    world_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (project_id, world_id),
    CONSTRAINT fk_project_world_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_project_world_world FOREIGN KEY (world_id)
        REFERENCES core.worlds(id) ON DELETE RESTRICT,
    CONSTRAINT uq_project_world_position UNIQUE (project_id, position),
    CONSTRAINT ck_project_world_position CHECK (position >= 0)
);

CREATE TABLE core.project_props (
    project_id uuid NOT NULL,
    prop_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (project_id, prop_id),
    CONSTRAINT fk_project_prop_project FOREIGN KEY (project_id)
        REFERENCES core.projects(id) ON DELETE RESTRICT,
    CONSTRAINT fk_project_prop_prop FOREIGN KEY (prop_id)
        REFERENCES core.props(id) ON DELETE RESTRICT,
    CONSTRAINT uq_project_prop_position UNIQUE (project_id, position),
    CONSTRAINT ck_project_prop_position CHECK (position >= 0)
);

CREATE TABLE core.content_version_characters (
    content_version_id uuid NOT NULL,
    character_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (content_version_id, character_id),
    CONSTRAINT fk_content_character_version FOREIGN KEY (content_version_id)
        REFERENCES core.content_versions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_content_character_character FOREIGN KEY (character_id)
        REFERENCES core.characters(id) ON DELETE RESTRICT,
    CONSTRAINT uq_content_character_position UNIQUE (content_version_id, position),
    CONSTRAINT ck_content_character_position CHECK (position >= 0)
);

CREATE TABLE core.content_version_worlds (
    content_version_id uuid NOT NULL,
    world_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (content_version_id, world_id),
    CONSTRAINT fk_content_world_version FOREIGN KEY (content_version_id)
        REFERENCES core.content_versions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_content_world_world FOREIGN KEY (world_id)
        REFERENCES core.worlds(id) ON DELETE RESTRICT,
    CONSTRAINT uq_content_world_position UNIQUE (content_version_id, position),
    CONSTRAINT ck_content_world_position CHECK (position >= 0)
);

CREATE TABLE core.content_version_props (
    content_version_id uuid NOT NULL,
    prop_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (content_version_id, prop_id),
    CONSTRAINT fk_content_prop_version FOREIGN KEY (content_version_id)
        REFERENCES core.content_versions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_content_prop_prop FOREIGN KEY (prop_id)
        REFERENCES core.props(id) ON DELETE RESTRICT,
    CONSTRAINT uq_content_prop_position UNIQUE (content_version_id, position),
    CONSTRAINT ck_content_prop_position CHECK (position >= 0)
);

CREATE TABLE core.scene_characters (
    scene_id uuid NOT NULL,
    character_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (scene_id, character_id),
    CONSTRAINT fk_scene_character_scene FOREIGN KEY (scene_id)
        REFERENCES core.scenes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_scene_character_character FOREIGN KEY (character_id)
        REFERENCES core.characters(id) ON DELETE RESTRICT,
    CONSTRAINT uq_scene_character_position UNIQUE (scene_id, position),
    CONSTRAINT ck_scene_character_position CHECK (position >= 0)
);

CREATE TABLE core.shot_characters (
    shot_id uuid NOT NULL,
    character_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (shot_id, character_id),
    CONSTRAINT fk_shot_character_shot FOREIGN KEY (shot_id)
        REFERENCES core.shots(id) ON DELETE RESTRICT,
    CONSTRAINT fk_shot_character_character FOREIGN KEY (character_id)
        REFERENCES core.characters(id) ON DELETE RESTRICT,
    CONSTRAINT uq_shot_character_position UNIQUE (shot_id, position),
    CONSTRAINT ck_shot_character_position CHECK (position >= 0)
);

CREATE TABLE core.shot_props (
    shot_id uuid NOT NULL,
    prop_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (shot_id, prop_id),
    CONSTRAINT fk_shot_prop_shot FOREIGN KEY (shot_id)
        REFERENCES core.shots(id) ON DELETE RESTRICT,
    CONSTRAINT fk_shot_prop_prop FOREIGN KEY (prop_id)
        REFERENCES core.props(id) ON DELETE RESTRICT,
    CONSTRAINT uq_shot_prop_position UNIQUE (shot_id, position),
    CONSTRAINT ck_shot_prop_position CHECK (position >= 0)
);

CREATE TABLE core.shot_reference_assets (
    shot_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (shot_id, asset_id),
    CONSTRAINT fk_shot_ref_shot FOREIGN KEY (shot_id)
        REFERENCES core.shots(id) ON DELETE RESTRICT,
    CONSTRAINT fk_shot_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_shot_ref_position UNIQUE (shot_id, position),
    CONSTRAINT ck_shot_ref_position CHECK (position >= 0)
);

CREATE TABLE core.character_version_reference_assets (
    character_version_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (character_version_id, asset_id),
    CONSTRAINT fk_character_version_ref_owner FOREIGN KEY (character_version_id)
        REFERENCES core.character_versions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_character_version_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_character_version_ref_position UNIQUE (character_version_id, position),
    CONSTRAINT ck_character_version_ref_position CHECK (position >= 0)
);

CREATE TABLE core.character_look_reference_assets (
    character_look_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (character_look_id, asset_id),
    CONSTRAINT fk_character_look_ref_owner FOREIGN KEY (character_look_id)
        REFERENCES core.character_looks(id) ON DELETE RESTRICT,
    CONSTRAINT fk_character_look_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_character_look_ref_position UNIQUE (character_look_id, position),
    CONSTRAINT ck_character_look_ref_position CHECK (position >= 0)
);

CREATE TABLE core.world_reference_assets (
    world_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (world_id, asset_id),
    CONSTRAINT fk_world_ref_owner FOREIGN KEY (world_id)
        REFERENCES core.worlds(id) ON DELETE RESTRICT,
    CONSTRAINT fk_world_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_world_ref_position UNIQUE (world_id, position),
    CONSTRAINT ck_world_ref_position CHECK (position >= 0)
);

CREATE TABLE core.location_reference_assets (
    location_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (location_id, asset_id),
    CONSTRAINT fk_location_ref_owner FOREIGN KEY (location_id)
        REFERENCES core.locations(id) ON DELETE RESTRICT,
    CONSTRAINT fk_location_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_location_ref_position UNIQUE (location_id, position),
    CONSTRAINT ck_location_ref_position CHECK (position >= 0)
);

CREATE TABLE core.prop_reference_assets (
    prop_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (prop_id, asset_id),
    CONSTRAINT fk_prop_ref_owner FOREIGN KEY (prop_id)
        REFERENCES core.props(id) ON DELETE RESTRICT,
    CONSTRAINT fk_prop_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_prop_ref_position UNIQUE (prop_id, position),
    CONSTRAINT ck_prop_ref_position CHECK (position >= 0)
);

CREATE TABLE core.style_reference_assets (
    style_profile_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (style_profile_id, asset_id),
    CONSTRAINT fk_style_ref_owner FOREIGN KEY (style_profile_id)
        REFERENCES core.style_profiles(id) ON DELETE RESTRICT,
    CONSTRAINT fk_style_ref_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_style_ref_position UNIQUE (style_profile_id, position),
    CONSTRAINT ck_style_ref_position CHECK (position >= 0)
);

CREATE TABLE core.asset_parents (
    child_asset_id uuid NOT NULL,
    parent_asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (child_asset_id, parent_asset_id),
    CONSTRAINT fk_asset_parent_child FOREIGN KEY (child_asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asset_parent_parent FOREIGN KEY (parent_asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_asset_parent_position UNIQUE (child_asset_id, position),
    CONSTRAINT ck_asset_parent_position CHECK (position >= 0),
    CONSTRAINT ck_asset_parent_self CHECK (child_asset_id <> parent_asset_id)
);

CREATE TABLE core.generation_attempt_input_assets (
    attempt_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (attempt_id, asset_id),
    CONSTRAINT fk_attempt_input_attempt FOREIGN KEY (attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_attempt_input_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_attempt_input_position UNIQUE (attempt_id, position),
    CONSTRAINT ck_attempt_input_position CHECK (position >= 0)
);

CREATE TABLE core.generation_attempt_qa_records (
    attempt_id uuid NOT NULL,
    qa_record_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (attempt_id, qa_record_id),
    CONSTRAINT fk_attempt_qa_attempt FOREIGN KEY (attempt_id)
        REFERENCES core.generation_attempts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_attempt_qa_record FOREIGN KEY (qa_record_id)
        REFERENCES core.qa_records(id) ON DELETE RESTRICT,
    CONSTRAINT uq_attempt_qa_position UNIQUE (attempt_id, position),
    CONSTRAINT ck_attempt_qa_position CHECK (position >= 0)
);

CREATE TABLE core.take_qa_records (
    take_id uuid NOT NULL,
    qa_record_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (take_id, qa_record_id),
    CONSTRAINT fk_take_qa_take FOREIGN KEY (take_id)
        REFERENCES core.takes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_take_qa_record FOREIGN KEY (qa_record_id)
        REFERENCES core.qa_records(id) ON DELETE RESTRICT,
    CONSTRAINT uq_take_qa_position UNIQUE (take_id, position),
    CONSTRAINT ck_take_qa_position CHECK (position >= 0)
);

CREATE TABLE core.job_dependencies (
    job_id uuid NOT NULL,
    dependency_job_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (job_id, dependency_job_id),
    CONSTRAINT fk_job_dependency_job FOREIGN KEY (job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT fk_job_dependency_dep FOREIGN KEY (dependency_job_id)
        REFERENCES core.jobs(id) ON DELETE RESTRICT,
    CONSTRAINT uq_job_dependency_position UNIQUE (job_id, position),
    CONSTRAINT ck_job_dependency_position CHECK (position >= 0),
    CONSTRAINT ck_job_dependency_self CHECK (job_id <> dependency_job_id)
);

CREATE TABLE core.timeline_marker_assets (
    timeline_id uuid NOT NULL,
    asset_id uuid NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (timeline_id, asset_id),
    CONSTRAINT fk_timeline_marker_timeline FOREIGN KEY (timeline_id)
        REFERENCES core.timelines(id) ON DELETE RESTRICT,
    CONSTRAINT fk_timeline_marker_asset FOREIGN KEY (asset_id)
        REFERENCES core.assets(id) ON DELETE RESTRICT,
    CONSTRAINT uq_timeline_marker_position UNIQUE (timeline_id, position),
    CONSTRAINT ck_timeline_marker_position CHECK (position >= 0)
);

CREATE TABLE core.timeline_track_items (
    track_id uuid NOT NULL,
    item_external_id text NOT NULL,
    position integer NOT NULL,
    PRIMARY KEY (track_id, item_external_id),
    CONSTRAINT fk_timeline_track_item_track FOREIGN KEY (track_id)
        REFERENCES core.timeline_tracks(id) ON DELETE RESTRICT,
    CONSTRAINT uq_timeline_track_item_position UNIQUE (track_id, position),
    CONSTRAINT ck_timeline_track_item_position CHECK (position >= 0)
);

ALTER TABLE core.projects
    ADD CONSTRAINT fk_project_content_owner
    FOREIGN KEY (content_id, id)
    REFERENCES core.contents(id, project_id)
    ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE core.projects
    ADD CONSTRAINT fk_project_active_timeline_owner
    FOREIGN KEY (active_timeline_id, id)
    REFERENCES core.timelines(id, project_id)
    ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE core.contents
    ADD CONSTRAINT fk_content_active_version_owner
    FOREIGN KEY (active_version_id, id)
    REFERENCES core.content_versions(id, content_id)
    ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE core.characters
    ADD CONSTRAINT fk_character_active_version_owner
    FOREIGN KEY (active_version_id, id)
    REFERENCES core.character_versions(id, character_id)
    ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE core.shots
    ADD CONSTRAINT fk_shot_selected_take_owner
    FOREIGN KEY (selected_take_id, id)
    REFERENCES core.takes(id, shot_id)
    ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE core.jobs
    ADD CONSTRAINT fk_job_selected_attempt_owner
    FOREIGN KEY (selected_attempt_id, id)
    REFERENCES core.generation_attempts(id, job_id)
    ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE core.timelines
    ADD CONSTRAINT fk_timeline_otio_asset
    FOREIGN KEY (otio_asset_id)
    REFERENCES core.assets(id) ON DELETE RESTRICT;

ALTER TABLE core.shots
    ADD CONSTRAINT fk_shot_first_frame_asset
    FOREIGN KEY (first_frame_asset_id)
    REFERENCES core.assets(id) ON DELETE RESTRICT;

ALTER TABLE core.shots
    ADD CONSTRAINT fk_shot_end_frame_asset
    FOREIGN KEY (end_frame_asset_id)
    REFERENCES core.assets(id) ON DELETE RESTRICT;

CREATE INDEX ix_content_project ON core.contents(project_id);
CREATE INDEX ix_content_version_content ON core.content_versions(content_id);
CREATE INDEX ix_character_version_character ON core.character_versions(character_id);
CREATE INDEX ix_character_version_voice ON core.character_versions(voice_profile_id);
CREATE INDEX ix_character_look_version ON core.character_looks(character_version_id);
CREATE INDEX ix_world_style ON core.worlds(style_profile_id);
CREATE INDEX ix_location_world ON core.locations(world_id);
CREATE INDEX ix_timeline_project ON core.timelines(project_id);
CREATE INDEX ix_track_timeline ON core.timeline_tracks(timeline_id);
CREATE INDEX ix_act_project ON core.acts(project_id);
CREATE INDEX ix_act_timeline ON core.acts(timeline_id);
CREATE INDEX ix_sequence_act ON core.sequences(act_id);
CREATE INDEX ix_scene_sequence ON core.scenes(sequence_id);
CREATE INDEX ix_scene_location ON core.scenes(location_id);
CREATE INDEX ix_shot_scene ON core.shots(scene_id);
CREATE INDEX ix_shot_location ON core.shots(location_id);
CREATE INDEX ix_take_shot ON core.takes(shot_id);
CREATE INDEX ix_take_attempt ON core.takes(attempt_id);
CREATE INDEX ix_take_asset ON core.takes(asset_id);
CREATE INDEX ix_job_project_queue ON core.jobs(project_id, status, priority DESC, lease_expires_at);
CREATE INDEX ix_job_parent ON core.jobs(parent_job_id);
CREATE INDEX ix_job_shot ON core.jobs(shot_id);
CREATE INDEX ix_job_content ON core.jobs(content_id);
CREATE INDEX ix_attempt_job ON core.generation_attempts(job_id);
CREATE INDEX ix_attempt_project ON core.generation_attempts(request_project_id);
CREATE INDEX ix_attempt_shot ON core.generation_attempts(request_shot_id);
CREATE INDEX ix_attempt_content ON core.generation_attempts(request_content_id);
CREATE INDEX ix_asset_project ON core.assets(project_id);
CREATE INDEX ix_asset_attempt ON core.assets(generation_attempt_id, generation_output_position);
CREATE INDEX ix_asset_sha256 ON core.assets(sha256);
CREATE INDEX ix_asset_rights ON core.assets(rights_record_id);
CREATE INDEX ix_qa_subject ON core.qa_records(subject_type, subject_id, created_at);
CREATE INDEX ix_cost_project_time ON core.cost_records(project_id, recorded_at);
CREATE INDEX ix_cost_attempt ON core.cost_records(attempt_id);
CREATE INDEX ix_rights_subject ON core.rights_records(subject_type, subject_id);
CREATE INDEX ix_rights_blocked ON core.rights_records(publication_blocked)
    WHERE publication_blocked = true;
CREATE INDEX ix_approval_project_time ON core.approvals(project_id, created_at);
CREATE INDEX ix_legacy_import_content ON core.legacy_content_imports(content_id);
CREATE INDEX ix_legacy_import_version ON core.legacy_content_imports(content_version_id);
