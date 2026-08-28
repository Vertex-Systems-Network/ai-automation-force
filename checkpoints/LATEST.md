# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m01-complete.md`

Current phase: **M01 — Core Domain & Persistence Boundary**

Status: **M01_COMPLETE**

## Consent state

Explicit operator consent for scoped M01 development was received on 2026-08-29 and has now been fully consumed by completed M01 work.

That consent does **not** authorize M02+, provider execution, public publishing, paid provider behavior, or any materially expanded scope.

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

Merged via PR #5.

Merge commit:
`b456c1732dcd01e0505f501b3560387613ce54be`

Checkpoint:
`checkpoints/2026-08-29-m01-wp5-postgresql-architecture-complete.md`

Canonical mapping:
`docs/architecture/POSTGRESQL-PERSISTENCE-ARCHITECTURE.md`

### WP6 — Reversible PostgreSQL migration scaffold

Merged via PR #6.

Merge commit:
`6f7d5fcd7dd152f5bc5db9c93658e8fc152ed3b3`

Checkpoint:
`checkpoints/2026-08-29-m01-wp6-migrations-complete.md`

Verified GitHub Actions run/job:
`33219768541 / 99011168309`

### WP7 — Persistence repositories and round trips

Merged via PR #7.

Merge commit:
`8fcc33ae900e2781db34d52622577b2993cf45b8`

Verified PR executable head:
`c4cb38a385a5412987f160c75c9db190c21df4f7`

Verified GitHub Actions run/job:
`33221966779 / 99017705054`

The verified PR head and merged squash commit resolve to the same executable tree:
`89e649726bf071bfb143e4a3a0021eb2317502d9`

Permanent Python 3.12 + PostgreSQL 18 CI passed Ruff, strict mypy, unit/integration tests, schema synchronization and compile checks.

### WP8 — Final M01 verification

Complete.

Final checkpoint:
`checkpoints/2026-08-29-m01-complete.md`

M01 acceptance includes:
- domain/full-lineage/aggregate tests;
- legacy importer and non-mutation protection;
- PostgreSQL constraints and reversible migration lifecycle;
- 2-minute and 90-minute persistence round trips;
- >3-hour rejection protection;
- pinned CharacterVersion/selected Take retention;
- fail-closed Rights behavior;
- transaction rollback/integrity behavior;
- generated-schema reproducibility;
- permanent Python 3.12 + PostgreSQL 18 CI evidence.

## Current next step

**Planning/review only for M02 unless new explicit development consent is received.**

Next development milestone:
`M02 — Durable Workflow Control Plane`

M02 executable development requires a new scoped development brief and fresh explicit operator consent.

Generic `continue`, `next`, `resume`, or `audit` instructions do not authorize M02 development.

## Scope boundary

M01 completion does not include Temporal runtime orchestration, provider adapters/generation calls, object storage/media execution, web/mobile product implementation, auth/RBAC, publishing/analytics, autonomous spend, production DB rollout, or M02+ development.

## Known governance risk

GitHub currently reports `main` as unprotected with no required-status-check enforcement. This should be hardened before or during M02 governance work without bypassing the consent gate.

## GitHub ↔ Linear

GitHub remains canonical for engineering contracts, implementation evidence, and checkpoints. Linear mirrors work-package status and acceptance evidence.
