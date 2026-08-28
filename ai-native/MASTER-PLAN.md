# Lullabies AI-Native Kids Media Studio — Master Plan

## 1. Product vision

Build a persistent, repository-backed AI-native children's media studio that can take a minimal operator command such as `next` and autonomously move the project forward from research to published media while preserving safety, originality, continuity, cost control, provenance, and learning history.

The system is not a single AI model and not a single content generator. It is a provider-agnostic production operating system.

Primary production domains:
- songs
- sung lullabies
- spoken lullabies
- poems
- rhymes
- bedtime stories
- stories
- educational narration
- guided imagination
- future registered content types

Target age architecture remains segmented. 0–12 years is never treated as one audience.

## 2. Core operating principle

The repository is the canonical brain.

Chat history is not the source of truth. Provider history is not the source of truth. Every AI/provider is replaceable.

Canonical project state includes:
- approved content
- rejected ideas
- research
- duplicate fingerprints
- characters
- worlds
- visual references
- audio direction
- prompts and prompt versions
- provider attempts
- generated asset hashes
- QA results
- license/provenance records
- costs/credits
- publishing records
- analytics
- learned hypotheses

A new capable agent should be able to enter the repository, read the operating contract and memory, and continue without asking what happened in previous chats.

## 3. Operator experience

### Main command

`next`

`next` means: inspect the current state and perform the highest-value safe next unit of work.

It must not blindly mean "generate another script".

Examples:
- if no content exists, research and create content;
- if approved content lacks audio, render/prepare audio;
- if audio is approved but video is missing, build storyboard/keyframes/video;
- if a scene failed QA, repair only that scene;
- if video is ready but upload approval is missing, prepare publish package;
- if published items need analytics review, ingest/analyze them;
- if current provider quota is exhausted, preserve checkpoint and route elsewhere;
- if all automated routes are blocked, create a precise manual handoff instead of losing state.

### Additional commands

- `status` — show current pipeline state, blocked jobs, quota/budget state and next recommendation.
- `next content` — force next content-intelligence job.
- `next audio` — process next eligible audio job.
- `next video` — process next eligible visual/video job.
- `next publish` — process next publish-ready item within policy.
- `retry <job>` — retry a failed job using routing policy.
- `audit` — reconcile repository state, manifests, hashes, schemas and memory.
- `providers` — refresh provider capability/quota registry.
- `costs` — show free credits, paid spend, projected spend and caps.

## 4. State architecture

Use two related state machines.

### Content lifecycle

`idea -> researched -> uniqueness-cleared -> drafted -> content-qa-passed -> audio-ready -> audio-generated -> audio-qa-passed -> video-planned -> keyframes-approved -> scenes-generated -> video-assembled -> video-qa-passed -> publish-ready -> uploaded-private -> approved-publication -> published -> analyzed`

### Job lifecycle

`queued -> eligible -> claimed -> running -> waiting-external -> qa -> completed`

Failure states:
- `retryable-failed`
- `blocked-quota`
- `blocked-license`
- `blocked-budget`
- `blocked-capability`
- `manual-handoff`
- `permanent-failed`

Jobs must be idempotent. Re-running a completed job must not create duplicate canonical output unless explicitly creating a new version.

## 5. Major system modules

### A. Control Plane / Orchestrator

Responsibilities:
- parse commands;
- load state;
- choose the next eligible job;
- acquire a job lock;
- choose provider route;
- execute/retry;
- trigger QA;
- save result atomically;
- update memory and ledgers;
- report next state.

The orchestrator never embeds provider-specific assumptions in core business logic.

### B. Research Intelligence

Research current and evergreen opportunities:
- parent/search intent;
- age-specific learning opportunities;
- seasonal/calendar relevance;
- platform policy changes;
- competitor/topic saturation without copying;
- portfolio gaps;
- language/localization opportunities;
- provider capability/price changes.

Research records have source URLs, dates, claims and freshness.

### C. Portfolio Brain

Chooses what to create next based on a weighted opportunity model.

Candidate score can include:
- audience opportunity;
- portfolio gap;
- educational/emotional value;
- entertainment value;
- originality space;
- series/IP potential;
- localization potential;
- production feasibility;
- cost feasibility;
- seasonal relevance;
- historical performance;
- fatigue/saturation penalty;
- duplicate/derivative risk;
- safety risk.

The portfolio brain should prevent overproduction of the same topic/type even when it performed well.

### D. Memory & Originality Engine

Use multiple layers:
1. exact IDs/titles/slugs;
2. normalized lexical similarity;
3. keyphrase/refrain overlap;
4. structured concept fingerprint;
5. semantic/vector similarity;
6. plot/learning-goal/creative-device comparison;
7. character/situation saturation;
8. final full-text recheck before approval.

Keep rejected concepts/failures so the system does not repeatedly rediscover and reject the same idea.

### E. Content Authoring Engine

Produces age-specific structured content with frozen canonical text/lyrics once approved.

Every item includes:
- target age;
- type;
- duration target;
- objective;
- entertainment goal;
- learning/emotional goal;
- structure;
- script/lyrics;
- pronunciation;
- safety notes;
- originality rationale;
- downstream production intent.

### F. Safety / Quality Policy Engine

Mandatory gates:
- age fit;
- child safety;
- narrative coherence;
- factual accuracy where relevant;
- language quality;
- originality;
- copyright/IP risk;
- real-person/voice risk;
- audio readiness;
- visual readiness;
- platform-quality risk;
- metadata/provenance completeness.

Critical safety failures cannot be averaged away by a high overall score.

### G. Audio Director & Router

The human should not need to specify music details for each item.

The AI autonomously decides:
- speech vs chant vs full music vs speech-with-bed;
- female narrator/singer profile;
- genre;
- BPM/tempo;
- key/scale when useful;
- instrumentation;
- structure;
- energy map;
- background music behavior;
- pronunciation;
- mixing intent.

Routes:
- speech -> Gemini TTS or best eligible speech provider;
- full song/sung lullaby -> Lyria or best eligible music provider;
- narration + music -> separate voice and instrumental stems, then deterministic mix.

Generated audio is never approved merely because an API returned a file. Run transcript/lyric fidelity, pronunciation, clipping, loudness and age-fit QA.

### H. Visual IP / Character Memory

This is mandatory before serious video scaling.

Canonical entities:
- character ID;
- character sheet;
- face/body proportions;
- color palette;
- wardrobe variants;
- expressions;
- pose references;
- voice association;
- personality;
- forbidden mutations;
- world/environment IDs;
- props;
- art-style rules;
- lighting/camera style.

Visual memory must be provider-independent.

### I. Storyboard / Timing Compiler

Master audio is the timeline source.

Compile:
- shot IDs;
- timestamps;
- story beat/lyric segment;
- characters;
- action;
- environment;
- camera;
- motion;
- first frame;
- target/end frame;
- continuity state;
- provider prompt;
- negative constraints;
- transition intent.

Do not ask a video model to invent a complete 1–2 minute production in one generation.

### J. Keyframe & Continuity Engine

Long-form continuity is maintained externally, not inside a provider's hidden state.

For every approved shot:
- first-frame anchor;
- last/end-frame anchor when useful;
- character references;
- scene-state JSON;
- camera-state JSON;
- style ID;
- adjacent-shot relationship.

Provider switching uses these canonical anchors.

Preferred video route order:
1. native provider extension when it is a genuine same-shot continuation;
2. first+last frame/keyframe generation;
3. image-to-video with canonical reference;
4. reference video/video-to-video;
5. text-only video only for continuity-insensitive shots.

### K. Video Provider Router

The video router chooses per-shot, not necessarily per-video.

Inputs:
- capability requirement;
- continuity requirement;
- target quality;
- free quota;
- paid price;
- budget remaining;
- expected success rate from history;
- licensing;
- watermark;
- latency;
- provider health;
- retry history.

Outputs:
- selected provider/model;
- route reason;
- predicted cost/credit use;
- fallback chain.

### L. Continuity QA

Compare every generated shot with canonical references and adjacent shots.

Score:
- identity;
- proportions;
- wardrobe;
- environment;
- props;
- palette/style;
- lighting;
- camera;
- motion direction;
- temporal transition;
- unwanted text/logo;
- malformed anatomy/objects;
- end-frame suitability;
- safety.

Failed scenes are regenerated independently.

### M. Deterministic Post-Production

Use code/FFmpeg for deterministic tasks where generative AI adds no value:
- exact timeline assembly;
- audio sync;
- trim;
- transitions;
- music ducking;
- captions;
- loudness normalization;
- aspect-ratio variants;
- final checksum;
- render manifest.

### N. Free + Paid Hybrid Cost Engine

The system supports both free and paid resources.

Execution policies:
- `FREE_ONLY`
- `FREE_FIRST`
- `HYBRID_SMART` (recommended default)
- `BUDGET_CAPPED`
- `QUALITY_FIRST`

`HYBRID_SMART` behavior:
- use legitimate free API capacity when quality/capability is sufficient;
- use approved manual-free web capacity where appropriate;
- prefer paid APIs when free routes materially increase continuity failure, retries or labor;
- never silently exceed per-run/daily/monthly budget caps;
- estimate expected total cost including retry probability, not just nominal call price;
- record actual cost/credits after every attempt.

Cheap generation that fails three times can be more expensive than a single higher-quality paid generation. Routing should optimize expected accepted-output cost, not lowest sticker price.

### O. Provider Capability Registry

Provider facts are dynamic and versioned.

Store per model:
- capability;
- API/web mode;
- free quota;
- paid pricing;
- clip duration;
- resolution;
- native audio;
- first/end-frame support;
- reference support;
- video extension;
- watermark;
- commercial rights status;
- automation status;
- rate limits;
- source URL;
- verified date;
- health/failure statistics.

Stale facts are refreshed from official sources before costly production.

### P. Manual Free Handoff Queue

Some providers offer free consumer credits but no usable free API.

The system must prepare a precise handoff package:
- provider;
- model/mode;
- required source images/video;
- prompt;
- duration/settings;
- target end frame;
- expected output filename;
- return/import instructions.

Once the operator imports the result, the same automated QA/history pipeline resumes.

Manual handoff is a first-class state, not an ad-hoc interruption.

### Q. Asset Graph & Provenance

Every artifact is a node linked to its parents.

Example:
`content -> voice prompt -> voice render -> storyboard -> keyframe -> video attempt -> approved shot -> final render -> YouTube upload`

For every artifact store:
- stable ID;
- parent IDs;
- content hash;
- prompt version/hash;
- provider/model;
- generation ID;
- source asset hashes;
- timestamp;
- license/provenance;
- QA result;
- storage URI;
- canonical/non-canonical status.

Never lose lineage when regenerating or switching providers.

### R. Prompt Registry

Prompts are code.

Store:
- prompt ID;
- semantic version;
- task type;
- compatible providers/models;
- variables/schema;
- changelog;
- performance history;
- test fixtures.

Never silently overwrite production prompts without versioning.

### S. Rights / License Registry

For every generated or imported asset record:
- provider;
- plan/tier;
- commercial-use status;
- watermark requirement;
- source/copyright basis;
- public-domain basis where applicable;
- voice/character ownership status;
- publication restrictions;
- evidence/source URL and verification date.

A technically good asset with unclear publication rights is `blocked-license`, not publish-ready.

### T. Publishing OS

Prepare:
- title;
- description;
- tags where useful;
- language;
- playlist;
- thumbnail brief/render;
- captions;
- Made-for-Kids review;
- synthetic-media disclosure review where applicable;
- upload manifest.

Use resumable upload for YouTube.

Default publish workflow:
`upload private -> verify -> approval gate -> schedule/public`

Public autonomous publishing remains configurable and disabled until explicitly enabled.

### U. Analytics Learning Engine

After publication ingest available metrics and connect them back to content attributes.

Track cohorts by:
- age band;
- type;
- topic;
- character;
- duration;
- music style;
- opening hook;
- visual style;
- pacing;
- language;
- series.

Learn hypotheses, not clones.

Example:
"Preschool call-and-response animal songs show stronger first-30-second retention" may influence future planning, but the system must still pass originality and fatigue checks.

### V. Localization Engine

Canonical content has lineage-preserving language variants.

Lyrics must be adapted for rhyme/meter/naturalness, not literal-translated.

Each localized version reruns:
- safety;
- factual checks;
- originality;
- audio direction;
- metadata;
- cultural fit.

## 6. Free and paid routing model

Do not split the product into a separate "free system" and "paid system" with duplicated workflows.

Use one workflow with interchangeable provider adapters.

Each generation request describes WHAT is needed; the router decides HOW to obtain it.

Example video request:

`need: 6-second image-to-video shot, strict face consistency, end-frame target, commercial-use output`

Possible routes:
- free API provider if eligible;
- manual free provider if accepted;
- paid Veo/Kling/Runway/etc. adapter if budget allows;
- wait/block if no route meets policy.

The canonical job and continuity state remain unchanged across provider switches.

## 7. Provider scoring

Suggested provider utility model:

`utility = quality_fit + capability_fit + continuity_fit + historical_success + license_confidence + speed_value + free_credit_value - expected_cost - expected_retry_cost - watermark_penalty - manual_labor_penalty - failure_risk`

Routing should use historical accepted-output rate from this project's ledger as it accumulates.

## 8. Budget hierarchy

Support caps at:
- per attempt;
- per shot;
- per content item;
- per run;
- daily;
- monthly;
- provider-specific.

Before a paid call:
1. estimate cost;
2. estimate retry-adjusted expected cost;
3. verify remaining cap;
4. choose route;
5. reserve expected spend;
6. reconcile actual spend after completion.

Never store payment secrets in Git.

## 9. Resilience and malfunction prevention

Implement:
- job locks;
- idempotency keys;
- atomic state writes;
- exponential backoff;
- provider circuit breakers;
- retry budgets;
- provider fallback chains;
- artifact checksum validation;
- schema validation;
- interrupted-job recovery;
- generation ledger;
- deterministic IDs;
- partial pipeline resume.

A provider outage or free-quota exhaustion must not restart completed production.

## 10. Storage strategy

Git stores canonical text/state/provenance, not unlimited raw media.

Recommended:
- Git: policies, code, schemas, prompts, manifests, metadata, hashes, research, QA, state;
- local/object storage: WAV/MP3/images/videos;
- optional Git LFS only for intentionally versioned media masters;
- every external media asset has a manifest and hash in Git.

## 11. Repository target architecture

```text
/
  AGENTS.md
  README.md
  ROADMAP.md
  ai-native/
    MASTER-PLAN.md
    SYSTEM.md
    WORKFLOW.md
    QUALITY-GATES.md
    MEMORY-BANK.md
    AUDIO-ROUTER.md
    VIDEO-CONTINUITY.md
    FREE-TIER-ROUTER.md
    prompts/
  config/
    content-policy.yaml
    execution-policy.yaml
    provider-registry.yaml
  schemas/
  memory/
    state.json
    content-index.json
    fingerprint-index.json
    generation-ledger.json
    quota-ledger.json
    cost-ledger.json
    experiment-index.json
  studio/
    cli/
    orchestrator/
    jobs/
    research/
    planning/
    memory/
    authors/
    qa/
    audio/
    visual/
    video/
    providers/
    routing/
    postproduction/
    publishing/
    analytics/
    storage/
  content/
  visual-bible/
  assets-manifests/
  tests/
```

## 12. Development milestones

### Milestone 0 — Architecture lock
- master plan;
- policies;
- schemas;
- provider registry;
- budget model;
- state model.

### Milestone 1 — Core executable OS
- Python package;
- CLI;
- job state machine;
- locks/idempotency;
- repository persistence;
- schema validation;
- audit/status;
- provider adapter interface.

### Milestone 2 — Content Intelligence
- research adapter;
- planner;
- duplicate engine;
- writer;
- quality gates;
- first real `next content` run.

### Milestone 3 — Audio OS
- Gemini TTS free/paid-capable adapter;
- music-provider adapter interface;
- Lyria paid adapter;
- autonomous audio director;
- voice/music QA;
- deterministic mix;
- cost/quota ledger.

### Milestone 4 — Visual Memory
- character/world schemas;
- visual bible;
- canonical reference generation/import;
- visual QA.

### Milestone 5 — Video Planning
- audio timing/transcription;
- storyboard compiler;
- shot packages;
- keyframe planning;
- continuity state.

### Milestone 6 — Hybrid Video Router
- provider capability registry refresh;
- free API adapters where legitimate;
- manual-free handoff queue;
- paid video adapters;
- budget-aware routing;
- fallback/circuit-breaker logic;
- generation history.

### Milestone 7 — Video QA & Assembly
- continuity judge;
- retry strategy;
- FFmpeg assembly;
- captions;
- render manifests;
- final QA.

### Milestone 8 — Publishing OS
- YouTube OAuth;
- resumable uploads;
- metadata;
- audience/disclosure fields;
- private-first workflow;
- publish approvals.

### Milestone 9 — Analytics Learning
- analytics ingestion;
- cohort analysis;
- hypothesis memory;
- portfolio feedback.

### Milestone 10 — Localization & Scale
- language variants;
- localized audio/video;
- multi-channel/platform expansion;
- books/streaming/apps as separate downstream adapters.

## 13. Definition of AI-native

The system qualifies as AI-native only when:
- repository memory survives model/provider changes;
- `next` resumes from actual state;
- selection is research/memory-driven;
- duplicates are prevented;
- prompts are versioned;
- provider switching is normal, not exceptional;
- free and paid capacity are routed by policy;
- costs/credits are recorded;
- failed attempts become memory;
- partial work is resumable;
- quality gates are automated;
- characters/worlds remain canonical;
- audio/video lineage is traceable;
- publishing state is traceable;
- analytics influence future planning;
- no provider is the system's single point of truth.

## 14. Recommended default operating policy

For this project use:

`execution_mode: HYBRID_SMART`

Principles:
- free capacity is valuable and should be used;
- paid capacity is allowed under explicit budget caps;
- quality and continuity cannot be silently sacrificed to stay free;
- manual free web credits are supported as handoffs;
- paid calls are automated only within configured authorization/caps;
- every attempt is recorded;
- every accepted asset passes the same QA regardless of price/provider.

## 15. Immediate implementation order

Do not start with many provider integrations.

Build the stable core first:
1. executable orchestrator;
2. job/state/ledger layer;
3. content intelligence;
4. one free speech adapter + one paid music adapter;
5. visual memory;
6. storyboard/continuity engine;
7. provider interface + one video adapter;
8. then add free/paid provider adapters incrementally.

This prevents the architecture from becoming a collection of brittle API scripts.
