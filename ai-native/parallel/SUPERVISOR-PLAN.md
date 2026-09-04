# AI-Native Supervisor Parallel Development Plan

## Purpose

This is the canonical human-readable plan for Supervisor-led multi-agent development. It binds module branches, agent lanes, slot occupancy, dependency state, write ownership, completion signals, review order, synchronization behavior, onboarding, and merge strategy.

The Supervisor is the only normal authority that assigns incoming agents, reviews submitted work, changes shared coordination state, and promotes incoming agent branches to `main`.

This plan supplements `MULTI-AGENT-PROTOCOL.md`, `INTEGRATION-PROTOCOL.md`, `ACTIVE-WORK.yaml`, `AGENT-SLOTS.json`, `DEPENDENCY-GRAPH.yaml`, `MIGRATION-REGISTRY.yaml`, `MODULE-OWNERSHIP.yaml`, `SHARED-FILES.yaml`, and the repository development consent gate.

## Mandatory branch-bootstrap-first rule

When a Supervisor orchestration request requires multiple parallel module agents, the Supervisor creates the dedicated branch for every intended module lane before implementation begins. Branch creation never grants executable development permission; dependency and consent gates remain authoritative.

Each new bounded executable submission uses a branch based on current `main`. A branch whose previous submission has merged is retired or replaced before the next bounded executable slice begins.

## New Agent Onboarding — mandatory

Every new agent begins from current `main`. A new agent may not start from a feature branch, stale checkpoint branch, another agent's branch, or chat-only state.

Before the new agent writes any project file:

1. the new agent starts from current `main` and performs the working-instruction audit;
2. the Supervisor loads this plan and `AGENT-SLOTS.json`;
3. the Supervisor checks for a slot whose `status` is `open` and `accepts_new_agent` is `true`;
4. when a valid slot exists, the Supervisor assigns that exact module/branch and records agent identity, occupancy, start status, and `ACTIVE-WORK.yaml` state before work starts;
5. only after the assignment is recorded may the agent switch from `main` to the assigned branch and work within its claimed paths.

A new agent may never self-select, replace an occupied agent, or claim a branch merely because it exists.

If there is no eligible open slot, the Supervisor stops onboarding immediately and responds exactly:

> **Go Home Come Back Next Time**

That response means no module, branch, research, planning, code, documentation, or repository mutation is assigned to the rejected arrival.

`AGENT-SLOTS.json` is the machine-readable occupancy authority. This document is the human-readable assignment/merge plan. Both must remain synchronized.

### Current onboarding capacity

All defined module slots are occupied. An additional new agent therefore receives **Go Home Come Back Next Time** until the Supervisor intentionally opens/releases a slot in canonical repository state.

## Current branch matrix

| Lane | Slot | Assigned agent role | Branch | Module / scope | Current execution state | Promotion strategy |
| --- | --- | --- | --- | --- | --- | --- |
| Supervisor | occupied / not new-agent assignable | `supervisor-agent` | `supervisor/m03-wp7-temp-cleanup` | M03-WP7 bounded temporary upload cleanup | executable cleanup slice on current `main@6e892e3417788d2fc9a1ea0a91cfc5d44ce47be6` | finish terminal abandoned upload/quarantine cleanup before export staging |
| Acceptance | occupied | `acceptance-agent` | `agent/m03-wp8-acceptance` | M03-WP8 end-to-end acceptance | sync-required; planning-only until all WP7 exit criteria land | synchronize broadcast 6 before any promotion, then promote after WP7 |
| Character | occupied | `character-agent` | `agent/m04-character-library` | M04 Character and Entity Library | sync-required planning/contract preparation only | synchronize before any promotion; executable work waits for entry + consent gates |
| Content | occupied | `content-agent` | `agent/m05-content-memory` | M05 Content Intelligence and Memory | sync-required planning/contract preparation only | synchronize before any promotion; then follow M04 contracts |
| Audio | occupied | `audio-agent` | `agent/m06-audio-production` | M06 provider-neutral audio production | sync-required planning/contract preparation only | synchronize before any promotion; executable work waits for entry + consent gates |
| Timeline | occupied | `timeline-agent` | `agent/m07-storyboard-timeline` | M07 storyboard/hierarchy/timeline engine | sync-required planning-only | synchronize before any promotion; ordered after Character/Content/Audio contracts |
| Provider | occupied | `provider-agent` | `agent/m08-video-provider-router` | M08 hybrid image/video provider router | sync-required planning-only | synchronize before any promotion; ordered after Character/Timeline contracts |
| QA / Security | occupied | `qa-security-agent` | `agent/cross-cutting-qa-security` | adversarial QA/security planning and audits | sync-required audit/planning | synchronize before any promotion; independent conflict-free QA work may resume afterward |

## Write-claim isolation

Parallel work is permitted only when authoritative `writes` scopes in `ACTIVE-WORK.yaml` do not overlap.

Planning lanes use dedicated milestone directories and exact per-task checkpoint files:
- M04 -> `docs/milestones/M04/**` + `ai-native/parallel/checkpoints/M04-PARALLEL-LANE.md`
- M05 -> `docs/milestones/M05/**` + `ai-native/parallel/checkpoints/M05-PARALLEL-LANE.md`
- M06 -> `docs/milestones/M06/**` + `ai-native/parallel/checkpoints/M06-PARALLEL-LANE.md`
- M07 -> `docs/milestones/M07/**` + `ai-native/parallel/checkpoints/M07-PARALLEL-LANE.md`
- M08 -> `docs/milestones/M08/**` + `ai-native/parallel/checkpoints/M08-PARALLEL-LANE.md`
- QA -> `docs/qa/**` + `ai-native/parallel/checkpoints/CROSS-CUTTING-QA.md`

A `future_executable_writes` entry is informational only. It does not reserve or authorize those paths until the Supervisor explicitly promotes the task to executable state and rechecks collisions.

The active Supervisor write set for this bounded slice is limited to:
- `packages/python-core/src/lullabies_core/temporary_cleanup.py`;
- `packages/python-core/src/lullabies_core/persistence/temporary_cleanup.py`;
- `packages/python-core/tests/test_temporary_cleanup.py`.

Coordination files are maintained only by the Supervisor to keep branch/slot/broadcast authority synchronized and are not shared implementation lanes.

## Current merge order

Default merge order is dependency-driven:

1. `supervisor/m03-wp7-temp-cleanup`
2. next bounded M03-WP7 export-staging branch
3. next bounded M03-WP7 vector/index cleanup branch
4. `agent/m03-wp8-acceptance` after synchronization and WP7 completion
5. M03 close/checkpoint reconciliation
6. M04 Character/Entity public contract foundation
7. M05 Content/Memory and M06 Audio when independently ready
8. M07 Storyboard/Timeline after required upstream contracts land
9. M08 Provider Router after relevant Character/Timeline contracts land
10. Later milestones follow `DEPENDENCY-GRAPH.yaml`

The QA/Security lane is continuous but is currently sync-required by broadcast 6 and cannot seek promotion until it records synchronization.

If a new dependency appears, `DEPENDENCY-GRAPH.yaml` and affected task instructions are updated before further work. Contract-owner branches promote before consumers that require those contracts.

## Completion signal

Every agent, including the Supervisor, uses the exact announcement when its bounded submission is ready for Supervisor review:

> **Work Done and Submitted**

The signal means the bounded assigned scope is complete on the agent branch, scoped checks were run or reported unavailable, known risks are documented, and the branch/PR is frozen for Supervisor review unless fixes/synchronization are requested. It does not mean merged or production-ready.

## Supervisor interrupt and review behavior

When an agent submits **Work Done and Submitted**:

1. Supervisor records a pause checkpoint for its own current work.
2. Supervisor switches to review/integration mode.
3. Supervisor verifies exact head, scope, ownership, dependency state, migration reservations, shared-file requests, current-main relation, tests, security/data implications, consent, and PR diff.
4. Rejected work returns with precise fixes and is not merged.
5. Approved work synchronizes with current `main` when required and obtains exact-head promotion CI.
6. Supervisor merges with an expected-head guard where supported.
7. Supervisor records the merge and emits the synchronization broadcast.
8. Supervisor resumes its saved work only after coordination state is reconciled.

## Mandatory post-merge broadcast

After every promotion merge that active agents must observe, emit exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**

`SUPERVISOR-BROADCASTS.yaml` records sequence, merged PR/branch, submitted head, new `main` SHA, changed contracts/migrations/shared areas, recipients, and mandatory/advisory classification.

## Agent response to merge alerts

Before continuing after a mandatory broadcast, every affected agent must:

1. stop at a safe checkpoint;
2. synchronize current `main`;
3. resolve textual and semantic conflicts;
4. rerun the working-instruction audit;
5. revalidate contracts, dependencies, migration state, write ownership, and consent;
6. record `last_synced_main_sha` and `last_acknowledged_broadcast`;
7. rerun relevant scoped checks when the merge affects its consumers;
8. resume only after the sync is recorded.

An unacknowledged mandatory broadcast makes the task `sync-required` and blocks submission/promotion.

## Review queue rules

Supervisor priority:

1. security/data-loss/blocking fixes;
2. contract-owner work that unblocks multiple agents;
3. current critical path;
4. independent small changes;
5. future planning/documentation.

Completion order never overrides dependency safety, contract compatibility, current-main synchronization, or exact-head verification.

## Current Supervisor assignment

PR #57 merged the approved deletion-propagation execution slice at `main@6e892e3417788d2fc9a1ea0a91cfc5d44ce47be6`. The completed branch `supervisor/m03-wp7-deletion-execution` is retired for new executable work.

The Supervisor now owns Issue #58 on `supervisor/m03-wp7-temp-cleanup`, created from that exact current main. This slice may clean only `ABORTED` or `EXPIRED` upload/quarantine state after an explicit grace cutoff. It must fail closed when canonical storage metadata exists for either the upload storage-object identity or exact physical location, must preserve project/key boundaries, must not touch `OPEN`, `UPLOADING`, or `COMPLETED` sessions, and must treat missing temporary backend state as idempotent cleanup success. Incomplete S3 multipart uploads are aborted before orphan quarantine object deletion when an UploadId exists.

No migration, export staging, vector/index cleanup, provider integration, production credential change, or cost-bearing scope is authorized in this slice. Remaining WP7 scope after it lands is export staging, vector/index cleanup hooks, and final WP7 acceptance/promotion.

Broadcast sequence 6 is current. The Supervisor temp-cleanup branch is synchronized to sequence 6/current main; all other occupied planning/QA lanes listed in `ACTIVE-WORK.yaml` are sync-required and cannot seek promotion until they acknowledge sequence 6.

Migration `20260901_0015` is landed history and is no longer an active reservation.

## Branch retirement and slot release

After a branch is merged:
- mark the landed slice and release/land any migration reservation;
- update dependencies/contracts/checkpoints;
- emit the merge broadcast;
- decide whether the module slot remains occupied for a next bounded branch or becomes `open`;
- if opened, clear `assigned_agent` before a future agent can claim it;
- retire/delete the completed task branch when repository policy permits.

Long-lived module names may remain planning concepts, but executable submissions should use bounded task branches so stale heads cannot absorb unrelated future work.
