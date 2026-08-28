# M01 / WP5 — PostgreSQL Persistence Architecture Complete

Date: 2026-08-29

Status: `M01_DEVELOPMENT_IN_PROGRESS`

Work package: `WP5 — PostgreSQL persistence architecture`

## Result

WP5 is architecture-complete.

Canonical persistence contract:

`docs/architecture/POSTGRESQL-PERSISTENCE-ARCHITECTURE.md`

The document maps every current M01 entity/value-object boundary into an explicit PostgreSQL storage strategy without introducing ORM or migration implementation prematurely.

## Locked persistence decisions

- PostgreSQL operational state lives in application schema `core`;
- independently persisted entities use internal UUID primary keys;
- stable external IDs remain separate unique business/audit identifiers;
- internal relationships use UUID foreign keys;
- expandable taxonomy values remain text rather than PostgreSQL ENUM;
- domain value objects use validated JSONB where independent relational identity is unnecessary;
- scalar metadata collections use arrays where appropriate;
- entity relationships use relational join tables, with explicit `position` when canonical order must round-trip;
- hierarchy collections are derived from parent FKs/order rather than redundantly storing ID arrays;
- cyclic active/selected/pinned relationships use DEFERRABLE same-owner FK designs;
- Rights publication remains fail-closed at SQL CHECK level;
- canonical production/history records use conservative `ON DELETE RESTRICT`/append-oriented semantics;
- WP4 idempotency is operationalized through a persistence-only `legacy_content_imports` ledger;
- optimistic revision semantics and aggregate transaction boundaries are defined;
- DB-enforced versus Pydantic/repository aggregate invariants are explicitly separated;
- expected initial indexes and WP6/WP7 proof requirements are defined.

## Coverage

Explicit mappings exist for:

- Project and Project value objects;
- Content / ContentVersion / ContentObjective;
- Character / CharacterVersion / CharacterLook / CharacterLock;
- World / Location / Prop / StyleProfile / VoiceProfile;
- Timeline / TimelineTrack / Act / Sequence / Scene / Shot / Take / continuity state;
- Asset;
- Job;
- GenerationAttempt / GenerationRequest / ProviderModelRef;
- QARecord;
- CostRecord;
- RightsRecord;
- Approval;
- ordered relationship collections;
- legacy content import ledger.

## Verification evidence

PR #5 is documentation-only.

Changed executable/config/schema files: `0`.

Changed architecture files before checkpointing: `1`:

`docs/architecture/POSTGRESQL-PERSISTENCE-ARCHITECTURE.md`

The persistence contract was checked against the current M01 Pydantic domain and `M1-EXECUTION-PLAN.md`. No conflicting pre-existing ORM/migration-tool decision was found.

Because WP5 changes no executable code or machine-readable runtime configuration, no fake CI pass is claimed. Executable PostgreSQL/migration verification begins in WP6.

## Scope boundary preserved

WP5 did **not**:

- install SQLAlchemy/Alembic or any DB driver;
- create tables or migration files;
- connect to or mutate PostgreSQL;
- import legacy repository content;
- implement repositories;
- add provider execution, Temporal, auth/UI, publishing, analytics, or M02+ behavior.

## Next authorized work

Within the already-approved M01 scope:

`WP6 — Reversible initial database migration scaffold`

WP6 must implement the WP5 contract, add dependency/tooling only as required, and verify upgrade/downgrade plus core constraints against PostgreSQL without automatically importing repository data.
