# M02 Current Stack Revalidation — 2026-08-29

Status: `PLANNING_EVIDENCE_ONLY`

This document refreshes mutable implementation facts for M02. It does not add dependencies, change CI, enable infrastructure, or authorize executable development.

## Scope

M02 is the durable workflow/control-plane milestone. The existing architectural decision remains:

- Python 3.12+ backend;
- FastAPI for the HTTP/OpenAPI control plane;
- Temporal for durable multi-step workflows;
- PostgreSQL for operational canonical state;
- provider-neutral fake activities during M02;
- SSE initially for progress streaming;
- no real AI provider execution in M02.

Canonical milestone plan:
`docs/milestones/M02/PLAN.md`

## Current upstream facts checked on 2026-08-29

### Temporal Python SDK

Current public GitHub release observed:
- `temporalio/sdk-python` — `1.30.0`

Relevant current SDK behavior:
- workflow code must remain deterministic;
- Python workflows run in the workflow sandbox by default;
- external side effects belong in Activities;
- workflow history can be replayed with `Replayer` to detect non-determinism/regression;
- workflow sandbox bypass is possible but explicitly discouraged as a normal design;
- current SDK/core behavior requires an Activity close timeout to be configured.

M02 implication:
- keep workflow modules minimal and deterministic;
- keep Pydantic/domain imports explicitly safe/passthrough where justified;
- never perform network, file, process, environment, random or database side effects directly inside workflow code;
- require explicit Activity timeout policy in the workflow conventions;
- make replay compatibility a permanent CI gate before changing workflow code.

Sources checked:
- https://github.com/temporalio/sdk-python
- https://github.com/temporalio/sdk-python/releases
- https://docs.temporal.io/

### Temporal Server

Current public GitHub release observed:
- `temporalio/temporal` — `v1.31.2`

M02 is not a production Temporal deployment milestone. For development/CI, prefer a pinned local development server/CLI path rather than designing production cluster topology here.

M02 implication:
- do not use floating `latest` tags in durable CI evidence;
- pin an exact tested Temporal CLI/server version or digest when implementation starts;
- run dependency/container vulnerability checks at implementation time;
- production Temporal Cloud/self-host topology, HA, scaling and DR remain later operations scope unless a narrow M02 test dependency requires configuration.

Sources checked:
- https://github.com/temporalio/temporal
- https://github.com/temporalio/temporal/releases

### Temporal CLI

Current public GitHub release observed:
- `temporalio/cli` — `v1.8.1`

The current CLI includes `temporal server start-dev` for local development. Historical `tctl` is deprecated/end-of-support and must not be introduced into new M02 tooling.

M02 implication:
- use the current Temporal CLI, not `tctl`;
- exact version must be pinned in implementation/CI;
- persistent/restart acceptance must not rely only on an in-memory test that cannot prove process-restart recovery.

Sources checked:
- https://github.com/temporalio/cli
- https://github.com/temporalio/cli/releases

### FastAPI

Current public GitHub release observed:
- `fastapi/fastapi` — `0.141.1`

Current official FastAPI documentation confirms:
- application lifespan hooks are appropriate for app-scoped resource setup/cleanup;
- dependency injection remains the request-resource boundary;
- SSE is available in current FastAPI releases;
- `BackgroundTasks` is suitable for small post-response work but is not a durable distributed workflow engine; heavy work that does not need to share the process should be delegated to a separate worker/tool.

M02 implication:
- FastAPI starts/inspects/signals Temporal work; it does not own durable execution;
- do not implement long media/job execution with `BackgroundTasks`;
- use lifespan-managed clients/pools where appropriate;
- use versioned REST/OpenAPI for control APIs;
- use SSE first for progress unless a concrete bidirectional WebSocket need appears.

Sources checked:
- https://fastapi.tiangolo.com/advanced/events/
- https://fastapi.tiangolo.com/tutorial/background-tasks/
- https://fastapi.tiangolo.com/tutorial/dependencies/
- https://github.com/fastapi/fastapi/releases

## Proposed implementation-time dependency policy

Do not hard-code dependency versions from this planning document into runtime files before consent.

At M02 implementation start:
1. re-check latest stable FastAPI, Temporal Python SDK, Temporal CLI and compatible Temporal Server behavior;
2. choose exact compatible pins/ranges according to repository dependency policy;
3. record the chosen versions in the M02 executable PR;
4. pin CI Temporal tooling exactly rather than using floating tags;
5. run vulnerability/advisory checks;
6. reject a version upgrade if replay/determinism, Python 3.12 compatibility or existing M01 contracts regress.

Current planning candidates, not executable pins:
- FastAPI: current stable `0.141.1` line;
- Temporal Python SDK: current stable `1.30.0` line;
- Temporal CLI: current stable `1.8.1` line;
- Temporal Server/dev-server compatibility target: current `1.31.2` line.

## Architecture decisions reaffirmed

### FastAPI is a control plane, not the durable engine

HTTP request lifecycle and background-task execution must never be treated as authoritative workflow durability.

### PostgreSQL owns application/job projection; Temporal owns workflow execution history

Do not duplicate Temporal history inside PostgreSQL. Store canonical application state plus workflow/run references, idempotency records, projections, audit/event/outbox data required by the product.

### External side effects are Activities

Provider calls, callbacks, database mutations requiring side-effect boundaries, filesystem/media calls and future external integrations belong outside deterministic workflow code.

### Durable idempotency is multi-layered

M02 must combine:
- stable workflow IDs;
- request/idempotency keys;
- operation fingerprints;
- PostgreSQL uniqueness/concurrency constraints;
- activity-side idempotency/attempt semantics;
- callback deduplication;
- workflow replay compatibility.

Temporal retries alone are not sufficient to guarantee no duplicated external side effects.

### Long workflow history must have an explicit continuation policy

M02 should define a safe Continue-As-New/history-growth policy before long-form milestones depend on the control plane. The initial 100-shot acceptance should prove the architecture without prematurely optimizing for three-hour real generation.

### Replay testing is mandatory

Workflow code changes require replay tests against retained representative histories. A green ordinary unit test does not substitute for replay compatibility.

## Security and cost position

M02 uses fake/synthetic providers by default and requires no production AI provider credentials or paid generation.

Workflow payloads must not contain:
- provider secrets;
- raw large media blobs;
- unnecessary sensitive user data.

Use stable IDs/references to canonical PostgreSQL/object-storage records instead.

## Revalidation verdict

`PASS — EXISTING FASTAPI + TEMPORAL ARCHITECTURE REMAINS VALID`

No current upstream fact found requires replacing the M02 architecture.

Implementation still requires explicit M02 development consent.