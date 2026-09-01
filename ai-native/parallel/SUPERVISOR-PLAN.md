# AI-Native Supervisor Parallel Development Plan

## Purpose

This is the canonical human-readable plan for Supervisor-led multi-agent development. It binds module branches, agent lanes, dependency state, completion signals, review order, synchronization behavior, and merge strategy.

The Supervisor is the agent operating the main repository/integration lane. The Supervisor is the only normal authority that reviews and promotes incoming agent branches to `main`.

This plan supplements `MULTI-AGENT-PROTOCOL.md`, `INTEGRATION-PROTOCOL.md`, `ACTIVE-WORK.yaml`, `DEPENDENCY-GRAPH.yaml`, `MIGRATION-REGISTRY.yaml`, and the repository development consent gate.

## Mandatory branch-bootstrap-first rule

When a Supervisor orchestration request requires multiple parallel module agents, the Supervisor's first repository action is to create the dedicated branch for every intended parallel module lane, including its own module branch, before documenting assignments or starting implementation.

Branch creation does not grant executable development permission. A branch whose dependencies or consent are not ready remains planning/contract-only until the applicable gate becomes satisfied.

## Current branch matrix

| Lane | Assigned agent role | Branch | Module / scope | Current execution state | Promotion strategy |
| --- | --- | --- | --- | --- | --- |
| Supervisor | `supervisor-agent` | `supervisor/m03-wp7-retention` | M03-WP7 retention/archive/delete/export primitives | executable work authorized under existing M03 scope; instruction/main sync required before promotion | highest current feature priority; promote before M03-WP8 |
| Acceptance | `acceptance-agent` | `agent/m03-wp8-acceptance` | M03-WP8 end-to-end acceptance, recovery, lineage, delivery/lifecycle verification | planning/test-matrix only until WP7 is landed | promote after WP7, then close M03 if all acceptance gates pass |
| Character | `character-agent` | `agent/m04-character-library` | M04 Character and Entity Library | planning/contract preparation only until milestone entry and consent gates allow executable work | contract-owner work lands before dependent M05/M07/M08 consumers |
| Content | `content-agent` | `agent/m05-content-memory` | M05 Content Intelligence and Memory | planning/contract preparation only until entry/consent gates | promote after required character/public contracts are stable; may run independently from audio where dependency graph allows |
| Audio | `audio-agent` | `agent/m06-audio-production` | M06 provider-neutral audio production | planning/contract preparation only until entry/consent gates | contract foundation may promote independently once eligible; runtime waits on required contracts |
| Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | M07 storyboard/hierarchy/timeline engine | planning-only until required Character/Content/Audio contracts are stable | ordered after required upstream contracts |
| Provider | `provider-agent` | `agent/m08-video-provider-router` | M08 hybrid image/video provider router | planning-only until Character/Timeline/provider capability boundaries are ready | ordered after relevant M04/M07 contracts; adapters may fan out later |
| QA / Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | adversarial tests, security, races, recovery, compatibility | may audit immediately; writes require claimed QA/test paths and must not collide with feature branch ownership | independent QA-only PRs may promote at any safe point; feature-coupled findings return to owning branch |

## Current merge order

The default merge order is dependency-driven, not simply numeric:

1. `supervisor/m03-wp7-retention`
2. `agent/m03-wp8-acceptance`
3. M03 close/checkpoint reconciliation
4. M04 Character/Entity public contract foundation
5. M05 Content/Memory and M06 Audio contract/runtime slices when independently ready
6. M07 Storyboard/Timeline after required upstream contracts land
7. M08 Provider Router after relevant Character/Timeline contracts land
8. Later milestones follow `DEPENDENCY-GRAPH.yaml`, not a hard-coded serial queue

The QA/Security lane is continuous and may submit independent test/governance PRs whenever its write set is conflict-free.

If a branch introduces a contract required by another branch, the contract-owner branch promotes first. If a new dependency appears, `DEPENDENCY-GRAPH.yaml` and affected task instructions are updated before further work.

## Completion signal

Every agent, including the Supervisor, must use the exact completion announcement when its assigned submission is ready for Supervisor review:

> **Work Done and Submitted**

The signal means:
- the bounded assigned scope is complete on the agent branch;
- required scoped checks were run or explicitly reported as unavailable;
- the branch/PR is ready for Supervisor review;
- remaining known risks are documented;
- the agent stops changing the submitted head unless the Supervisor requests fixes or a main-sync update.

The phrase does not itself mean the work is merged or production-ready.

## Supervisor interrupt and review behavior

The Supervisor also works on its own module branch. When another agent submits **Work Done and Submitted**:

1. Supervisor records a pause checkpoint for its own current work.
2. Supervisor switches to review/integration mode.
3. Supervisor verifies scope, ownership, dependency state, migration reservations, shared-file requests, current-main relation, tests, security/data implications, and PR diff.
4. If changes are rejected, Supervisor returns precise fixes and does not merge.
5. If approved, Supervisor synchronizes the candidate with current `main` when required, obtains exact-head promotion CI, and merges with an expected-head guard where supported.
6. Supervisor records the merge in canonical coordination state.
7. Supervisor emits a repository-wide synchronization broadcast.
8. Supervisor restores its saved checkpoint and resumes its own module work only after the integration event is recorded.

A review interruption never permits the Supervisor to discard uncommitted conceptual state; the pause checkpoint must identify branch, head, current subtask, files in progress, and exact next action.

## Mandatory post-merge broadcast

After each Supervisor merge, the canonical alert text is:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**

The Supervisor records the alert in `SUPERVISOR-BROADCASTS.yaml` with:
- monotonically increasing broadcast sequence;
- merged PR/branch;
- new `main` SHA;
- affected/required recipient branches;
- contract/migration/shared-file changes;
- whether resynchronization is mandatory or advisory.

The alert is repository state, not only conversational text, so another agent or a replacement agent can recover it without chat history.

## Agent response to merge alerts

Before continuing after a new mandatory broadcast, every affected agent must:

1. stop implementation at a safe checkpoint;
2. fetch/merge/rebase current `main` according to repository policy;
3. resolve textual and semantic conflicts;
4. rerun the working-instruction audit;
5. verify consumed contracts, migration parent/reservation, shared-file rules, and dependencies remain valid;
6. update `last_synced_main_sha` and `last_acknowledged_broadcast` in its task state;
7. rerun relevant scoped checks when the merge affects its consumers;
8. only then resume its assigned task.

An agent with an unacknowledged mandatory broadcast is `sync-required` and must not announce completion or seek promotion.

## Review queue rules

Supervisor review priority:

1. security/data-loss/blocking fixes;
2. contract-owner PRs that unblock multiple branches;
3. current critical-path work;
4. independent small PRs;
5. future planning/documentation.

Never merge merely because an agent finished first. Dependency safety, contract compatibility, current-main synchronization, and exact-head verification remain authoritative.

## Current Supervisor assignment

The Supervisor's own module is M03-WP7 on `supervisor/m03-wp7-retention`, preserving the implementation already present on the prior WP7 branch. Before that branch can be promoted it must incorporate/reconcile the Supervisor governance changes now on `main` and complete the mandatory working-instruction audit.

## Branch retirement

After a branch is merged:
- mark its task complete/landed;
- release migration reservations or mark them landed;
- update dependencies/contracts/checkpoints;
- emit the merge broadcast;
- retire/delete the branch when repository policy permits and no recovery need remains.

Long-lived module names may be reused as planning concepts, but each executable work package should normally use a bounded task branch so stale submissions cannot silently absorb unrelated future work.
