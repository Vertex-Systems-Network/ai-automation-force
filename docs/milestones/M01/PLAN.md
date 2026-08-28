# M01 — Core Domain and Persistence Boundary

## Objective

Freeze provider-neutral domain contracts and establish PostgreSQL persistence/migration boundaries without starting workflows/providers/UI.

## Entry criteria

- Full Project Preplanning Gate complete.
- Explicit M01 development consent granted.
- Current existing Python domain work audited as baseline.
- Target Python/PostgreSQL versions revalidated.

## Dependencies

`P0 Full Preplanning -> M01`

No dependency on external AI providers.

## Work packages

### M01-WP1 — Contract freeze and generated schemas
- audit Pydantic models/enums;
- reconcile generated JSON Schemas;
- deterministic schema export;
- compatibility/version markers.

### M01-WP2 — Full lineage fixtures/invariants
Fixtures for:
- Project -> Content Version;
- Character -> Version -> Lock;
- Asset -> Rights/Provenance;
- Job -> Attempt -> QA -> Cost;
- Scene/Shot -> Take -> approved take;
- approval references.

### M01-WP3 — Aggregate validation hardening
- cross-reference validity;
- duration 60–10,800 sec;
- timeline hierarchy;
- locked entity/version rules;
- approval/rights linkage;
- provider-neutral invariants.

### M01-WP4 — Legacy content importer boundary
- import old `CNT-*` records;
- map into canonical content/version model;
- idempotent import;
- preserve source references;
- reject ambiguous/corrupt legacy input safely.

### M01-WP5 — PostgreSQL persistence architecture
- table/domain mapping;
- IDs/timestamps/version columns;
- JSONB vs normalized decisions;
- tenant/workspace columns reserved where future model requires;
- pgvector extension boundary but no content-memory implementation yet;
- repository interfaces.

### M01-WP6 — Reversible initial migrations
- migration framework;
- create schema/indexes/constraints;
- upgrade from empty;
- downgrade where safe;
- forward-recovery note for irreversible operations.

### M01-WP7 — Repositories and round trips
- repository implementations;
- transactions;
- optimistic concurrency/version handling;
- 2-minute song round trip;
- 90-minute movie-plan round trip;
- >3h rejection.

### M01-WP8 — Verification/checkpoint
- lint/type/tests;
- schema determinism;
- migration tests;
- persistence/integrity;
- final evidence/checkpoint;
- no automatic M02 start.

## Expected modules/files

- `packages/python-core/`
- `schemas/`
- new persistence/repository package location decided within monorepo conventions;
- migration directory;
- `tests/domain/`, `tests/persistence/`;
- M01 checkpoint/docs.

## Data/migration impact

Creates initial operational relational schema. No production customer migration expected yet. Legacy repository content import is explicit and non-destructive.

## API/UI impact

None beyond machine contracts. No public FastAPI or web UI required.

## Security/cost/rights impact

- enforce tenant-ready ownership fields where modeled;
- no secrets/provider calls;
- no paid spend;
- rights/provenance records persisted but not externally enforced yet.

## Test/acceptance

Apply Master QA:
- static/unit/domain;
- migration upgrade/recovery;
- repository integration;
- cross-reference invariants;
- short/long fixtures;
- no provider spend.

## Rollout/rollback

Development-only initial schema. Roll back code/migrations in isolated DB. Never overwrite legacy source data during importer tests.

## Exit criteria

- provider-neutral schemas stable/generated;
- persistence round trips pass for representative 2m and 90m projects;
- 180m allowed/over-limit rejected according to contract;
- migrations verified;
- known gaps recorded;
- M01 acceptance bundle complete.

## Non-goals

- FastAPI runtime;
- Temporal;
- object storage;
- provider adapters;
- generation;
- web/mobile;
- auth/billing/social/publishing implementation.
