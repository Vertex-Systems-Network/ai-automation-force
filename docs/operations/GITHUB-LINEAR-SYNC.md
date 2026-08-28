# GitHub ↔ Linear Planning Sync Policy

## Purpose

Define how AI Automation Force planning/status stays synchronized between GitHub and Linear without allowing planning automation to mutate executable product behavior.

## System roles

### GitHub — canonical engineering source
GitHub owns:
- architecture and engineering contracts;
- product/AI system specifications;
- schemas/prompts/configuration definitions;
- implementation history;
- tests/CI evidence;
- research/provenance evidence;
- checkpoints;
- releases/code state.

Canonical repository:
`https://github.com/Vertex-Systems-Network/ai-automation-force`

### Linear — canonical planning/status mirror
Linear owns:
- project roadmap visibility;
- milestone tracking;
- work packages/issues;
- dependencies;
- owner/priority/status;
- project planning documents;
- concise progress/status updates.

Linear project:
`AI Automation Force`

## Current development state

`PLANNING_READY_FOR_CONSENT`

Current milestone:
`M1 — Core Domain & Persistence Boundary`

Current M1 issue chain:
- ABD-128 — WP1 Contract freeze + generated schemas
- ABD-129 — WP2 Full lineage fixtures/invariants
- ABD-130 — WP3 Aggregate validation hardening
- ABD-131 — WP4 Legacy CNT importer
- ABD-132 — WP5 PostgreSQL persistence architecture
- ABD-133 — WP6 Reversible migrations
- ABD-134 — WP7 Persistence repositories + round trips
- ABD-135 — WP8 M1 verification/checkpoint

## Sync direction

Synchronization is bidirectional for planning metadata but not equal-authority for engineering facts.

### GitHub → Linear
Mirror material changes such as:
- current checkpoint/milestone;
- milestone scope changes;
- new approved planning work packages;
- completed/blocked/verified status supported by repository evidence;
- new major product documentation areas;
- implementation/verification results once development is authorized.

### Linear → GitHub
Linear planning changes may be reflected back into GitHub only as planning/documentation when they do not alter executable behavior.

Examples allowed without development consent:
- roadmap clarification;
- milestone/work-package descriptions;
- planning status;
- documentation completeness/index updates;
- non-executable risk/acceptance planning.

Examples NOT allowed through sync without applicable development consent:
- source-code changes;
- runtime schemas/validators;
- database migrations;
- dependency changes;
- CI/CD behavior;
- provider adapters/API integration;
- authentication implementation;
- UI implementation;
- publishing behavior;
- budget/payment behavior;
- infrastructure deployment changes.

## Conflict policy

When GitHub and Linear disagree:
1. verified repository/code/test evidence wins for engineering state;
2. GitHub checkpoint wins for current development gate;
3. Linear may contain newer planning intent, but it must not silently override engineering contracts;
4. unresolved material conflict should be surfaced rather than auto-resolved destructively.

## Development consent protection

The sync process must obey `ai-native/DEVELOPMENT-CONSENT-GATE.md`.

A generic user command such as `continue`, `next`, or `resume` is not development consent.

Synchronization itself must never be interpreted as approval to start executable work.

## Idempotency / duplicate prevention

Sync jobs should:
- search before creating a Linear project/issue/document;
- update existing matching entities instead of duplicating them;
- avoid duplicate comments/status updates;
- use stable GitHub paths and Linear issue identifiers when available;
- add a new status update only when material state changed;
- preserve issue dependency chains.

## Status mapping

Suggested mapping:
- GitHub `PLANNING_READY_FOR_CONSENT` -> Linear Backlog / awaiting approval
- development approved + WP started -> Linear started/in-progress state
- repository verification passed -> eligible for Linear Done
- blocked external credential/runner/approval -> Linear blocked/appropriate state + reason
- repository `Not Verified` -> never mark Linear Done

## Milestone completion rule

A Linear milestone must not be marked complete solely because its issues were manually moved.

Completion requires repository/checkpoint evidence that the milestone acceptance criteria were verified.

## Sync cadence

Recommended default automated cadence: every 6 hours.

The scheduler should also permit manual/ad-hoc sync when the operator requests it.

Frequent sync should remain lightweight and avoid creating noise when nothing material changed.

## Scheduled sync procedure

On each run:
1. read GitHub `checkpoints/LATEST.md`;
2. read `docs/architecture/DEVELOPMENT-PLAN.md`;
3. read current milestone execution/consent brief where applicable;
4. read `docs/product/DOCUMENTATION-COMPLETENESS-MATRIX.md` when planning scope changed;
5. inspect relevant recent GitHub commits/PR/status evidence;
6. read Linear `AI Automation Force` project, milestones, issues and latest status update;
7. compare state;
8. update Linear planning/status where GitHub has newer verified state;
9. reflect Linear-only planning changes into GitHub documentation only when safe and non-executable;
10. preserve consent gates and dependencies;
11. post/update a concise Linear project status only if material state changed;
12. record unresolved conflicts/blocks rather than guessing.

## Security/privacy

Sync must never copy into Linear:
- provider API keys/tokens;
- database credentials;
- verification/reset tokens;
- private user media/content unless explicitly required and safe;
- secrets from CI/environment.

Use references/IDs/links instead of sensitive payloads.

## Acceptance criteria

The GitHub↔Linear planning sync is correctly governed when:
- both systems describe the same current milestone and status;
- Linear mirrors the roadmap and work packages;
- GitHub remains canonical for engineering evidence;
- duplicate planning entities are not created;
- no executable development can begin through sync alone;
- verified completion is required before closing milestones;
- material conflicts are surfaced explicitly.
