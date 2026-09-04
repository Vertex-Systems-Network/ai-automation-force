# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed executable branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are currently occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03-WP7 Supervisor | `supervisor-agent` | `supervisor/m03-wp7-vector-index-cleanup` | active bounded vector/index cleanup hooks |
| M03-WP8 | `acceptance-agent` | `agent/m03-wp8-acceptance` | sync-required planning-only |
| M04 Character | `character-agent` | `agent/m04-character-library` | sync-required planning-only |
| M05 Content | `content-agent` | `agent/m05-content-memory` | sync-required planning-only |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | sync-required planning-only |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | sync-required planning-only |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | sync-required planning-only |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | sync-required audit/planning |

## Current Supervisor slice

PR #61 landed bounded private export staging at `main@98e6808ec4034b93a4f1b417563f27866c6e91de`. Migration `20260901_0016` is landed history and the export-staging branch is retired for new executable work.

Issue #62 runs on `supervisor/m03-wp7-vector-index-cleanup`, created from that exact main. This slice adds deterministic vector/index cleanup-hook contracts only. Hooks must be explicit, project-scoped, idempotent, auditable, and fail closed on asset/project/revision identity mismatch. No direct external vector/database credentials, provider spend, broad index mutation, hidden side effects, public delivery authority, or unrelated milestone work is authorized.

Authoritative implementation writes are limited to:
- `packages/python-core/src/lullabies_core/index_cleanup.py`
- `packages/python-core/tests/test_index_cleanup.py`

No migration is reserved for this slice. If durable execution state proves necessary, implementation stops and the Supervisor must first reserve a new migration revision.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for write claims. Overlapping authoritative write claims block execution. All non-Supervisor occupied lanes are sync-required by broadcast 8 and cannot seek promotion until synchronization is recorded.

## Merge order

1. `supervisor/m03-wp7-vector-index-cleanup`
2. M03-WP8 acceptance after synchronization and WP7 completion
3. M03 close/reconciliation
4. later milestones according to dependency/consent gates

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. That signal means ready for Supervisor review, not merged.

Before promotion, the Supervisor verifies exact head/base, write ownership, migration state, dependency/consent state, tests, security/data implications, current-main freshness, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**

Then reconcile broadcasts, state, slots, active work, migration state, and affected branch synchronization before the next executable slice starts.
