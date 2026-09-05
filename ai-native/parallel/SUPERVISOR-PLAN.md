# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03 Governance Hold | `supervisor-agent` | `supervisor/m03-wp8-closeout` | active governance-only hold |
| M04 Character | `character-agent` | `agent/m04-character-library` | sync-required planning-only |
| M05 Content | `content-agent` | `agent/m05-content-memory` | sync-required planning-only |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | sync-required planning-only |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | sync-required planning-only |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | sync-required planning-only |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | sync-required audit/planning |

The completed `agent/m03-wp8-acceptance-v2` and `supervisor/m03-wp8-review` branches are retired from active execution authority. The earlier `agent/m03-wp8-acceptance` branch also remains retired and is not promotion authority.

## M03 source completion

PR #68 landed the canonical WP8 acceptance matrix/checkpoint at `main@c61955f56ef5c9c7f3e6ff717e12dac5364d8fc3`. Its exact head `66d81de4a4c0aea16186dae43d3a1922cd8d2123` passed Repository Governance, Core Domain Contracts, and Durable Control Plane before merge.

Broadcast 11 records that successful promotion. WP7 implementation and WP8 source acceptance are complete. Migrations `20260901_0015` and `20260901_0016` remain landed; there is no active M03 migration reservation.

No further WP7/WP8 product/API/schema/provider implementation is authorized by this closeout.

## External governance boundary

Issue #36 is now the only M03 blocker. Live GitHub repository ruleset read-back still returns `[]`, so protected-main enforcement is not verified.

The current connector exposes ruleset read-only access and no administration/environment write action. Therefore the Supervisor must not claim, simulate, or bypass live protection. An administrator must apply and verify the retained protection policy from an admin-capable context, after which Issue #36 can be re-evaluated against repository-native read-back evidence.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. The M03 governance-hold lane owns only:

- `ai-native/parallel/checkpoints/M03-GOV-HOLD.md`

All later milestone and QA lanes remain disjoint, sync-required by broadcast 11, and planning-only until their dependency/consent gates are explicitly satisfied.

## Merge / hold order

1. merge `supervisor/m03-wp8-closeout` only after exact-head Repository Governance, Core Domain Contracts and Durable Control Plane are green;
2. keep Issue #36 open while live ruleset/protection read-back is absent;
3. do not start new M03 source implementation while the external governance hold is active;
4. later milestone execution requires fresh scope/dependency synchronization and may not treat unresolved M03 governance as completed.

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
