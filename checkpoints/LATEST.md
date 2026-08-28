# Latest Checkpoint

Current checkpoint:
`checkpoints/2026-08-29-m01-wp2-lineage-complete.md`

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

Verified on Python 3.12 with Ruff, strict mypy, tests, generated-schema synchronization, and compile checks.

### WP2 — Full lineage model fixture

Implementation and verification complete on the WP2 branch/PR.

Checkpoint:
`checkpoints/2026-08-29-m01-wp2-lineage-complete.md`

The full provider-neutral production lineage now validates Project/Content/Character/Timeline/Take/Job/Attempt/Asset/QA/Cost/Rights ownership and fail-closed rights behavior.

## Current next step

`WP3 — Aggregate validation hardening`

WP3 may proceed under the existing M01 consent after WP2 is merged. Only invariants supported by current canonical contracts may be added; unresolved advanced editorial semantics remain deferred.

## Remaining M01 sequence

1. WP3 — aggregate validation hardening;
2. WP4 — legacy `CNT-*` content importer boundary;
3. WP5 — PostgreSQL persistence architecture;
4. WP6 — reversible migration scaffold;
5. WP7 — repositories and short/long project round-trip verification;
6. WP8 — complete M01 verification and final checkpoint.

## Scope boundary

M01 still excludes Temporal runtime orchestration, provider adapters/generation calls, web/mobile product implementation, publishing/analytics, autonomous spend, and M02+ development.

## GitHub ↔ Linear

GitHub remains canonical for engineering contracts, implementation evidence, and checkpoints. Linear mirrors work-package status and acceptance evidence.
