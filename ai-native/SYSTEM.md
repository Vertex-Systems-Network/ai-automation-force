# AI-Native Content OS — System Architecture

## Goal

Turn a one-word operator command (`next`) into a safe, resumable, research-aware, memory-backed content production run that produces one fully classified, original, production-ready children's content package.

## System layers

### 1. Control layer

Interprets operator commands and loads repository state.

Inputs:
- operator command
- repository policy
- memory state
- portfolio balance
- research freshness

Outputs:
- run ID
- selected workflow
- current state

### 2. Research intelligence layer

Collects current and evergreen signals that can improve content selection.

Research dimensions:
- current children's content trends without copying competitors
- educational themes and seasonal opportunities
- parent/search intent
- platform-quality requirements
- age suitability
- cultural/calendar opportunities
- portfolio gaps inside this repository

Research must generate opportunity abstractions, not derivative copies.

### 3. Portfolio planner

Scores possible age-band/content-type combinations before writing.

Suggested score components:

`opportunity_score = demand_signal + portfolio_gap + educational_value + repeatability + brand_fit + production_fit - duplication_risk - safety_risk - derivative_risk`

The exact numeric weighting can be implemented later; the planning logic is mandatory from Phase 1.

### 4. Concept generator

Generates a minimum of three candidate concepts with:
- working title
- content type
- age band
- hook
- learning/emotional goal
- creative device
- estimated duration
- why-now/research rationale

No full script is written at this stage.

### 5. Memory and duplicate intelligence

Runs each candidate against the repository memory bank and approved content.

Checks include:
- normalized title similarity
- slug collision
- topic overlap
- concept/plot similarity
- hook similarity
- learning-objective overlap
- distinctive phrase overlap
- lyric/refrain similarity
- character/situation reuse
- research-source dependence
- future: semantic vector similarity

The system can reuse broad educational domains (e.g. colors, counting) but must create a meaningfully different creative treatment.

### 6. Content author

Writes one uniqueness-cleared concept using age-specific policy.

The author produces structured content rather than a loose block of text.

### 7. QA and policy engine

Runs mandatory gates:
- child safety
- age fit
- narrative/coherence
- factual/educational correctness where applicable
- language quality
- originality
- copyright/character/voice risk
- audio readiness
- platform-quality risk
- metadata completeness

### 8. Audio handoff compiler

Transforms the approved script/lyrics into a Gemini TTS production contract.

The contract specifies:
- exact text to perform
- target age and listener context
- female voice direction
- vocal age impression without impersonation
- tone
- pace
- articulation
- energy
- pauses
- emotional arc
- pronunciation
- section-by-section performance
- do-not-do constraints
- file/version metadata

Current provider implementation should remain configurable because model names and capabilities change.

### 9. Repository writer

Saves approved artifacts under a deterministic classification path and updates machine-readable memory only after QA passes.

Recommended path:

`content/<age-band>/<content-type>/<content-id>-<slug>/`

Each package should eventually contain:
- `content.md`
- `metadata.json`
- `audio-prompt.md`
- `qa.json`
- `research.md`
- future: `video-plan.json`
- future: `publishing.json`
- future: `analytics.json`

### 10. Memory updater

Updates indexes atomically at the end of a successful run.

Memory is append-oriented. Historical approved records should not be rewritten casually.

## State machine

1. `START`
2. `LOAD_STATE`
3. `RESEARCH`
4. `PLAN_PORTFOLIO`
5. `GENERATE_CANDIDATES`
6. `DUPLICATE_CHECK`
7. `SELECT_CONCEPT`
8. `WRITE`
9. `QA`
10. `AUDIO_COMPILE`
11. `SAVE_PACKAGE`
12. `UPDATE_MEMORY`
13. `COMPLETE`

Failure branches:

- duplicate -> replace candidate -> duplicate check
- QA failure -> revise -> QA
- unrecoverable memory failure -> halt approval and repair state
- provider capability uncertainty -> preserve provider-neutral production spec and flag downstream action

## Idempotency

A repeated `next` command must not accidentally recreate the last item.

Each run should have a unique run ID and memory should track:
- last completed content ID
- last completed run ID
- in-progress run if automation is later implemented
- content fingerprints

Before saving, re-run duplicate detection because repository state may have changed since concept selection.

## Human/AI boundary

The AI may autonomously research, plan, write, QA, classify, and prepare audio prompts.

Until explicitly enabled in a later policy, the AI must not autonomously:
- publish publicly
- incur paid API usage
- weaken safety controls
- delete canonical history
- impersonate a real person's voice

## Phase roadmap

### Phase 1 — Content Intelligence OS
Current foundation.

### Phase 2 — Audio Production
Gemini API integration, render queue, audio QA, loudness/format normalization, artifact storage.

### Phase 3 — Visual/Video Production
Storyboard compiler, character/world bible, scene prompts, image/video generation, lip/beat sync where relevant, captions, render QA.

### Phase 4 — Publishing OS
YouTube metadata, Made-for-Kids classification workflow, thumbnails, playlists, scheduling, publishing gates.

### Phase 5 — Analytics Learning Loop
Performance ingestion, retention analysis, topic/type/age cohort scoring, experimentation, content recommendations.

### Phase 6 — Localization/IP Expansion
Multilingual adaptation, dubbing, canonical character system, books/printables/music catalogue licensing metadata.
