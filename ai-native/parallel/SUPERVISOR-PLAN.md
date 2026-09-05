# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03 Governance Hold | `supervisor-agent` | `supervisor/m03-governance-hold-current` | active governance-only hold |
| M04 Character | `character-agent` | `agent/m04-character-library` | broadcast-11 synchronized; planning-only; dependency-gated |
| M05 Content | `content-agent` | `agent/m05-content-memory` | broadcast-11 synchronized; planning-only; dependency-gated |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | broadcast-11 synchronized; planning-only; dependency-gated |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | broadcast-11 synchronized; planning-only; dependency-gated |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | broadcast-11 synchronized; planning-only; dependency-gated |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | broadcast-11 synchronized; audit/planning only |

The completed `agent/m03-wp8-acceptance-v2`, `supervisor/m03-wp8-review`, and `supervisor/m03-wp8-closeout` branches are retired from active execution authority. The earlier `agent/m03-wp8-acceptance` branch also remains retired and is not promotion authority.

## M03 source completion

PR #68 landed the canonical WP8 acceptance matrix/checkpoint. PR #70 then reconciled post-WP8 governance state and merged to `main@0d79b73e112c8145244f01abcaa7b2489ac03560`. Both promotions passed exact-head Repository Governance, Core Domain Contracts, and Durable Control Plane before merge.

Broadcast 11 records WP8 source acceptance. WP7 implementation and WP8 source acceptance/closeout are complete. Migrations `20260901_0015` and `20260901_0016` remain landed; there is no active M03 migration reservation.

No further WP7/WP8 product/API/schema/provider implementation is authorized by this closeout.

## Broadcast 11 synchronization

Before Issue #71 reconciliation, M04, M05, M06, M07, M08, and cross-cutting QA were each exactly 0 commits ahead and 11 commits behind current main. Each branch was non-force fast-forwarded to `main@0d79b73e112c8145244f01abcaa7b2489ac03560`; no unique work was discarded.

This synchronization clears only the stale mandatory broadcast receipt. It does **not** expand consent or satisfy dependency gates.

## External governance boundary

Issue #36 is the remaining M03 blocker. Live GitHub branch read-back shows `main` is not protected and repository rulesets remain empty. Protected-main enforcement is therefore not verified.

The current connector exposes ruleset/protection read evidence but no administration/environment write action. The Supervisor must not claim, simulate, or bypass live protection. An administrator must apply and verify the retained protection policy from an admin-capable context, after which Issue #36 can be re-evaluated against repository-native read-back evidence.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. The M03 governance-hold lane owns only:

- `ai-native/parallel/checkpoints/M03-GOV-HOLD.md`

Later milestone lanes are now synchronized but remain planning-only under their existing consent/dependency contracts. In particular, M04 and M06 depend on `M03-GOV-HOLD`; M05 depends on M04; M07 depends on M04/M05/M06; M08 depends on M04/M07. Cross-cutting QA remains audit/planning only unless an applicable executable scope is granted.

## Hold order

1. keep Issue #36 open while live protected-main evidence is absent;
2. do not start new M03 product implementation while the external governance hold is active;
3. do not treat broadcast synchronization as feature-execution authority;
4. later milestone execution requires its dependency chain plus explicit executable scope/consent to be satisfied.

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion that active agents must observe, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
