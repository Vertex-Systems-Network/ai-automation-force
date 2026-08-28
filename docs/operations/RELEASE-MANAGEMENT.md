# Release Management, Feature Flags and Rollback

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define how code, database, prompts/models, provider adapters, configuration and infrastructure changes move from development to production with evidence, staged rollout and rollback.

## Release artifact identity

Every production deployment records:
- Git commit SHA;
- build ID;
- container/image digests;
- schema/migration version;
- API version;
- web build version;
- worker versions;
- prompt/agent policy versions where relevant;
- provider registry/config snapshot;
- IaC revision;
- feature-flag snapshot or change references.

User/support-visible version can be semantic/calendar release label, but exact SHA/digests remain canonical operational identity.

## Change classes

### Class A — Low-risk compatible
Examples:
- copy/UI fix;
- non-breaking observability;
- additive safe API field;
- documentation-only.

Can use normal rolling release after tests.

### Class B — Behavioral product change
Examples:
- new feature;
- workflow logic;
- provider routing changes;
- new UI module;
- entitlement behavior.

Requires staged rollout/feature flag when feasible.

### Class C — High-risk
Examples:
- auth/security;
- billing/credits;
- public publishing;
- destructive migration;
- secrets/KMS;
- major Temporal workflow compatibility;
- high-spend provider logic;
- privacy/delete behavior.

Requires explicit release plan, staging evidence, rollback/containment, and elevated approval.

## Release pipeline

`PR -> Static/Unit/Contract -> Integration/E2E -> Security/AI Eval as applicable -> Merge -> Immutable Build -> Staging Deploy -> Staging Smoke/Acceptance -> Production Approval Gate -> Canary/Rolling -> Observe -> Promote -> Closeout`

No rebuilding between staging and production when avoidable; promote the same immutable artifact.

## Branch/repository model

- protected `main` is production-intent source;
- changes via PR except emergency procedure;
- required checks/reviews by change class;
- release tags point to exact deployed commit where used;
- no direct unreviewed production edits as normal workflow.

## Feature flags

Flag categories:
- release flag;
- operational kill switch;
- entitlement-controlled feature;
- experiment flag;
- provider/model routing flag.

Do not use a feature flag as substitute for RBAC or paid entitlement.

Flag metadata:
- key;
- owner;
- type;
- default;
- environments;
- audience/targeting;
- created/expiry/review date;
- dependency;
- rollback semantics;
- audit history.

Temporary release flags must be removed after stabilization to avoid permanent flag debt.

## Canary strategy

Initial production canary options:
- internal workspace first;
- allowlisted beta workspaces;
- small percentage for stateless web/API;
- specific worker task queue/build IDs for workflow changes;
- provider/model candidates through routing canary.

Canary must have:
- defined metric baseline;
- hard stop thresholds;
- max duration/min sample;
- no expansion of security permissions;
- spend cap for AI/provider changes;
- rollback command.

## Prompt/model/provider releases

AI behavior releases follow AI Evaluation Framework:
- offline suite;
- adversarial/security suite;
- cost/latency benchmark;
- human preference if applicable;
- canary;
- promotion/rollback.

Prompt or provider-registry changes that alter runtime behavior are release-managed executable changes, not casual documentation edits.

## Temporal workflow compatibility

Workflow code changes must respect durable histories.

Strategies:
- deterministic backwards-compatible code/versioning;
- Temporal patch/version mechanisms as current SDK recommends;
- old workers kept until old histories drain when needed;
- continue-as-new/migration for long histories;
- replay tests against representative histories before release.

Never deploy code that makes existing durable workflows nondeterministic without migration plan.

## Database release strategy

Prefer expand/migrate/contract:

### Expand
Add backwards-compatible structures.

### Migrate/backfill
Populate asynchronously with observability/idempotency.

### Switch
Move reads/writes after compatibility verified.

### Contract
Remove old schema only after all deployed code/workflows no longer depend on it.

High-risk migrations require restore/rollback plan and current backup health.

## API compatibility

Before production:
- OpenAPI diff;
- generated-client compatibility;
- breaking change blocked unless versioned/migration approved;
- webhook schema compatibility;
- mobile older-client compatibility window considered when mobile ships.

## Infrastructure release

OpenTofu plan reviewed before production apply.

Classify:
- no-op/additive;
- replace/restart;
- destructive/stateful.

Stateful/destructive plan requires explicit approval/backup/recovery path.

## Security release gate

Depending change:
- SAST;
- dependency scan;
- secret scan;
- container/IaC scan;
- auth/tenant tests;
- ASVS-aligned tests;
- AI adversarial tests;
- SBOM/provenance checks.

Critical unresolved security findings block release unless documented emergency risk acceptance by authorized operator.

## Release acceptance

Production promotion requires applicable evidence:
- tests green on exact artifact;
- migrations compatible;
- staging smoke passes;
- SLO health before deploy;
- no active incident that makes change unsafe;
- canary metrics within thresholds;
- change approval for Class C;
- documentation/runbook/support notes updated.

## Rollback types

### Code rollback
Redeploy previous known-good image.

### Feature disable
Kill switch/flag when behavior isolated.

### Provider/model rollback
Restore previous routing/model/prompt stack.

### Database rollback
Prefer forward fix/compatible schema; use migration downgrade only when safe and tested. Data-destructive downgrade is not assumed.

### Infrastructure rollback
Reapply prior IaC only when resource semantics permit; stateful recovery may require DR procedure.

### Publication/billing compensation
External side effects are not undone by code rollback. Use reconciliation/compensating actions.

## Auto rollback

Safe candidates for automatic rollback:
- stateless deployment health failure;
- severe error-rate/latency regression;
- AI canary hard safety failure;
- provider adapter duplicate/idempotency regression detected before broad rollout.

Do not automatically perform destructive DB rollback or delete external published posts/payments without explicit recovery logic.

## Release freeze

Freeze risky releases during:
- SEV0/SEV1 incident;
- exhausted error budget according to policy;
- major provider/platform outage affecting validation;
- backup/restore health failure for stateful changes;
- unresolved security compromise.

Emergency remediation can proceed under incident change protocol.

## Emergency change

Requires:
- incident/security reference;
- minimal scoped fix;
- peer/authorized review where feasible;
- exact artifact recording;
- post-deploy verification;
- retrospective PR/docs if normal process bypassed;
- no unrelated opportunistic changes.

## Changelog

Maintain user-facing release notes for material features/behavior.

Internal changelog additionally covers:
- migrations;
- provider/model changes;
- security/ops changes;
- breaking API/deprecation;
- known issues.

Security fixes may have delayed/redacted public details.

## Versioning

Product app can use calendar/semantic releases; API remains explicitly versioned. Package/component versions can follow SemVer where appropriate.

Versioning choice must not imply API compatibility automatically; compatibility is tested/declared.

## Deployment verification

After production release:
- health/readiness;
- synthetic critical journeys;
- API error/latency;
- workflow queues;
- DB/storage errors;
- auth;
- media worker basic fixture;
- publishing/billing integration health as applicable;
- canary/flag state.

## Release closeout

Record:
- released artifact IDs;
- time/actor;
- migrations;
- flags;
- monitoring window;
- incidents/rollbacks;
- known issues;
- final status.

## Acceptance criteria

Implementation does not need to invent:
- release/change classes;
- pipeline;
- feature flags/canary;
- AI/Temporal/DB/API/IaC release compatibility;
- security/acceptance gates;
- rollback/compensation rules;
- emergency/freeze/changelog/versioning behavior.
