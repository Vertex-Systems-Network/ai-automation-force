# AGENTS.md — Mandatory AI Operating Contract

This file is the first instruction source for any AI agent working in this repository.

## Mission

Operate this repository as a persistent, provider-agnostic AI-native media production platform with research intelligence, memory, originality control, reusable/locked entities, autonomous audio direction, editorial timelines, visual continuity, hybrid free/paid provider routing, cost control, production history, rights/provenance, publishing and analytics learning.

The initial business/content profile is child-directed media, but the core platform also supports general/adult-audience projects. Child-specific age and safety rules remain mandatory whenever a project is child-directed.

The repository is the canonical engineering/policy/history source during the current repository-first phase. Chat history and any individual provider history are secondary.

The normal operator command is `next`.

`next` does not always mean "write new content". It means inspect canonical project state and autonomously execute the highest-value safe next unit of work in the lifecycle.

## Mandatory startup sequence

Before doing project work:

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read `ai-native/ENGINEERING-CONTRACT.md`.
4. Read `ai-native/MASTER-PLAN.md`.
5. Read `docs/architecture/DEVELOPMENT-PLAN.md` when development is relevant.
6. Read `docs/architecture/TECH-STACK.md` when architecture/code is relevant.
7. Read `config/project-taxonomy.yaml`.
8. Read `config/execution-policy.yaml`.
9. Read `config/content-policy.yaml` for child/content-policy work.
10. Read `config/provider-registry.yaml`.
11. Read `config/update-policy.yaml` when provider research/self-update is relevant.
12. Read `ai-native/SYSTEM.md` and `ai-native/WORKFLOW.md` where applicable.
13. Read `ai-native/QUALITY-GATES.md` and `ai-native/MEMORY-BANK.md`.
14. Read `ai-native/AUDIO-ROUTER.md` when audio is relevant.
15. Read `ai-native/VIDEO-CONTINUITY.md` when visual/video work is relevant.
16. Read `ai-native/FREE-TIER-ROUTER.md` when provider routing/cost is relevant.
17. Read product docs for character/timeline/project-option work.
18. Read all machine-readable state/ledger files required for the current job.
19. Inspect current implementation, tests and recent relevant Git history.
20. Determine the first incomplete or highest-value eligible job.

Never rely only on chat memory when repository/runtime state exists.

## Product model invariants

### Project configuration

Keep these dimensions separate:
- audience class;
- cast age composition;
- cast gender composition;
- character source/reuse strategy;
- content format;
- creative treatment/genre;
- duration;
- language;
- visual/camera/audio controls;
- pacing/rhythm;
- provider/cost policy;
- review/publishing policy.

Do not store `kids`, `adult`, `man`, `woman`, `both` as one ambiguous enum.

### Character/entity continuity

Recurring characters must be selected from a canonical library or created and locked before recurring use.

Never silently change a locked identity. Use versioned character/look/scene-state records.

Provider-specific reference IDs are derived implementation details, not the canonical identity.

### Timeline hierarchy

Long-form media uses:

`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take`

Provider clip limits do not define artistic shot duration or project duration.

Supported product duration is registry-driven, currently from 60 seconds up to 10,800 seconds (3 hours).

Long-form output is built through resumable shot jobs and deterministic assembly, not one giant model call.

## `next` contract

A normal `next` run must:
- load canonical repository/runtime state;
- detect incomplete, blocked, failed and ready jobs;
- choose the highest-value eligible job;
- refresh research/provider facts if stale and material;
- preserve idempotency and job history;
- execute only within safety, rights, licensing and cost policy;
- route across free or paid providers using execution policy;
- run mandatory QA;
- save canonical artifacts/manifests only after relevant gates pass;
- record rejected attempts as history;
- update state atomically;
- summarize completed work, remaining work and genuine blocks.

If no production item is in progress, `next` may begin a content/project planning cycle according to project settings and portfolio policy.

## Non-negotiable rules

### Audience/safety

When a project is child-directed, use configured age bands and child-safety/content policy. Never treat ages 0–12 as one audience.

For baby audio, design for parent-controlled listening rather than encouraging infant screen engagement.

General/adult-audience support does not disable universal safety, rights, platform or consent requirements.

### Originality

Do not copy, closely imitate or intentionally evoke protected songs, recordings, branded characters, celebrity voices, distinctive fictional universes, lyrics, melodies, plots or catchphrases.

A public-domain concept is not permission to copy a modern recording/arrangement.

### Memory before creation

Never create final canonical content before checking relevant memory/originality state. If state is corrupt or unavailable, repair/reconcile it before approval.

### Provider independence

No provider is the system of record. Switching provider must not reset project, content, audio, character, shot, timeline, continuity, cost, rights or QA history.

### Free + paid hybrid policy

Both free and paid providers may be used. Default mode is `HYBRID_SMART` unless configuration changes it.

- legitimate free capacity should be used when capability, quality, continuity and license are sufficient;
- free consumer web credits are not automatically free API capacity;
- manual-free provider handoffs are explicit jobs;
- paid calls occur only inside configured authorization/budget policy;
- never create/rotate accounts to evade quotas;
- never automate a provider contrary to terms;
- do not accept lower-quality output merely because it was free;
- optimize expected accepted-output cost, including retry/manual-labor risk.

### Audio architecture

Speech, music, dialogue and narration-with-background are distinct routes.

- speech -> speech/TTS provider;
- full song -> capable music model;
- narration + background -> separate voice + music stems then deterministic mix;
- dialogue -> versioned character voice assignments and scene timing;
- SFX/ambience -> independent assets/tracks where appropriate.

The AI may infer music/audio direction unless the operator/project overrides it.

### Visual continuity

Never assume different video providers share hidden generation state.

Use storyboard/timeline + canonical characters/entities + keyframes/references + scene/shot state + continuity QA.

### No mass-generation shortcut

Do not optimize output count at the expense of originality, coherence, continuity, rights, safety or platform quality.

## Engineering contract

All implementation/maintenance work must follow `ai-native/ENGINEERING-CONTRACT.md`.

This includes architecture-first work, impact analysis, current official-source research when material, security, risk-based testing, durable workflows, provider abstraction, data/media integrity, provenance, observability, controlled dependencies, checkpoints and honest completion status.

## Daily provider self-update governance

The daily scout is controlled by:
- `.github/workflows/provider-scout.yml`;
- `automation/provider_scout.py`;
- `config/update-policy.yaml`;
- `config/provider-sources.json`.

It may auto-merge only permitted low-risk Class A/B changes after validation and repository rules.

It must not blindly self-merge:
- new provider integrations;
- executable code changes;
- schemas/migrations;
- security/auth changes;
- budget behavior;
- publishing behavior;
- destructive changes.

A newly discovered provider starts disabled/evaluation-only until adapter, tests, license and capability validation exist.

## Lifecycle/history

Content/project lifecycle may progress through planning, writing, audio, storyboard, keyframes, shots, assembly, QA, publishing and analytics states. Do not mark a stage complete unless its gate actually passed.

Record successful and rejected attempts with relevant:
- run/job/project/content/asset/scene/shot/take IDs;
- provider/model;
- access tier;
- prompt version/hash;
- input/output hashes;
- generation ID;
- QA scores;
- rejection reason;
- quota/cost;
- rights/provenance;
- timestamps.

Failed history is valuable and must not be discarded merely because the asset was rejected.

## Change discipline

- Prefer additive, backwards-compatible changes.
- Version schemas, prompts and locked entities.
- Keep policies, prompts, research, machine state and automation code separated.
- Never commit secrets.
- Use deterministic IDs/checksums.
- Do not overwrite the only canonical approved asset/version.
- Do not silently weaken safety, licensing, cost or review controls.

## Human escalation

Human/independent approval remains required when configured or materially necessary, especially for:
- public publishing until policy explicitly enables otherwise;
- paid use without configured authorization/caps;
- destructive deletion of canonical history/assets;
- weakening child-safety or security controls;
- changing locked canonical character/brand identity;
- unresolved commercial-use/consent/license state;
- Class C/D automated self-update changes.

Routine research, planning, generation, QA, provider routing and already-authorized paid calls may proceed without unnecessary per-step questions.
