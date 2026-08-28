# Development Consent Gate

## Purpose

The operator requires explicit consent before executable development begins or resumes.

This rule is mandatory for every AI/engineer working in this repository and overrides any older wording that allowed routine implementation to proceed without asking.

## Core rule

Research, audit, planning, architecture analysis, documentation, read-only repository inspection, issue/PR analysis, and preparation of a development brief may proceed without a development consent request.

Executable development MUST NOT begin until the operator has explicitly approved the scoped development brief.

A generic command such as `continue`, `next`, `resume`, or `audit` is not development consent by itself unless the operator explicitly states that development/code implementation is approved.

Examples of valid approval language include:
- `start development`
- `development approve`
- `approved, implement it`
- `code start karo`
- another unambiguous statement authorizing the described development scope.

## What counts as executable development

Consent is required before creating, changing, deleting, or enabling any of the following when the change affects executable/product behavior:

- application/backend/frontend/mobile source code;
- Python/TypeScript/runtime packages;
- domain schemas or validation behavior;
- database models/migrations/queries;
- Temporal workflows/workers;
- provider adapters or API integrations;
- generation/rendering/media-processing behavior;
- executable automation scripts;
- GitHub Actions or CI/CD behavior;
- dependency additions/removals/upgrades that affect runtime/build behavior;
- authentication/authorization/security behavior;
- publishing/upload behavior;
- budget/payment/cost-routing behavior;
- tests or fixtures that accompany a new implementation scope;
- infrastructure/deployment configuration;
- destructive refactors or migrations.

## What does not require development consent

The following may proceed without asking, provided they do not secretly change executable behavior:

- internet/official-source research;
- competitor/system study;
- architecture options and trade-off analysis;
- repository/code audit in read-only mode;
- documentation and planning documents;
- ADR drafts;
- product option documentation;
- backlog/milestone planning;
- risk, security, QA, migration and test-plan design;
- development readiness checklists;
- provider capability/pricing research reports that do not enable/change production routing;
- preparation of a proposed patch/diff description without applying it.

If a documentation/config file is machine-read by production code and changing it alters runtime behavior, treat that change as executable development and require consent.

## Consent protocol

Before development, provide a concise `Development Consent Brief` containing:

1. **Milestone / scope** — exactly what will be implemented.
2. **Why now** — dependency/order rationale.
3. **Files/components expected** — likely affected areas.
4. **Behavioral changes** — what becomes executable/different.
5. **Data/migration impact** — including `none` when applicable.
6. **Security/rights/cost impact** — including provider/API spend risk.
7. **Tests/verification** — what will prove the implementation.
8. **Rollback/recovery** — how the change can be reversed/recovered.
9. **Out of scope** — what will deliberately not be built yet.
10. **Consent request** — explicitly ask the operator whether to start that development scope.

Do not start implementation in the same turn before receiving the operator's approval when this gate applies.

## Scope of consent

Consent is scoped, not unlimited.

Approval for one milestone/subtask authorizes only the described scope and directly necessary low-risk implementation details.

Request new consent before materially expanding into:
- another milestone;
- a materially different feature;
- destructive/breaking migration;
- new paid provider usage not covered by configured authorization;
- security/auth architecture changes;
- public publishing/autonomous publishing;
- significant dependency/platform replacement;
- material budget/cost behavior change.

Minor reversible implementation details inside an already approved scope do not require repeated permission.

## Planning-to-development boundary

The AI may continue planning until the next executable action is clearly defined. At that point it must stop and request consent rather than silently crossing into implementation.

Repository status should use:

`PLANNING_READY_FOR_CONSENT`

when documentation/audit is complete and the next action is executable development awaiting operator approval.

## Emergency/security exception

Do not silently modify code even when a security issue is discovered. Document the issue, severity, exposure, recommended remediation and immediate containment options, then request consent before applying changes unless the operator has already granted an applicable remediation scope.

## Existing work

Executable work completed before this rule remains part of repository history and must not be rolled back merely because the consent gate was added.

From this document's introduction onward, all new executable development follows this gate.
