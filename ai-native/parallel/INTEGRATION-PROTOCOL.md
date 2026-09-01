# Integration Agent Protocol

## Mission

The Integration Agent is the single coordination authority for a parallel development window. Its job is to maximize safe throughput without becoming a bottleneck or weakening repository gates.

## Start-of-cycle checks

Before allocating work:
1. inspect current `main` head and open relevant PRs;
2. read `AGENTS.md`, engineering/consent rules, and `MULTI-AGENT-PROTOCOL.md`;
3. run the working-instruction audit;
4. reconcile `ACTIVE-WORK.yaml` with actual branches/PRs;
5. reconcile `MIGRATION-REGISTRY.yaml` with current main and active branches;
6. check module/path ownership and shared-file claims;
7. inspect dependency/contract changes that may invalidate active assignments;
8. update the README working-instruction summary when a material instruction delta exists.

## Allocation

For each candidate work package:
- confirm it is ready in the dependency graph;
- confirm applicable development consent;
- choose the smallest coherent write set;
- pin exact base SHA;
- assign a task branch;
- record consumed/produced contracts;
- reserve any migration identifier;
- list required scoped and promotion checks;
- reject or split the task if its write set overlaps another active task.

## Shared-file integration

Module agents normally do not edit shared files. The Integration Agent batches compatible deltas for:
- README/checkpoints;
- public package exports;
- generated schemas/OpenAPI;
- migration chain reconciliation;
- dependency manifests;
- repository-wide configuration/CI.

Do not batch unrelated behavior changes merely to reduce PR count.

## PR queue

Classify each PR:
- independent: may promote in any order after current-main sync;
- ordered: must land after named predecessor;
- contract owner: may unblock several dependent PRs;
- integration-only: shared-file/generated-artifact reconciliation;
- blocked: cannot promote until dependency/conflict is resolved.

## Promotion

Before merging an executable PR:
1. verify intended scope and changed files;
2. verify head/base relation against current main;
3. reconcile any dependency or shared-contract drift;
4. ensure migration reservation/parent is still valid;
5. run required exact-head promotion CI;
6. verify required checks are green, not skipped or stale;
7. merge using expected-head protection where available;
8. update registries/checkpoints and unblock dependents.

## Working instructions

The Integration Agent owns human-visible synchronization of materially changed agent instructions.

When any governance, architecture, module ownership, dependency, shared-file, migration, CI, consent, or contract rule changes how an agent should work:
- update canonical instruction source(s);
- update task manifests/active-work records affected by the change;
- update the root README `Current agent working instructions` section in the same integration cycle;
- identify active tasks needing re-review;
- do not allow an agent to continue on stale instructions when the delta changes its scope or safety obligations.

If no material delta exists, do not edit README merely to refresh a date.

## Throughput rule

The Integration Agent should continuously look for independent ready work rather than waiting for the current critical-path implementation to finish before preparing the next safe lanes. However, future executable work still respects development consent and milestone entry gates.

## Failure handling

If two branches conflict semantically:
- stop automatic promotion;
- identify contract/state owner;
- choose one canonical direction;
- update affected task instructions;
- rebase/rework dependent branches;
- rerun tests on exact candidate heads.

Never solve semantic conflicts by accepting both incompatible implementations.
