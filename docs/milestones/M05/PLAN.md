# M05 — Content Intelligence and Memory

## Planning authority and current state

This document is the planning contract for M05 only. It does **not** authorize executable M05 product/API/schema/provider work.

Current planning baseline: `main@a7aa25e86bd5092ab9979f26765d48a7b3f34ffc`, after cross-cutting adversarial QA and M04 planning/broadcast-13 reconciliation.

Executable M05 work remains blocked until executable M04 is accepted, explicit M05 executable consent is recorded, and all then-current governance/dependency/migration/write-ownership gates are revalidated. M04 planning completion is not executable M04 completion. Generic conversational continuation is not executable consent.

## Objective

Implement provider-neutral research, originality control, concept selection, script/lyrics/story generation, policy profiles and persistent semantic memory so `next content` can create a researched, uniqueness-cleared canonical content package without allowing low-trust research, retrieval, memory or model output to gain policy/security authority.

## Entry criteria

All are required before executable M05 work begins:

- P0 complete;
- M01–M03 accepted at required truth levels;
- executable M04 completed/accepted, not merely planning-hardened;
- explicit M05 executable consent recorded through Supervisor authority;
- current search/research/model APIs revalidated;
- current main, broadcast, dependency, write ownership and migration state revalidated immediately before implementation;
- cross-cutting adversarial QA obligations applicable to the proposed M05 executable surface mapped to targeted evidence.

Current state: planning may continue, but executable M05 entry criteria are **not satisfied** because executable M04 is not complete and explicit M05 executable consent is absent. Issue #36 also remains an upstream live-governance truth boundary and must not be fabricated as verified.

## Dependencies

`M01 -> M02 -> M03 -> M04 -> M05`

Downstream impact:

- M07 depends on executable M04/M05/M06;
- downstream synchronization or planning completion does not satisfy executable dependency gates.

## Work packages

### M05-WP1 — Research and evidence service
- research request model;
- official/primary-source preference;
- web/source provenance;
- freshness timestamps;
- evidence snapshots/references;
- conflicting-source handling;
- no web/retrieved content treated as instructions or policy authority;
- explicit source trust/provenance classification retained into downstream decisions.

### M05-WP2 — Portfolio memory and semantic retrieval
- PostgreSQL + pgvector memory store;
- embeddings for concepts/scripts/failures/research;
- tenant/project/series scoping;
- candidate vs approved memory lifecycle;
- freshness/authority filters;
- contradiction/expiry/source-class visibility;
- deletion/correction propagation;
- deterministic promotion path for stronger memory classes;
- retrieval result carries provenance/class/version instead of returning context as untyped trusted prose.

### M05-WP3 — Duplicate/originality engine
- title/theme/plot/hook/character/learning objective/lyrics/refrain/resolution/visual-concept comparison;
- exact and semantic similarity;
- configurable thresholds;
- explainable collision report;
- false-positive review path;
- similarity output is advisory evidence and cannot silently change canonical rights/policy/approval state.

### M05-WP4 — Concept and format selector
- use project audience/format/duration/policy;
- generate candidate concepts;
- score novelty/fit/feasibility/rights/risk;
- avoid portfolio repetition;
- record decision alternatives;
- retrieved memories/research remain evidence and cannot grant budget, publish, security or policy authority.

### M05-WP5 — Content generation services
Structured generation for:
- song/lullaby/lyrics;
- poem/rhyme;
- story/bedtime story;
- narration/explainer;
- episode/short film/movie outline;
- documentary/trailer/social derivative concepts.

Outputs are versioned canonical content artifacts, not provider-specific prompts only. Model/provider output remains untrusted until schema/policy/rights validation succeeds.

### M05-WP6 — Policy/safety/rights content QA
- audience/age profile;
- child-directed rules where applicable;
- originality/rights checks;
- forbidden claims/content rules;
- factual grounding for research-dependent content;
- structured QA findings;
- approve/revise/block states;
- approval state can only be produced by deterministic configured authority, never by retrieved/model-authored statements claiming approval.

### M05-WP7 — Memory promotion and learning history
- approved concepts/scripts become project/portfolio memory only through deterministic promotion authority;
- failed/rejected outputs recorded as appropriately classified failure memory;
- external evidence remains provenance-linked and low-trust unless explicitly promoted through an authorized path;
- no silent promotion of model hallucinations, retrieved instructions or malicious memory;
- AI decision ledger integration;
- correction/forget operations remove future retrieval authority while preserving required audit/history evidence;
- raw secrets, OAuth tokens and provider credentials are never ordinary memory payloads.

### M05-WP8 — `next content` orchestrator and acceptance
Flow:
`Research -> Portfolio Check -> Candidates -> Originality -> Select -> Generate -> QA -> Approve/Needs Review -> Persist Memory`

Acceptance fixtures:
- preschool song;
- general-audience story;
- duplicate-near-match rejection;
- stale/conflicting research;
- malicious retrieved-memory/prompt-injection case;
- deletion/correction/forget behavior;
- tenant-isolated retrieval;
- 90-minute outline package.

## Cross-cutting adversarial acceptance obligations

Broadcast 12 and `docs/qa/ADVERSARIAL-AUDIT-PLAN.md` are mandatory planning inputs. When M05 later requests executable promotion, QA must re-evaluate the exact proposed surface and add only targeted evidence for newly reachable authority paths.

At minimum M05 acceptance must prove:

1. **Memory cannot self-promote** — an observation, hypothesis, retrieved document, model output or malicious “admin rule” cannot become an approved/canonical rule without configured deterministic promotion authority.
2. **Policy precedence is explicit** — retrieved memory/research cannot override system/product policy, tenant permissions, approval class, budget or security controls.
3. **Provenance remains visible** — source, trust class, version, freshness, contradiction and expiry state remain attached to retrieved memory and evidence.
4. **Tenant/project/series isolation** — cross-tenant memory/embedding/result IDs are rejected through canonical authorization rather than trusted from vector/model/provider output.
5. **Correction/forget semantics are bounded** — corrected/forgotten content loses future retrieval authority without silently rewriting required audit history or corrupting unrelated memory.
6. **Secrets stay out of memory** — raw provider/OAuth/security credentials are references/secret handles outside ordinary memory, prompts, embeddings, logs and decision payloads.
7. **External research is untrusted** — web/upload/retrieved instructions remain evidence and cannot mutate tool/provider configuration or invoke privileged actions.
8. **Provider/model outputs are untrusted** — returned IDs, citations, URLs, classifications or instructions require schema validation, canonical lookup and policy checks.
9. **Retries/cost are bounded** — future research/model/embedding retries and fallbacks require attempt/time/fan-out/cost ceilings, idempotency and applicable budget authority.
10. **No synthetic production/security success** — deterministic fakes may prove source contracts; unavailable live admin/provider/publish evidence remains `NOT_VERIFIED` when a later gate requires it.

Do not add duplicate umbrella tests for already-proven lower-layer M03 properties unless M05 creates a new authority/trust path.

## Expected modules/files

Planned future executable surface only:

- research service/adapters;
- memory/retrieval package;
- originality service;
- content generators/templates/prompts registry integration;
- QA/policy services;
- content orchestration workflow/activity modules;
- `tests/content/`, `tests/memory/`, `tests/research/`.

Actual executable write ownership and migration reservations must be assigned fresh by the Supervisor after entry criteria pass.

## Data/migration impact

Expected future implementation adds memory records, embeddings, source/evidence records, concept candidates, content versions, originality reports and decision references.

This planning slice creates **no migration reservation and no schema change**. Future migration IDs must be reserved only after executable M05 authority exists and the then-current migration head is audited.

## API/UI impact

Future implementation may add APIs for research/content candidates, generation, originality reports, content versions and memory inspection/correction. Full polished content editor UI is later.

This planning slice changes no API or UI.

## Security/cost/rights impact

Future M05 must preserve:

- external research/retrieval as untrusted evidence;
- provider/model calls budgeted, bounded and logged without leaking secrets;
- embeddings and memory tenant/project/series scoped;
- private content not treated as training data by default;
- rights/originality checks before canonical approval;
- deterministic memory promotion authority;
- correction/forget semantics that remove future influence without destroying required auditability;
- explicit separation between evidence/memory and privileged policy/approval/security state.

## Test/acceptance plan

Targeted future evidence includes:

- prompt-injection research fixture cannot mutate policy/tool/provider configuration;
- malicious memory claiming administrative authority remains low-trust and cannot become approved policy;
- retrieved observation/hypothesis cannot override configured policy;
- duplicate detection and explainable collision behavior;
- source provenance/freshness/conflict visibility;
- memory poisoning and tenant-isolation rejection;
- correction/forget removes future retrieval authority while preserving audit history;
- raw secret material never enters memory/embedding/log payloads;
- structured output validation fails closed;
- model/prompt regression suite;
- cost-bounded fake-provider tests for source behavior only.

## Rollout/rollback

Future AI prompt/model/memory-policy behavior is versioned and release-gated. New memory-policy versions can be rolled back without deleting historical records. Embedding changes use versioned reindex/backfill. Correction/forget behavior must have explicit retention/audit semantics rather than ad-hoc destructive rewrites.

## Exit criteria

M05 can exit only when `next content` reliably produces a researched, originality-cleared, policy-checked, versioned canonical content package and records decisions/evidence/memory without provider lock-in, cross-tenant leakage, memory self-promotion or low-trust evidence gaining privileged authority.

Planning completion is **not** executable milestone completion.

## Non-goals

- image/video generation;
- final audio master;
- full web content editor;
- autonomous public publishing;
- analytics-driven self-modification without evaluation;
- production credentials or paid provider calls during this planning slice;
- using generic `continue`, branch synchronization, mocks or green planning CI as executable M05 consent.
