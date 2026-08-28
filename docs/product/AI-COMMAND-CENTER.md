# AI Command Center

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define one global AI-native control surface for planning, explaining, generating, retrying, comparing, approving and recovering work without forcing users to discover AI controls independently in every screen.

The Command Center is not a free-form chatbot with unlimited authority. It is a policy-aware control plane over canonical project/workspace state.

## Entry points

Accessible from:
- global app shell;
- keyboard shortcut;
- project context;
- selected storyboard/shot/take/asset;
- provider/cost screen;
- publishing screen;
- notifications/alerts;
- optional mobile quick actions.

Context is explicit and visible before execution.

## Core commands

### `next`
Find highest-value eligible incomplete work according to canonical state, dependencies, safety, consent, budget and approval policy.

`next` must never imply blanket permission for development, spend, publishing, security or destructive actions.

### `explain`
Explain a decision/action using:
- current state;
- policy/constraint gates;
- selected inputs/evidence;
- alternatives considered at summary level;
- cost/rights/security implications;
- blockers/uncertainty.

No private chain-of-thought is exposed.

### `dry run`
Simulate intended operations without external side effects.

Shows:
- affected scope;
- estimated provider calls;
- expected cost/credits;
- expected assets/jobs;
- required approvals;
- fallback routes;
- known risks;
- whether any action is irreversible.

### `generate`
Create authorized candidates/assets/jobs for selected scope.

### `retry failed`
Retry only failed/rejected eligible scope. Preserve successful/approved state.

### `compare alternatives`
Generate or surface alternatives side-by-side without replacing approved state.

### `repair`
Plan scoped repair for continuity, malformed provider output, missing asset, timeline gap, failed publication, etc.

### `approve` / `reject`
Available only when role/policy permits and the selected object is approval-capable.

### `undo`
Only exposed when a real reversible/compensating action exists.

### `publish` / `schedule`
Requires canonical publication package, connected account, permission and approval policy.

### `stop` / `cancel`
Stops eligible queued/running work while preserving completed canonical outputs.

## Command object

Every command resolves to a typed `CommandIntent`:
- command ID;
- actor/user;
- workspace/project;
- selected resource scope;
- intent type;
- parameters;
- authority class;
- estimated side effects;
- spend estimate;
- public/external impact;
- approval requirement;
- idempotency key;
- dry-run plan reference;
- status.

Free-form language is parsed into this typed structure before execution.

## Scope selector

Commands must state scope such as:
- current project;
- selected scene;
- selected shots;
- failed shots only;
- one character;
- one provider connection;
- current publish campaign;
- all eligible assets.

Before a bulk/high-impact action, UI displays resolved scope/count.

## Authority display

For each proposed action the UI shows:
- `READ_ONLY`
- `INTERNAL_REVERSIBLE`
- `BOUNDED_PRODUCTION`
- `PRIVILEGED`
- `ADMIN_SECURITY`

If user/agent lacks authority, Command Center explains exactly which role/approval/entitlement is missing.

## Plan -> approve -> execute pattern

High-impact action flow:

`Intent -> Normalize -> Policy/Permission Check -> Dry Plan -> Cost/Impact Preview -> Approval if required -> Execute -> Verify -> Decision/Audit Record`

Low-risk internal actions may skip separate approval when policy allows.

## Provider-aware commands

Examples:
- “Generate reference images for this character using free-first policy.”
- “Retry failed shots under $10 total.”
- “Compare Kling and Runway for these two shots without approving either.”
- “Why did this switch providers?”

Command Center resolves capability, funding, quota, continuity and rights through canonical router policies; it does not hard-code provider assumptions.

## Cost interaction

Before spend-capable execution show, where knowable:
- estimate range;
- reserved credits;
- funding source (`BYOK | PLATFORM_CREDIT | MIXED`);
- autonomous spend limit;
- additional approval threshold.

If estimate changes materially during execution beyond configured tolerance, pause for re-evaluation/approval rather than silently overspend.

## Long-running jobs

After command execution:
- Command Center returns immediately with job/run IDs;
- progress appears in global active-jobs area;
- user can navigate elsewhere;
- steps and partial outcomes remain inspectable;
- cancellation/retry options depend on workflow state;
- failures surface only affected scope.

## Context handling

The system may automatically include:
- canonical project settings;
- selected resource versions;
- approved character/world/style locks;
- current timeline state;
- relevant memories;
- provider capabilities;
- entitlement/budget state;
- active approvals.

UI exposes a concise “Using context” summary and allows safe user overrides for non-policy fields.

## Suggestions

The Command Center may proactively suggest:
- missing character lock;
- continuity issue;
- cheaper eligible provider;
- quota reset wait;
- duplicate concept risk;
- unapproved publish package;
- expiring credits;
- failed scheduled post;
- required rights record.

Suggestions do not become actions without applicable authority/automation policy.

## Automation levels

Workspace/project setting:
- `ADVISORY_ONLY`
- `AUTO_INTERNAL_LOW_RISK`
- `AUTO_PRODUCTION_WITHIN_BUDGET`
- `AUTO_WITH_APPROVAL_GATES`

No mode removes hard security/rights/entitlement constraints.

Public publishing and privileged account/security/billing actions remain separately governed even in high automation mode.

## Command history

Every command stores:
- normalized intent;
- actor;
- scope;
- dry-run plan;
- approval;
- execution jobs/actions;
- results;
- failures;
- undo/compensation if any;
- links to decision records.

Users can re-run compatible commands against new state only after fresh validation; history is not a permanent authorization token.

## Recovery UX

On failure, Command Center offers action-specific recovery:
- retry same provider;
- switch provider;
- wait for quota;
- reduce scope/quality;
- use BYOK/platform credits if policy permits;
- manual handoff;
- repair invalid input;
- request approval;
- abandon failed candidate while keeping success.

Never suggest an option that violates rights, ToS, permissions or budget policy.

## Search/command palette integration

Global palette can find:
- projects;
- characters;
- assets;
- shots;
- commands;
- settings;
- documentation/help actions.

Navigation search and action execution are visually distinct so a search result cannot accidentally trigger a side effect.

## Accessibility

- fully keyboard operable;
- commands have accessible labels;
- focus moves predictably to approval/error/progress states;
- streaming/progress updates do not spam assistive technologies;
- command history/filter supports non-pointer interaction.

## Empty/error states

If no project context:
- offer create project, open recent project, global account/provider/settings commands.

If disconnected/offline:
- allow read-only cached history when safe;
- do not queue privileged side effects unless explicitly designed for reliable replay.

If AI parser cannot confidently normalize free-form intent:
- present interpreted command for user edit/selection;
- do not guess a privileged action.

## Acceptance criteria

Implementation must know:
- global entry points;
- typed command schema;
- command catalog;
- scope resolution;
- authority/approval rules;
- dry-run/cost preview;
- long-job behavior;
- context/memory integration;
- automation levels;
- history/recovery/undo rules;
- failure behavior when intent is ambiguous.
