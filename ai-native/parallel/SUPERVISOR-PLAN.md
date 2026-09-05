# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

Planning synchronization, a green planning PR, or conversational continuation does not grant privileged/executable development authority.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03 Governance Hold | `supervisor-agent` | `supervisor/m03-governance-hold-current` | active governance-only hold; broadcast 13 synchronized |
| M04 Character | `character-agent` | `agent/m04-character-library-current` | broadcast 13 synchronized; planning hardened; executable hold |
| M05 Content | `content-agent` | `agent/m05-content-memory` | broadcast 13 synchronized; planning-only; dependent on executable M04 |
| M06 Audio | `audio-agent` | `agent/m06-audio-production` | broadcast 13 synchronized; planning-only; M03 governance dependency retained |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | broadcast 13 synchronized; planning-only; dependent on M04/M05/M06 |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | broadcast 13 synchronized; planning-only; dependent on M04/M07 |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security-current` | broadcast 13 synchronized; audit/planning only |

Completed `agent/m04-character-library` is retired after squash-merge PR #78 and is not force-reset or reusable as promotion authority. `agent/m04-character-library-current` is the fresh current-main planning branch. Earlier completed QA and M03/WP8 submission/review/closeout branches remain retired.

## M03 source completion and external hold

M03 implementation, WP8 source acceptance, and source-side closeout are complete. Issue #36 remains the final M03 protected-main governance blocker because live GitHub enforcement is not verified.

Migrations `20260901_0015` and `20260901_0016` remain landed; there is no active M03 or M04 migration reservation. No additional WP7/WP8 product/API/schema/provider work is authorized by this state.

## Cross-cutting QA promotion

PR #74 landed `docs/qa/ADVERSARIAL-AUDIT-PLAN.md` at `main@6eab0440ef32280c16e41b41851deb3f11937495`. Broadcast 12 made its authority/tenant/secret/memory/provider/budget/rights/multimodal adversarial obligations mandatory inputs for future milestone acceptance.

The QA plan is an audit/planning constraint. It does not grant feature execution, provider spend, production credentials, publication or security-setting authority.

## M04 planning promotion

PR #78 `M04: harden planning against adversarial trust boundaries` passed exact-head Repository Governance, Core Domain Contracts and Durable Control Plane and merged to `main@5367ffe5401292744cbe29d8f1a16c36591fae27`.

That promotion:

- hardened the M04 planning contract with canonical tenant/project authorization, lock integrity, append/version immutability, rights/consent/provenance continuity, reference-pack trust boundaries and provider-output distrust hooks;
- created the previously missing `ai-native/parallel/checkpoints/M04-PARALLEL-LANE.md`;
- explicitly retained Issue #36 live protected-main governance and explicit M04 executable consent as mandatory entry gates;
- created no product/API/schema/provider implementation and no migration reservation;
- did not complete executable M04 and therefore did not satisfy downstream M05/M07/M08 executable dependencies.

Broadcast 13 records this planning promotion for every affected active lane.

## Dependency and consent boundary

- M04 executable work remains dependent on `M03-GOV-HOLD` and explicit M04 executable consent.
- M05 executable work remains dependent on executable M04 completion; M04 planning completion is insufficient.
- M06 executable work retains its M03 governance dependency and requires applicable executable consent.
- M07 executable work remains dependent on executable M04/M05/M06 completion.
- M08 executable work remains dependent on executable M04/M07 completion.
- Cross-cutting QA has no module dependency but remains audit/planning only unless an applicable executable scope authorizes targeted tests.
- Generic `continue`, branch synchronization, green planning CI, mocks, or a planning checkpoint cannot satisfy a privileged development/publish/security gate.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. Planning lanes may update only their claimed milestone-plan/checkpoint surfaces. QA owns its documented QA/checkpoint surfaces plus explicitly requested security documentation access. Executable product/test/schema/provider writes require fresh applicable authority and collision-free ownership.

Future migration IDs are reserved only after executable authority exists and the then-current migration head has been re-audited.

## Hold order

1. keep Issue #36 `EXTERNAL_NOT_VERIFIED` until live protected-main evidence exists;
2. preserve broadcast 12 adversarial obligations and broadcast 13 M04 planning constraints in future milestone acceptance;
3. do not start executable M04 until Issue #36 and explicit M04 executable consent both clear;
4. do not treat M04 planning completion as satisfying M05/M07/M08 executable dependencies;
5. do not promote M06 executable work while its M03 governance/consent gates remain unresolved;
6. do not create synthetic provider/admin/production success from source CI, mocks or deterministic fakes.

## Next safe planning work

While executable gates remain closed, a later planning lane may be audited and hardened only within its existing planning consent scope. Any such planning slice must identify a real documentation/checkpoint gap, preserve all dependency/consent holds, avoid implementation/schema/provider work, and pass ordinary exact-head repository/source regression CI before merge.

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications and unresolved review findings. Required exact-head CI must be green.

After a successful promotion that active agents must observe, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
