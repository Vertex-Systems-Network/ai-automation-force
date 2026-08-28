# AI Automation Force — AI-Native Media Production Platform

This repository is the engineering and AI-memory foundation for a provider-agnostic media production platform. The initial niche remains child-directed content, but the core product is deliberately general enough to support songs, poems, stories, educational media, episodes, cinematic sequences, short films and movies up to a configured three-hour project duration.

Kids-specific age/safety rules remain mandatory whenever a project is child-directed; they are a policy profile, not a limitation of the underlying platform architecture.

## Core operating model

The system is not a single model or a `prompt -> video` script.

It manages:
- research and creative planning;
- persistent content/originality memory;
- project/audience/cast configuration;
- reusable locked characters and other entities;
- content/scripts/lyrics;
- autonomous audio direction;
- storyboard and editorial timeline;
- keyframes/references;
- hybrid free/paid provider routing;
- per-shot generation history;
- continuity and media QA;
- deterministic FFmpeg assembly;
- rights/provenance;
- budgets/quotas;
- publishing;
- analytics and learning.

## Primary operator command

`next`

Eventually `next` means: inspect canonical state and perform the highest-value safe eligible production job.

It may research/create content, render audio, plan scenes, generate/retry one shot, prepare a manual free-provider handoff, assemble a master, prepare publishing, or analyze results depending on project state.

## Product configuration

Machine-readable options live in:
- `config/project-taxonomy.yaml`
- `config/content-policy.yaml`
- `config/execution-policy.yaml`
- `config/provider-registry.yaml`

Human-facing option documentation:
- `docs/product/PROJECT-OPTIONS.md`
- `docs/product/CHARACTER-LOCK-SYSTEM.md`
- `docs/product/TIMELINE-SEQUENCE-ENGINE.md`

Important dimensions are stored separately rather than ambiguously combining them:
- audience class;
- cast age composition;
- cast gender composition;
- character strategy;
- content format;
- creative treatment;
- duration;
- language;
- visual/camera controls;
- audio controls;
- pacing/rhythm;
- provider/cost mode;
- review/publishing policy.

## Character continuity

Recurring production characters are selected from a canonical Character Library or created and locked before recurring use.

Supported strategies include:
- select locked existing;
- create new and lock;
- mixed existing/new;
- project-only one-off lock;
- no character;
- AI decide.

Provider-specific saved references are derived adapters. Character identity/version/reference packs in this system remain canonical.

## Long-form model

Projects use a hierarchy such as:

`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take`

A 1–3 minute piece and a three-hour movie use the same concepts at different scale.

Long duration is achieved through durable orchestration, scoped context, many resumable shot jobs and deterministic assembly—not by assuming an AI provider can generate a three-hour continuous clip.

## Free + paid providers

Default execution policy is `HYBRID_SMART`.

One provider-neutral workflow can use:
- legitimate free API capacity;
- manual free web tiers where permitted;
- paid APIs within authorization/budget;
- provider fallbacks.

The router optimizes capability, quality, continuity, rights, expected retry cost and budget rather than simply selecting the cheapest nominal call.

## Technical direction

Canonical stack decision: `docs/architecture/TECH-STACK.md`.

Recommended:
- Python + FastAPI for backend/API/AI/media logic;
- Temporal for durable workflows;
- PostgreSQL + pgvector for future application operational state and semantic memory;
- S3-compatible object storage for large media;
- FFmpeg for deterministic media processing;
- OpenTimelineIO for editorial interchange where practical;
- TypeScript + Next.js/React for web;
- TypeScript + React Native/Expo for the future mobile app.

## Engineering contract

Every engineering agent must follow:
- `AGENTS.md`
- `ai-native/ENGINEERING-CONTRACT.md`
- `ai-native/MASTER-PLAN.md`
- relevant product/architecture documentation.

The engineering constitution requires architecture-first development, current official-source research when material, security, tests, durable recovery, provenance, clear Git/checkpoints, and no fake completion.

## Daily provider research

`.github/workflows/provider-scout.yml` runs a daily provider/API scout.

Governance:
- `config/update-policy.yaml`
- `config/provider-sources.json`
- `docs/operations/DAILY-PROVIDER-SCOUT.md`

The scout can auto-merge only low-risk evidence/high-confidence provider fact changes when repository rules allow. New provider integrations, executable code, schemas, security, budget and publishing behavior require review.

## Development plan

Canonical implementation sequence:
`docs/architecture/DEVELOPMENT-PLAN.md`

The recommended first vertical slice after core foundations is:

**2-minute song + one locked recurring character + one environment + 12–20 shots + hybrid free/paid routing + final FFmpeg master.**

This proves the difficult architecture before scaling to longer productions.
