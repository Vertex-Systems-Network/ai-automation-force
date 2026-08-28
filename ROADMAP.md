# Lullabies AI-Native Studio Roadmap

Canonical architecture: `ai-native/MASTER-PLAN.md`

Default execution policy: `HYBRID_SMART` from `config/execution-policy.yaml`.

The project uses one provider-agnostic production workflow with interchangeable free/manual-free/paid provider adapters. Do not build separate duplicated free and paid pipelines.

## Milestone 0 — Architecture Lock

Status: substantially implemented.

Includes:
- repository-as-memory principle;
- mandatory AI operating contract;
- master architecture;
- one-command `next` concept;
- age segmentation;
- content policy;
- persistent content/duplicate memory;
- generation history;
- audio router;
- free-tier/provider router;
- video continuity design;
- hybrid free/paid execution policy;
- provider capability registry;
- canonical content schema.

Remaining architecture-lock items to add during implementation:
- job schema;
- asset/provenance schema;
- character/world schemas;
- cost/quota ledger schemas;
- prompt registry schema;
- publication/analytics schemas.

## Milestone 1 — Executable Core OS

Goal: make repository state executable rather than relying only on agent interpretation.

Build Python 3.12+ package under `studio/` with:
- CLI entry point;
- `lullabies next`;
- `status`;
- `audit`;
- job queue/state machine;
- deterministic IDs;
- job locks;
- idempotency keys;
- atomic repository state writes;
- interrupted-run recovery;
- schema validation;
- retry budgets;
- circuit-breaker framework;
- provider adapter interface;
- provider router interface;
- cost/quota reservation interface;
- tests/fixtures.

Exit criterion:
`next` can safely inspect state, choose one eligible job, execute a dry-run, record the job and resume without duplication.

## Milestone 2 — Content Intelligence OS

Implement:
- current/evergreen research adapters;
- portfolio planner;
- candidate generator;
- lexical duplicate checks;
- semantic duplicate checks;
- rejected-concept memory;
- structured content writer;
- safety/factual/originality QA;
- canonical package persistence;
- first real `next content` run.

Exit criterion:
one content package is autonomously researched, selected, uniqueness-cleared, written, QA-passed and saved with complete provenance.

## Milestone 3 — Hybrid Audio OS

Implement:
- autonomous audio director;
- Gemini TTS adapter for speech;
- music-provider adapter interface;
- Lyria paid adapter;
- future free/manual-free music adapters through same interface;
- speech-with-background two-stem workflow;
- prompt versioning;
- transcript/lyric fidelity QA;
- pronunciation QA;
- loudness/clipping QA;
- deterministic stem mixing;
- cost/quota ledger;
- generation history.

Exit criterion:
one approved content item reaches `audio-qa-passed` with traceable provider, prompt, cost/quota and output hashes.

## Milestone 4 — Visual IP Memory

Before scaling video generation, create provider-independent visual memory:
- brand art direction;
- character IDs;
- character sheets;
- front/side/back references;
- expressions/poses;
- body/face proportions;
- wardrobe variants;
- props;
- world/environment IDs;
- palette/style rules;
- camera/lighting rules;
- forbidden mutations;
- visual asset hashes/provenance.

Exit criterion:
a new provider can receive canonical references without relying on prior-provider hidden state.

## Milestone 5 — Storyboard & Keyframe Compiler

Master audio becomes timeline source.

Implement:
- audio timing/transcription;
- story/lyric beat segmentation;
- shot IDs/timecodes;
- shot action/camera/motion;
- character/environment state;
- canonical first frames;
- planned end frames where useful;
- transition state;
- negative constraints;
- provider-neutral shot package;
- video-plan schema.

Exit criterion:
one 1–2 minute audio master can be converted into a fully deterministic shot plan before video spending begins.

## Milestone 6 — Hybrid Video Provider Router

Implement one workflow for both free and paid capacity.

Capabilities:
- refresh official provider facts when stale;
- classify `api_free`, `api_paid`, `web_free_manual`, etc.;
- per-shot provider selection;
- budget/credit awareness;
- expected retry-adjusted accepted-output cost;
- manual-free handoff queue;
- paid API adapter support;
- provider fallback chain;
- quota exhaustion checkpointing;
- no restart of already-approved shots;
- provider health/failure tracking.

Initial adapters should be intentionally limited. Build the router first, then add providers incrementally.

Exit criterion:
a multi-shot sequence can switch providers without losing canonical continuity/history.

## Milestone 7 — Continuity QA & Video Assembly

Implement:
- multimodal continuity judge;
- deterministic visual checks where practical;
- identity/wardrobe/environment/style/camera/action scoring;
- critical-failure rejection;
- failed-shot-only regeneration;
- overlap/cut strategy;
- FFmpeg assembly;
- exact master-audio sync;
- captions;
- aspect-ratio derivatives;
- final audio/video normalization;
- render manifest and checksum.

Exit criterion:
one long-form video reaches `video-qa-passed` from multiple short generated shots without manual timeline reconstruction.

## Milestone 8 — Rights, Provenance & Publishing OS

Implement:
- asset graph;
- commercial-use/license registry;
- watermark status;
- prompt/provider/output provenance;
- YouTube OAuth;
- resumable upload;
- title/description/tags/language/playlist;
- thumbnail workflow;
- captions;
- Made-for-Kids review;
- synthetic-media disclosure review;
- default private upload;
- post-upload verification;
- human gate before public publication.

Current YouTube API supports resumable uploads and child-directed/synthetic-media status fields; verify current official docs during implementation.

Exit criterion:
final master can be uploaded privately, verified, and scheduled/public only after policy gates.

## Milestone 9 — Analytics Learning Loop

Ingest available performance signals and connect them back to canonical attributes:
- impressions/CTR;
- retention/average view duration;
- traffic sources;
- content type;
- age band;
- topic;
- character;
- duration;
- audio style;
- opening hook;
- visual style;
- series/language.

Store hypotheses and experiments, not just raw metrics.

Do not blindly clone successful content; feed learning back through originality and fatigue controls.

## Milestone 10 — Localization & Multi-Platform Expansion

Implement lineage-preserving variants for:
- additional languages;
- dubbed/localized video;
- music streaming;
- YouTube Shorts;
- podcast/audio feeds;
- storybooks/ebooks;
- printables;
- future app/game/licensing adapters.

## Immediate next milestone

Proceed with Milestone 1: Executable Core OS.

Do not begin by integrating every AI provider. First implement the stable job/state/ledger/provider-interface foundation. Then build Content Intelligence and Audio. Visual memory must be locked before serious long-form video generation.
