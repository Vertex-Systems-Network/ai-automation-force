# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m01-wp5-postgresql-architecture-complete.md`

Current phase: **M01 — Core Domain & Persistence Boundary**

Status: **M01_DEVELOPMENT_IN_PROGRESS**

## Consent state

Explicit operator consent for scoped M01 development was received on 2026-08-29.

The consent remains valid only for M01. It does not authorize M02+, provider execution, public publishing, paid provider behavior, or other materially expanded scope.

Development consent policy:
`ai-native/DEVELOPMENT-CONSENT-GATE.md`

## Completed work packages

### WP1 — Contract freeze and generated schemas

Merged via PR #1.

Merge commit:
`89e2c69f939a2d2c2350d3f0715da0b310ebeff7`

### WP2 — Full production lineage

Merged via PR #2.

Merge commit:
`d3aa6ba6c36482628a5540473bac0386b40b808c`

Checkpoint:
`checkpoints/2026-08-29-m01-wp2-lineage-complete.md`

### WP3 — Aggregate validation hardening

Merged via PR #3.

Merge commit:
`2e648fd27c44d0186bab76668002114298cc82b8`

Checkpoint:
`checkpoints/2026-08-29-m01-wp3-aggregate-hardening-complete.md`

### WP4 — Legacy CNT content importer boundary

Merged via PR #4.

Merge commit:
`3e3e194be035c6aaf0888a6d2259f12a6219d8ec`

Checkpoint:
`checkpoints/2026-08-29-m01-wp4-legacy-content-import-complete.md`

### WP5 — PostgreSQL persistence architecture

Architecture contract complete on PR #5.

Checkpoint:
`checkpoints/2026-08-29-m01-wp5-postgresql-architecture-complete.md`

Canonical mapping:
`docs/architecture/POSTGRESQL-PERSISTENCE-ARCHITECTURE.md`

The persistence boundary now defines internal UUID keys vs stable external IDs, relational/JSONB/array mappings for every current M01 entity/value object, deterministic ordered joins, same-owner deferred selection/pin constraints, indexes, transaction/revision policy, fail-closed Rights checks, legacy import ledger design, and explicit DB-vs-aggregate invariant ownership.

## Current next step

`WP6 — Reversible initial database migration scaffold`

## Remaining M01 sequence

1. WP6 — reversible migration scaffold;
2. WP7 — repositories and short/long project round-trip verification;
3. WP8 — complete M01 verification and final checkpoint.

## Scope boundary

M01 still excludes Temporal runtime orchestration, provider adapters/generation calls, web/mobile product implementation, publishing/analytics, autonomous spend, and M02+ development.

## GitHub ↔ Linear

GitHub remains canonical for engineering contracts, implementation evidence, and checkpoints. Linear mirrors work-package status and acceptance evidence.
