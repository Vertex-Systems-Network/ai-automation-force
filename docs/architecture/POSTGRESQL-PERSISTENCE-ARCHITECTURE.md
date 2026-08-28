# PostgreSQL Persistence Architecture

Status: `M01/WP5 — CANONICAL PERSISTENCE MAPPING`

This document defines the first operational PostgreSQL persistence boundary for the stabilized M01 provider-neutral domain. It is an architecture and contract document. It does **not** create or apply database migrations; the executable reversible migration scaffold belongs to WP6.

## 1. Goals

The persistence model must:

- preserve every stable external domain ID (`PRJ-*`, `CNT-*`, `CHR-*`, etc.);
- separate database identity from business/audit identity;
- enforce ownership and referential integrity where PostgreSQL can do so locally;
- preserve list ordering required for deterministic Pydantic round trips;
- keep canonical/versioned history conservative and append-oriented;
- support short projects and long-form projects up to the current 10,800-second contract;
- support WP4 legacy import idempotency without mutating repository history;
- remain provider-neutral and avoid coupling domain models to an ORM;
- identify explicitly which invariants remain aggregate/repository validation rather than pretending every rule belongs in SQL.

## 2. Source-of-truth boundary

During the transition:

- Git remains canonical for engineering policy, schemas, prompts, ADR-like architecture decisions, research evidence, provider-source definitions and auditable exported manifests;
- PostgreSQL becomes canonical operational state for live domain records after the persistence runtime is introduced;
- legacy repository content remains immutable source material and enters PostgreSQL only through explicit importer/service operations;
- normal runtime/UI state must never depend on committing to Git as a database operation.

Migration does not rewrite historical source files.

## 3. Database key strategy

### 3.1 Internal primary keys

Every independently persisted entity receives an internal `id uuid PRIMARY KEY`.

Application/repository code should generate UUIDv7-style values where the selected Python/driver stack supports them safely. PostgreSQL storage itself remains generic `uuid`; M01 must not depend on a database-specific UUIDv7 generator extension.

Why:

- internal FKs are compact and independent from external-ID formatting;
- stable external IDs can evolve in width without rewriting relationship keys;
- external IDs remain human-auditable and contract-controlled;
- import/export can preserve domain identity without leaking storage implementation.

### 3.2 Stable external IDs

Every domain entity carrying a canonical external ID stores it in a dedicated `external_id text NOT NULL UNIQUE` column using the exact Pydantic value.

Examples:

- `projects.external_id = PRJ-*`
- `contents.external_id = CNT-*`
- `content_versions.external_id = CTV-*`
- `characters.external_id = CHR-*`
- `character_versions.external_id = CHV-*`
- `character_looks.external_id = LOOK-*`
- `worlds.external_id = WRL-*`
- `locations.external_id = LOC-*`
- `props.external_id = PRP-*`
- `style_profiles.external_id = STY-*`
- `voice_profiles.external_id = VOC-*`
- `timelines.external_id = TML-*`
- `timeline_tracks.external_id = TRK-*`
- `acts.external_id = ACT-*`
- `sequences.external_id = SEQ-*`
- `scenes.external_id = SCN-*`
- `shots.external_id = SHT-*`
- `takes.external_id = TAK-*`
- `assets.external_id = AST-*`
- `jobs.external_id = JOB-*`
- `generation_attempts.external_id = ATT-*`
- `qa_records.external_id = QAR-*`
- `cost_records.external_id = CST-*`
- `rights_records.external_id = RGT-*`
- `approvals.external_id = APR-*`

WP6 migrations should add prefix/shape checks only when they remain maintainable and consistent with the canonical `external_id_pattern()` contract. The domain schema remains authoritative for exact pattern semantics.

## 4. Common audit mapping

Entities containing `AuditFields` map:

- `schema_version smallint NOT NULL`
- `created_at timestamptz NOT NULL`
- `updated_at timestamptz NOT NULL`
- `created_by text NULL`
- `revision integer NOT NULL DEFAULT 1 CHECK (revision >= 1)`
- `CHECK (updated_at >= created_at)`

Rows without `AuditFields` retain their canonical entity-specific timestamps rather than receiving invented audit semantics.

All timestamps are `timestamptz`; application code must use timezone-aware datetimes.

## 5. Type and normalization policy

### 5.1 JSONB value objects

Use `jsonb` for structured value objects whose fields are domain-owned but do not independently need relational identity in M01:

- `Project.audience`
- `Project.cast`
- `Project.output`
- `Project.creative`
- `Project.provider_policy`
- `ContentVersion.objective`
- `Shot.camera`
- `Shot.incoming_state`
- `Shot.outgoing_state`
- `Scene.incoming_state`
- `Scene.outgoing_state`
- `GenerationRequest.constraints`
- provider reference snapshot inside a generation attempt, where immutable attempt evidence is required.

Repository code validates these JSONB values through current Pydantic contracts on write and read.

### 5.2 Scalar lists

Use PostgreSQL `text[]` where the collection is scalar metadata, not entity ownership, and exact order can be naturally preserved:

- tags;
- rules;
- identity constraints;
- wardrobe/accessories/palette;
- findings/notes;
- pronunciation notes;
- evidence URLs;
- structure maps;
- other current string-only metadata arrays.

Do not use JSONB or arrays for relationships merely to avoid join tables.

### 5.3 Registry-owned/open taxonomy values

Expandable taxonomy fields remain `text`, not PostgreSQL ENUM, because the product intentionally permits future configured values without a database type migration.

Examples:

- content format/taxonomy value;
- audience/cast configured values inside JSONB;
- character type/species/presentation;
- track kind;
- job type;
- QA gate/subject type;
- rights subject type.

Lifecycle values that are currently code enums may use `text` plus CHECK constraints in WP6 if the check can be changed safely. PostgreSQL ENUM is not required for M01.

### 5.4 Money/credits

`Decimal` values map to `numeric` with non-negative checks. WP6 should choose precision high enough for provider micro-costs without floating-point loss; application code continues to use Decimal.

Currency remains a three-character text field and preserves the current canonical value.

## 6. Table mapping

### 6.1 `projects`

Persists `Project`.

Core columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `title text NOT NULL`
- `status text NOT NULL`
- `audience jsonb NOT NULL`
- `cast jsonb NOT NULL`
- `content_format text NOT NULL`
- `custom_content_format text NULL`
- `language text NOT NULL`
- `target_duration_seconds integer NOT NULL`
- `output jsonb NOT NULL`
- `creative jsonb NOT NULL`
- `provider_policy jsonb NOT NULL`
- `content_id uuid NULL`
- `active_timeline_id uuid NULL`
- `tags text[] NOT NULL DEFAULT '{}'`
- common audit columns

Checks:

- duration 60..10800;
- custom format presence rule equivalent to the Pydantic validator where practical.

`content_id` and `active_timeline_id` are cyclic relationships and are added as deferred FKs after dependent tables exist.

Project character/world/prop membership uses ordered join tables, not arrays of external IDs.

### 6.2 `contents`

Persists `Content`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `active_version_id uuid NULL initially during creation transaction`
- `project_id uuid NULL`
- `status text NOT NULL`
- `source_legacy_package_path text NULL`
- common audit columns

Constraints:

- project FK `RESTRICT`;
- active version relationship must point to a `content_versions` row owned by the same content. Use a DEFERRABLE composite FK as described below.

### 6.3 `content_versions`

Persists `ContentVersion`.

Columns include:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `content_id uuid NOT NULL`
- `version integer NOT NULL CHECK (version >= 1)`
- `title text NOT NULL`
- `content_format text NOT NULL`
- `custom_content_format text NULL`
- `language text NOT NULL`
- `target_duration_seconds integer NOT NULL CHECK (60..10800)`
- `objective jsonb NOT NULL`
- `premise text NOT NULL DEFAULT ''`
- `hook text NOT NULL DEFAULT ''`
- `script_or_lyrics text NOT NULL`
- `structure_map text[] NOT NULL DEFAULT '{}'`
- `pronunciation_notes text[] NOT NULL DEFAULT '{}'`
- `tags text[] NOT NULL DEFAULT '{}'`
- `originality_fingerprint text NULL`
- common audit columns

Constraints/indexes:

- FK content `RESTRICT`;
- `UNIQUE(content_id, version)`;
- `UNIQUE(id, content_id)` to support same-owner composite selection FK.

Character/world/prop references use ordered join tables.

### 6.4 `characters`

Persists `Character`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `name text NOT NULL`
- `active_version_id uuid NOT NULL` (deferred relationship)
- `rights_record_id uuid NULL`
- `reusable boolean NOT NULL`
- `tags text[] NOT NULL DEFAULT '{}'`
- common audit columns

The active version must belong to the same Character. Use a composite FK to `(character_versions.id, character_versions.character_id)` with `(active_version_id, characters.id)`.

### 6.5 `character_versions`

Persists `CharacterVersion`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `character_id uuid NOT NULL`
- `version integer NOT NULL CHECK (version >= 1)`
- `display_name text NOT NULL`
- `character_type text NOT NULL`
- `species text NULL`
- `apparent_age text NULL`
- `gender_presentation text NULL`
- `personality_traits text[] NOT NULL DEFAULT '{}'`
- `movement_style text NULL`
- `voice_profile_id uuid NULL`
- `identity_constraints text[] NOT NULL DEFAULT '{}'`
- `status text NOT NULL`
- common audit columns

Constraints:

- FK Character `RESTRICT`;
- `UNIQUE(character_id, version)`;
- `UNIQUE(id, character_id)` for ownership-aware composite FKs.

Canonical reference assets use an ordered join table.

### 6.6 `character_looks`

Persists `CharacterLook` as a separately addressable version-owned record because it carries stable `LOOK-*` identity and can be pinned.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `character_version_id uuid NOT NULL`
- `position integer NOT NULL`
- `name text NOT NULL`
- `wardrobe text[]`
- `accessories text[]`
- `hair text NULL`
- `eyes text NULL`
- `palette text[]`
- `expression_defaults text[]`
- `body_notes text[]`
- `prohibited_mutations text[]`

Constraints:

- FK version `RESTRICT`;
- `UNIQUE(character_version_id, position)`;
- `UNIQUE(id, character_version_id)` to support lock ownership.

Reference assets use an ordered join table.

### 6.7 `character_locks`

Persists the current `CharacterLock` as one row per Character.

Columns:

- `id uuid PK`
- `character_id uuid UNIQUE NOT NULL`
- `scope text NOT NULL`
- `pinned_character_version_id uuid NULL`
- `pinned_look_id uuid NULL`
- `project_id uuid NULL`
- `scene_id uuid NULL`

Enforcement:

- one-to-one Character FK `RESTRICT`;
- scope-specific NULL/presence CHECKs mirror current Pydantic rules;
- composite FK `(pinned_character_version_id, character_id)` ensures a pinned version belongs to the Character;
- look pin must belong to the pinned version through a composite relationship;
- project lock's `project_id` uses FK `RESTRICT`;
- scene lock's `scene_id` uses FK `RESTRICT`.

Because lock and selected version relationships are cyclic during creation, relevant FKs should be `DEFERRABLE INITIALLY DEFERRED` so a whole aggregate can be inserted atomically without disabling integrity.

### 6.8 `worlds`

Persists `World`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `name text NOT NULL`
- `description text NOT NULL DEFAULT ''`
- `style_profile_id uuid NULL`
- `rules text[]`
- `forbidden_mutations text[]`
- common audit columns

Canonical reference assets use an ordered join table.

### 6.9 `locations`

Persists `Location`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `world_id uuid NULL`
- `name text NOT NULL`
- `description text NOT NULL DEFAULT ''`
- `environment_constraints text[]`
- common audit columns

Reference assets use ordered join table.

### 6.10 `props`

Persists `Prop`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `name text NOT NULL`
- `description text NOT NULL DEFAULT ''`
- `identity_constraints text[]`
- common audit columns

Reference assets use ordered join table.

### 6.11 `style_profiles`

Persists `StyleProfile`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `name text NOT NULL`
- treatment/palette/lighting/camera/texture/negative constraint arrays
- common audit columns

Reference assets use ordered join table.

### 6.12 `voice_profiles`

Persists `VoiceProfile`.

Columns include:

- internal/external IDs;
- name/presentation/language;
- optional timbre/pace/articulation;
- emotion/pronunciation arrays;
- `impersonation_prohibited boolean NOT NULL`;
- `provider_voice_refs jsonb NOT NULL DEFAULT '{}'`;
- `rights_record_id uuid NULL`;
- common audit columns.

Provider voice refs are lookup metadata, not provider credentials. Secrets never live here.

### 6.13 `timelines`

Persists `Timeline`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `project_id uuid NOT NULL`
- `version integer NOT NULL CHECK(version >= 1)`
- `duration_seconds numeric NOT NULL`
- `fps numeric NOT NULL`
- `otio_asset_id uuid NULL`
- common audit columns

Constraints:

- `UNIQUE(project_id, version)`;
- duration 60..10800;
- fps >0 and <=120.

`act_ids` are derived from Act rows ordered by `order`; they are not redundantly stored.

Marker assets use ordered join table.

### 6.14 `timeline_tracks`

Persists `TimelineTrack`.

Columns:

- `id uuid PK`
- `external_id text UNIQUE NOT NULL`
- `timeline_id uuid NOT NULL`
- `position integer NOT NULL`
- `kind text NOT NULL`
- `name text NOT NULL`
- `muted boolean NOT NULL`
- `locked boolean NOT NULL`

`UNIQUE(timeline_id, position)`.

Because `item_ids` is deliberately generic and may point to several future timeline object kinds, M01 stores it in ordered `timeline_track_items` rows with:

- `track_id uuid`
- `position integer`
- `item_external_id text`

This preserves round-trip order without pretending a generic item can have one FK target today. Typed track-item references can replace/augment this once the editorial interchange model is richer.

### 6.15 `acts`

Persists `Act`.

Columns:

- internal/external ID;
- `project_id uuid NOT NULL`;
- `timeline_id uuid NOT NULL`;
- `order integer NOT NULL CHECK(order>=1)`;
- title;
- target duration;
- audit.

The domain `Act` carries project ownership while `Timeline.act_ids` owns timeline membership. Persistence stores both explicit FKs so orphaned or cross-timeline acts are impossible.

Constraints:

- `UNIQUE(timeline_id, order)`;
- each Act project must equal Timeline project. This cross-table equality is validated by repository/aggregate code in M01 unless WP6 can express it safely with a composite FK.

### 6.16 `sequences`

Persists `Sequence`:

- IDs;
- `act_id uuid NOT NULL`;
- `order integer NOT NULL`;
- title;
- target duration;
- audit.

`UNIQUE(act_id, order)`.

`Act.sequence_ids` is derived by ordered query.

### 6.17 `scenes`

Persists `Scene`:

- IDs;
- `sequence_id uuid NOT NULL`;
- `order integer NOT NULL`;
- title/summary;
- `location_id uuid NULL`;
- target duration;
- incoming/outgoing state JSONB;
- audit.

`UNIQUE(sequence_id, order)`.

Scene characters use ordered relationship table.

### 6.18 `shots`

Persists `Shot`.

Columns include:

- IDs;
- `scene_id uuid NOT NULL`;
- `order integer NOT NULL`;
- `start_seconds numeric NOT NULL`;
- `duration_seconds numeric NOT NULL`;
- purpose/action;
- `location_id uuid NULL`;
- `camera jsonb`;
- incoming/outgoing continuity JSONB;
- first/end frame asset FKs;
- `selected_take_id uuid NULL`;
- transition in/out;
- handles seconds;
- generation notes array;
- audit.

Constraints:

- `UNIQUE(scene_id, order)`;
- non-negative start and positive duration;
- handles 0..10;
- selected Take must belong to same Shot via DEFERRABLE composite FK `(selected_take_id, shots.id) -> (takes.id, takes.shot_id)`.

Shot characters/props/reference assets are ordered joins.

Primary-video overlap remains an aggregate/editorial invariant; PostgreSQL does not globally prohibit shot overlap because parallel B-roll/overlay tracks are valid.

### 6.19 `takes`

Persists `Take`.

Columns:

- IDs;
- `shot_id uuid NOT NULL`;
- persistence-only `position integer NOT NULL` to preserve `Shot.take_ids` order;
- `attempt_id uuid NULL`;
- `asset_id uuid NULL`;
- canonical status;
- continuity score;
- audit.

Constraints:

- `UNIQUE(shot_id, position)`;
- `UNIQUE(id, shot_id)` for selected-Take composite FK;
- continuity score 0..100.

QA relationships use ordered join table.

### 6.20 `assets`

Persists `Asset` metadata only; binary media lives in S3-compatible/object storage.

Columns:

- IDs;
- `project_id uuid NULL`;
- kind;
- URI;
- SHA-256;
- MIME;
- size;
- duration/width/height;
- provider/model metadata;
- `generation_attempt_id uuid NULL`;
- persistence-only `generation_output_position integer NULL` when the asset is an attempt output;
- `rights_record_id uuid NULL`;
- canonical status;
- retention class;
- audit.

Constraints:

- SHA-256 shape;
- size >=0;
- positive optional duration/dimensions;
- `(generation_attempt_id, generation_output_position)` unique when both present.

Parent lineage uses `asset_parents(child_asset_id, parent_asset_id, position)` and rejects self-reference by CHECK. General cycles remain aggregate validation; a recursive-cycle trigger is not introduced in WP5.

### 6.21 `jobs`

Persists `Job`.

Columns include:

- IDs;
- project FK;
- job type/status/priority;
- `idempotency_key text NOT NULL`;
- parent job FK;
- optional Shot/Content FKs;
- `selected_attempt_id uuid NULL`;
- retry budget;
- blocked reason;
- claimed_by/lease expiry;
- audit.

Constraints:

- `UNIQUE(project_id, idempotency_key)` to make application idempotency scoped and deterministic;
- priority 0..100;
- retry >=0;
- selected attempt belongs to same Job via DEFERRABLE composite FK.

Dependencies use `job_dependencies(job_id, dependency_job_id, position)` with self-dependency CHECK.

`attempt_ids` are derived from attempts ordered by attempt number.

### 6.22 `generation_attempts`

Persists `GenerationAttempt` plus an immutable request/provider snapshot.

Columns:

- IDs;
- `job_id uuid NOT NULL`;
- attempt number;
- provider/model/capability/access-class scalar snapshot;
- provider registry verification timestamp;
- request snapshot fields: project/shot/content IDs as FKs where available, prompt metadata, constraints JSONB, target duration, rights/continuity flags, request idempotency key;
- provider generation ID;
- started/finished timestamps;
- status/error fields;
- free credits/paid cost/currency.

Constraints:

- `UNIQUE(job_id, attempt_number)`;
- `UNIQUE(id, job_id)` for selected-attempt composite FK;
- finished >= started;
- numeric non-negative cost/credit checks.

Input assets use ordered `generation_attempt_input_assets` join table.
Output assets are derived from `assets.generation_attempt_id` ordered by `generation_output_position`.
Attempt QA references use ordered join table.

Generation attempts are append-oriented evidence; casual UPDATE/DELETE semantics should be restricted by repository/service policy.

### 6.23 `qa_records`

Persists `QARecord`.

Columns:

- IDs;
- `subject_type text NOT NULL`;
- `subject_id text NOT NULL` using the canonical external subject ID;
- gate;
- passed/critical;
- optional score;
- findings array;
- reviewer;
- created_at.

Index `(subject_type, subject_id, created_at)`.

The current domain uses polymorphic `subject_type + subject_id`; one universal SQL FK cannot safely target multiple tables. M01 therefore keeps the polymorphic pair and uses explicit join/FK tables where a concrete owner already exists (Take/Attempt QA membership). Aggregate validation remains authoritative for subject matching.

### 6.24 `cost_records`

Persists `CostRecord`.

Columns:

- IDs;
- project FK;
- optional Job FK;
- optional Attempt FK;
- provider/model fields;
- free credits/paid cost numeric;
- currency;
- estimated boolean;
- recorded_at.

Checks:

- non-negative amounts;
- actual (`estimated=false`) cost requires `attempt_id`, matching current lineage rule at repository/aggregate boundary;
- provider/model agreement with attempt is aggregate/repository validation unless safely duplicated from immutable attempt snapshot.

Cost history is append-oriented.

### 6.25 `rights_records`

Persists `RightsRecord`.

Columns:

- IDs;
- polymorphic `subject_type`, `subject_id` external ID;
- provider/model/tier metadata;
- commercial-use state;
- watermark requirement;
- source basis;
- consent reference;
- evidence URLs array;
- verified_at;
- `publication_blocked boolean NOT NULL DEFAULT true`;
- notes array.

Critical SQL CHECK:

`publication_blocked = TRUE OR commercial_use = 'allowed'`

This preserves fail-closed publication behavior even if application validation is bypassed.

Index `(subject_type, subject_id)` and optionally partial index on blocked records when runtime query patterns justify it.

### 6.26 `approvals`

Persists `Approval`.

Columns:

- IDs;
- project FK;
- polymorphic subject type/external ID;
- decision;
- actor;
- optional reason;
- created_at.

Approvals are append-oriented audit evidence.

## 7. Ordered relationship tables

Relationship lists that must round-trip exactly use explicit `position integer NOT NULL CHECK(position>=0)`.

Canonical M01 joins:

- `project_characters(project_id, character_id, position)`
- `project_worlds(project_id, world_id, position)`
- `project_props(project_id, prop_id, position)`
- `content_version_characters(content_version_id, character_id, position)`
- `content_version_worlds(content_version_id, world_id, position)`
- `content_version_props(content_version_id, prop_id, position)`
- `scene_characters(scene_id, character_id, position)`
- `shot_characters(shot_id, character_id, position)`
- `shot_props(shot_id, prop_id, position)`
- `shot_reference_assets(shot_id, asset_id, position)`
- `character_version_reference_assets(character_version_id, asset_id, position)`
- `character_look_reference_assets(character_look_id, asset_id, position)`
- `world_reference_assets(world_id, asset_id, position)`
- `location_reference_assets(location_id, asset_id, position)`
- `prop_reference_assets(prop_id, asset_id, position)`
- `style_reference_assets(style_profile_id, asset_id, position)`
- `asset_parents(child_asset_id, parent_asset_id, position)`
- `generation_attempt_input_assets(attempt_id, asset_id, position)`
- `generation_attempt_qa_records(attempt_id, qa_record_id, position)`
- `take_qa_records(take_id, qa_record_id, position)`
- `job_dependencies(job_id, dependency_job_id, position)`
- `timeline_marker_assets(timeline_id, asset_id, position)`
- `timeline_track_items(track_id, item_external_id, position)`

Each join has:

- PK/unique pair preventing duplicate membership where the domain requires uniqueness;
- `UNIQUE(owner_id, position)`;
- FKs `ON DELETE RESTRICT` unless the row is a purely dependent association that may safely be removed when its owner is explicitly deleted during non-production rollback/testing.

## 8. Derived collection rules

Do not persist the same hierarchy both as FK ownership and duplicate ID arrays when it can be derived deterministically.

Derived on read:

- `Timeline.act_ids` from Acts ordered by `acts.order`;
- `Act.sequence_ids` from Sequences ordered by `sequences.order`;
- `Sequence.scene_ids` from Scenes ordered by `scenes.order`;
- `Scene.shot_ids` from Shots ordered by `shots.order`;
- `Shot.take_ids` from Takes ordered by persistence `takes.position`;
- `Job.attempt_ids` from Attempts ordered by `attempt_number`;
- `GenerationAttempt.output_asset_ids` from Assets ordered by `generation_output_position`.

The repository layer reconstructs canonical Pydantic models from these queries and then validates the assembled graph.

## 9. Selected/active cyclic relationships

Some domain pointers create cycles:

- Project -> active Timeline while Timeline -> Project;
- Content -> active ContentVersion while Version -> Content;
- Character -> active CharacterVersion while Version -> Character;
- Shot -> selected Take while Take -> Shot;
- Job -> selected Attempt while Attempt -> Job;
- CharacterLock -> pinned CharacterVersion/Look while lock belongs to Character.

Policy:

- keep all real relationships as FKs;
- make cyclic selection FKs `DEFERRABLE INITIALLY DEFERRED` where PostgreSQL supports the intended transaction pattern;
- insert/update a complete aggregate inside one transaction;
- validate constraints at transaction commit;
- never disable FK checks as normal application behavior.

## 10. Delete, archival and immutability policy

Canonical production history is conservative.

Default FK delete action: `ON DELETE RESTRICT`.

M01 does not introduce broad `ON DELETE CASCADE` from Project to production history.

Policy expectations:

- version rows are append-oriented;
- attempts, QA, cost, rights and approvals are audit/history records;
- assets may later have retention lifecycle for object bytes, but metadata lineage should not disappear casually;
- product-level archive state is preferred to hard delete when the domain exposes it;
- hard deletion, GDPR/account deletion and workspace lifecycle are later security/privacy concerns and are not invented in M01.

WP6 downgrade may drop newly created empty M01 tables as a migration rollback; that is different from runtime cascade behavior.

## 11. Legacy import ledger

Add persistence-only `legacy_content_imports` to operationalize WP4 idempotency without changing canonical Content models.

Columns:

- `id uuid PK`
- `mapping_version text NOT NULL`
- `source_schema_version integer NOT NULL`
- `source_content_external_id text NOT NULL`
- `source_fingerprint_sha256 text NOT NULL`
- `import_key text NOT NULL UNIQUE`
- `source_run_id text NOT NULL`
- `source_package_path text NOT NULL`
- `content_id uuid NOT NULL`
- `content_version_id uuid NOT NULL`
- `imported_at timestamptz NOT NULL`

Recommended uniqueness:

- `UNIQUE(mapping_version, source_content_external_id, source_fingerprint_sha256)`;
- `UNIQUE(import_key)`.

The application performs WP4 reconciliation before insert:

- missing canonical identity -> create within same transaction;
- exact prior import -> noop;
- changed/partial/drifted stable identity -> conflict and rollback.

The database migration itself must never auto-import repository content.

## 12. Constraint ownership matrix

### Enforce in PostgreSQL

- internal PK uniqueness;
- stable external ID uniqueness;
- direct FKs;
- hierarchy parent ownership;
- scoped sibling order uniqueness;
- version number uniqueness per owner;
- selected Take/Attempt same-owner composite FK;
- Character active/pinned version same-owner composite FK;
- lock scope presence rules where local columns suffice;
- basic numeric/time bounds;
- rights fail-closed publication CHECK;
- attempt timestamp ordering;
- import-key uniqueness;
- simple self-reference rejection on relationship tables.

### Enforce in repository + Pydantic aggregate validation

- timeline target duration equals Project target duration;
- primary-video editorial non-overlap/order semantics;
- asset-parent graph cycle detection;
- polymorphic QA/Rights/Approval subject resolution;
- provider/model consistency across Attempt/Asset/Cost;
- exact ContentVersion entity references loaded in the aggregate;
- scene/shot declaration consistency not reducible to one local FK;
- multi-entity continuity semantics;
- other invariants already owned by `ProjectBundle` / `ProductionLineageBundle`.

Repositories must validate reconstructed aggregates before returning them for high-impact use. Database success alone does not mean the creative/lineage aggregate is valid.

## 13. Index plan

Unique constraints already provide B-tree indexes for stable external IDs and scoped uniqueness.

Additional indexes expected in the initial migration:

- every FK used for child lookup;
- `content_versions(content_id, version)` unique;
- `character_versions(character_id, version)` unique;
- `timelines(project_id, version)` unique;
- hierarchy `(parent_id, order)` unique indexes;
- `jobs(project_id, status, priority DESC, lease_expires_at)` for future claim scans;
- `generation_attempts(job_id, attempt_number)` unique;
- `assets(project_id)`;
- `assets(generation_attempt_id, generation_output_position)`;
- `assets(sha256)` for dedupe/integrity lookup, not global content ownership equivalence;
- `qa_records(subject_type, subject_id, created_at)`;
- `cost_records(project_id, recorded_at)`;
- `cost_records(attempt_id)`;
- `rights_records(subject_type, subject_id)`;
- `approvals(project_id, created_at)`;
- `legacy_content_imports(import_key)` unique.

Do not add speculative GIN/JSONB/vector indexes in WP6 until a real query path requires them.

## 14. Repository transaction boundaries

### 14.1 Aggregate write

A canonical Project aggregate write should be one transaction:

1. resolve/create internal IDs for stable external identities;
2. upsert only records whose domain lifecycle permits mutation;
3. insert immutable/versioned/history rows append-oriented;
4. synchronize ordered membership rows;
5. set active/selected deferred pointers;
6. reconstruct/validate the intended aggregate state where practical;
7. commit, causing deferred FK checks to run.

Failure at any step rolls back the whole aggregate.

No half-persisted canonical graph is acceptable.

### 14.2 Legacy import

One transaction covers:

1. read existing Content/Version/import-ledger state with appropriate locking;
2. run WP4 reconciliation;
3. on `create`, insert Content + Version + import ledger;
4. on `noop`, make no duplicate write;
5. on `conflict`, rollback/return structured conflict;
6. commit only a coherent state.

### 14.3 Job/attempt evidence

Attempt creation/completion and its cost/output lineage must use transaction boundaries that avoid an Attempt claiming outputs/costs that were not persisted. Exact service sequencing is WP7, but the schema must make atomicity possible.

## 15. Concurrency and revision policy

`AuditFields.revision` is the first optimistic-concurrency signal for mutable canonical rows.

Repository update pattern should be compatible with:

`UPDATE ... SET ..., revision = revision + 1 WHERE id = :id AND revision = :expected_revision`

Zero affected rows means stale writer/conflict.

Append-oriented rows generally avoid in-place business edits; status transitions that must mutate remain explicit and audited.

Do not introduce database-wide advisory locks as the default concurrency strategy in M01.

## 16. PostgreSQL schema namespace

Use a dedicated application schema such as `core` rather than relying on an unconstrained `public` namespace.

Canonical WP5 name: `core`.

Migration tooling should set/qualify schema explicitly so tests and production behave consistently.

Temporal's own persistence, if self-hosted later, must use a separate database/schema managed by Temporal and is outside this contract.

## 17. ORM and migration-tool boundary

WP5 intentionally defines relational contracts independently of ORM classes.

WP6 may use SQLAlchemy 2.x-style mappings plus Alembic if selected during implementation because the backend is Python, but the relational contract in this document is authoritative over ORM convenience. A tool must not change identity, FK, delete, ordering or fail-closed semantics merely because its defaults differ.

The final dependency/tool selection is made in WP6 together with executable migration tests; this WP5 document does not claim an unverified library version.

## 18. WP6 migration requirements

The initial migration scaffold must prove:

- dependency-safe table creation order;
- empty PostgreSQL database upgrades successfully;
- stable external IDs are unique;
- direct and same-owner composite FKs are active;
- ordered-child uniqueness is active;
- rights fail-closed CHECK is active;
- import ledger uniqueness is active;
- all expected FK lookup indexes exist;
- downgrade/rollback is reversible on an empty/test database where practical;
- migration does not import or mutate repository legacy data;
- no production provider credentials/state are required.

Migration rollback strategy:

- before any production data exists, downgrade may drop the M01 schema/tables in reverse dependency order;
- once operational data exists, a destructive downgrade is not an ordinary production rollback. Application rollback should prefer forward-compatible schema and code rollback procedures;
- WP6 tests must distinguish test-schema downgrade from runtime data deletion.

## 19. WP7 repository proof requirements

Repositories must demonstrate:

- 2-minute project write/read exact canonical round trip;
- 90-minute project write/read exact canonical round trip;
- Character active/pinned historical version survives unchanged;
- ordered Timeline/Act/Sequence/Scene/Shot/Take reconstruction;
- selected Take and selected Attempt ownership survives;
- rights remain publication-blocked by default;
- duplicate external IDs rejected;
- exact WP4 legacy retry becomes noop;
- changed WP4 legacy source becomes conflict;
- forced mid-transaction failure leaves no partial aggregate.

## 20. Explicitly deferred from M01

Not part of this persistence schema yet:

- users/workspaces/RBAC/tenancy;
- billing/subscriptions/entitlements;
- provider credentials/secrets;
- Temporal persistence tables;
- social publishing/analytics/community data;
- web/mobile session state;
- pgvector embeddings and similarity indexes;
- full provider registry/quota runtime;
- production event/outbox architecture unless a later milestone explicitly requires it;
- privacy deletion/account lifecycle beyond current canonical entity semantics.

Adding any of these is not justified merely because PostgreSQL can store it.

## 21. Acceptance verdict for WP5

WP5 is complete when:

1. every current M01 entity has an explicit persistence mapping;
2. stable external IDs are separated from internal DB identity;
3. ordered collections have deterministic storage/reconstruction rules;
4. direct and same-owner relationship constraints are defined;
5. DB-enforced vs aggregate-enforced invariants are explicit;
6. indexes and transaction boundaries are defined;
7. legacy import idempotency has a persistence ledger design;
8. delete/history/rollback policy is explicit;
9. WP6 can implement migrations without making first-time architecture decisions.
