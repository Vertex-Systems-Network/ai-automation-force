# M02 Development Consent Brief — Durable Workflow Control Plane

Status: `M02_READY_FOR_CONSENT`

Prepared: 2026-08-29

This document requests scoped executable-development approval for M02 only. It does not itself authorize implementation.

## Prerequisites verified

- P0 Full Project Preplanning Gate: `FULL_PROJECT_PLANNING_READY_FOR_CONSENT`.
- M01 Core Domain & Persistence Boundary: `M01_COMPLETE`.
- M01 final checkpoint: `checkpoints/2026-08-29-m01-complete.md`.
- M02 canonical plan: `docs/milestones/M02/PLAN.md`.
- Mutable FastAPI/Temporal facts revalidated: `docs/architecture/M02-CURRENT-STACK-REVALIDATION-2026-08-29.md`.

## 1. Milestone / scope

Implement **M02 — Durable Workflow Control Plane** only.

Goal:
build the provider-neutral FastAPI + Temporal execution foundation that can start, inspect, pause, retry, cancel, resume and recover long-running project jobs without duplicating completed work or external side effects.

Approved scope would cover these work packages in order:

### M02-WP1 — FastAPI control scaffold
- `apps/api/` application scaffold;
- validated environment/settings boundary;
- lifespan-managed application resources;
- liveness/readiness endpoints;
- request/correlation IDs;
- structured API errors;
- versioned REST/OpenAPI contract generation;
- internal development identity only where an endpoint requires a caller identity; no full auth/RBAC implementation.

### M02-WP2 — Temporal foundation
- `apps/worker/` scaffold;
- current Temporal Python SDK integration;
- client/namespace/task-queue configuration;
- worker bootstrap and shutdown;
- workflow/activity conventions;
- deterministic sandbox rules;
- explicit Activity timeout policy;
- workflow/run references persisted in application state;
- test/dev Temporal server path with exact version pinning at implementation time.

### M02-WP3 — Job, command and idempotency control
- canonical execution/job state transitions using existing M01 domain direction;
- mutation idempotency keys;
- operation fingerprints;
- duplicate command suppression;
- DB uniqueness/concurrency boundary;
- leases/claim/version conflict where application-level coordination needs them;
- transactional outbox/inbox or equivalent durable event handoff where required to close DB↔Temporal failure windows.

### M02-WP4 — Retry, timeout, circuit and cancellation policy
- normalized retry/failure classes;
- bounded exponential backoff/jitter policy;
- Activity/workflow timeouts;
- retry exhaustion behavior;
- circuit/open/degraded provider placeholder behavior using fake activities;
- cancellation propagation;
- terminal/manual-action states;
- retry-scoped behavior that does not restart completed sibling jobs.

### M02-WP5 — Durable human/approval waits
- pause for explicit approval;
- approval signal/update contract;
- stale version/revision rejection;
- expiry/timeout behavior;
- manual-handoff and budget-wait state representation without actual provider spend;
- safe resume after worker/API restart.

### M02-WP6 — External asynchronous callback/reconciliation pattern
Using a **fake provider only**:
- submit asynchronous external job;
- poll path;
- webhook/callback path;
- callback verification abstraction;
- duplicate callback suppression;
- out-of-order/stale callback handling;
- provider timeout/unavailable simulation;
- reconciliation to canonical state.

No real provider credential, endpoint or paid generation is included.

### M02-WP7 — Job/control API and progress surface
- create/start synthetic job/workflow;
- inspect job/workflow/project execution state;
- cancel/retry supported operations;
- cursor-paginated history where needed;
- normalized errors;
- SSE progress stream initially;
- WebSocket remains out unless a concrete bidirectional requirement is proven.

### M02-WP8 — Recovery, replay and 100-shot acceptance
- synthetic 100-shot fan-out/join workflow;
- controlled worker termination/restart;
- API process restart while workflow continues;
- Activity retry/recovery;
- duplicate callback/event injection;
- cancellation tests;
- manual approval wait/resume;
- retained Temporal histories + replay verification;
- Continue-As-New/history-growth policy proof where the acceptance fixture reaches the configured threshold;
- assert no duplicate terminal work/side effects.

## 2. Why now

M01 has stabilized and verified:
- provider-neutral domain contracts;
- full lineage/aggregate invariants;
- PostgreSQL schema/migrations;
- repository round trips;
- stable IDs, rights and persistence boundaries.

M02 is therefore the next dependency-safe layer. Provider adapters, asset storage, content intelligence, media generation and product UI should not build their own ad-hoc retry/background-job systems before the durable control plane exists.

## 3. Expected files/components

Likely new/changed areas:

```text
apps/
  api/
  worker/
packages/
  python-core/
    workflow/job/control services as needed
  contracts/
    generated OpenAPI artifacts when introduced
tests/
  api/
  workflows/
  integration/
packages/python-core/migrations/
  versions/   # additive M02 persistence changes if needed
infra/ or test tooling
  only minimal local/CI Temporal dev-server configuration required for M02 verification
.github/workflows/
  only if permanent M02 CI gates need to be added
```

Exact paths may be refined without expanding the approved behavior.

## 4. Behavioral changes

After M02, the repository will have executable capability to:
- start synthetic durable project workflows through an API/control interface;
- execute workflow activities on Temporal workers;
- persist application-facing job/workflow references/state;
- safely deduplicate repeated start/mutation commands;
- wait durably for approval/callback/timers;
- retry bounded failures;
- cancel supported executions;
- survive process restart;
- report progress/state;
- replay retained histories for deterministic compatibility.

It will **not** generate real AI media.

## 5. Data / migration impact

M02 may add **expand-only, reversible where practical** PostgreSQL structures needed for durable control-plane state, for example:
- workflow execution references;
- command/idempotency records;
- operation fingerprints;
- durable inbox/outbox/event-delivery records where required;
- callback deduplication/reconciliation records;
- execution projections/attempt metadata not already represented by M01;
- indexes/uniqueness constraints supporting the above.

Rules:
- do not copy Temporal event history into PostgreSQL;
- do not make provider-specific payloads canonical application state;
- preserve M01 stable external IDs;
- no destructive rewrite of M01 canonical records;
- every migration gets upgrade + downgrade/recovery verification appropriate to its safety model.

## 6. Security / rights / cost impact

### Security
- no provider secrets are required;
- API and worker settings must fail closed on missing/invalid configuration;
- workflow payloads carry stable references rather than raw secrets/large media;
- fake webhook verification must establish the interface for later signed callbacks without pretending a real provider signature scheme exists;
- request/idempotency keys are bounded/validated and must not become an injection/storage-abuse surface;
- structured logs must avoid secrets and large/sensitive payload dumps;
- Temporal workflow sandbox remains enabled by default;
- direct workflow side effects/network/DB/filesystem/process calls are prohibited;
- current dependency/container advisories must be checked before pinning implementation versions.

### Rights
No new media rights decision is introduced. Existing fail-closed Rights behavior remains unchanged.

### Cost
- no paid AI/provider generation;
- fake/synthetic providers only;
- local/CI Temporal infrastructure should use free/local tooling where practical;
- no autonomous spend behavior.

## 7. Tests / verification

M02 cannot be marked complete from unit tests alone.

Required permanent gates include, as applicable:
- Ruff;
- strict mypy;
- existing M01 domain/persistence tests remain green;
- FastAPI/OpenAPI contract tests;
- settings/config fail-closed tests;
- API idempotency tests;
- PostgreSQL migration/constraint/transaction tests;
- Temporal workflow/activity integration tests;
- deterministic sandbox tests;
- retained-history replay tests;
- Activity timeout/retry/cancellation tests;
- signal/update/manual-wait tests;
- callback duplicate/out-of-order tests;
- DB↔Temporal failure-window/idempotency tests;
- worker restart recovery;
- API restart independence;
- synthetic 100-shot fan-out/join acceptance;
- assertion that completed work/terminal side effects are not duplicated.

CI evidence must use pinned test tooling and identify the tested Python/Temporal/FastAPI versions.

## 8. Rollback / recovery

Rollback strategy:
- code/workflow changes through normal PR/revert;
- additive M02 DB migrations reversible where safe;
- no destructive M01 data rewrite;
- retain representative workflow histories so code rollback/forward replay compatibility can be evaluated;
- do not deploy incompatible workflow-code changes without a Temporal versioning/change strategy;
- in-progress synthetic/dev workflows may be terminated/reset only inside test/dev evidence procedures;
- external side effects in M02 are fake, limiting irreversible rollback risk.

If a workflow-code change is non-deterministic against retained histories, CI must fail rather than silently accepting it.

## 9. Explicitly out of scope

M02 approval would **not** authorize:
- real Google/Runway/Pika/Kling/Hailuo/Luma or other AI provider integration;
- provider production credentials;
- paid/free-credit generation routing execution;
- object-storage/media upload pipeline (M03);
- Character Library implementation (M04);
- content intelligence/pgvector memory (M05);
- production audio/video generation (M06+);
- FFmpeg production assembly;
- full Next.js product UI;
- full authentication/RBAC/workspaces;
- billing/entitlements;
- social publishing;
- autonomous spend;
- production Temporal cluster provisioning/HA/DR;
- production deployment/public launch;
- M03+ executable development.

## Repository-governance preflight risk

Current GitHub API evidence shows `main` is not branch-protected and has no required status-check enforcement.

M02 implementation should preserve PR-only discipline and, if repository permissions allow, branch-protection/required-check hardening should be handled as an explicitly reviewed repository-governance change. It must not be silently changed under a generic planning instruction.

This risk does not block presenting the M02 development brief, but it should be resolved early in the approved M02 execution window or explicitly accepted as a temporary governance exception.

## Current dependency revalidation snapshot

Planning evidence observed on 2026-08-29:
- FastAPI latest stable observed: `0.141.1`;
- Temporal Python SDK latest stable observed: `1.30.0`;
- Temporal CLI latest stable observed: `1.8.1`;
- Temporal Server latest stable observed: `1.31.2`.

These are **not yet executable dependency pins**. Revalidate once more immediately before changing dependency/runtime files.

## 10. Consent request

M02 is planning-ready, but executable work is still blocked.

To authorize only the scope above, the operator can explicitly state:

**`Milestone 2 development approve — start.`**

Any generic `continue`, `next`, `resume`, `audit`, or planning instruction remains non-authorizing.