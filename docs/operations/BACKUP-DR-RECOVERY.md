# Backup, Disaster Recovery and Recovery Objectives

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define what must survive failure, target RPO/RTO, backup strategy, restore verification and disaster-recovery operations before production deployment.

## Recovery tiers

### Tier 0 — Identity, security, billing/entitlement control
Includes:
- users/workspaces/members/roles;
- security settings/session/recovery metadata;
- subscriptions/entitlements/usage ledger;
- provider/social credential metadata (encrypted secrets handled by secrets system);
- audit/security records required for safe recovery.

Target:
- `RPO <= 5 minutes`
- `RTO <= 60 minutes` for major platform recovery objective.

### Tier 1 — Canonical project/production state
Includes:
- project/content versions;
- characters/entities/locks;
- timeline/storyboard;
- jobs/workflow references;
- approvals/rights/provenance;
- publication state;
- canonical approved/source media.

Metadata target:
- `RPO <= 5 minutes`
- `RTO <= 2 hours`

Critical canonical object-media regional disaster target:
- `RPO <= 15 minutes` where cross-region replication policy applies;
- `RTO <= 4 hours` for restored/redirected access to critical assets.

### Tier 2 — Regenerable/derived media
Includes:
- proxies;
- thumbnails;
- rejected candidates where retention permits;
- rebuildable render intermediates;
- caches/search indexes.

Target:
- `RPO <= 24 hours` or regenerate;
- `RTO <= 24 hours` depending scale.

### Tier 3 — Ephemeral
- temp FFmpeg files;
- incomplete upload parts beyond resumable session records;
- caches;
- transient provider handoff files.

No durability guarantee. Workflows must recover/recreate them safely.

## Failure scopes

Plan recovery for:
- single process/container;
- worker pool;
- database instance;
- accidental row/object deletion;
- bad migration;
- bad deployment;
- object corruption;
- storage bucket policy mistake;
- secrets compromise;
- Temporal worker outage;
- Temporal workflow/control-plane outage;
- AWS Availability Zone loss;
- AWS region loss;
- provider/social/billing vendor outage;
- malicious/admin destructive action;
- ransomware/credential compromise scenario.

## PostgreSQL backup

Production managed PostgreSQL requires:
- automated continuous/PITR capability;
- encrypted backups;
- cross-account/cross-region backup copy appropriate to Tier 0/1 disaster plan;
- retention policy;
- deletion protection for production where compatible with operations;
- restricted restore/delete permissions;
- periodic logical export only as supplementary portability, not sole backup.

## Database PITR

Recovery procedure:
1. determine safe restore timestamp;
2. create new restored DB instance rather than overwrite current immediately;
3. validate schema/migrations/integrity;
4. reconcile events/side effects after restore timestamp;
5. rotate connection/endpoints through controlled failover;
6. preserve old instance for investigation until safe disposal.

## Object storage protection

Critical buckets:
- versioning enabled;
- encryption;
- public access block;
- lifecycle rules;
- deletion permissions restricted;
- cross-region replication for Tier 1 critical canonical media according to launch policy;
- object lock/immutability only where audit/legal need justifies it because it affects deletion/privacy behavior.

Derived/temp buckets may use less expensive durability policies.

## Media integrity

Canonical asset has content hash. Restore verifies:
- object exists;
- size;
- hash;
- MIME/media probe;
- lineage metadata.

Corrupted/missing derivative can regenerate; corrupted source/master escalates.

## Secrets and KMS recovery

Back up/replicate configuration references, not plaintext secrets.

Recovery plan covers:
- KMS key availability;
- secret versions;
- rotation after compromise;
- emergency replacement credentials;
- inability to decrypt if keys are destroyed.

Key deletion requires long safety window/multi-person controls where cloud supports it.

## Temporal recovery

Temporal Cloud reference provides durable workflow service. Platform still stores canonical business state/reference IDs outside workflow history.

Recovery scenarios:
- workers unavailable -> workflows wait/resume;
- bad worker release -> rollback compatible worker code;
- workflow history large -> continue-as-new/design controls;
- control-plane vendor incident -> queue user-facing new-work restrictions/degraded mode; preserve canonical state;
- catastrophic Temporal data loss (rare) -> reconciliation tooling reconstructs safe pending/terminal workflow work from canonical DB/jobs without duplicating completed side effects.

## External side-effect reconciliation after DB restore

PITR can restore DB to before an external side effect that actually occurred.

Therefore after restore reconcile:
- social posts;
- billing/invoices/payments;
- provider generation jobs/cost;
- emails/webhooks;
- object storage objects;
- OAuth/token changes.

Use external IDs/idempotency/event logs to discover reality before retrying.

Never blindly replay all post-restore events.

## Cross-region disaster strategy

Initial product is single-primary-region, warm-recovery rather than active-active.

DR region has/preplans:
- IaC capable of recreating network/compute;
- replicated/backup DB recovery;
- replicated critical object assets;
- secrets/KMS recovery strategy;
- DNS/traffic failover plan;
- Temporal/environment accessibility;
- observability/status communication.

Activation requires incident declaration and controlled runbook.

## Restore order

1. security/identity/KMS/secrets
2. database Tier 0/1
3. object storage critical assets
4. API/auth control plane
5. Temporal workers/workflows
6. media workers
7. publishing/billing reconciliation
8. derived assets/search/analytics
9. optional integrations

## Degraded mode

During partial recovery:
- protect data first;
- read-only project access may be enabled if safe;
- block generation/publishing/billing mutation when canonical state is uncertain;
- show explicit service status;
- queued scheduled publication may be paused/reconciled rather than blindly late-posted.

## Backup retention classes

Initial operational targets, subject to final legal/storage cost review:
- PITR window: at least 14 days, target 35 days where managed service supports economically;
- daily DB snapshots: 35 days;
- monthly recovery snapshots: 12 months for production business continuity unless privacy/legal policy requires shorter/different treatment;
- object versions/lifecycle by asset retention class;
- IaC/source/config in Git with protected history.

Customer deletion semantics follow privacy document; backup copies age out and deletion tombstones prevent improper resurrection.

## Restore testing

### Monthly
Automated or operator-assisted small restore verification:
- restore DB snapshot/PITR into isolated environment;
- validate schema/integrity/basic synthetic project.

### Quarterly
Full recovery drill:
- DB restore;
- critical object validation;
- application/workers against restored state;
- external side-effect reconciliation simulation;
- measure RPO/RTO.

### At least annually / major architecture change
Regional DR exercise where production maturity justifies it.

Failed drill creates urgent remediation work.

## Backup monitoring

Alert on:
- backup/PITR disabled;
- snapshot failure;
- cross-region replication lag/failure;
- restore test failure;
- storage versioning/public-block drift;
- backup encryption/key issue;
- unexpected deletion surge.

## Disaster declaration

SEV0/SEV1 incident commander decides DR activation using:
- primary recovery estimate;
- data-integrity confidence;
- RTO burn;
- region/service status;
- external side-effect risk.

Avoid premature split-brain by enforcing one active write region/control plane.

## Runbook records

Every recovery records:
- incident ID;
- restore source/timestamp;
- expected data loss window;
- validation checks;
- external reconciliation scope;
- traffic cutover time;
- customer communications;
- unresolved risks.

## Ransomware/credential compromise

Containment includes:
- revoke credentials/sessions;
- disable compromised deploy identities;
- preserve immutable/isolated backup copies;
- do not restore into still-compromised environment;
- rotate keys/secrets;
- validate IaC/source integrity;
- investigate unauthorized deletions/exports.

## Customer-facing expectations

Do not market “zero data loss” universally. Publish SLA/backup commitments only after measuring the implemented architecture.

Internal target RPO/RTO values are engineering objectives until formal customer SLA approved.

## Acceptance criteria

Implementation does not need new planning for:
- data recovery tiers;
- exact initial RPO/RTO targets;
- DB/PITR/object protection;
- Temporal/external-side-effect reconciliation;
- regional DR topology/order;
- degraded mode;
- retention/drill cadence;
- backup monitoring/security recovery.
