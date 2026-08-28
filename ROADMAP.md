# Lullabies AI-Native Media Platform Roadmap

Canonical architecture foundation: `ai-native/MASTER-PLAN.md`

Engineering constitution: `ai-native/ENGINEERING-CONTRACT.md`

Detailed implementation sequence: `docs/architecture/DEVELOPMENT-PLAN.md`

Technical stack: `docs/architecture/TECH-STACK.md`

Project options: `docs/product/PROJECT-OPTIONS.md`

Default execution policy: `HYBRID_SMART` from `config/execution-policy.yaml`.

The platform uses one provider-agnostic workflow with interchangeable free/manual-free/paid provider adapters. The initial niche remains kids media, but the core project model now supports general/adult audiences, many content formats and projects up to a configured three-hour duration.

## Milestone 0 — Architecture/Documentation Lock

Status: substantially complete.

Implemented/documented:
- repository-backed AI memory foundation;
- mandatory agent contract;
- project-specific engineering constitution;
- provider-neutral master architecture;
- project taxonomy;
- audience/cast dimensions;
- character type registry;
- reusable character lock/version system;
- songs/poems/stories/episodes/movies and other format registry;
- duration model: 60 seconds to 10,800 seconds;
- visual/camera/audio/pacing/transition option model;
- hierarchical long-form timeline design;
- free+paid execution policy;
- generation history;
- audio router;
- provider/free-tier router;
- video continuity design;
- provider research study;
- technical stack decision;
- daily provider scout workflow/governance.

Remaining implementation-era schemas:
- project schema;
- character/entity schemas;
- act/sequence/scene/shot/take schemas;
- job/workflow schema;
- asset/provenance schema;
- cost/quota schema;
- timeline/OTIO mapping schema;
- prompt registry schema;
- publishing/analytics schemas.

## Milestone 1 — Core Domain + Runtime Persistence Boundary

Build typed Python domain models and schemas for projects, audience/cast, characters/entities, content, hierarchy, assets, providers, jobs, QA, costs, rights and approvals.

Design the migration from current Git-backed state to PostgreSQL operational state while keeping Git canonical for engineering policy/prompts/research/exported manifests.

Exit: sample 2-minute and 90-minute projects validate without provider calls.

## Milestone 2 — Durable Workflow Control Plane

Build FastAPI + Temporal foundation:
- API/control plane;
- durable workflows/workers;
- idempotency;
- locks/leases;
- retries/backoff;
- circuit breakers;
- cancellation;
- manual/approval waits;
- provider polling/webhooks;
- crash recovery;
- logs/run IDs.

Exit: synthetic 100-shot workflow resumes after interruption without duplicate completed work.

## Milestone 3 — Asset Storage + Provenance

Implement S3-compatible object storage, media probing/checksums, asset graph, rights/provenance and signed access.

Exit: every media asset is verified and traceable without bloating Git.

## Milestone 4 — Character/Entity Library

Implement selectable reusable entities:
- characters;
- versions/looks;
- lock modes;
- reference packs;
- voices;
- locations/worlds;
- props;
- styles;
- identity QA;
- rights/consent.

Exit: one locked recurring character can be reused in multiple version-pinned projects.

## Milestone 5 — Content Intelligence + Memory

Generalize kids-first content intelligence into project policy profiles:
- research;
- candidate/format selection;
- script/lyrics/story structures;
- semantic duplicate/originality memory;
- pgvector;
- safety/profile rules;
- content versioning.

Exit: `next content` creates a researched, uniqueness-cleared canonical package.

## Milestone 6 — Hybrid Audio OS

Implement provider-neutral narration, songs/music, dialogue, ambience/SFX, stems, pronunciation, autonomous music direction, QA and deterministic mixing.

Exit: one song and one narrated story reach approved audio master with cost/provenance history.

## Milestone 7 — Storyboard + Timeline + Rhythm Engine

Implement:
- Project -> Act -> Sequence -> Scene -> Shot -> Take;
- storyboard;
- timeline tracks;
- beat/audio markers;
- pacing/emotional curves;
- incoming/outgoing continuity state;
- keyframes;
- handles/overlap;
- transitions;
- OpenTimelineIO mapping;
- non-destructive edits.

Exit: a 10-minute project becomes an editable provider-neutral shot plan before video spending.

## Milestone 8 — Hybrid Image/Video Router

Implement provider capability adapters and free/paid selection by capability, continuity, expected accepted-output cost, rights and budget.

Start with a small adapter set. Do not integrate every discovered AI merely because it exists.

Exit: same canonical shot can switch between at least two providers without losing state.

## Milestone 9 — Continuity/Generated Media QA

Implement multimodal identity/environment/camera/action/style/anatomy/text/safety QA with critical hard failures and take comparison.

Exit: failed takes are rejected and only affected shots are regenerated.

## Milestone 10 — Deterministic Assembly

Implement FFmpeg-based trim/concat/audio mix/transitions/captions/aspect variants/normalization/final encodes and reproducible render manifests.

Exit: multi-provider project renders without manual timeline reconstruction.

## Milestone 11 — Web Application

Build TypeScript + Next.js UI:
- projects;
- new-project wizard;
- Character/Entity Library;
- script/content;
- storyboard;
- timeline;
- audio;
- shot inspector/take comparison;
- QA;
- cost/quota;
- publishing;
- analytics;
- provider research/admin.

Exit: full 2-minute vertical slice can be operated from UI.

## Milestone 12 — Publishing + Analytics

Begin with YouTube private-first upload, metadata/captions/thumbnail, audience/synthetic-media reviews, approvals and analytics feedback.

Exit: publish/analyze loop retains full lineage to project attributes.

## Milestone 13 — Mobile/API Product

Build Expo/React Native review/approval/status application using the same versioned OpenAPI backend.

Exit: mobile can safely review and approve production without duplicated backend logic.

## Milestone 14 — Long-Form Hardening

Scale tests through 30/60/90/120/180-minute project plans and workloads. Validate workflow history, DB queries, timeline virtualization, scoped AI context, object storage, provider outages, quota waits, cost caps, incremental renders and disaster recovery.

Three-hour support is a production-orchestration capability, not a single-model-generation requirement.

## Milestone 15 — Production Operations

Deployments, migrations, backups, monitoring/tracing, audit logs, security hardening, incident runbooks, releases and disaster recovery.

## Parallel Maintenance Lane — Daily Provider Scout

`.github/workflows/provider-scout.yml` researches providers daily and creates PRs only for material changes.

Safe Class A/B evidence/provider facts may merge after validation when repository rules permit. New integrations, architecture/code/schema/security/budget/publishing changes require review.

## Immediate Development Recommendation

Proceed with **Milestone 1**, then **Milestone 2**, then **Milestone 3**.

Do not start with a complex UI or ten AI integrations.

First production vertical slice after foundations:

**2-minute song + one locked recurring character + one environment + 12–20 planned shots + hybrid free/paid routing + continuity QA + final FFmpeg master.**

After that, add multi-character narration/dialogue and increase duration progressively.
