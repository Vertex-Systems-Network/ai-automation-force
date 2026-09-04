# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices always start from current `main`; completed executable branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are currently occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03-WP7 Supervisor | `supervisor-agent` | `supervisor/m03-wp7-export-staging` | active export-staging slice |
| M03-WP8 | `acceptance-agent` | `agent/m03-wp8-acceptance` | sync-required planning-only |
| M04 Character | `character-agent` | `agent/m04-character-library` | sync-required planning-only |
| M05 Content | `content-agent` | `agent/m05-content-memory` | sync-required planning-only |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | sync-required planning-only |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | sync-required planning-only |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | sync-required planning-only |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | sync-required audit/planning |

## Current Supervisor slice

PR #59 landed bounded temporary cleanup at `main@f78a855f0b20dd150af93190b25bffbe6e1a0856`. Branch `supervisor/m03-wp7-temp-cleanup` is retired for new executable work.

Issue #60 runs on `supervisor/m03-wp7-export-staging`, created from that exact main. Migration `20260901_0016` is reserved with parent `20260901_0015` because existing `storage_objects` metadata cannot durably represent both export-source provenance and bounded expiry.

Authoritative writes are limited to:
- `packages/python-core/src/lullabies_core/export_staging.py`
- `packages/python-core/src/lullabies_core/persistence/export_staging.py`
- `packages/python-core/migrations/versions/20260901_0016_export_staging.py`
- `packages/python-core/migrations/sql/0016_export_staging_up.sql`
- `packages/python-core/migrations/sql/0016_export_staging_down.sql`
- `packages/python-core/tests/test_export_staging.py`
- `packages/python-core/tests/test_migrations.py`

Export staging must remain private and must not widen signed delivery, share-link, or public publishing authority. Stage/reuse is bound to project, source storage identity, source SHA-256, deterministic staging object identity/key, and expiry. Conflicting reuse fails closed. No vector/index cleanup, provider spend, production credential, release, or public endpoint work is authorized in this slice.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for write claims. Overlapping authoritative write claims block execution. `future_executable_writes` are informational only. Migration reservations must be recorded before files are created.

All non-Supervisor occupied lanes are currently sync-required by broadcast 7 and cannot seek promotion until synchronization is recorded.

Planning path ownership remains:
- M04: `docs/milestones/M04/**` and `ai-native/parallel/checkpoints/M04-PARALLEL-LANE.md`
- M05: `docs/milestones/M05/**` and `ai-native/parallel/checkpoints/M05-PARALLEL-LANE.md`
- M06: `docs/milestones/M06/**` and `ai-native/parallel/checkpoints/M06-PARALLEL-LANE.md`
- M07: `docs/milestones/M07/**` and `ai-native/parallel/checkpoints/M07-PARALLEL-LANE.md`
- M08: `docs/milestones/M08/**` and `ai-native/parallel/checkpoints/M08-PARALLEL-LANE.md`
- QA: `docs/qa/**` and `ai-native/parallel/checkpoints/CROSS-CUTTING-QA.md`

## Merge order

1. `supervisor/m03-wp7-export-staging`
2. fresh bounded M03-WP7 vector/index cleanup branch
3. M03-WP8 acceptance after synchronization and WP7 completion
4. M03 close/reconciliation
5. later milestones according to dependency/consent gates

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. That signal means ready for Supervisor review, not merged.

Before promotion, the Supervisor verifies exact head/base, write ownership, migration reservation, dependency/consent state, tests, security/data implications, current-main freshness, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**

Then update `SUPERVISOR-BROADCASTS.yaml`, `SUPERVISOR-STATE.yaml`, slot/active registries, migration state, and affected branch synchronization before the next executable slice starts.
