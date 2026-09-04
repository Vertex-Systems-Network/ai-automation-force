# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are currently occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03-WP7 Closeout | `supervisor-agent` | `supervisor/m03-wp7-closeout` | governance-only closeout/handoff |
| M03-WP8 | `acceptance-agent` | `agent/m03-wp8-acceptance` | sync-required planning-only until closeout lands |
| M04 Character | `character-agent` | `agent/m04-character-library` | sync-required planning-only |
| M05 Content | `content-agent` | `agent/m05-content-memory` | sync-required planning-only |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | sync-required planning-only |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | sync-required planning-only |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | sync-required planning-only |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | sync-required audit/planning |

## WP7 closeout

PR #63 landed deterministic provider-neutral vector/index cleanup hooks at `main@4a898d0465382c62ae911a4d7f4581b4fdd2d60c`. The bounded WP7 implementation sequence now includes lifecycle state/retention, deletion planning/execution, temporary cleanup, private export staging, and vector/index cleanup hooks. Migrations `20260901_0015` and `20260901_0016` are landed; no active migration reservation remains.

Issue #64 on `supervisor/m03-wp7-closeout` records mandatory broadcast 9 and the handoff checkpoint only. No product/API/schema/provider change is authorized.

After this closeout lands, `agent/m03-wp8-acceptance` may synchronize to the resulting current main and move from planning-only to bounded executable acceptance. Source acceptance may run, but final M03 governance/promotion remains blocked by Issue #36 until live GitHub main protection/ruleset evidence exists.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for write claims. Overlapping authoritative write claims block execution. All non-Supervisor lanes are sync-required by broadcast 9 and cannot seek promotion until synchronization is recorded.

## Merge order

1. `supervisor/m03-wp7-closeout`
2. synchronized `agent/m03-wp8-acceptance`
3. M03 close/reconciliation only after acceptance and external governance gate evaluation
4. later milestones according to dependency/consent gates

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, write ownership, migration state, dependency/consent state, tests, security/data implications, current-main freshness, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
