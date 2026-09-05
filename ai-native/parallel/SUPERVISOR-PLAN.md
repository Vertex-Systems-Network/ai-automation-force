# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03 Governance Hold | `supervisor-agent` | `supervisor/m03-governance-hold-current` | active governance-only hold; broadcast 12 synchronized |
| M04 Character | `character-agent` | `agent/m04-character-library` | broadcast 12 synchronized; planning-only; dependency-gated |
| M05 Content | `content-agent` | `agent/m05-content-memory` | broadcast 12 synchronized; planning-only; dependency-gated |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | broadcast 12 synchronized; planning-only; dependency-gated |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | broadcast 12 synchronized; planning-only; dependency-gated |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | broadcast 12 synchronized; planning-only; dependency-gated |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security-current` | broadcast 12 synchronized; audit/planning only |

Completed QA submission branch `agent/cross-cutting-qa-security` is retired from active authority after PR #74. `agent/cross-cutting-qa-security-current` is the fresh current-main audit/planning branch. Earlier completed M03/WP8 submission/review/closeout branches remain retired.

## M03 source completion and external hold

M03 implementation, WP8 source acceptance, and source-side closeout are complete. Issue #36 remains the final M03 protected-main governance blocker because live GitHub enforcement is not verified. No additional WP7/WP8 product/API/schema/provider work is authorized by this state.

Migrations `20260901_0015` and `20260901_0016` remain landed; there is no active M03 migration reservation.

## Cross-cutting QA promotion

PR #74 landed `docs/qa/ADVERSARIAL-AUDIT-PLAN.md` and the QA checkpoint at `main@6eab0440ef32280c16e41b41851deb3f11937495` after exact-head Repository Governance, Core Domain Contracts and Durable Control Plane passed.

The plan reuses current M03 focused evidence and assigns future adversarial obligations only where later modules introduce new trust or authority surfaces. It covers authority isolation, tenant validation, memory poisoning, provider-output distrust, secret handling, budget/retry ceilings, rights/provenance and multimodal instruction isolation.

Broadcast 12 records this cross-cutting acceptance guidance because future M04-M08 work must observe it. The broadcast is an acceptance/planning constraint, not feature-execution authority.

## Dependency and consent boundary

- M04 and M06 remain dependent on `M03-GOV-HOLD`.
- M05 remains dependent on M04.
- M07 remains dependent on M04/M05/M06.
- M08 remains dependent on M04/M07.
- Cross-cutting QA has no module dependency but remains audit/planning only unless an applicable executable scope authorizes tests.
- `docs/milestones/M04/PLAN.md` requires M01-M03 accepted plus explicit M04 consent before executable M04 work.
- The repository threat model explicitly states generic `continue` is not privileged development, publish or security authorization.

Therefore no later module may treat branch synchronization or conversational continuation as satisfying its executable entry criteria.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. Later planning lanes remain disjoint and may update only their claimed planning/checkpoint surfaces. QA owns `docs/qa/**` and its checkpoint plus shared-request access to security docs; executable product/test changes require separate applicable scope.

## Hold order

1. maintain Issue #36 as `EXTERNAL_NOT_VERIFIED` while protected-main evidence is absent;
2. preserve broadcast 12 adversarial obligations in future milestone acceptance;
3. do not start M04/M06 executable work until M03 acceptance/governance dependency and explicit executable consent are satisfied;
4. do not promote downstream M05/M07/M08 past their dependency chain;
5. do not create synthetic provider/admin/production evidence from mocks or source CI.

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications, and unresolved review findings. Required exact-head CI must be green.

After a successful promotion that active agents must observe, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
