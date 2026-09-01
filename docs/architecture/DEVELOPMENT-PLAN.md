# Development Plan — AI-Native Media Production Platform

## Product direction

The repository began as a kids/lullabies content system. Preserve that child-directed policy profile, but build the underlying product as a general AI-native media production platform capable of:
- child-directed media;
- general/adult-audience media;
- songs/poems/stories;
- educational video;
- shorts/episodes;
- cinematic sequences;
- short films;
- movies up to a configured three-hour project duration;
- future formats through registries.

The first production niche can remain kids, but the core data model must not hard-code `kids` into every entity.

## Development strategy

Build the stable production operating system before integrating many providers or creating a sophisticated UI.

Use vertical slices to prove architecture:
1. 2-minute project;
2. 5–10 minute multi-scene project;
3. 30-minute reliability test;
4. long-form scalability/load/recovery tests toward 3 hours.

Do not attempt a three-hour generated movie as the first acceptance test.

## Parallel multi-agent development strategy

Development is dependency-aware, contract-first, and parallel by default where scopes are genuinely independent.

Canonical protocol and registries live under `ai-native/parallel/`:
- `MULTI-AGENT-PROTOCOL.md`;
- `MODULE-OWNERSHIP.yaml`;
- `ACTIVE-WORK.yaml`;
- `DEPENDENCY-GRAPH.yaml`;
- `MIGRATION-REGISTRY.yaml`;
- `SHARED-FILES.yaml`;
- `CONTRACT-REGISTRY.yaml`;
- `AGENT-TASK-SCHEMA.yaml`;
- `INTEGRATION-PROTOCOL.md`.

Operating model:

`contract/freeze boundary -> identify independent ready work -> claim scopes -> isolated task branches -> scoped CI -> integration queue -> current-main synchronization -> full exact-head promotion CI -> merge`

Concurrency guidance:
- current/default safe target: **4–5 active agents**, including integration and QA/planning lanes;
- after ownership and contract boundaries are stable: **6–8 implementation/review agents plus one Integration Agent**;
- mature repository target: **8–12 active agents** only when enough independent ready nodes exist;
- never split tightly coupled work merely to increase agent count.

The plan's milestone numbering is an architecture/dependency guide, not a requirement that all work be executed serially. Independent planning, contract preparation, QA, frontend preparation, provider research, or module implementation may run in parallel when dependencies, ownership, consent, and shared-file rules permit.

Every agent may read the full repository but may write only its claimed paths. Shared files, generated artifacts, public export surfaces, migration identifiers, global contracts, and repository-wide CI are coordinated by the Integration Agent unless a task receives an explicit scoped grant.

Before every start/resume, the agent must perform the working-instruction audit defined in `MULTI-AGENT-PROTOCOL.md`. If a material change alters how agents must work, the canonical instruction source and affected task records must be updated, and the root README `Current agent working instructions` summary must be synchronized in the same integration cycle. If no material instruction delta exists, README should not be churned merely to refresh a date.

Development consent remains scoped and authoritative. Parallel readiness or a dependency-graph `ready` state never grants executable-development permission by itself.

---

## Milestone 0 — Architecture and contract lock

Status: documentation phase substantially complete.

Deliverables:
- AI engineering constitution;
- project taxonomy;
- character lock design;
- timeline/rhythm design;
- free+paid execution policy;
- provider registry;
- provider scout governance;
- technical stack decision;
- current-system research study.

Exit:
A new senior engineer/AI can explain the domain and implementation order without relying on chat history.

---

## Milestone 1 — Core domain model and repository migration boundary

Implement typed domain models/schemas for:
- Project
- AudienceProfile
- CastProfile
- Character
- CharacterVersion
- CharacterLook
- Location/World
- Prop
- StyleProfile
- VoiceProfile
- Content
- Act/Chapter
- Sequence
- Scene
- Shot
- Take
- Asset
- Timeline
- Provider/Model
- GenerationAttempt
- Job
- QARecord
- CostRecord
- RightsRecord
- Approval

Decide and document runtime persistence migration:
- current Git-backed state remains importable;
- PostgreSQL becomes live operational state when application starts;
- Git retains engineering policies/prompts/research/exported manifests.

Exit:
Schemas validate sample projects including a two-minute song and a 90-minute movie plan without provider calls.

---

## Milestone 2 — Durable workflow/control plane

Implement:
- Python core package;
- FastAPI control API;
- Temporal workflows/workers;
- job/activity IDs;
- idempotency;
- job locks/leases;
- retries/backoff;
- circuit breakers;
- cancellation;
- waiting states;
- approval signals;
- provider webhook/poll reconciliation;
- checkpoint/recovery tests;
- structured logs/run IDs.

Exit:
A synthetic 100-shot workflow can crash/restart and resume without duplicating completed jobs.

---

## Milestone 3 — Asset/object storage and provenance

Implement:
- S3-compatible storage abstraction;
- local development storage;
- signed upload/download flow;
- checksums;
- MIME/media validation;
- FFprobe metadata;
- asset graph;
- provenance/rights fields;
- retention/temp/canonical classes.

Exit:
Every media asset is addressable, verified and traceable to its parents without placing raw media in ordinary Git history.

---

## Milestone 4 — Character and entity library

Implement web/API-ready backend for:
- character list/search/filter;
- new character creation;
- select existing;
- global/project/look/scene locks;
- versioning;
- canonical reference packs;
- voice association;
- locations/worlds;
- props;
- styles;
- rights/consent records;
- identity QA.

Exit:
A recurring character can be created once, locked, selected into two projects, and remain version-pinned.

---

## Milestone 5 — Content intelligence and memory

Generalize current kids content system into policy profiles.

Implement:
- project audience/content profile;
- research;
- portfolio planning;
- content format selection;
- duplicate/originality engine;
- semantic memory using PostgreSQL + pgvector;
- script/lyrics/story structures;
- content versioning;
- child-specific safety rules when child-directed;
- general safety/rights rules for all projects.

Exit:
`next content` creates a policy-compliant, uniqueness-cleared canonical script/lyrics package for a selected project profile.

---

## Milestone 6 — Hybrid audio production

Implement provider-neutral audio contracts:
- narration/TTS;
- full song/music;
- dialogue;
- ambience/SFX;
- speech + music bed;
- voice IDs;
- pronunciation;
- stems;
- automated music direction;
- lip-sync metadata;
- audio QA;
- deterministic mix.

Initial adapters:
- one reliable speech adapter;
- one music adapter;
- manual import path;
- free/paid router integration.

Exit:
One song and one narrated story produce traceable audio masters with QA/cost/provenance.

---

## Milestone 7 — Storyboard, hierarchy and timeline engine

Implement:
- Project -> Act -> Sequence -> Scene -> Shot -> Take;
- storyboard compiler;
- timeline tracks;
- beat/audio markers;
- pacing curves;
- emotional/motion curves;
- incoming/outgoing continuity state;
- first/mid/end keyframes;
- handles/overlap;
- transitions;
- OpenTimelineIO import/export/mapping;
- non-destructive revisions.

Exit:
A 10-minute audio/script project produces an editable provider-neutral shot plan and valid editorial timeline before any video generation.

---

## Milestone 8 — Hybrid image/video provider router

Implement adapter interface first, then a small number of providers.

Capabilities:
- text-to-image;
- reference image;
- image-to-video;
- first/end frames;
- native extension;
- video-to-video/reference video;
- native audio where applicable;
- pricing/quota/licensing metadata;
- manual-free handoff;
- free/paid cost scoring;
- provider health/history.

Do not integrate every discovered provider immediately.

Exit:
The same shot request can route through at least two providers without changing canonical shot/character state.

---

## Milestone 9 — Continuity and generated-media QA

Implement multimodal QA for:
- character identity;
- apparent age/species;
- wardrobe/look;
- props;
- locations;
- composition;
- style;
- lighting;
- camera/screen direction;
- motion/action;
- anatomy/object integrity;
- unwanted text/logo;
- shot boundaries;
- safety;
- rights/provenance completeness.

Use critical hard failures plus scored secondary dimensions.

Exit:
Failed takes are rejected and only affected shots are retried.

---

## Milestone 10 — Deterministic media assembly

Implement FFmpeg pipeline for:
- trim/concat;
- audio sync;
- stem mix/ducking;
- transitions;
- captions;
- graphics;
- aspect variants;
- loudness normalization;
- proxies;
- final masters;
- checksums/render manifests.

Exit:
A multi-provider 5–10 minute project renders reproducibly from approved assets without manual timeline reconstruction.

---

## Milestone 11 — Web application

Build TypeScript + Next.js UI after core workflows are real.

Screens:
- login/workspaces later
- dashboard/projects
- New Project wizard
- Character Library
- Location/Prop/Style library
- Content/script editor
- Storyboard
- Timeline
- Audio
- Shot inspector
- provider/take comparison
- QA/review
- cost/quota
- publishing
- analytics
- provider/admin research

Exit:
A user can configure a project, select/lock characters, run the production flow, inspect costs/QA, regenerate a single shot and approve a master from the UI.

---

## Milestone 12 — Publishing and analytics

Implement platform adapters beginning with YouTube:
- OAuth;
- resumable upload;
- private-first upload;
- audience/Made-for-Kids review;
- synthetic-media disclosure review;
- metadata/captions/thumbnail;
- publishing approvals;
- analytics ingestion;
- learning hypotheses.

Exit:
A final video can be privately uploaded, verified, approved, published and analyzed with lineage back to project attributes.

---

## Milestone 13 — Mobile/API product

Build Expo/React Native app against same versioned API.

Start with:
- project status;
- notifications;
- approvals;
- character/keyframe/take review;
- budget/provider alerts;
- publication approval.

Do not clone the desktop timeline editor initially.

Exit:
Mobile can safely operate review/approval workflows without special backend logic.

---

## Milestone 14 — Long-form hardening

Test increasingly large projects:
- 30 min;
- 60 min;
- 90 min;
- 120 min;
- 180 min synthetic/real workloads.

Verify:
- DB/query performance;
- timeline virtualization;
- scoped AI context;
- workflow history/continue-as-new strategy where required;
- object storage scale;
- retries/provider outages;
- quota waits;
- budget caps;
- incremental renders;
- recovery;
- archival/export.

Three-hour support is an orchestration/timeline/storage capability, not a promise that one model can render a three-hour continuous generation.

---

## Milestone 15 — Production operations

Implement:
- deploy strategy;
- migrations;
- backups;
- object lifecycle;
- metrics/tracing/alerts;
- security hardening;
- audit logs;
- billing/cost governance if multi-user;
- incident/runbooks;
- release process;
- disaster recovery.

---

## Parallel maintenance lane — Daily AI Provider Scout

The daily GitHub Action runs independently from product milestones.

It may safely update research/high-confidence provider facts under policy, but it must not bypass the milestone architecture or automatically rewrite core executable behavior.

## Recommended first vertical slice

After Milestone 1–3 foundations:

**2-minute song + one locked recurring character + one environment + 12–20 shots + hybrid free/paid routing + final FFmpeg master.**

This slice exercises nearly every difficult boundary without hiding architectural mistakes behind a huge movie project.

Then add narrated story and multi-character dialogue before scaling duration.
