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
- `ai-native/parallel/SUPERVISOR-PLAN.md` when parallel Supervisor mode is active;
- relevant product/architecture documentation.

The engineering constitution requires architecture-first development, current official-source research when material, security, tests, durable recovery, provenance, clear Git/checkpoints, and no fake completion.

## Current agent working instructions

This is the concise human-visible summary. Canonical details live in `AGENTS.md`, `ai-native/ENGINEERING-CONTRACT.md`, `ai-native/DEVELOPMENT-CONSENT-GATE.md`, and `ai-native/parallel/`.

Current rules:
- canonical compact resume state lives under `ai-native/parallel/state/`; on every start/resume read `CURRENT-STATE.yaml` and `LAST-CHECKPOINT.md` first, then resolve exact main, OPEN Issues, OPEN PRs, claims/queue, and Runner Benchmark before broad historical reading;
- compact resume state is an index only and never overrides live repository/runtime evidence;
- full-project preplanning is complete and canonical status is `FULL_PROJECT_PLANNING_READY_FOR_CONSENT`; this does not authorize executable development, which still requires explicit scoped consent plus applicable milestone/dependency/governance gates;
- one operator `continue`/`resume` turn defaults to one bounded logical milestone; do not chain unrelated development, repeated CI polling, merge, post-merge work, and another task in the same turn;
- perform at most one consolidated CI/status refresh per milestone by default and never tight-poll remote checks;
- persist `VERIFYING`/`WAITING_EXTERNAL` before final exact-head observation when remote checks are expected; if CI is still running, record run IDs on the PR/Issue status surface without creating a state-only source commit that invalidates the tested head;
- register material remote/container/browser/runtime/full-regression/performance work in `ai-native/parallel/state/RUNNER-BENCHMARK.yaml`; runner registration never grants execution authority;
- every engineering response ends with repository name, evidence-based current-module progress bar, and evidence-based overall roadmap progress bar; unknown progress is reported as unknown rather than guessed;
- before every engineering response, reconcile the README `Live development progress` snapshot against live repository truth; whenever exact main, active PR/Issue, current module/status/percentage, accepted-milestone count, genuine blocker, or exact next action materially changes, update that README snapshot in the same integration cycle;
- a strictly read-only turn with no material progress/state change must verify the README snapshot but must not fabricate percentage movement or create a timestamp-only commit solely to look active;
- on **every start or resume**, including `continue`/`next`/`resume`, perform a working-instruction audit before proceeding;
- read current repository/PR/checkpoint state rather than relying on chat memory;
- in multi-agent Supervisor mode, the agent controlling the main integration lane is the **Supervisor** and owns assignment/review/merge authority;
- when a new multi-agent orchestration assignment specifies parallel modules, the Supervisor's **first repository action is to create every intended module branch, including its own module branch, before documenting/starting the work**;
- every **new agent must start from current `main`** and may not start directly from a feature branch or self-assign a module;
- on a new-agent arrival, the Supervisor checks `AGENT-SLOTS.json` + `SUPERVISOR-PLAN.md`; if an eligible `open` slot exists, the Supervisor assigns that module/branch and records the occupied agent/start state before work begins;
- if all eligible module slots are occupied, the Supervisor stops the new agent immediately and says exactly **`Go Home Come Back Next Time`**; that agent receives no module/branch and starts no work;
- branch creation or slot assignment does not bypass dependency or development-consent gates; future/blocked lanes remain planning/contract-only;
- for development work, read `MULTI-AGENT-PROTOCOL.md`, `SUPERVISOR-PLAN.md`, `AGENT-SLOTS.json`, module ownership, active-work, dependency, migration, shared-file, contract, merge-queue, Supervisor-state, and broadcast registries;
- an agent may **read the entire repository but write only its claimed paths**;
- use task/work-package branches and pin an exact base commit when implementation starts;
- overlapping active write claims are not allowed until the Supervisor resolves/splits ownership;
- shared files, generated artifacts, public export surfaces, repository-wide CI and global contracts are Supervisor/integration-owned unless a task receives a scoped grant;
- reserve migration identifiers before creating migrations;
- define/freeze shared contracts before fanning dependent implementations out to multiple agents;
- every agent must announce exactly **`Work Done and Submitted`** when its bounded branch submission is ready for Supervisor review;
- when another agent submits, the Supervisor checkpoints/pauses its own module work, reviews the submission, promotes only after required synchronization and exact-head gates, records the merge, then resumes its saved checkpoint;
- after a promotion merge that active agents must observe, the Supervisor emits and records exactly: **`New changes have been merged — please merge these changes into your branch first, then resume your own work.`**;
- a broadcast bookkeeping/reconciliation merge does not recursively create another broadcast unless that merge itself introduces new material state active agents must observe;
- affected agents must synchronize the new `main`, rerun the working-instruction audit, revalidate contracts/dependencies/migration state, acknowledge the broadcast, and only then resume; as of broadcast 23 the active M03/M04/M05/M06/M07/M08/QA branches were reverified `ahead_by=0` and non-force fast-forwarded to `main@94160c21e2f7a6511c6d4fd58c6db9cbad168a5b`; PR #110 subsequently promoted the Broadcast 23/M04 consent-readiness handoff to `main@c4671a83173f84da058d82f28da2d4ee3d58229f`;
- an unacknowledged mandatory merge broadcast places a branch in `sync-required` and blocks submission/promotion;
- parallel readiness does not bypass development consent;
- scoped CI may accelerate feedback, but required exact-head full promotion CI remains mandatory before merge;
- Repository Governance validates Supervisor/slot state, slot-to-plan/task consistency, exact completion/broadcast phrases, broadcast sequence consistency, and duplicate migration reservations;
- if a material governance/ownership/dependency/contract/CI/consent/Supervisor-workflow instruction changes how agents should work, update affected task instructions and **synchronize this README section in the same integration cycle**;
- if the instruction audit finds no material change, do not churn README only to refresh a date.

Parallel capacity guidance:
- current/default: **4–5 active agents** including Supervisor and QA/planning lanes;
- after stable module/contract boundaries: **6–8 implementation/review agents + 1 Supervisor**;
- mature repository: **8–12 active agents** only when the dependency graph exposes enough independent ready work;
- current defined slot registry is fully occupied, so an extra agent currently receives **`Go Home Come Back Next Time`** until a slot is explicitly released/opened.

Canonical coordination files:
- `ai-native/parallel/state/CURRENT-STATE.yaml`
- `ai-native/parallel/state/LAST-CHECKPOINT.md`
- `ai-native/parallel/state/EXECUTION-JOURNAL.md`
- `ai-native/parallel/state/RUNNER-BENCHMARK.yaml`
- `ai-native/parallel/MULTI-AGENT-PROTOCOL.md`
- `ai-native/parallel/SUPERVISOR-PLAN.md`
- `ai-native/parallel/AGENT-SLOTS.json`
- `ai-native/parallel/SUPERVISOR-STATE.yaml`
- `ai-native/parallel/SUPERVISOR-BROADCASTS.yaml`
- `ai-native/parallel/MERGE-QUEUE.yaml`
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

The scout does not auto-merge. It may prepare bounded evidence updates, while provider integrations, executable code, schemas, security, budget, publishing behavior, credentials, paid calls and production changes require the applicable review/consent gates.

## Development plan

Canonical implementation sequence:
`docs/architecture/DEVELOPMENT-PLAN.md`

The recommended first vertical slice after core foundations is:

**2-minute song + one locked recurring character + one environment + 12–20 shots + hybrid free/paid routing + final FFmpeg master.**

This proves the difficult architecture before scaling to longer productions.

## Milestone progress

### Live development progress

This is the authoritative human-visible progress snapshot. It must be reconciled before every engineering response and updated in the same integration cycle whenever material repository progress/state changes.

- **Last reconciled:** 2026-09-22
- **Exact live main before this progress-contract branch:** `c4671a83173f84da058d82f28da2d4ee3d58229f`
- **Accepted roadmap milestones:** `3/16` — `██░░░░░░░░` **19%**
- **M03 Protected Main Governance:** `████████░░` **80%** — source/closeout complete; Issue #36 live GitHub admin protection remains
- **M04 execution preflight:** `██████████` **100%** — existing domain/persistence reuse confirmed; minimal early Workspace ownership substrate selected in Issue #111
- **M04 executable development:** `░░░░░░░░░░` **0%** — blocked by Issue #36 and explicit scoped M04 executable consent
- **Open PRs at reconciliation start:** `0`
- **Open planning/governance Issues:** #36 and #111
- **Current bounded work:** make README progress reconciliation a mandatory AI-Native operating contract
- **Exact next product-development path:** promote this progress-contract change; satisfy Issue #36 live protected-main gate; record explicit scoped M04 consent; revalidate ownership/migration state; begin M04-WP1A

README progress is evidence, not an activity counter: percentages move only when repository-defined gates move. If a turn is read-only and nothing changes, the snapshot is verified as unchanged rather than artificially incremented.

Current repository truth: M03 source implementation and WP8 source acceptance are complete, but M03 is **not fully accepted/governed** because Issue #36 still lacks live protected-main enforcement. Full-project preplanning is complete with canonical status `FULL_PROJECT_PLANNING_READY_FOR_CONSENT`; executable M04+ development still requires Issue #36 closure where applicable and explicit scoped development consent.

The table below is retained as a **historical 2026-09-01 snapshot**, not current execution truth. Current execution truth comes from `ai-native/parallel/state/CURRENT-STATE.yaml`, live GitHub evidence, and the current Supervisor plan.

Last historical repository review represented below: **2026-09-01**.

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
| **M03-WP7** | Retention/archive/delete/export primitives | 2026-09-01 | TBD | 🟡 Active — lifecycle foundation synchronized; promotion pending | `░░░░░░░░░░` **0% landed; implementation active** |
| **M03-WP8** | Acceptance | TBD | TBD | ⚪ Pending | `░░░░░░░░░░` **0%** |

### Current engineering checkpoint

M03 source work, WP8 source acceptance, Issue #97 security remediation, PR #106 security-governance closeout, PR #109 planning-ready reconciliation, and PR #110 Broadcast 23/M04 consent-readiness handoff are complete. Current live `main` before this progress-contract branch is `c4671a83173f84da058d82f28da2d4ee3d58229f`.

The remaining M03 governance gate is Issue #36: live GitHub `main` protection is still not verified/applied in an admin-capable context. No additional WP7/WP8 product/API/schema/provider work is authorized merely to create activity.

Current continuation order:

`README progress-contract promotion -> close Issue #36 live protected-main gate -> record explicit scoped M04 development consent -> fresh ownership/migration/security revalidation -> M04-WP1A minimal Workspace ownership substrate + standalone Character/Entity repository boundary`

M04–M08 planning is hardened but not executable completion. M09 remains unactivated by implication.
