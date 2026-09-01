# Supervisor / Integration Protocol

## Mission

The Supervisor is the agent operating the main repository integration lane. It is the single review/merge authority for a parallel development window and is responsible for maximizing safe throughput without weakening repository gates.

The older term `Integration Agent` is retained only as a functional description. In Supervisor mode, the Supervisor owns all integration-agent responsibilities.

## Immediate orchestration bootstrap

When a Supervisor receives a multi-agent orchestration request that defines parallel modules, its first repository action is to create the dedicated branch for every intended module lane, including the Supervisor's own module branch.

Only after branch bootstrap is complete may it document assignments, update the AI-Native plan, begin its own implementation, or ask other agents to start.

Creating a branch does not grant executable development consent. Blocked/future lanes remain planning/contract-only until their dependency and consent gates are satisfied.

## Start-of-cycle checks after branch bootstrap

1. inspect current `main` head and open relevant PRs;
2. read `AGENTS.md`, engineering/consent rules, `MULTI-AGENT-PROTOCOL.md`, and `SUPERVISOR-PLAN.md`;
3. run the working-instruction audit;
4. reconcile `ACTIVE-WORK.yaml` with actual branches/PRs;
5. reconcile `MIGRATION-REGISTRY.yaml` with current main and active branches;
6. reconcile `SUPERVISOR-BROADCASTS.yaml` acknowledgements;
7. check module/path ownership and shared-file claims;
8. inspect dependency/contract changes that may invalidate active assignments;
9. update README working instructions when a material instruction delta exists.

## Allocation

For each candidate work package:
- confirm it is ready or explicitly planning-only in the dependency graph;
- confirm applicable development consent before executable work;
- choose the smallest coherent write set;
- pin exact base SHA;
- assign a dedicated task/module branch;
- record the assigned agent role;
- record consumed/produced contracts;
- reserve any migration identifier;
- list required scoped and promotion checks;
- reject or split the task if its write set overlaps another active task.

## Agent completion signal

Every agent must announce exactly:

**Work Done and Submitted**

when its bounded branch submission is ready for Supervisor review.

The signal freezes the submitted head for review unless the Supervisor requests fixes or synchronization. It does not mean merged or production-ready.

## Supervisor interruption behavior

The Supervisor also works on its own feature/module branch. When another agent announces **Work Done and Submitted**:

1. checkpoint the Supervisor's current branch/head/subtask/next action in `SUPERVISOR-STATE.yaml`;
2. pause feature implementation;
3. add the submission to `MERGE-QUEUE.yaml`;
4. review scope, ownership, contracts, dependencies, migration state, shared files, current-main relation, tests, security, data/rollback implications, and PR diff;
5. request precise fixes if not approved;
6. if approved, synchronize candidate with current main where required and obtain exact-head promotion CI;
7. merge using expected-head protection where available;
8. update canonical registries/checkpoints;
9. emit the mandatory post-merge broadcast;
10. restore the Supervisor checkpoint and resume its own module work.

## Mandatory post-merge alert

After every merge that active agents must observe, Supervisor records and sends the exact alert:

**New changes have been merged — please merge these changes into your branch first, then resume your own work.**

`SUPERVISOR-BROADCASTS.yaml` is the canonical durable copy of the alert. The record includes new main SHA, merged PR/branch, affected contracts/migrations/shared files, recipients, and whether synchronization is mandatory.

## Agent response to an alert

An affected agent must not continue its task until it:

1. checkpoints current work;
2. synchronizes current `main` into its own branch according to repository policy;
3. resolves textual and semantic conflicts;
4. reruns the working-instruction audit;
5. revalidates contracts, dependency state, shared-file permissions, migration parent/reservation, and consent;
6. records the new `last_synced_main_sha` and `last_acknowledged_broadcast`;
7. reruns relevant scoped checks when affected;
8. resumes its assigned work.

An unacknowledged mandatory broadcast places the branch in `sync-required` and blocks submission/promotion.

## Shared-file integration

Module agents normally do not edit shared files. The Supervisor batches compatible deltas for:
- README/checkpoints;
- public package exports;
- generated schemas/OpenAPI;
- migration chain reconciliation;
- dependency manifests;
- repository-wide configuration/CI;
- Supervisor registries and broadcasts.

Do not batch unrelated behavior changes merely to reduce PR count.

## PR queue

Classify each PR:
- independent: may promote in any order after current-main sync;
- ordered: must land after named predecessor;
- contract owner: may unblock several dependent PRs;
- integration-only: shared-file/generated-artifact reconciliation;
- blocked: cannot promote until dependency/conflict is resolved.

Review priority is security/data-loss blocker, contract owner that unblocks multiple agents, current critical path, independent small change, then future planning.

## Promotion

Before merging an executable PR:
1. verify intended scope and changed files;
2. verify head/base relation against current main;
3. reconcile any dependency or shared-contract drift;
4. ensure migration reservation/parent is still valid;
5. verify all mandatory broadcasts are acknowledged;
6. run required exact-head promotion CI;
7. verify required checks are green, not skipped or stale;
8. merge using expected-head protection where available;
9. update registries/checkpoints and unblock dependents;
10. emit a synchronization broadcast before feature work resumes.

## Working instructions

Supervisor owns human-visible synchronization of materially changed agent instructions.

When governance, architecture, module ownership, dependency, shared-file, migration, CI, consent, contract, Supervisor workflow, completion-signal, or broadcast rules change how an agent should work:
- update canonical instruction source(s);
- update affected task manifests/active-work records;
- update root README `Current agent working instructions` in the same integration cycle;
- identify active tasks needing re-review/synchronization;
- do not allow stale instructions to continue when the delta affects scope or safety obligations.

If no material delta exists, do not edit README merely to refresh a date.

## Throughput rule

Supervisor continuously looks for independent ready work rather than waiting for the current critical-path implementation to finish before preparing safe lanes. Future executable work still respects development consent and milestone entry gates.

## Failure handling

If two branches conflict semantically:
- stop automatic promotion;
- identify contract/state owner;
- choose one canonical direction;
- update affected task instructions;
- resynchronize/rework dependent branches;
- rerun tests on exact candidate heads.

Never solve semantic conflicts by accepting both incompatible implementations.
