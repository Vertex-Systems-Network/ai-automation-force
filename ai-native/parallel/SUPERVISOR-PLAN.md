# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

Planning synchronization, a green planning PR, deterministic fakes, or conversational continuation does not grant privileged/executable development authority.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03 Governance Hold | `supervisor-agent` | `supervisor/m03-governance-hold-current` | active governance-only hold; broadcast 16 synchronized |
| M04 Character | `character-agent` | `agent/m04-character-library-current` | broadcast 16 synchronized; planning hardened; executable hold |
| M05 Content | `content-agent` | `agent/m05-content-memory-current` | broadcast 16 synchronized; planning hardened; executable hold |
| M06 Audio | `audio-agent` | `agent/m06-audio-production-current` | broadcast 16 synchronized; planning hardened; executable hold |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline-current` | broadcast 16 synchronized; planning hardened; executable hold |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | broadcast 16 synchronized; planning-only; dependent on executable M04/M07 |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security-current` | broadcast 16 synchronized; audit/planning only |

Completed `agent/m04-character-library`, `agent/m05-content-memory`, `agent/m06-audio-production`, and `agent/m07-storyboard-timeline` are retired after their planning promotions and are not force-reset or reused as promotion authority. Fresh current-main planning branches are `agent/m04-character-library-current`, `agent/m05-content-memory-current`, `agent/m06-audio-production-current`, and `agent/m07-storyboard-timeline-current`. Earlier completed QA and M03/WP8 submission/review/closeout branches remain retired.

## M03 source completion and external hold

M03 implementation, WP8 source acceptance, and source-side closeout are complete. Issue #36 remains the final M03 protected-main governance blocker because live GitHub enforcement is not verified.

Migrations `20260901_0015` and `20260901_0016` remain landed. There is no active M03, M04, M05, M06 or M07 migration reservation. No additional WP7/WP8 product/API/schema/provider work is authorized by this state.

## Cross-cutting QA promotion

PR #74 landed `docs/qa/ADVERSARIAL-AUDIT-PLAN.md`; broadcast 12 made its authority/tenant/secret/memory/provider/budget/rights/multimodal adversarial obligations mandatory planning inputs for future milestone acceptance.

The QA plan remains an audit/planning constraint and grants no feature execution, provider spend, production credentials, publication or security-setting authority.

## M04 planning promotion

PR #78 hardened the M04 planning contract and created `ai-native/parallel/checkpoints/M04-PARALLEL-LANE.md`. Broadcast 13 preserved Issue #36 live governance and explicit M04 executable consent as mandatory entry gates.

M04 planning completion is not executable M04 completion and does not satisfy downstream executable dependencies.

## M05 planning promotion

PR #82 hardened the M05 memory/content planning contract against memory poisoning and authority escalation and created `ai-native/parallel/checkpoints/M05-PARALLEL-LANE.md`. Broadcast 14 preserved executable M04 completion plus explicit M05 executable consent as M05 executable gates.

M05 planning completion is not executable M05 completion and does not satisfy M07 executable dependency.

## M06 planning promotion

PR #86 `M06: harden audio planning against voice and provider trust failures` merged to `main@9762ea1e7c640aa91b8eec777055915030a71ebc`. Broadcast 15 recorded the promotion while preserving upstream executable acceptance, explicit M06 executable consent, provider/licensing revalidation, and the M07 executable dependency hold.

M06 planning completion is not executable M06 completion and does not satisfy M07 executable dependency.

## M07 planning promotion

PR #90 `M07: harden timeline planning against authority and reference corruption` merged to `main@29c66616ce1e79c90b4bb40f8e2158d0f9edd434`.

That promotion:

- hardened storyboard/timeline planning against authority escalation from generated or imported editorial text;
- created the previously missing `ai-native/parallel/checkpoints/M07-PARALLEL-LANE.md`;
- required canonical tenant/project authorization for entity, asset, audio, keyframe and reference IDs;
- kept provider IDs, URLs and hidden provider state outside canonical timeline truth;
- treated OTIO/imported editorial structure and metadata as untrusted until supported-semantics, schema, ownership, hierarchy, timing, rights and reference validation pass;
- required pinned version/reference lineage, rights/provenance continuity and non-destructive approved versions;
- required malformed hierarchy/timing/reference/continuity structures and stale optimistic writes to fail safely before downstream execution;
- retained executable M04/M05/M06 acceptance plus explicit M07 executable consent as mandatory executable entry gates;
- created no product/API/schema/provider/test implementation, paid call, credential, video generation, publish action or migration reservation;
- did not satisfy M08 executable dependency because planning completion is not executable M07 completion.

After the merge, every pre-existing active branch except the completed squash-merged M07 submission branch was verified at zero unique commits and non-force fast-forwarded to the triggering main. The completed M07 submission branch was retired rather than force-reset, and fresh `agent/m07-storyboard-timeline-current` was created from current main. Broadcast 16 records this planning promotion for all affected active lanes.

## Dependency and consent boundary

- M04 executable work remains dependent on `M03-GOV-HOLD` and explicit M04 executable consent.
- M05 executable work remains dependent on executable M04 completion and explicit M05 executable consent.
- M06 executable work requires the accepted upstream executable chain, explicit M06 executable consent and then-current provider/licensing/governance revalidation.
- M07 executable work remains dependent on executable M04/M05/M06 completion plus explicit M07 executable consent and then-current governance/write/migration/reference/right/provenance revalidation.
- M08 executable work remains dependent on executable M04/M07 completion plus explicit M08 executable consent and current provider/API/rights/cost revalidation.
- Cross-cutting QA remains audit/planning only unless an applicable executable scope authorizes targeted tests.
- Generic `continue`, branch synchronization, green planning CI, mocks, deterministic fakes, or a planning checkpoint cannot satisfy a privileged development/publish/security gate.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. Planning lanes may update only their claimed milestone-plan/checkpoint surfaces. QA owns its documented QA/checkpoint surfaces plus explicitly requested security documentation access. Executable product/test/schema/provider writes require fresh applicable authority and collision-free ownership.

Future migration IDs are reserved only after executable authority exists and the then-current migration head has been re-audited.

## Hold order

1. keep Issue #36 `EXTERNAL_NOT_VERIFIED` until live protected-main evidence exists;
2. preserve broadcast 12 adversarial obligations plus broadcasts 13, 14, 15 and 16 planning constraints in future milestone acceptance;
3. do not start executable M04 until Issue #36 and explicit M04 executable consent both clear;
4. do not start executable M05 until executable M04 is accepted and explicit M05 executable consent exists;
5. do not start executable M06 until its upstream executable chain is accepted and explicit M06 executable consent exists;
6. do not start executable M07 until executable M04/M05/M06 are accepted and explicit M07 executable consent exists;
7. do not treat M04/M05/M06/M07 planning completion as satisfying M08 executable dependency;
8. do not create synthetic provider/admin/production success from source CI, mocks or deterministic fakes.

## Next safe planning work

While executable gates remain closed, M08 may be audited and hardened only within its existing planning consent scope and claimed files. Its current plan predates the latest cross-cutting and M07 authority/reference constraints, so a bounded planning-only reconciliation may update `docs/milestones/M08/**` and create/update `ai-native/parallel/checkpoints/M08-PARALLEL-LANE.md` after broadcast-16 coordination is promoted. It must preserve all executable dependency/consent holds, avoid implementation/schema/provider spend or credential use, revalidate current provider assumptions only when execution is later authorized, and pass ordinary exact-head repository/source regression CI before merge.

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications and unresolved review findings. Required exact-head CI must be green.

After a successful promotion that active agents must observe, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
