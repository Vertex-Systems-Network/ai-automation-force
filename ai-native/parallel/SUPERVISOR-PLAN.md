# AI-Native Supervisor Parallel Development Plan

## Authority

The Supervisor owns assignment, coordination-state mutation, review order, and promotion to `main`. New executable slices start from current `main`; completed or superseded branches are retired before the next bounded slice.

New agents start from `main`, read `AGENT-SLOTS.json`, and may work only after Supervisor assignment. All defined slots are occupied, so an additional arrival receives exactly **Go Home Come Back Next Time**.

Planning synchronization, a green planning PR, deterministic fakes, or conversational continuation does not grant privileged/executable development authority.

## Current branch matrix

| Lane | Agent | Branch | State |
| --- | --- | --- | --- |
| M03 Governance Hold | `supervisor-agent` | `supervisor/m03-governance-hold-current` | active governance-only hold; broadcast 17 synchronized |
| M04 Character | `character-agent` | `agent/m04-character-library-current` | broadcast 17 synchronized; planning hardened; executable hold |
| M05 Content | `content-agent` | `agent/m05-content-memory-current` | broadcast 17 synchronized; planning hardened; executable hold |
| M06 Audio | `audio-agent` | `agent/m06-audio-production-current` | broadcast 17 synchronized; planning hardened; executable hold |
| M07 Timeline | `timeline-agent` | `agent/m07-storyboard-timeline-current` | broadcast 17 synchronized; planning hardened; executable hold |
| M08 Provider | `provider-agent` | `agent/m08-video-provider-router` | broadcast 17 synchronized; planning hardened; executable hold |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security-current` | broadcast 17 synchronized; audit/planning only |

Completed `agent/m04-character-library`, `agent/m05-content-memory`, `agent/m06-audio-production`, and `agent/m07-storyboard-timeline` are retired after their planning promotions and are not force-reset or reused as promotion authority. Fresh current-main planning branches are `agent/m04-character-library-current`, `agent/m05-content-memory-current`, `agent/m06-audio-production-current`, and `agent/m07-storyboard-timeline-current`. Earlier completed QA and M03/WP8 submission/review/closeout branches remain retired.

## M03 source completion and external hold

M03 implementation, WP8 source acceptance, and source-side closeout are complete. Issue #36 remains the final M03 protected-main governance blocker because live GitHub enforcement is not verified.

Migrations `20260901_0015` and `20260901_0016` remain landed. There is no active M03, M04, M05, M06, M07 or M08 migration reservation. No additional WP7/WP8 product/API/schema/provider work is authorized by this state.

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

That promotion hardened storyboard/timeline planning against generated/imported authority escalation, created the missing M07 checkpoint, required canonical tenant/project authorization for entity/asset/audio/keyframe/reference IDs, kept provider IDs/URLs/hidden state outside canonical timeline truth, required pinned version/reference lineage and rights/provenance continuity, and preserved executable M04/M05/M06 acceptance plus explicit M07 executable consent as gates. Broadcast 16 recorded those constraints.

M07 planning completion is not executable M07 completion and does not satisfy M08 executable dependency.

## M08 planning promotion

PR #94 `M08: harden provider-router planning trust boundaries` merged to `main@9bc9e5f7e3ebda5166dca42a04be27dc9c3096bc` from exact submitted head `8d4c1770598f4a5dac8a87304076ff62d4dad47d` after Repository Governance, Durable Control Plane and Core Domain Contracts passed.

That promotion:

- hardened the M08 provider-router plan and created the previously missing `ai-native/parallel/checkpoints/M08-PARALLEL-LANE.md`;
- treats provider-returned IDs, URLs, metadata, JSON, OCR, transcripts and instructions as untrusted evidence;
- requires canonical tenant/project re-authorization for provider-returned and M07-supplied entity, asset, reference and version identifiers;
- preserves pinned reference/version lineage plus rights/provenance through routing and fallback;
- prevents provider/generated/imported content from minting tool, publish, budget, account or security authority;
- keeps raw provider/OAuth/signing secrets outside prompts, memory, generated artifacts, manifests, ledgers and logs;
- bounds retry, fallback, fan-out, time and cost with idempotency, circuit-breaking and budget reservation;
- requires ambiguous external completion to reconcile before retry or fallback;
- rejects unknown, stale or unsupported capability instead of silently substituting a privileged operation;
- keeps deterministic fake/source acceptance distinct from live provider/admin/production truth;
- creates no product/API/schema/provider adapter/test implementation, migration, credential use, paid call, media generation, publication or production-data access.

Before broadcast 17 coordination, every active Supervisor/M04/M05/M06/M07/M08/QA branch was verified at zero unique commits relative to resulting main and was non-force fast-forwarded to `9bc9e5f7e3ebda5166dca42a04be27dc9c3096bc`.

M08 planning completion is not executable M08 completion. It does not activate M09 or any provider execution authority.

## Dependency and consent boundary

- M04 executable work remains dependent on `M03-GOV-HOLD` and explicit M04 executable consent.
- M05 executable work remains dependent on executable M04 completion and explicit M05 executable consent.
- M06 executable work requires the accepted upstream executable chain, explicit M06 executable consent and then-current provider/licensing/governance revalidation.
- M07 executable work remains dependent on executable M04/M05/M06 completion plus explicit M07 executable consent and then-current governance/write/migration/reference/right/provenance revalidation.
- M08 executable work remains dependent on executable M04/M07 completion plus explicit M08 executable consent, fresh ownership/migration state, canonical reference authority and current provider API/scope/quota/rights/licensing/cost revalidation.
- Cross-cutting QA remains audit/planning only unless an applicable executable scope authorizes targeted tests.
- Generic `continue`, branch synchronization, green planning CI, mocks, deterministic fakes, or a planning checkpoint cannot satisfy a privileged development/publish/security/provider/spend gate.

## Parallel safety

`ACTIVE-WORK.yaml` is authoritative for active write claims. Planning lanes may update only their claimed milestone-plan/checkpoint surfaces. QA owns its documented QA/checkpoint surfaces plus explicitly requested security documentation access. Executable product/test/schema/provider writes require fresh applicable authority and collision-free ownership.

Future migration IDs are reserved only after executable authority exists and the then-current migration head has been re-audited.

## Hold order

1. keep Issue #36 `EXTERNAL_NOT_VERIFIED` until live protected-main evidence exists;
2. preserve broadcasts 12 through 17 adversarial/planning constraints in future milestone acceptance;
3. do not start executable M04 until Issue #36 and explicit M04 executable consent both clear;
4. do not start executable M05 until executable M04 is accepted and explicit M05 executable consent exists;
5. do not start executable M06 until its upstream executable chain is accepted and explicit M06 executable consent exists;
6. do not start executable M07 until executable M04/M05/M06 are accepted and explicit M07 executable consent exists;
7. do not start executable M08 until executable M04/M07 are accepted, explicit M08 executable consent exists, and current provider/reference/rights/cost gates pass;
8. do not treat planning completion as satisfying executable dependencies or as authorization for M09;
9. do not create synthetic provider/admin/production success from source CI, mocks or deterministic fakes.

## Next safe planning work

No new executable milestone is authorized by the M08 planning promotion. While Issue #36 and upstream executable gates remain closed, current lanes may only perform their already-claimed planning/audit work after broadcast-17 synchronization. M09 is not activated by implication. Any future planning expansion must first receive an explicit collision-free scope and must not introduce provider spend, credentials, schema/product writes or privileged execution authority.

## Completion and review

Every ready bounded submission announces exactly **Work Done and Submitted**. Before promotion, the Supervisor verifies exact head/base, current-main freshness, write ownership, migration state, consent/dependencies, tests, security/data implications and unresolved review findings. Required exact-head CI must be green.

After a successful promotion that active agents must observe, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**
