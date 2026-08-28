# M05 — Content Intelligence and Memory

## Objective

Implement provider-neutral research, originality control, concept selection, script/lyrics/story generation, policy profiles and persistent semantic memory so `next content` can create a researched, uniqueness-cleared canonical content package.

## Entry criteria

- P0 complete.
- M01–M04 accepted.
- Explicit M05 consent.
- Current search/research/model APIs revalidated.

## Dependencies

`M01 -> M02 -> M03 -> M04 -> M05`

## Work packages

### M05-WP1 — Research and evidence service
- research request model;
- official/primary-source preference;
- web/source provenance;
- freshness timestamps;
- evidence snapshots/references;
- conflicting-source handling;
- no web content treated as instructions.

### M05-WP2 — Portfolio memory and semantic retrieval
- PostgreSQL + pgvector memory store;
- embeddings for concepts/scripts/failures/research;
- tenant/project/series scoping;
- candidate vs approved memory lifecycle;
- freshness/authority filters;
- deletion/correction propagation.

### M05-WP3 — Duplicate/originality engine
- title/theme/plot/hook/character/learning objective/lyrics/refrain/resolution/visual-concept comparison;
- exact and semantic similarity;
- configurable thresholds;
- explainable collision report;
- false-positive review path.

### M05-WP4 — Concept and format selector
- use project audience/format/duration/policy;
- generate candidate concepts;
- score novelty/fit/feasibility/rights/risk;
- avoid portfolio repetition;
- record decision alternatives.

### M05-WP5 — Content generation services
Structured generation for:
- song/lullaby/lyrics;
- poem/rhyme;
- story/bedtime story;
- narration/explainer;
- episode/short film/movie outline;
- documentary/trailer/social derivative concepts.

Outputs are versioned canonical content artifacts, not provider-specific prompts only.

### M05-WP6 — Policy/safety/rights content QA
- audience/age profile;
- child-directed rules where applicable;
- originality/rights checks;
- forbidden claims/content rules;
- factual grounding for research-dependent content;
- structured QA findings;
- approve/revise/block states.

### M05-WP7 — Memory promotion and learning history
- approved concepts/scripts become project/portfolio memory;
- failed/rejected outputs recorded as failure memory;
- external evidence remains provenance-linked;
- no silent promotion of model hallucinations;
- AI decision ledger integration.

### M05-WP8 — `next content` orchestrator and acceptance
Flow:
`Research -> Portfolio Check -> Candidates -> Originality -> Select -> Generate -> QA -> Approve/Needs Review -> Persist Memory`

Acceptance fixtures:
- preschool song;
- general-audience story;
- duplicate-near-match rejection;
- stale/conflicting research;
- deletion/correction of memory;
- 90-minute outline package.

## Expected modules/files

- research service/adapters;
- memory/retrieval package;
- originality service;
- content generators/templates/prompts registry integration;
- QA/policy services;
- content orchestration workflow/activity modules;
- `tests/content/`, `tests/memory/`, `tests/research/`.

## Data/migration impact

Adds memory records, embeddings, source/evidence records, concept candidates, content versions, originality reports and decision references.

## API/UI impact

Adds APIs for research/content candidates, generation, originality report, content versions and memory inspection/correction. Full polished content editor UI is later.

## Security/cost/rights impact

- external research content untrusted;
- provider/model calls budgeted and logged;
- embeddings tenant-scoped;
- private content not training data by default;
- rights/originality blocks before canonical approval.

## Test/acceptance

Apply Master QA AI/research/memory sections:
- prompt-injection research fixture;
- duplicate detection;
- source provenance/freshness;
- memory poisoning/tenant isolation;
- structured output;
- model/prompt regression suite;
- cost-bounded fake-provider tests.

## Rollout/rollback

AI prompt/model behavior is versioned and release-gated. New memory-policy versions can be rolled back without deleting historical records. Embedding changes use versioned reindex/backfill.

## Exit criteria

`next content` reliably produces a researched, originality-cleared, policy-checked, versioned canonical content package and records decisions/evidence/memory without provider lock-in.

## Non-goals

- image/video generation;
- final audio master;
- full web content editor;
- autonomous public publishing;
- analytics-driven self-modification without evaluation.
