# Milestone 1 — Execution Plan

Status: `PLANNING_READY_FOR_CONSENT`

This document refines Milestone 1 into buildable work packages. It does not authorize executable development. `ai-native/DEVELOPMENT-CONSENT-GATE.md` remains mandatory.

## Goal

Stabilize the generalized provider-neutral domain contracts and persistence boundary before Milestone 2 introduces durable runtime orchestration.

Milestone 1 is complete only when current repository-backed content can coexist safely with a tested PostgreSQL persistence model without rewriting historical source files.

## Work package order

### WP1 — Contract freeze and generated schemas

Objective:
- reconcile all current Pydantic domain contracts;
- generate JSON Schema Draft 2020-12 artifacts;
- decide which generated artifacts are committed versus build-only;
- assign schema IDs and versioning rules;
- verify schemas remain backwards-compatible with the existing repository-first content layer.

Acceptance gates:
- all current models export schemas deterministically;
- generated files are reproducible from source contracts;
- no legacy schema is overwritten;
- schema versioning policy is documented.

Rollback:
- generated artifacts are disposable/regenerable;
- source domain models remain the authoritative code layer during M1.

### WP2 — Full lineage model fixture

Build one complete non-provider fixture that connects:

`Project -> Content -> Character -> CharacterVersion -> CharacterLock -> Timeline -> Act -> Sequence -> Scene -> Shot -> Take -> Job -> GenerationAttempt -> Asset -> QARecord -> CostRecord -> RightsRecord`

The fixture should prove:
- stable external IDs remain intact;
- selected Take belongs to the intended Shot;
- GenerationAttempt belongs to the intended Job;
- generated Asset points to the correct attempt/parents;
- QA outcome belongs to the actual asset/take;
- CostRecord belongs to the actual generation attempt;
- RightsRecord is fail-closed until explicitly resolved;
- locked CharacterVersion cannot silently change.

Acceptance gates:
- valid full-lineage fixture passes;
- broken parent linkage fails;
- cross-project linkage fails;
- missing locked version fails;
- unresolved rights remain publication-blocking.

### WP3 — Aggregate validation hardening

Current `ProjectBundle` already validates graph membership and important references. Extend only where the current domain model has sufficient ownership information.

Planned checks:
- deterministic sibling ordering;
- no duplicate canonical primary-video ownership where disallowed;
- timeline start/end bounds;
- selected Take consistency;
- referenced Character/Look/Location/Prop/World existence;
- Character lock pin ownership;
- timeline/project duration agreement;
- primary-video overlap rules once canonical track semantics are typed.

Do not invent editing rules that have not yet been modeled.

### WP4 — Legacy content importer boundary

Goal:
preserve existing `schemas/content-package.schema.json` and historical `CNT-*` packages while allowing them to be represented inside the generalized domain.

Importer behavior:
1. read legacy package without modifying it;
2. validate legacy schema;
3. normalize supported fields;
4. map legacy age band into AudienceProfile/policy profile;
5. map legacy content type into generalized ContentFormat/content subtype;
6. preserve original `CNT-*` external ID;
7. produce generalized `Content` + `ContentVersion` records;
8. attach import provenance including source path/hash/schema version;
9. reject invalid/ambiguous packages instead of guessing destructive mappings;
10. be idempotent when the same legacy package is imported twice.

Migration principle:
legacy content is an input source, not an object to rewrite in place.

Acceptance gates:
- valid legacy fixture imports deterministically;
- second import does not create duplicate canonical content;
- malformed legacy package fails safely;
- original files remain byte-for-byte unchanged.

### WP5 — PostgreSQL persistence architecture

Do not begin with ORM tables blindly. First map aggregates and invariants.

Recommended persistence rules:
- internal DB primary keys: UUID/UUIDv7-style identifiers where supported and operationally practical;
- stable external IDs remain unique business/audit identifiers (`PRJ-*`, `CHR-*`, `CNT-*`, etc.);
- parent/child relationships use DB foreign keys internally;
- external IDs get unique indexed columns;
- ordered children use explicit order fields plus scoped uniqueness constraints;
- locked versions use foreign keys to immutable/versioned records;
- selected Take uses an explicit relationship constrained to the parent Shot where practical;
- Rights publication state remains fail-closed;
- generation/cost/history records are append-oriented;
- destructive cascade behavior is conservative for canonical history.

Initial persistence areas:
- projects and profiles;
- characters + versions + looks + locks;
- worlds/locations/props/styles/voices;
- content + versions;
- hierarchy: acts/sequences/scenes/shots/takes/timeline;
- assets;
- jobs/attempts;
- QA/cost/rights/approvals.

Out of scope:
- provider API state machines;
- Temporal persistence;
- users/workspaces/RBAC unless absolutely required for schema isolation design (not expected in M1);
- analytics tables;
- publishing tables beyond fields already required by canonical rights/approval records.

### WP6 — Migration scaffold

Initial database migration must:
- create tables in dependency-safe order;
- enforce stable external-ID uniqueness;
- enforce required foreign keys;
- use explicit indexes for common lookup paths;
- remain reversible where practical;
- avoid destructive transformation of repository data;
- include a clean empty-database upgrade test;
- include downgrade/rollback validation where supported and safe.

No automatic import of the repository into production DB should occur as a side effect of migration itself. Import remains an explicit application/maintenance operation.

### WP7 — Persistence repositories and round trips

Create repository/service boundaries only after tables are stable.

Required proof cases:
- 2-minute song project write/read round trip;
- 90-minute movie-plan write/read round trip;
- Character + pinned version survives round trip unchanged;
- timeline hierarchy preserves ordering;
- selected Take survives round trip;
- RightsRecord keeps publication blocked by default;
- duplicate stable external ID is rejected;
- transaction failure does not leave half-persisted canonical aggregate.

### WP8 — Milestone 1 verification

Required gates before M1 can be marked DONE:
- Ruff/lint;
- Python compile/import checks;
- all domain tests;
- full lineage tests;
- aggregate graph tests;
- schema reproducibility check;
- legacy importer tests;
- PostgreSQL constraint tests;
- migration upgrade test;
- migration rollback/downgrade test where practical;
- 2-minute project round trip;
- 90-minute project round trip;
- >3-hour invalid project rejection remains green;
- no mutation of existing legacy content fixtures/files.

If GitHub-hosted Actions remain unavailable, use an approved/self-hosted runner or report CI as `NOT VERIFIED`; local passing tests do not become a fake CI pass.

## Proposed implementation sequence

1. freeze current domain contract surface;
2. generate/reconcile schemas;
3. add lineage fixture/tests;
4. harden aggregate validators;
5. implement legacy importer;
6. write persistence ADR/mapping;
7. scaffold PostgreSQL models/migrations;
8. add persistence repositories;
9. run round-trip/integrity/migration tests;
10. update checkpoint;
11. request separate consent before Milestone 2.

## Risk register

### Risk: premature DB coupling
Mitigation: keep Pydantic domain contracts provider/ORM-neutral; map persistence separately.

### Risk: legacy data loss
Mitigation: importer is read-only toward repository history and idempotent.

### Risk: over-constraining timeline model too early
Mitigation: validate only invariants supported by current product model; defer advanced editorial semantics to timeline milestone.

### Risk: external ID versus DB key confusion
Mitigation: preserve stable external IDs as unique audit/business identifiers while using separate DB keys internally.

### Risk: cascade deletes destroying history
Mitigation: conservative delete behavior; canonical history is append-oriented and explicitly archived rather than casually cascaded.

### Risk: tests passing only against one runtime
Mitigation: target Python 3.12 in CI plus current local compatibility checks.

## Development boundary

The next action after this planning document is executable development beginning with WP1.

That action is BLOCKED until explicit operator consent is received for `docs/architecture/M1-DEVELOPMENT-CONSENT-BRIEF.md`.
