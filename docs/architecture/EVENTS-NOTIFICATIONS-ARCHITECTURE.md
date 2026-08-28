# Events and Notifications Architecture

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define the canonical event model that connects workflows, jobs, approvals, billing, providers, publishing, notifications, analytics and integrations without hard-coding direct service-to-service coupling.

This is an architecture contract. Exact transport technology may be selected during implementation from the approved stack without changing event semantics.

## Principles

- events describe facts that happened;
- commands request actions;
- events are immutable append-oriented records;
- side effects are idempotent;
- event consumers cannot bypass domain authorization;
- tenant/workspace identity is explicit;
- sensitive payloads are minimized;
- events are versioned;
- ordering requirements are declared, not assumed globally;
- retries must not create duplicate customer-facing actions.

## Event envelope

Canonical fields:
- `event_id`
- `event_type`
- `event_version`
- `occurred_at`
- `recorded_at`
- `workspace_id`
- `user_id/actor_id` optional
- `project_id` optional
- `resource_type/resource_id` optional
- `correlation_id`
- `causation_id`
- `request_id`
- `workflow_id/run_id/job_id` optional
- `source_service`
- `classification`
- `payload`
- `trace_context` optional

Secrets are never placed in event payloads.

## Event naming

Use stable domain names, e.g.:
- `project.created.v1`
- `generation.requested.v1`
- `generation.completed.v1`
- `generation.failed.v1`
- `approval.requested.v1`
- `approval.resolved.v1`
- `provider.connection.revoked.v1`
- `publish.scheduled.v1`
- `publish.verified.v1`
- `billing.payment_failed.v1`

Avoid transport/vendor names in canonical event types.

## Event domains

### Identity/security
- account created/verified;
- login/security risk;
- session revoked;
- MFA/passkey changed;
- email/password changed;
- account deletion/export requested/completed.

### Workspace/collaboration
- workspace created/restricted/deleted;
- member invited/joined/removed;
- role changed;
- ownership transferred;
- comment/mention;
- review/approval requested/resolved.

### Project/content
- project created/updated/archived/deleted;
- content version created/approved;
- character/entity locked/versioned;
- storyboard/timeline changed;
- rights/provenance status changed.

### Production/jobs
- job queued/started/progress/completed/failed/canceled;
- generation requested/attempted/accepted/rejected;
- provider fallback selected;
- render started/completed/failed;
- QA passed/failed;
- asset created/quarantined/approved/deleted.

### Provider/quota/cost
- provider connected/disconnected/degraded;
- capability changed;
- quota threshold/exhausted/reset-known;
- usage reserved/settled/released;
- spend threshold/approval required.

### Publishing/social
- social account connected/revoked;
- publish package approved;
- post scheduled/started/processing/published/failed/removed/restricted;
- manual handoff required;
- analytics sync completed/failed.

### Billing
- subscription changed;
- invoice created/paid/failed;
- payment failed/recovered;
- entitlement changed;
- credit granted/expired/adjusted;
- billing restriction applied/removed.

### Product/system
- feature flag changed;
- deployment/release event;
- provider scout material finding;
- security incident state changed;
- export ready/expired.

## Command vs event

Examples:
- Command: `GenerateShot`
- Event: `shot.generation_requested.v1`
- Event: `generation.attempt_failed.v1`
- Event: `generation.accepted.v1`

Consumers must not interpret an informational event as permission to perform a privileged action unless a domain workflow explicitly subscribes and revalidates authorization/policy.

## Delivery semantics

Assume at-least-once delivery for asynchronous consumers unless the selected transport proves stronger semantics.

Therefore every consumer must have:
- idempotency/deduplication;
- durable cursor/processed-event state when needed;
- retry/backoff;
- dead-letter/quarantine path;
- observable failure state.

Exactly-once customer side effects are achieved through idempotent business keys/state, not belief in exactly-once messaging.

## Ordering

Do not require global order.

Declare partition/order key per domain when needed, e.g.:
- workspace ID;
- project ID;
- job ID;
- subscription ID;
- publication target ID.

Consumers must tolerate delayed/out-of-order events using version/state checks.

## Outbox pattern

For DB-backed domain mutations that emit events, prefer transactional outbox/equivalent pattern so state and event intent cannot diverge silently.

Flow:
`DB transaction updates state + writes outbox -> dispatcher publishes -> consumer idempotently processes`

Exact implementation can vary, but dual-write without reconciliation is not acceptable for critical events.

## Workflow/Temporal integration

Temporal remains durable orchestration for long-running workflows.

Events are used for:
- UI notifications;
- analytics;
- decoupled integrations;
- audit/support observability;
- cross-domain triggers where appropriate.

Do not recreate Temporal workflow state machine solely through a generic event bus.

## Notification projection

A notification service consumes canonical events and applies:
- recipient resolution;
- severity/category mapping;
- preference policy;
- dedup/grouping;
- localization variables;
- channel routing;
- delivery status.

Notification record remains separate from source event.

## Recipient resolution

Based on:
- actor/owner;
- workspace/project members with permissions;
- approval assignees;
- billing/security contacts;
- notification preferences;
- explicit watcher/subscriber sets.

Mentioned users must have access to referenced resource.

## Deduplication

Canonical dedupe key examples:
- `provider_outage:{workspace}:{provider}:{incident}`
- `job_failed:{job_id}:{terminal_version}`
- `budget_threshold:{workspace}:{period}:{threshold}`

A repeated event can update/group one notification rather than generate spam.

## Event retention

Different layers have different retention:
- source business/audit records may be long-lived;
- event transport retention can be shorter;
- notification projection has product retention;
- analytics warehouse/event lake if later used has privacy policy.

Never assume the event bus is the sole historical system of record.

## Event schema evolution

Rules:
- additive backwards-compatible changes within same major event version where safe;
- breaking semantic change creates new version;
- consumers declare supported versions;
- producers do not silently repurpose fields;
- deprecation window documented;
- unknown new optional fields ignored safely;
- unknown event versions quarantine/fail predictably.

## Internal transport decision

Architecture requirements:
- durable enough for critical async events;
- supports retries/consumer groups or equivalent;
- observable lag/failures;
- tenant-safe payloads;
- integrates with Python services;
- does not become necessary for synchronous request validation.

Potential implementation could use Postgres outbox + worker/stream, managed queue/broker, or another approved transport depending production scale. Technology selection must satisfy this contract.

## Webhook event bridge

If public webhooks are enabled later:
- only explicitly allowlisted canonical event types are exposed;
- transform internal event into stable external schema;
- remove internal/sensitive fields;
- sign delivery;
- retry safely;
- provide event/delivery IDs;
- tenant subscription controls.

## Security

- producer identity authenticated;
- consumer access scoped;
- event payload authorization is not assumed merely because consumer can read stream;
- security-sensitive event channels/logs restricted;
- no raw access tokens/API keys;
- replay-sensitive actions re-check current state;
- event injection attempts are validated/schema-checked.

## Observability

Metrics:
- publish rate;
- consumer lag;
- retries;
- dead-letter count;
- processing latency;
- dedupe rate;
- notification delivery failures;
- per-event-type error rates.

Correlation IDs connect event -> workflow/job -> notification -> external delivery.

## Testing

Required:
- duplicate event does not duplicate side effect;
- out-of-order membership/billing/project events resolve safely;
- unsupported version quarantines;
- event payload cannot cross tenants;
- notification preferences respected;
- critical security notification policy overrides optional preference correctly;
- dead-letter/replay does not republish already successful social post/payment adjustment;
- event schema contract fixtures validate.

## Acceptance criteria

Implementation can determine:
- event envelope/naming/domains;
- command/event separation;
- at-least-once/idempotency strategy;
- ordering/outbox rules;
- Temporal boundary;
- notification projection;
- schema evolution/security/retention/observability;
- public webhook bridge boundary.
