# AI-Native Supervisor Parallel Development Plan

## Purpose

This is the canonical human-readable plan for Supervisor-led multi-agent development. It binds module branches, agent lanes, slot occupancy, dependency state, completion signals, review order, synchronization behavior, onboarding and merge strategy.

The Supervisor is the agent operating the main integration lane and is the normal authority for agent assignment, submission review and promotion to `main`.

Canonical machine state lives beside this file in `AGENT-SLOTS.json`, `ACTIVE-WORK.yaml`, `DEPENDENCY-GRAPH.yaml`, `MIGRATION-REGISTRY.yaml`, `MERGE-QUEUE.yaml`, `SUPERVISOR-STATE.yaml`, `SUPERVISOR-BROADCASTS.yaml`, `SHARED-FILES.yaml` and `CONTRACT-REGISTRY.yaml`.

## Mandatory branch-bootstrap-first rule

When a Supervisor orchestration request requires parallel module agents, the Supervisor's first repository action is to create a dedicated branch for every intended module lane, including its own lane, before documenting assignments or starting implementation.

Branch creation never grants development consent. Blocked/future lanes remain planning-only until dependency and consent gates are satisfied.

## New Agent Onboarding

Every new agent starts from current `main` and performs the working-instruction audit before assignment.

The Supervisor then checks `AGENT-SLOTS.json`:

1. if a slot is `open` and `accepts_new_agent: true`, assign that exact module/branch;
2. update slot, plan and active-work state before the agent writes anything;
3. only after the assignment is persisted may the agent switch to its branch and work within its claim;
4. an agent may never self-assign, replace an occupied agent or steal an existing branch.

If no eligible slot exists, stop onboarding and respond exactly:

> **Go Home Come Back Next Time**

No module, branch, planning, research, docs or code work is assigned to that rejected arrival.

## Current branch matrix

| Lane | Agent | Branch | Scope | Current state |
| --- | --- | --- | --- | --- |
| Supervisor | `supervisor-agent` | `supervisor/m03-wp7-retention-continuation` | remaining M03-WP7 retention/delete/export work | active after PR #51 lifecycle foundation |
| Acceptance | `acceptance-agent` | `agent/m03-wp8-acceptance` | M03-WP8 end-to-end acceptance | planning-only; waits for full WP7 completion |
| Character | `character-agent` | `agent/m04-character-library` | M04 Character/Entity | planning-only |
| Content | `content-agent` | `agent/m05-content-memory` | M05 Content/Memory | planning-only |
| Audio | `audio-agent` | `agent/m06-audio-production` | M06 Audio | planning-only |
| Timeline | `timeline-agent` | `agent/m07-storyboard-timeline` | M07 Storyboard/Timeline | planning-only |
| Provider | `provider-agent` | `agent/m08-video-provider-router` | M08 Provider Router | planning-only |
| QA/Security | `qa-security-agent` | `agent/cross-cutting-qa-security` | adversarial QA/security planning | audit/planning ready |

All defined slots are currently occupied. A ninth arrival therefore receives **Go Home Come Back Next Time** unless the Supervisor first releases/opens a slot in canonical state.

## Conflict-free write ownership

An agent may read the whole repository but may write only paths listed in its authoritative `ACTIVE-WORK.yaml` `writes` claim.

Rules:
- two active tasks may not have overlapping authoritative write claims;
- planning agents use dedicated milestone directories plus one exact per-task checkpoint file;
- broad shared checkpoint globs such as `ai-native/checkpoints/**` are forbidden for parallel tasks;
- `future_executable_writes` are planning metadata only and confer no current write authority;
- shared files and `shared_requests` remain Supervisor/integration-owned until explicitly granted;
- Repository Governance must fail when authoritative active write claims overlap.

## Current M03 state and merge order

PR #51 landed the durable asset lifecycle foundation at `8ed99a094cb443b789929d71c468464e2e0bb72a`. It does **not** complete WP7.

Current critical path:

1. `supervisor/m03-wp7-retention-continuation` completes deletion propagation, lifecycle delivery denial, bounded temp cleanup, export staging, vector/index cleanup hooks and WP7 acceptance;
2. promote full M03-WP7 only after exact-head required CI;
3. `agent/m03-wp8-acceptance` executes final M03 acceptance;
4. close M03;
5. promote M04/M06 contract foundations when their entry/consent gates allow;
6. M05, M07 and M08 follow `DEPENDENCY-GRAPH.yaml` contract dependencies rather than numeric serialization.

QA/Security may submit independent conflict-free audit/governance work at any safe point.

## Completion signal

Every agent, including the Supervisor, announces exactly:

> **Work Done and Submitted**

This means the bounded branch submission is ready for Supervisor review. It does not mean merged or production-ready. The submitted head is treated as immutable unless fixes or synchronization are requested.

## Supervisor interrupt/review behavior

When an agent submits **Work Done and Submitted**:

1. Supervisor records/checkpoints its own current work;
2. pauses feature implementation and enters review mode;
3. validates scope, ownership, write claims, dependencies, consent, migrations, contracts, shared-file requests, current-main relation and tests;
4. requests precise fixes if rejected;
5. if approved, synchronizes with current `main` when needed and requires exact-head promotion CI;
6. merges with an expected-head guard;
7. reconciles migration/task/slot/queue state;
8. emits the mandatory merge broadcast;
9. only after coordination state is durable does Supervisor resume its saved work.

## Mandatory post-merge broadcast

After a promotion merge that active agents must observe, Supervisor records and sends exactly:

> **New changes have been merged — please merge these changes into your branch first, then resume your own work.**

`SUPERVISOR-BROADCASTS.yaml` records monotonically increasing sequence, merged PR/branch/head/main SHA, changed contracts/migrations/shared areas, recipients and acknowledgement state.

A branch with an unacknowledged mandatory broadcast is `sync-required` and cannot submit or promote.

## Agent response to merge alerts

Before resuming after a mandatory alert, each affected agent must:

1. synchronize current `main` into its branch;
2. resolve textual and semantic conflicts;
3. rerun working-instruction audit;
4. revalidate dependencies, contracts, migration reservation/parent and write ownership;
5. record `last_synced_main_sha` and `last_acknowledged_broadcast`;
6. rerun affected scoped checks;
7. only then resume its assigned work.

## Migration ownership

Migration revisions are reserved by the Supervisor before creation. Active reservations must be unique. A landed revision moves out of active reservations into landed history and must not continue blocking the next revision allocation.

Migration `20260901_0015` landed with PR #51 and is now historical, not reserved.

## Review queue priority

1. security/data-loss blocker;
2. contract-owner change that unblocks multiple agents;
3. current critical path;
4. independent small change;
5. future planning.

Finishing first never overrides dependencies, ownership, security or current-main synchronization.

## Branch retirement and continuation

After a bounded submission merges:
- retire/replace the completed submission branch before starting the next bounded executable slice;
- mark migrations landed/released;
- update dependencies/contracts/checkpoints;
- emit the merge broadcast;
- choose whether its slot stays occupied for a named continuation task or becomes open;
- if opened, clear `assigned_agent` before another agent may use it.

The PR #51 branch `supervisor/m03-wp7-retention` is a completed submission branch. Remaining WP7 work continues on fresh current-main branch `supervisor/m03-wp7-retention-continuation`.

## Live GitHub main-protection boundary

Repository rules require PR-only exact-head promotion discipline, but the latest live GitHub read reports `main` as unprotected. Repository governance mitigates this operationally through Supervisor-only promotion, exact-head merge guards, required CI policy, write-claim validation and sensitive-path CODEOWNERS. Actual branch/ruleset protection must be enabled in GitHub repository settings; repository files alone cannot make an unprotected GitHub branch protected.
