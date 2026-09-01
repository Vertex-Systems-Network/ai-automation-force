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
- `ai-native/parallel/MULTI-AGENT-PROTOCOL.md` for development/maintenance work;
- relevant product/architecture documentation.

The engineering constitution requires architecture-first development, current official-source research when material, security, tests, durable recovery, provenance, clear Git/checkpoints, and no fake completion.

## Current agent working instructions

This is the concise human-visible summary. Canonical details live in `AGENTS.md`, `ai-native/ENGINEERING-CONTRACT.md`, `ai-native/DEVELOPMENT-CONSENT-GATE.md`, and `ai-native/parallel/`.

Current rules:
- on **every start or resume**, including `continue`/`next`/`resume`, perform a working-instruction audit before proceeding;
- read current repository/PR/checkpoint state rather than relying on chat memory;
- for development work, read `MULTI-AGENT-PROTOCOL.md`, module ownership, active-work, dependency, migration, shared-file and contract registries;
- an agent may **read the entire repository but write only its claimed paths**;
- use task/work-package branches and pin an exact base commit when implementation starts;
- overlapping active write claims are not allowed until the Integration Agent resolves/splits ownership;
- shared files, generated artifacts, public export surfaces, repository-wide CI and global contracts are integration-owned unless a task receives a scoped grant;
- reserve migration identifiers before creating migrations;
- define/freeze shared contracts before fanning dependent implementations out to multiple agents;
- parallel readiness does not bypass development consent;
- scoped CI may accelerate feedback, but required exact-head full promotion CI remains mandatory before merge;
- if a material governance/ownership/dependency/contract/CI/consent instruction changes how agents should work, update affected task instructions and **synchronize this README section in the same integration cycle**;
- if the instruction audit finds no material change, do not churn README only to refresh a date.

Parallel capacity guidance:
- current/default: **4–5 active agents** including Integration and QA/planning lanes;
- after stable module/contract boundaries: **6–8 implementation/review agents + 1 Integration Agent**;
- mature repository: **8–12 active agents** only when the dependency graph exposes enough independent ready work.

Canonical coordination files:
- `ai-native/parallel/MULTI-AGENT-PROTOCOL.md`
- `ai-native/parallel/MODULE-OWNERSHIP.yaml`
- `ai-native/parallel/ACTIVE-WORK.yaml`
- `ai-native/parallel/DEPENDENCY-GRAPH.yaml`
- `ai-native/parallel/MIGRATION-REGISTRY.yaml`
- `ai-native/parallel/SHARED-FILES.yaml`
- `ai-native/parallel/CONTRACT-REGISTRY.yaml`
- `ai-native/parallel/AGENT-TASK-SCHEMA.yaml`
- `ai-native/parallel/INTEGRATION-PROTOCOL.md`

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

## Milestone progress

Last repository-history review: **2026-09-01**.

The table below tracks the currently active implementation milestone. Completed dates are derived from repository/PR history. Active or not-yet-started packages keep `TBD` end dates until completion is evidenced; progress is based on landed work packages rather than speculative estimates.

| Phase / Module | Scope | Start date | End date | Status | Progress |
| --- | --- | --- | --- | --- | --- |
| **M03 Overall** | Asset Storage and Provenance — 8 work packages | 2026-08-29 | TBD | 🟡 In progress | `███████▌░░` **75% landed (6/8)** |
| **M03-WP1** | Storage adapter and object metadata | 2026-08-29 | 2026-08-29 | ✅ Complete / landed | `██████████` **100%** |
| **M03-WP2** | Upload sessions | 2026-08-29 | 2026-08-29 | ✅ Complete / landed | `██████████` **100%** |
| **M03-WP3** | Quarantine/probe/security | 2026-08-29 | 2026-08-30 | ✅ Complete / landed | `██████████` **100%** |
| **M03-WP4** | Asset lineage/provenance/rights | 2026-08-30 | 2026-08-31 | ✅ Complete / promoted to `main` | `██████████` **100%** |
| **M03-WP5** | Derivatives/proxies | 2026-08-31 | 2026-09-01 | ✅ Complete / promoted to `main` | `██████████` **100%** |
| ↳ **PR #41** | WP5 deterministic derivative foundation promotion | 2026-09-01 | 2026-09-01 | ✅ Merged | `██████████` **100%** |
| ↳ **PR #42** | WP5 executable resource-bounded derivative worker promotion | 2026-09-01 | 2026-09-01 | ✅ Merged — fresh Governance/Core/Durable green | `██████████` **100%** |
| **M03-WP6** | Signed delivery | 2026-09-01 | 2026-09-01 | ✅ Complete / promoted to `main` | `██████████` **100%** |
| ↳ **PR #43** | Signed-delivery authorization and S3 grant foundation | 2026-09-01 | 2026-09-01 | ✅ Merged | `██████████` **100%** |
| ↳ **PR #44** | Durable share-link authority and atomic use accounting | 2026-09-01 | 2026-09-01 | ✅ Merged — fresh Governance/Core/Durable green | `██████████` **100%** |
| ↳ **PR #46** | Signed-delivery API, access policy and Range acceptance | 2026-09-01 | 2026-09-01 | ✅ Merged — fresh Governance/Core/Durable green | `██████████` **100%** |
| **M03-WP7** | Retention/archive/delete/export primitives | 2026-09-01 | TBD | 🟡 Active — architecture/persistence audit | `░░░░░░░░░░` **0% landed; implementation active** |
| **M03-WP8** | Acceptance | TBD | TBD | ⚪ Pending | `░░░░░░░░░░` **0%** |

### Current engineering checkpoint

The active development frontier is **M03-WP7 — Retention/archive/delete/export primitives**. WP6 is fully promoted to `main`: PR #43 landed the authorization/signing foundation, PR #44 landed durable share-link authority with atomic use accounting, and PR #46 landed the signed-delivery API plus explicit access policy and Range acceptance after fresh Repository Governance, Core Domain Contracts and Durable Control Plane verification.

WP7 must preserve canonical media safety while adding lifecycle transitions: temporary cleanup must be bounded, archive/restore must be reversible, soft deletion must precede destructive deletion, hard-delete propagation must be explicit and auditable, export staging must not widen delivery authority, and vector/index cleanup must be represented as deterministic hooks rather than hidden side effects.

Current continuation order:

`WP7 lifecycle contract -> archive/restore state -> soft/hard deletion propagation -> temp cleanup -> export staging -> vector/index cleanup hooks -> exact-head CI -> WP7 promotion -> WP8`
