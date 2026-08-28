# M15 — Production Operations, Security Hardening and Public Launch

## Objective

Deploy the preplanned platform into the reference production environment, implement production-grade security/privacy/observability/backup/release/support controls, validate commercial/public launch requirements and complete the final launch acceptance gate.

## Entry criteria

- P0 complete.
- M01–M14 accepted.
- Explicit M15 development/deployment consent.
- Final launch geography/legal entity/business mode known.
- Current cloud/provider/API/security/legal facts revalidated.

## Dependencies

`M01–M14 -> M15`

## Work packages

### M15-WP1 — Production AWS/OpenTofu foundation
Implement reference topology from deployment spec:
- production AWS account/boundary;
- VPC/private subnets/security groups;
- DNS/TLS;
- CloudFront/WAF where applicable;
- ECS/Fargate/API/light workers;
- heavy media worker pool;
- RDS/Aurora PostgreSQL-compatible;
- S3 buckets/CDN origins;
- KMS/Secrets Manager;
- Temporal Cloud production namespace;
- observability endpoints;
- GitHub OIDC deploy roles.

### M15-WP2 — Environment/secrets/security hardening
- production/staging credential separation;
- passkeys/MFA/step-up settings;
- session/device controls;
- least-privilege IAM/service identities;
- encryption/secret rotation;
- CSP/security headers;
- SSRF/webhook/upload/media sandbox controls;
- rate/bot/abuse protections;
- admin/support privileged access controls;
- secure SDLC scans/SBOM/provenance.

### M15-WP3 — Observability/SLO/status operations
- OpenTelemetry traces/metrics/logs;
- required dashboards;
- initial SLO/SLI measurement;
- burn-rate alerts;
- SEV0–SEV4 routing;
- health/readiness/synthetics;
- public status-page components;
- on-call/escalation/runbooks.

### M15-WP4 — Backup/PITR/DR implementation
- DB PITR/backups/copies;
- S3 versioning/replication for required tiers;
- backup encryption/access;
- restore tooling;
- deletion/tombstone recovery semantics;
- cross-region warm-recovery IaC;
- monthly/quarterly drill automation/runbooks;
- verify target RPO/RTO.

### M15-WP5 — CI/CD, release and migration operations
- protected release workflow;
- immutable build artifacts;
- staging promotion;
- feature flags/canaries;
- migration expand/migrate/contract;
- Temporal workflow compatibility gates;
- AI evaluation gates;
- release notes/changelog;
- rollback/kill-switch/emergency process;
- infrastructure drift detection.

### M15-WP6 — Billing/entitlements productionization
According to approved launch mode:
- billing vendor production credentials/integration;
- plan/entitlement configuration;
- metering/credit reconciliation;
- invoices/tax profile;
- payment failure/dunning;
- refunds/adjustments;
- support tooling;
- test/live mode separation.

If launch mode is `FREE_BETA_BYOK_ONLY` or `INVITE_ONLY_NO_BILLING`, paid checkout remains disabled but entitlement/usage controls still operate.

### M15-WP7 — Data privacy/legal launch operations
- data inventory/classification;
- export/delete/correct flows verified;
- retention/backup deletion behavior;
- subprocessor register;
- approved Terms/Privacy/AUP/Cookie/synthetic-media/IP complaint documents;
- consent/tracking configuration;
- child-directed content/account-age stance;
- data residency claims only if actually enforced.

Final legal text is approved externally by qualified counsel/operator, but product flows must match it.

### M15-WP8 — Support/admin/moderation productionization
- internal support console;
- privileged roles;
- job/provider diagnostics/retry;
- billing adjustments;
- suspension/restoration;
- moderation/abuse/privacy/rights cases;
- escalation channels;
- security contact;
- admin audit;
- customer content-access controls;
- no silent unrestricted impersonation.

### M15-WP9 — Production provider/social readiness
- current provider/social capability evidence refreshed;
- production credentials/scopes/app reviews;
- budget/rate/quota limits;
- platform publishing kill switches;
- official API compliance;
- test/private first publication;
- analytics/community automation modes validated;
- unverified platforms remain manual/evaluation.

### M15-WP10 — Production readiness and launch acceptance
Run complete Master QA release suite:
- exact production artifacts;
- auth/tenant/security;
- migrations;
- workflow recovery;
- storage/uploads;
- provider generation;
- media render;
- web/mobile/API journeys applicable to launch;
- billing mode;
- social publication;
- accessibility/browser/device;
- load/performance;
- backup restore/DR drill;
- AI eval/security suite;
- incident/rollback exercise.

Create final launch evidence bundle with `PASS | FAIL | NOT_APPLICABLE | NOT_VERIFIED`. Launch requires no blocking `FAIL`/`NOT_VERIFIED` in mandatory categories.

## Expected modules/files

- `infra/` OpenTofu;
- production environment/deploy config;
- CI/CD/release workflows;
- observability dashboards/alerts;
- security/backup/runbook automation;
- support/admin tooling;
- approved public legal pages/config;
- production launch checklist/evidence.

## Data/migration impact

Production DB/storage initialization and any final compatible migrations. Data lifecycle/backup/retention policies become active. No unplanned product-domain schema should first appear in M15.

## API/UI impact

Production domains, public/authenticated apps, mobile/API if launch-enabled, support/admin/status/legal surfaces become operational according to release flags.

## Security/cost/rights impact

Highest-risk milestone:
- production secrets;
- cloud/provider spend;
- public publishing;
- billing/customer data;
- legal/privacy obligations.

All Class C changes use explicit approvals, staged rollout and rollback/containment.

## Test/acceptance

Full Master Quality Acceptance Matrix plus measured SLO/RPO/RTO, security review, current provider/social integration evidence and final legal/commercial launch approvals.

## Rollout/rollback

- staging before production;
- internal/allowlisted canary;
- feature/provider/social/public-API kill switches;
- code/IaC rollback;
- forward-compatible DB recovery;
- external side effects reconciled/compensated;
- incident process available from first production traffic.

## Exit criteria

The product operates in production with measured service objectives, secure identity/tenant/secrets, tested backups/DR, controlled releases, support/moderation, privacy/legal operations, billing mode, verified providers/social integrations and a complete launch evidence bundle.

## Non-goals

- claiming certifications not obtained;
- active-active global multi-region by default;
- unlimited provider/platform support;
- bypassing app-review/ToS/legal requirements;
- inventing new major product systems during launch;
- removing the ongoing need to revalidate mutable external facts after launch.
