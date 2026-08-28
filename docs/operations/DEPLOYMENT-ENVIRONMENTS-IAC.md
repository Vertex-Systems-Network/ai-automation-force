# Deployment, Environments and Infrastructure as Code

## Status

`PREDEVELOPMENT_READY`

## Reference deployment decision

The production reference architecture uses **AWS as the initial cloud**, **Temporal Cloud (or a separately approved managed Temporal deployment)** for durable workflows, and **OpenTofu** as the canonical Infrastructure-as-Code tool.

This is the default implementation plan. A future cloud substitution requires an ADR and must preserve the contracts in this document; it is not an invitation to redesign architecture during coding.

## Environment model

Canonical environments:
- `local`
- `ci`
- `dev`
- `staging`
- `production`

Optional ephemeral preview environments may exist for web-only/isolated changes but cannot receive production secrets/provider/social credentials.

## Isolation rules

Production is isolated from non-production by:
- separate AWS account or strongest feasible account boundary;
- separate VPC/network;
- separate databases;
- separate object buckets;
- separate KMS/secrets;
- separate Temporal namespace/account environment;
- separate provider/social/billing credentials;
- separate domains;
- separate analytics/monitoring environment tags.

Non-production never connects to real public social accounts by default.

## Reference AWS topology

### DNS/TLS
- Route 53 or approved DNS provider;
- ACM-managed TLS certificates;
- HTTPS only in production;
- HSTS after domain readiness.

### Edge
- CloudFront for web/static/media delivery where appropriate;
- AWS WAF for public HTTP edge protections where justified;
- private media origin access.

### Web application
Next.js production deployment as containerized service behind Application Load Balancer / edge path, rather than making business logic dependent on a proprietary serverless runtime.

Static assets may use CDN/object storage where build architecture supports it.

### API
FastAPI container service on ECS/Fargate initially.

Properties:
- stateless HTTP layer;
- horizontal scaling;
- private DB/Temporal/storage access;
- health/readiness endpoints;
- no local persistent media state.

### Temporal workers
Separate worker services/queues:
- orchestration/light activities;
- provider network activities;
- media/probe workers;
- FFmpeg render workers;
- optional GPU/local-model workers later.

Light workers may use ECS/Fargate.

Heavy FFmpeg/GPU workload can use ECS on EC2/Auto Scaling or another dedicated compute pool when Fargate economics/resource ceilings are unsuitable. Resource class is selected by job declaration, not manual operator choice.

### Temporal
Reference: Temporal Cloud for fastest durable-workflow production foundation.

Use separate namespaces for staging/production. If self-hosting is later required for contractual reasons, migration is an infrastructure ADR while workflow contracts remain stable.

### PostgreSQL
AWS RDS/Aurora PostgreSQL-compatible managed service, with PostgreSQL feature compatibility required for:
- relational state;
- JSONB where appropriate;
- pgvector support;
- PITR/backups;
- read replicas later if needed.

Do not use Aurora-specific application semantics that prevent ordinary PostgreSQL compatibility without ADR.

### Object storage
S3 for canonical media/object storage.

Use separate buckets/prefix/access policies for:
- source/private assets;
- temporary/quarantine;
- public/CDN-derived output where required;
- backups/exports if separated.

### Cache/ephemeral state
Redis/ElastiCache is **not mandatory at initial architecture**. Add only for measured needs such as rate-limit coordination, hot cache or ephemeral pub/sub where Postgres/Temporal cannot satisfy requirements cleanly.

### Event transport
Initial reference:
- PostgreSQL transactional outbox for canonical domain events;
- event dispatcher/consumer workers;
- optionally SQS/SNS/EventBridge for scalable delivery once required.

Application semantics remain defined by event contract, not AWS service behavior.

### Secrets/KMS
- AWS KMS for encryption key management;
- AWS Secrets Manager/Parameter Store for runtime secrets according to sensitivity;
- application services access through IAM roles, not static cloud credentials.

### Observability
OpenTelemetry instrumentation exports to an approved telemetry backend. AWS CloudWatch can host infrastructure/log data initially; vendor-neutral OTEL preserves future backend choice.

### Email
Transactional email provider is adapter-based. AWS SES is the reference low-level production option, but a dedicated transactional provider can be selected if deliverability/product needs justify it without changing communication contracts.

## Networking

VPC design:
- public subnets only for load balancers/NAT where needed;
- application/worker/database in private subnets;
- DB never publicly accessible;
- restrictive security groups;
- VPC endpoints for S3/Secrets where useful;
- controlled outbound egress for provider APIs;
- media sandbox workers have restricted networking.

## Regions

Default production region is not hard-coded before launch-country/data-residency decision.

Selection criteria are already defined:
- primary customer geography;
- latency;
- provider availability;
- data residency/legal;
- service feature availability;
- cost.

Once selected, region becomes IaC config/ADR, not a new architecture planning exercise.

Initial architecture is single-primary-region with tested backup/recovery. Multi-region active-active is not v1 scope.

## Domains

Plan separate domains/subdomains such as:
- public web/root domain;
- `app.` authenticated UI;
- `api.` API;
- `assets.` CDN/media where useful;
- `status.` public status page;
- `docs.` developer/help docs where enabled.

Exact brand domain selected before launch.

## Local development

Docker Compose/equivalent local stack provides:
- PostgreSQL + pgvector;
- local S3-compatible storage (e.g. MinIO) or filesystem adapter;
- Temporal dev server/container;
- API;
- workers;
- web app;
- fake provider services/fixtures.

Local dev does not require paid cloud/provider credentials for ordinary tests.

## CI environment

CI uses ephemeral services/containers:
- PostgreSQL;
- Temporal test/dev infrastructure where needed;
- fake object storage;
- fake provider/webhook servers;
- small media fixtures.

No production secrets in pull-request CI.

## Staging

Staging mirrors production architecture at reduced scale:
- real managed DB/storage/workflow where feasible;
- test provider credentials/sandboxes;
- social test/private accounts only;
- billing sandbox/test mode;
- synthetic data;
- release candidate validation.

Never clone production customer media into staging by default.

## Production deployment units

Separate independently deployable images/services:
- web;
- API;
- orchestration worker;
- provider worker;
- media/probe worker;
- render worker;
- event/notification worker;
- scheduled/reconciliation worker where not represented by Temporal schedules.

Use monorepo builds but avoid one giant all-purpose process.

## Container standards

- minimal pinned base images;
- non-root user;
- read-only filesystem where feasible;
- explicit temp mount;
- health checks;
- resource limits;
- SBOM;
- image signing/provenance where CI supports it;
- vulnerability scans;
- no build secrets in final layers.

## Infrastructure as Code

OpenTofu code under `infra/` is canonical for production infrastructure.

Structure may use modules:
- network;
- identity/IAM;
- compute;
- database;
- storage/CDN;
- secrets/KMS;
- observability;
- DNS/TLS;
- CI deploy roles.

Rules:
- no manual production resource as the undocumented canonical configuration;
- state stored remotely/encrypted/locked;
- plan reviewed before apply;
- production apply permission restricted;
- drift detection scheduled;
- destructive changes gated.

## CI/CD authentication

GitHub Actions uses OIDC/workload identity to assume scoped AWS deployment roles. Do not store long-lived AWS access keys as repository secrets when OIDC is supported.

Separate staging vs production deploy roles.

## Deployment pipeline

`PR checks -> merge main -> build immutable artifacts -> security/contract tests -> deploy staging -> smoke/E2E -> approval/automated gate -> production canary/rolling deploy -> verify -> promote or rollback`

Exact auto-promotion policy defined in Release Management.

## Database migration deployment

Sequence:
1. migration compatibility review;
2. backup/PITR healthy;
3. expand-compatible migration where possible;
4. deploy code supporting old/new schema;
5. backfill async if needed;
6. switch reads/writes;
7. contract/remove old fields in later release.

Avoid irreversible schema+code changes in one unrollbackable step.

## Worker scaling

Scale signals:
- Temporal task queue backlog/age;
- CPU/memory;
- render queue;
- provider concurrency quotas;
- workspace plan priorities.

Limits:
- provider rate/concurrency;
- global spend;
- DB/storage capacity;
- account entitlements.

Autoscaling must not turn a backlog into uncontrolled provider spend.

## GPU/local model future pool

Not required for v1. Architecture reserves dedicated GPU worker queue/compute pool. It cannot share unrestricted production secrets/network access simply because it is a worker.

## Feature flags

Use typed feature flags/config for:
- gradual feature rollout;
- provider/model enablement;
- risky workflow paths;
- public API/social/community features.

Flags are not a replacement for permissions/entitlements. Production flag changes are audited and can be rolled back.

## Configuration

Config classes:
- static code config;
- environment config;
- secrets;
- tenant settings;
- dynamic feature flags;
- provider capability registry.

Validate at startup; fail clearly on missing critical config.

## Maintenance

Planned maintenance:
- communicated where customer impact expected;
- avoids unnecessary forced downtime through rolling/compatible changes;
- status page reflects maintenance;
- scheduled publication/long-running workflows evaluated for impact.

## Capacity planning

Track:
- API request rate;
- active workflows;
- worker queue lag;
- DB connections/storage/IO;
- object storage/egress;
- FFmpeg CPU hours;
- provider concurrency;
- notification/publishing throughput.

Capacity reviews occur before crossing configured thresholds.

## Infrastructure security tests

- public ports scan/verification;
- DB not public;
- least-privilege IAM review;
- bucket public-access block for private buckets;
- signed media path test;
- secret access policies;
- network egress restrictions;
- IaC static/security scans;
- backup encryption/access;
- staging cannot assume prod role.

## Acceptance criteria

Implementation does not need to invent:
- environment topology;
- initial cloud/IaC choice;
- service deployment units;
- networking/DB/storage/Temporal topology;
- local/CI/staging/prod differences;
- CI OIDC/deployment flow;
- migration/scaling/feature-flag model;
- production isolation/security expectations.
