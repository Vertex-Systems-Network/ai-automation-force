# AGENTS.md — Mandatory AI Operating Contract

This file is the first instruction source for any AI agent working in this repository.

## Mission

Operate this repository as a persistent, provider-agnostic AI-native children's media studio with research intelligence, memory, originality control, age-aware content, child-safety QA, autonomous audio direction, visual continuity, hybrid free/paid provider routing, cost control, production history, publishing, and analytics learning.

The repository is the canonical source of truth. Chat history and any individual provider history are secondary.

The normal operator command is `next`.

`next` does not always mean "write new content". It means inspect canonical project state and autonomously execute the highest-value safe next unit of work in the lifecycle.

## Mandatory startup sequence

Before doing project work:

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read `ai-native/MASTER-PLAN.md`.
4. Read `config/execution-policy.yaml`.
5. Read `config/content-policy.yaml`.
6. Read `config/provider-registry.yaml`.
7. Read `ai-native/SYSTEM.md`.
8. Read `ai-native/WORKFLOW.md`.
9. Read `ai-native/QUALITY-GATES.md`.
10. Read `ai-native/MEMORY-BANK.md`.
11. Read `ai-native/AUDIO-ROUTER.md` when audio is relevant.
12. Read `ai-native/VIDEO-CONTINUITY.md` when visual/video work is relevant.
13. Read `ai-native/FREE-TIER-ROUTER.md` when provider routing/cost is relevant.
14. Read all machine-readable state/ledger files required for the current job.
15. Inspect current canonical content/assets and determine the first incomplete or highest-value eligible job.

Never rely only on chat memory when repository state exists.

## `next` contract

A normal `next` run must:

- load canonical repository state;
- detect incomplete, blocked, failed and ready jobs;
- choose the highest-value eligible next job;
- refresh research/provider facts if stale and material;
- preserve idempotency and job history;
- execute only within current safety, licensing and cost policy;
- route across free or paid providers using `config/execution-policy.yaml`;
- run mandatory QA;
- save canonical artifacts/manifests only after QA passes;
- record rejected attempts as history;
- update memory/state atomically;
- summarize what completed, what remains and any genuine block.

If no production item is in progress, `next` may begin a new content-intelligence cycle:
- research current and evergreen opportunities;
- select an age band and content type using portfolio balance;
- generate multiple candidate concepts;
- run duplicate detection before full writing;
- select one original candidate;
- write and QA it;
- create downstream audio/visual specifications;
- classify and save it.

## Non-negotiable rules

### Age appropriateness

Do not treat 0–12 years as one audience. Use the configured age band and its language, duration, pacing, emotional complexity, educational scope and safety constraints.

For baby audio, design for parent-controlled listening rather than encouraging infant screen engagement.

### Originality

Do not copy, closely imitate or intentionally evoke protected children's songs, modern nursery arrangements, branded characters, celebrity voices, distinctive fictional universes, lyrics, melodies, plots or catchphrases.

A public-domain concept is not permission to copy a modern recording or arrangement.

### Memory before creation

Never create final canonical content before checking memory. If memory is corrupt or unavailable, repair/reconcile it before approval.

### Provider independence

No provider is the system of record. Switching provider must not reset content, audio, shot, continuity, cost or QA history.

### Free + paid hybrid policy

Both free and paid providers may be used.

Default mode is `HYBRID_SMART` unless configuration changes it.

- legitimate free capacity should be used when capability, quality, continuity and license are sufficient;
- free consumer web credits are not automatically free API capacity;
- manual-free provider handoffs are supported as explicit jobs;
- paid API calls may occur only inside configured authorization/budget policy;
- never create/rotate accounts to evade quotas;
- never automate a provider in a way that violates its terms;
- do not accept lower-quality output merely because it was free;
- routing should minimize expected cost of an accepted asset, including retry/manual-labor risk, not just nominal per-call price.

### Female voice default

Default narration/singing direction is an appropriate adult female-presenting voice unless a content package explicitly defines otherwise. Never imitate a known real person.

### Audio architecture

Speech, music and narration-with-background are distinct production routes.

- speech -> TTS/speech provider;
- full song/sung lullaby -> capable music model;
- narration + background -> voice stem + instrumental music stem + deterministic mix.

The AI should autonomously infer music direction from content; the operator should not need to choose BPM/instruments/genre per item unless desired.

### Visual continuity

Never assume different video providers share hidden generation state.

Long-form video is built from master audio -> storyboard -> canonical keyframes/references -> short shots -> continuity QA -> deterministic assembly.

When switching providers, preserve canonical character references, scene state, first/end frames, prompt/version and generation history.

### No mass-generation behavior

Do not optimize for output count at the expense of originality, coherence, child suitability, continuity or platform-quality risk.

## Canonical lifecycle

Content lifecycle may progress through:

`idea -> researched -> uniqueness-cleared -> drafted -> content-qa-passed -> audio-ready -> audio-generated -> audio-qa-passed -> video-planned -> keyframes-approved -> scenes-generated -> video-assembled -> video-qa-passed -> publish-ready -> uploaded-private -> approved-publication -> published -> analyzed`

Do not mark a state complete unless its gate has actually passed.

## Canonical history

Record successful and rejected attempts.

History should include where relevant:
- run/job/content/asset/shot IDs;
- provider/model;
- access tier;
- prompt version/hash;
- input hashes;
- generation ID;
- output hash/location;
- QA scores;
- rejection reason;
- free credits/quota;
- paid cost;
- license/provenance;
- timestamp.

Failed history must not be deleted just because output was rejected.

## Change discipline

- Prefer additive, backwards-compatible changes.
- Version schemas and production prompts.
- Keep prompts, policies, memory, generated content and automation code separated.
- Never commit API keys/payment secrets.
- Use deterministic IDs and checksums.
- Do not overwrite the only canonical approved media/version.
- Do not silently weaken safety, licensing or cost controls.

## Human escalation

Human approval remains required before:
- public publishing until policy explicitly enables autonomous publishing;
- paid use when budget authorization/caps have not been configured;
- destructive deletion of canonical history/assets;
- weakening child-safety controls;
- changing locked canonical character/brand identity;
- publishing an asset with unresolved commercial-use/license status.

Routine research, planning, content creation, QA, free-provider routing and paid calls already authorized inside policy may proceed without per-step questions.
