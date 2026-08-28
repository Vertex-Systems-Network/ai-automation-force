# Observability, SLOs and Incident Response

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define telemetry, service-level objectives, alerting, incident response and postmortem behavior before production implementation.

## Observability principles

- OpenTelemetry-compatible traces/metrics/log correlation is the vendor-neutral instrumentation baseline;
- every user request and long-running workflow is traceable through stable IDs;
- logs are structured and privacy-redacted;
- external provider failures are distinguishable from platform failures;
- SLOs measure customer-visible service behavior, not vanity infrastructure uptime;
- alerts are actionable and tied to runbooks;
- no alert is created without an owner/severity/action.

## Correlation identifiers

Every relevant path propagates:
- `request_id`
- `trace_id`
- `workspace_id` as safe structured metadata where allowed
- `project_id` optional
- `workflow_id/run_id`
- `job_id`
- `generation_attempt_id`
- `asset_id`
- `publish_target_id`
- `provider_request_id` where available

Secrets/raw auth tokens are never telemetry fields.

## Telemetry domains

### API/control plane
- request count/status;
- latency;
- auth/authorization failures;
- DB/cache/object-store calls;
- rate limiting;
- idempotency conflicts.

### Temporal/workflows
- workflow start/completion/failure/cancel;
- activity latency/retries;
- task queue lag;
- stuck/waiting states;
- replay/nondeterminism failures;
- manual approval wait duration.

### Provider adapters
- calls by provider/model/capability;
- normalized outcomes;
- latency;
- 4xx/5xx/429;
- queue/poll duration;
- quota state;
- retry/fallback;
- accepted-output rate;
- cost.

### Media workers
- FFmpeg/probe/transcode/render duration;
- CPU/memory/disk usage;
- job timeout/OOM;
- failed codec/container;
- output validation.

### Storage
- upload completion/failure;
- validation/quarantine;
- object bytes/egress;
- signed URL errors;
- temp cleanup/orphans;
- archive/restore.

### Publishing/social
- scheduled jobs due/started;
- platform API latency/failure;
- processing time;
- verified/failed posts;
- duplicate-prevention conflicts;
- analytics ingestion lag.

### Billing/usage
- usage reservation/settlement failures;
- credit balance anomalies;
- webhook failures;
- invoice/payment state sync lag;
- entitlement reconciliation differences.

### AI quality/security
- structured-output failure;
- hard QA failures;
- injection/security block events;
- unauthorized tool attempts;
- human override rate;
- eval/canary regressions.

## Logs

Structured JSON fields:
- timestamp;
- level;
- service/component;
- event code;
- correlation IDs;
- safe resource IDs;
- result/error class;
- duration;
- retry count;
- provider/model when applicable;
- deployment/release version.

No raw passwords, access tokens, provider keys, payment secrets or unrestricted private prompt/media content.

## Traces

Trace spans should cover:
- HTTP request;
- DB/storage query;
- workflow/activity submission;
- provider call/poll;
- media task;
- publish API call;
- webhook handling;
- event/notification delivery.

Do not attempt one continuously open trace spanning a 3-hour/days-long workflow. Link durable workflow/job traces using stable workflow/run/job IDs and trace links/context records.

## Metrics

Use bounded-cardinality labels. Do not use user-generated project titles, prompts or arbitrary IDs as high-cardinality metric labels.

## Initial service SLOs

These are canonical initial targets and may be revised only through an ADR/product-operations decision, not ad hoc during implementation.

### Web/API availability
`99.9%` monthly availability for authenticated control-plane API and web app core routes, excluding announced maintenance and clearly classified upstream provider outages where contract permits exclusion.

### Authentication core
`99.9%` monthly successful service availability for login/session verification endpoints under platform control.

### Control-plane latency
For non-media/non-provider synchronous API operations under normal load:
- p95 server response <= `500 ms`;
- p99 <= `1500 ms`.

Large list/search endpoints may have separately documented budgets but must remain within UI performance acceptance.

### Job acceptance
`99.9%` of valid authorized generation/render requests accepted into durable workflow control within `5 seconds`, excluding entitlement/budget/provider-unavailable intentional blocks.

### Scheduled publication dispatch
For platform-scheduled direct publishing, `99.5%` of eligible jobs begin dispatch within `5 minutes` of scheduled time, excluding platform/provider account authorization failures or external platform outages.

### Notification dispatch
`99.5%` of critical in-app notification records created within `60 seconds` of canonical source event under platform control.

### Data durability
No acknowledged canonical DB/object asset may be lost within the defined backup/durability architecture. Recovery objectives are specified in Backup/DR document.

### Provider generation quality
External provider generation success is **not** platform availability SLO. Track separately:
- provider success;
- accepted-output rate;
- fallback success;
- provider-caused failure.

This prevents an external model outage from being misreported as an API uptime failure while still making user impact visible.

## Error budgets

For each SLO:
- monthly error budget = allowed failure portion;
- burn-rate alerts at fast and slow windows;
- sustained budget burn can freeze risky releases/provider changes;
- error-budget policy is reviewed in operational status.

Example 99.9% availability yields ~0.1% monthly unavailable request/time budget according to measurement method.

## SLIs

Every SLO defines numerator/denominator from real telemetry and synthetic health probes.

Avoid using infrastructure host uptime as sole API availability SLI.

## Health endpoints

- liveness: process should be restarted or not;
- readiness: can safely receive traffic;
- dependency readiness should distinguish optional external providers from critical DB/workflow dependencies;
- deep diagnostics restricted to authorized ops/admin.

## Dashboards

Required dashboards:
1. Executive service health
2. API/web health
3. Temporal/workflow health
4. Provider routing/quality/cost
5. Media processing
6. Storage/uploads/egress
7. Publishing/social
8. Billing/entitlements
9. Security/auth
10. AI quality/evaluations
11. Release/canary comparison
12. Long-form project health

## Alert severities

### SEV0 — Critical security/data integrity emergency
Examples: confirmed cross-tenant exposure, secret compromise with active exploitation, widespread irreversible data corruption.

Immediate incident commander/security escalation.

### SEV1 — Major outage/customer impact
Examples: auth unavailable, DB/control-plane unavailable, widespread job duplication/publication duplication, severe billing corruption.

### SEV2 — Significant degradation
Examples: queue backlog, one critical worker pool unavailable, publishing delays, provider routing systematically failing without fallback.

### SEV3 — Limited/non-urgent issue
Examples: one optional integration degraded, minor dashboard lag, isolated support issue.

### SEV4 — Informational
Tracked, not paged.

## Paging policy

Only SEV0/SEV1 and selected high-confidence SEV2 alerts page an on-call human. Lower severities create tickets/status signals.

Avoid paging on single provider 429 when fallback is functioning and user SLO is healthy.

## Alert quality

Every alert includes:
- what failed;
- affected service/tenant scope where safe;
- current severity;
- SLO/error-budget context;
- dashboard/trace link;
- runbook;
- recent deployment/config/provider change;
- suggested immediate containment.

## Incident lifecycle

`DETECTED -> TRIAGED -> DECLARED -> CONTAINING -> MITIGATED -> RECOVERING -> RESOLVED -> POSTMORTEM`

Incident record:
- ID;
- severity;
- commander/roles;
- timeline;
- affected services/customers;
- hypotheses/evidence;
- containment actions;
- customer/status communications;
- recovery verification;
- follow-up tasks.

## Incident roles

For significant incidents:
- Incident Commander
- Operations/Technical Lead
- Communications Lead
- Security/Privacy Lead when relevant
- Scribe/Timeline role as team size permits.

Small team may combine roles but responsibilities remain explicit.

## Containment capabilities

Ops must be able to:
- disable provider adapter/model;
- pause public publishing;
- pause expensive generation;
- revoke compromised credentials;
- suspend workspace/account;
- roll back release/config;
- drain worker queue;
- disable feature flag;
- switch read-only/degraded mode where supported;
- preserve evidence.

## Status communication

Public status page strategy is required before production launch.

Components can include:
- Web/API
- Authentication
- Generation workflows
- Media processing
- Publishing
- Storage

Third-party providers may be shown as upstream degradation where useful.

Do not disclose tenant/security-sensitive details publicly.

## Postmortems

Required for SEV0/SEV1 and selected SEV2.

Blameless technical structure:
- impact;
- detection;
- timeline;
- root/contributing causes;
- what went well/poorly;
- why safeguards failed;
- remediation actions with owners/priorities;
- test/runbook/monitoring updates.

Security incidents may require restricted report plus public/customer summary.

## Synthetic monitoring

Production synthetic checks include:
- public landing;
- login/auth health using safe test identity;
- create/read minimal project in isolated synthetic workspace;
- enqueue/complete fake-provider job;
- signed asset delivery;
- non-public test publication adapter only where safe/sandboxed.

Synthetic checks must never accidentally publish or spend real provider credits unless specifically controlled.

## Long-form monitoring

Track per project:
- percent planned/generated/approved/rendered;
- stuck scenes/shots;
- workflow history size/continuations;
- provider retries;
- storage growth;
- estimated vs actual cost;
- render progress;
- continuity QA failure hotspots.

## Retention

Telemetry retention by class:
- high-volume traces shorter;
- metrics medium/long;
- security/audit records according to data policy;
- full private payload logging off by default.

Exact retention durations documented in deployment/privacy config before launch.

## Acceptance criteria

Implementation can determine:
- trace/log/metric model;
- initial SLO numbers and SLIs;
- error-budget behavior;
- dashboards/alerts/severity;
- incident lifecycle/roles/containment;
- status/postmortem/synthetic monitoring;
- provider vs platform failure classification.
