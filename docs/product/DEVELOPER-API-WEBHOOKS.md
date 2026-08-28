# Developer API, Webhooks and SDK Contract

## Status

`PREDEVELOPMENT_READY`

## Product decision

The platform will be **API-capable by architecture from day one**, but public customer API access may be disabled at initial launch until authentication, quotas, billing, documentation and abuse controls are production-ready.

Canonical stance:

`INTERNAL_VERSIONED_API_FIRST -> PUBLIC_API_WHEN_ENTITLED_AND_LAUNCH_APPROVED`

This avoids a later backend redesign while preventing an immature public API from becoming a support/security liability.

## API principles

- REST/JSON + OpenAPI is the primary external contract;
- backend domain behavior is shared with web/mobile, not duplicated;
- stable resource IDs;
- explicit API versioning;
- idempotency for side-effectful operations;
- cursor pagination;
- structured machine-readable errors;
- asynchronous jobs for long-running work;
- signed upload/download flows for large media;
- least-privilege credentials/scopes;
- tenant authorization on every resource;
- no provider secrets returned to clients;
- webhook events are derived from stable canonical events.

## API surfaces

### Identity/workspace
- current user/profile;
- workspaces/members/roles where authorized;
- workspace settings safe for API exposure;
- entitlements/usage summaries.

### Projects
- create/read/update/archive project;
- project options/presets;
- content/script versions;
- status/progress;
- approvals.

### Characters/entities
- list/create/version/lock according to permissions;
- reference-pack metadata;
- no raw provider secret/reference leakage beyond safe public contract.

### Assets
- metadata/search;
- signed upload initiation;
- upload completion/validation status;
- signed download/streaming access;
- archive/delete/restore according to policy.

### Storyboard/timeline/shots
- structured plans;
- shot/take state;
- generation request;
- retry failed scope;
- approval/comparison metadata;
- export/interchange requests.

### Jobs/workflows
- job status;
- progress/steps;
- cancellation where allowed;
- retry/recovery actions;
- result/error references.

### Providers
- capability/connection state;
- connect flows normally use server-managed OAuth/secret UI rather than accepting raw credentials on every endpoint;
- routing policy/settings where authorized.

### Publishing/social
- publish packages;
- schedules;
- account targets;
- publication status;
- analytics where available.

### Billing/usage
- plan/entitlements;
- usage/credit summaries;
- invoice/subscription links/metadata;
- no direct payment-card handling through ordinary product API.

### Audit/decision history
- appropriate user-facing decision/audit records according to role/security policy.

## Versioning

Public route convention may use `/v1/...` or equivalent versioned contract.

Rules:
- additive fields generally backwards-compatible;
- breaking semantic/resource changes require new API version or explicit migration policy;
- deprecation announced/documented before removal;
- webhook schemas version independently but map to API resource concepts;
- SDK versions declare supported API versions.

## Authentication modes

### Browser/mobile first-party
Use product session/OIDC flow appropriate to client.

### Personal/workspace API credentials
If enabled:
- opaque API key shown only at creation;
- server stores hash/reference, not retrievable plaintext;
- named credential;
- workspace/user owner;
- scopes;
- optional expiry;
- last-used metadata;
- revoke/rotate;
- step-up auth on creation/revocation.

### OAuth for third-party apps
Future public integration framework can support OAuth clients with:
- registered redirect URIs;
- PKCE;
- scopes;
- client types;
- consent screen;
- token revocation;
- app review for sensitive scopes.

Do not build custom OAuth authorization server unless product demand justifies it; use a proven identity architecture compatible with this contract.

## Scope model

Example scopes:
- `projects:read`
- `projects:write`
- `generation:execute`
- `assets:read`
- `assets:write`
- `characters:read/write`
- `publishing:read`
- `publishing:write`
- `analytics:read`
- `workspace:read`
- `members:manage`
- `billing:read`
- `webhooks:manage`

High-risk scopes may be unavailable to personal tokens or require stronger plan/admin policy.

Scopes never bypass resource-level RBAC/entitlements.

## Idempotency

Required for operations such as:
- create project;
- generation request;
- retry job;
- create publish schedule;
- billing-affecting product usage reservation if externally exposed;
- destructive/archive actions where replay risk exists.

Client supplies idempotency key; server stores outcome/fingerprint for bounded retention and rejects incompatible reuse.

## Async operation pattern

Long-running action returns:
- accepted HTTP response;
- job/resource ID;
- status URL/resource;
- optional estimated state, not guaranteed completion time;
- webhook/event option when public webhooks enabled.

Do not hold HTTP request open for multi-minute generation/render.

## Error model

Structured error fields:
- stable error code;
- HTTP status;
- safe human message;
- field errors;
- retryable flag;
- request ID;
- relevant resource/job ID;
- rate-limit/retry metadata when appropriate.

Examples:
- `AUTHENTICATION_REQUIRED`
- `FORBIDDEN`
- `ENTITLEMENT_REQUIRED`
- `BUDGET_APPROVAL_REQUIRED`
- `PROVIDER_UNAVAILABLE`
- `RESOURCE_VERSION_CONFLICT`
- `VALIDATION_FAILED`
- `RATE_LIMITED`
- `JOB_NOT_RETRYABLE`

Never return raw provider stack traces/secrets.

## Pagination/filtering

- cursor pagination;
- bounded page size;
- stable sort fields;
- filters explicitly supported per resource;
- search is tenant-scoped;
- no arbitrary database query/filter language exposed initially.

## Rate limits and quotas

Rate limiting considers:
- credential/user;
- workspace;
- endpoint/action class;
- IP/risk where appropriate;
- plan entitlement;
- generation concurrency/budget separately.

Response exposes standardized retry metadata.

Expensive AI operations use job/concurrency/budget gates, not just request-per-second throttles.

## Large media

API does not proxy ordinary multi-GB uploads/downloads through JSON.

Flow:
`Request upload -> server authorizes and creates Asset/Upload session -> signed multipart/resumable object-storage upload -> complete -> validation/quarantine/probe -> usable asset`

Downloads/streaming use authorized short-lived signed URLs or controlled CDN tokens.

## Outgoing webhooks

Workspace can register endpoints when plan/feature permits.

Webhook subscription fields:
- ID;
- workspace;
- endpoint URL;
- subscribed event types;
- secret/version;
- active/disabled state;
- creation actor;
- failure state;
- delivery history.

### Delivery
- HTTPS only in production unless explicitly internal/dev;
- signed payload;
- event ID + timestamp;
- delivery ID;
- versioned schema;
- bounded timeout;
- retry with exponential backoff/jitter;
- dedupe/event idempotency expected from consumers;
- disable/pause after persistent failure according to policy.

### Security
- webhook URLs pass SSRF-safe validation;
- secret shown at creation/rotation only;
- signature verification docs/examples;
- replay protection guidance;
- no sensitive internal fields;
- test-delivery feature.

## External webhook event families

Initial candidates:
- `project.status_changed`
- `job.completed`
- `job.failed`
- `asset.approved`
- `approval.requested/resolved`
- `publish.published/failed`
- `usage.threshold_reached`

Security/billing events exposed only after explicit product/security decision.

## Inbound provider webhooks

Provider callbacks are internal integration endpoints, not part of customer developer API. They use provider-specific verification and map into canonical jobs/events.

## SDK strategy

When public API launches:
- generated/maintained TypeScript SDK first because web/mobile/customer ecosystem likely benefits;
- Python SDK next for AI/automation users;
- other languages only with demand.

SDK wraps transport/types/idempotency/pagination but does not hide canonical asynchronous job behavior.

OpenAPI remains source for generated types where practical; handwritten ergonomic layers may sit above it.

## Developer portal

Public API launch requires:
- getting started;
- auth/scopes;
- API reference;
- webhooks/signature verification;
- pagination/idempotency/errors;
- job lifecycle;
- media upload examples;
- changelog/version/deprecation;
- rate limits;
- SDK links;
- sandbox/test mode documentation;
- status/support route.

## Sandbox/test mode

Prefer product sandbox/fake provider paths so developers can test without uncontrolled provider spend.

Sandbox objects are explicitly tagged and cannot accidentally publish publicly or charge production credits unless a deliberate live transition occurs.

## API entitlements and billing

Entitlement keys can control:
- API enabled;
- request rate;
- number of credentials;
- webhook endpoints;
- generation concurrency;
- SDK/support tier.

API usage may be metered separately from AI/provider usage.

## Audit

Record:
- credential create/revoke;
- OAuth app authorization/revoke;
- webhook create/rotate/disable;
- privileged API actions;
- repeated authorization failures/security signals.

## Launch gates

Public API remains `DISABLED` until:
- auth/RBAC/security packs implemented;
- rate limiting/idempotency tested;
- API version/contract stability acceptable;
- documentation exists;
- billing/entitlement model ready if monetized;
- abuse/support process exists;
- webhook delivery security/operations ready.

First-party web/mobile may still consume the same internal versioned API contract before public API launch.

## Acceptance criteria

Implementation can determine without new planning:
- public API product stance;
- resource surfaces;
- auth/scopes;
- versioning/errors/pagination/idempotency;
- async job/media upload patterns;
- webhooks/security/retries;
- SDK/developer portal/sandbox strategy;
- launch-disable behavior.
