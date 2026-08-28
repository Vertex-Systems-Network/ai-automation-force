# M02 — Durable Workflow Control Plane

## Objective

Build the FastAPI control plane and Temporal durable-workflow foundation so long-running AI/media jobs survive retries, provider waits, human approvals and process restarts without duplicate side effects.

## Entry criteria

- P0 complete.
- M01 accepted.
- Explicit M02 consent.
- Temporal/FastAPI current versions revalidated.

## Dependencies

`M01 -> M02`

## Work packages

### M02-WP1 — FastAPI application/control scaffold
- app structure;
- config validation;
- health/readiness;
- request IDs;
- structured errors;
- OpenAPI generation;
- auth placeholder/internal dev identity only if auth milestone not implemented.

### M02-WP2 — Temporal foundation
- client/namespace configuration;
- worker bootstrap;
- task queues/resource classes;
- workflow/activity conventions;
- deterministic workflow rules;
- workflow IDs/run references persisted.

### M02-WP3 — Job and idempotency control
- canonical job lifecycle;
- client idempotency keys;
- operation fingerprint;
- leases/locks/version conflict;
- duplicate suppression;
- DB/outbox linkage.

### M02-WP4 — Retry/backoff/circuit/cancel
- normalized retry classes;
- bounded exponential backoff;
- circuit breakers;
- deadlines/timeouts;
- cancellation propagation;
- terminal/manual-action states.

### M02-WP5 — Human/approval waits
- workflow pause for approval;
- approval expiry/stale-version handling;
- budget/manual handoff waits;
- signals/updates;
- safe resume.

### M02-WP6 — External async callback pattern
Using fake provider:
- submit async job;
- poll;
- verified webhook callback;
- duplicate callback;
- provider timeout;
- status reconciliation.

### M02-WP7 — API job surface and progress
- create/inspect/cancel/retry job;
- workflow/project status;
- SSE initially for progress stream, WebSocket only if concrete need;
- pagination/history;
- normalized errors.

### M02-WP8 — Recovery/load acceptance
- synthetic 100-shot fan-out/join;
- kill workers/API and resume;
- duplicate events/callbacks;
- manual approval wait;
- no duplicate terminal assets/actions;
- Temporal replay tests.

## Expected modules/files

- `apps/api/`
- `apps/worker/`
- shared workflow/activity packages;
- `packages/python-core/` job/domain services;
- `tests/workflows/`, `tests/api/`;
- environment/Temporal configs.

## Data/migration impact

Adds workflow/job/idempotency/outbox/reference tables and indexes. No provider-specific generation payloads as canonical state.

## API/UI impact

Introduces internal/versioned REST/OpenAPI job/control APIs. No full web UI; basic developer/docs interface acceptable for verification.

## Security/cost/rights impact

- internal tool/service identity;
- no production external credentials required;
- fake providers default;
- idempotency protects cost/side effects;
- workflow payloads avoid secrets/private large media.

## Test/acceptance

- Temporal replay;
- restart recovery;
- duplicate callback/idempotency;
- cancellation;
- circuit breaker;
- 100-shot synthetic workflow;
- API schema/error tests;
- DB transaction/outbox behavior.

## Rollout/rollback

No customer production release yet. Workflow code version compatibility required even in staging fixtures. DB changes expand-compatible.

## Exit criteria

A synthetic 100-shot project can enqueue, fan out, pause, fail/retry, survive worker/API restarts and complete without duplicated completed work or side effects.

## Non-goals

- real AI providers;
- full assets/object storage;
- content intelligence;
- web product/auth/billing/social implementation.
