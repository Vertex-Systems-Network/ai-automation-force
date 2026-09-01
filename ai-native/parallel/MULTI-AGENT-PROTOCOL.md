# Parallel Multi-Agent Development Protocol

## Purpose

Make repository development safely parallel so multiple AI or human agents can work at the same time without silently overwriting, duplicating, or invalidating each other's work.

This protocol is repository-wide and applies to current and future milestones. It supplements `AGENTS.md`, `ai-native/ENGINEERING-CONTRACT.md`, the development consent gate, milestone plans, and CI rules. It does not weaken any existing security, testing, consent, or exact-head verification requirement.

## Target concurrency

Use concurrency according to repository maturity and dependency independence:

- current/default safe target: 4-5 active agents including integration/QA lanes;
- after module ownership and contract boundaries are stable: 6-8 implementation/review agents plus one integration agent;
- mature target: 8-12 active agents only when the dependency graph contains enough independent ready work;
- never create parallel work merely to reach an agent count.

The scheduler must prefer fewer independent agents over many overlapping agents.

## Core model

Parallel development is dependency-aware and contract-first:

`plan -> contract/freeze boundary -> identify independent ready work -> claim scopes -> isolated branches -> scoped CI -> integration queue -> current-main sync -> full promotion CI -> merge`

A work package is parallel-safe only when its write set, schema/migration ownership, public contracts, and dependencies are known.

## Mandatory roles

### Integration Agent

Exactly one integration authority owns repository-wide coordination for a promotion window.

Responsibilities:
- allocate/confirm work claims;
- maintain `ACTIVE-WORK.yaml`;
- reserve migration identifiers;
- arbitrate shared-file edits;
- preserve public contract compatibility;
- track PR dependencies/blockers;
- reconcile generated schemas/public exports/checkpoints/README;
- require current-main synchronization before promotion;
- run/verify full exact-head CI;
- merge only certified candidates.

The Integration Agent should not become the default feature implementer when independent module work can be delegated.

### Module Agents

A module agent may read the entire repository but may write only its claimed paths plus explicitly granted shared files.

A module agent must:
- work from a pinned base commit;
- use a task/work-package branch, not an agent-personality branch;
- preserve public contracts unless the task explicitly owns the contract change;
- avoid opportunistic refactors outside scope;
- report any needed shared-file changes to the Integration Agent;
- keep its PR small enough to review and rebase safely.

### QA / Adversarial Agent

A QA agent independently evaluates implementation assumptions, race conditions, tenant/security boundaries, crash/retry behavior, migration reversibility, compatibility, and regression risk. QA may propose tests/fixes but must still claim write paths before modifying them.

### Planning / Contract Agent

A planning/contract agent may prepare future dependency-ready work without touching executable behavior unless applicable development consent exists. Contract changes that affect executable behavior follow the consent gate.

## Write ownership rule

Default rule:

> Every agent may READ the whole repository. Every agent may WRITE only the paths explicitly claimed for its task.

If two active tasks need the same non-shared write path, they are not parallel-safe until the work is split or ownership is reassigned.

## Shared files

Shared/high-conflict files are centrally coordinated. Canonical list: `SHARED-FILES.yaml`.

Examples include:
- root `README.md`;
- `AGENTS.md`;
- public package `__init__.py` export surfaces;
- dependency manifests/lock files;
- generated schemas/OpenAPI artifacts;
- migration chain/head metadata;
- repository-wide CI workflows;
- common/global domain contracts;
- global configuration used by multiple modules.

Module agents should normally record requested shared-file deltas in the PR description instead of editing shared files directly. The Integration Agent may grant temporary ownership when a shared edit is intrinsic to the task.

## Migration reservation

No agent invents a migration identifier independently.

Before creating a migration:
1. inspect `MIGRATION-REGISTRY.yaml`;
2. obtain/reserve the next identifier through the integration lane;
3. record owner task, branch, dependency/base revision, and status;
4. create only the reserved migration;
5. release/cancel reservations that will not be used.

Two active branches must never own the same migration identifier.

## Contract-first parallelization

When several implementations depend on the same boundary, define and freeze the minimal contract first.

Example:

`Character contract -> persistence | API | QA | UI client work in parallel`

Agents consume the public contract rather than another agent's private implementation details. A contract-breaking change invalidates dependent work and must be coordinated before merge.

Canonical contract inventory: `CONTRACT-REGISTRY.yaml`.

## Dependency graph

Canonical dependency state lives in `DEPENDENCY-GRAPH.yaml`.

A task is eligible only when:
- required predecessor contracts/landed work exist;
- required development consent exists;
- its write set does not conflict with another active claim;
- any migration slot is reserved;
- no shared-file ownership conflict is unresolved.

Blocked work may still perform read-only research/planning when permitted.

## Branching

Use task identity, not model/agent identity:

- good: `agent/M06-WP2-audio-persistence`
- good: `agent/M04-WP1-character-contracts`
- avoid: `agent/gpt-work`
- avoid: `agent/claude-2`

Every task record carries its exact `base_sha`.

## Synchronization and promotion

Before promotion:
1. verify the PR still represents the intended task scope;
2. compare against current `main`;
3. resolve contract/schema/shared-file changes through the integration lane;
4. synchronize/rebase/merge current main as repository policy permits;
5. rerun required full CI on the exact candidate head;
6. merge with an expected-head guard where available;
7. update active-work/dependency/contract/migration state and checkpoints.

Passing scoped CI earlier does not replace exact-head promotion CI.

## CI strategy

Two layers are permitted:

### Scoped agent CI
Fast feedback on affected modules:
- format/lint;
- typing;
- module unit tests;
- relevant contract/database tests;
- relevant security checks.

### Promotion CI
Required before merge for executable work:
- repository governance;
- full applicable core/API/worker tests;
- PostgreSQL/migration checks;
- Temporal/workflow checks where applicable;
- generated schema/OpenAPI synchronization;
- compile/build/security checks required by repository policy.

Path-scoped CI may accelerate feedback but must never weaken the promotion gate.

## Working-instruction audit — mandatory on every start/resume

Before an agent starts or resumes work, it must explicitly determine the current working instructions for that task.

The audit must check at minimum:
- `AGENTS.md`;
- `ai-native/ENGINEERING-CONTRACT.md`;
- `ai-native/DEVELOPMENT-CONSENT-GATE.md`;
- this protocol;
- relevant milestone/architecture docs;
- `MODULE-OWNERSHIP.yaml`;
- `ACTIVE-WORK.yaml`;
- `DEPENDENCY-GRAPH.yaml`;
- `MIGRATION-REGISTRY.yaml` when data/schema work is possible;
- `SHARED-FILES.yaml`;
- `CONTRACT-REGISTRY.yaml`;
- relevant recent Git/PR/checkpoint state.

The agent must decide whether its previous working instructions are still correct.

If instructions changed materially, the agent must:
1. update its task/PR/checkpoint instructions before continuing;
2. update the root README `Current agent working instructions` summary in the same integration cycle;
3. record what changed and why;
4. re-evaluate scope, ownership, dependencies, migration reservation, test obligations, and consent;
5. stop or re-plan if the change invalidates the active assignment.

If instructions did not change, no README churn is required; the agent records/notes that the instruction audit found no material delta where checkpoint reporting is applicable.

The README is a human-visible summary. Canonical detailed rules remain in repository governance/parallel files.

## Task manifest

Every implementation task should conform to `AGENT-TASK-SCHEMA.yaml` and identify:
- task/work-package ID;
- role/owner lane;
- pinned base SHA;
- branch;
- owned write paths;
- read-only dependencies;
- shared-file requests;
- consumed/produced contracts;
- dependency IDs;
- migration reservation if any;
- required verification;
- consent state;
- current status.

## Conflict policy

A conflict is not only a Git textual conflict. Treat these as conflicts too:
- two agents changing the same public contract differently;
- duplicate migration numbers;
- one PR depending on unmerged implementation internals from another;
- incompatible schema/OpenAPI changes;
- simultaneous global dependency changes;
- competing generated-artifact updates;
- two agents claiming authority over the same canonical state machine/table;
- stale-base implementation that violates newly landed invariants.

Such conflicts are resolved before promotion, not hidden by a textual merge.

## Speed principle

Parallelism should reduce critical-path idle time. Prefer independent lanes such as implementation, tests, future contract planning, provider research, frontend preparation, and adversarial QA when they do not share mutable ownership.

Do not parallelize tightly coupled sequential state transitions merely for speed. Contract definition, destructive migrations, global auth changes, and shared architecture changes often require a short serialized integration window before fan-out.

## Completion

A parallel task is not complete merely because its branch is coded. Completion requires the same evidence as any other repository work: relevant tests, security/data review, documentation/checkpointing, current-main compatibility, and exact-head promotion evidence where required.