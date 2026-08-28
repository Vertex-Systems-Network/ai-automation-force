# Commercial Plans, Entitlements, Usage Metering and Billing

## Status

`PREDEVELOPMENT_READY`

This document defines the commercial SaaS contract before implementation. The runtime entitlement and usage model is vendor-neutral. A payment/billing vendor may implement portions of this contract but must not become the canonical product authorization model.

## Principles

1. Product capability is authorized by canonical entitlements, not by frontend hiding.
2. Provider cost and customer billing are separate ledgers.
3. BYOK usage and platform-funded usage are separate funding modes.
4. No generation starts if the applicable entitlement, budget or credit gate fails.
5. Usage is idempotent and auditable from reservation through settlement/refund.
6. A billing provider outage must not corrupt product state.
7. Plan changes never silently delete customer assets/projects.
8. Exact prices, taxes and billing-provider APIs are mutable commercial facts and must be revalidated before implementation/launch.

## Commercial model

Launch architecture supports these product editions without hard-coding prices:

- `FREE` — onboarding/evaluation with restrictive limits and BYOK-first behavior.
- `CREATOR` — individual creator plan.
- `PRO` — higher concurrency, quality, storage and automation.
- `TEAM` — multi-seat/workspace collaboration and shared controls.
- `ENTERPRISE` — contractual limits, SSO/SCIM/data controls/support where enabled.
- `CUSTOM` — sales-negotiated entitlement bundle without introducing code forks.

A `TRIAL` is a time-bounded entitlement overlay, not a permanent plan type.

The initial launch may deliberately enable only a subset of editions. Unsupported editions remain registry entries with `launch_enabled=false`; no implementation must assume every edition is sold on day one.

## Funding modes

Every workspace has one generation funding policy:

- `BYOK_ONLY` — user supplies provider credentials; platform may charge subscription/software fees but does not fund provider calls.
- `PLATFORM_CREDITS_ONLY` — platform-funded providers consume canonical credits/allowances.
- `HYBRID_BYOK_FIRST` — use user-authorized provider credentials first, platform credits only when policy permits.
- `HYBRID_SMART` — route based on quality/capability/cost while respecting which source funds each attempt.
- `ADMIN_SPONSORED` — controlled internal/demo/support grants with audit trail.

Provider credentials and product billing credentials are separate secrets.

## Entitlement dimensions

Canonical entitlements are feature/limit records, not plan-name conditionals. Examples:

### Feature switches
- image generation;
- image editing/inpainting/outpainting;
- image-to-video;
- text-to-video;
- music generation;
- TTS/dialogue/dubbing;
- long-form project support;
- character locking;
- advanced continuity QA;
- premium provider access;
- social publishing;
- social analytics;
- API access;
- team collaboration;
- custom roles;
- priority workers;
- enterprise SSO/SCIM;
- custom retention/data residency where commercially supported.

### Numeric limits
- workspaces;
- seats;
- active projects;
- archived projects;
- concurrent generation jobs;
- concurrent renders;
- project duration ceiling;
- maximum source resolution;
- maximum output resolution;
- maximum FPS/bitrate class;
- storage bytes;
- monthly egress bytes;
- social accounts per workspace/platform;
- scheduled social posts;
- API requests/rate limits;
- provider connections;
- retained generations/takes;
- AI command executions where metered;
- included platform-funded usage units.

### Policy entitlements
- publishing approval required;
- spend approval threshold;
- provider allowlist;
- team approval routes;
- retention class;
- support SLA class.

## Canonical data model

### ProductPlan
- `plan_id`
- `code`
- `name`
- `version`
- `sale_status`
- `currency_strategy`
- `billing_interval_options`
- `default_entitlement_bundle_id`
- `metadata`

### EntitlementDefinition
- `entitlement_key`
- `type`: `BOOLEAN | INTEGER | DECIMAL | ENUM | SET | POLICY`
- `unit`
- `enforcement_mode`: `HARD | SOFT_WARN | APPROVAL_REQUIRED | METER_ONLY`
- `default_behavior`
- `description`

### WorkspaceEntitlement
- workspace
- entitlement key
- source (`PLAN | TRIAL | PURCHASED_ADDON | ADMIN_GRANT | CONTRACT | PROMO`)
- effective value
- starts/ends
- source reference
- precedence
- audit metadata

### Subscription
- workspace/customer
- product plan/version
- external billing references
- status
- term start/end
- cancellation mode
- trial state
- billing contact/tax profile reference

### UsageMeterDefinition
- stable meter key
- business unit
- aggregation rule
- reservation required flag
- settlement source
- refundable flag
- billable/non-billable classification

### UsageEvent
- idempotency key
- workspace/project/job/attempt references
- meter key
- quantity
- occurred/received timestamps
- funding source
- provider cost reference when applicable
- status (`RESERVED | SETTLED | RELEASED | ADJUSTED | REVERSED`)

### CreditLedgerEntry
- workspace
- credit pool
- amount/direction
- reason
- source invoice/promotion/admin adjustment
- expiry
- idempotency key
- running-balance snapshot or ledger sequence

## Metering model

Do not bill from provider invoices alone. Canonical product meters may include:

- accepted generated image units;
- attempted generation units when contract explicitly bills attempts;
- generated video seconds;
- rendered output minutes;
- audio/TTS/music seconds;
- premium-provider cost pass-through units;
- storage GB-month;
- egress GB;
- priority compute units;
- social publication units;
- API units.

A product can launch with a simpler subset. Every meter must explicitly declare whether rejected/failed provider attempts are customer-billable. Default product recommendation: platform-caused/provider-failed attempts are not charged as accepted-output credits unless commercial terms explicitly say otherwise.

## Reservation and settlement

Expensive platform-funded work follows:

`Entitlement Check -> Estimate -> Reserve -> Generate -> QA/Outcome -> Settle or Release -> Customer Usage Ledger -> Provider Cost Ledger`

Rules:
- reservation is idempotent;
- duplicate workflow replay cannot double-charge;
- failed jobs release unused reserved units;
- partial successful outputs settle only applicable units;
- refunds/adjustments are append-only ledger records, never destructive edits;
- provider cost may exceed customer charge or vice versa; margins are analytics, not authorization.

## Plan enforcement

### Hard limit
Block before side effect and explain:
- which entitlement failed;
- current usage/value;
- required value;
- allowed actions (upgrade, delete/archive, BYOK switch, wait for reset, request approval).

### Soft limit
Allow configured grace behavior and notify. Never silently increase paid spend.

### Downgrade behavior
A downgrade must not delete existing data. Possible state:
- existing projects remain readable;
- new creation/generation above limit is blocked;
- excess seats become `SUSPENDED_PENDING_ADMIN_ACTION` after defined grace;
- excess provider/social connections remain visible but disabled according to policy;
- high-resolution masters remain stored according to retention policy unless user deletes them.

## Trial

Trial fields:
- eligibility rules;
- duration;
- whether payment method required;
- trial entitlement overlay;
- trial credits;
- anti-abuse checks;
- conversion/end behavior;
- reminder notifications;
- one-trial-per-person/workspace policy according to lawful anti-abuse design.

Do not depend solely on email address for abuse prevention.

## Checkout and subscription lifecycle

Canonical states:

`PENDING -> TRIALING -> ACTIVE -> PAST_DUE -> RESTRICTED -> CANCELED`

Additional external billing-provider states are mapped into these canonical states.

Lifecycle must cover:
- checkout creation;
- successful payment;
- async payment;
- payment failure;
- retries/dunning;
- invoice finalized/paid/void/uncollectible;
- plan upgrade/downgrade;
- quantity/seat changes;
- scheduled cancellation;
- immediate cancellation where allowed;
- subscription reactivation;
- payment method updates;
- refund/credit note/adjustment;
- chargeback/dispute support workflow.

Webhook processing is signature-verified, replay-safe and idempotent; external events cannot directly bypass canonical business validation.

## Taxes and invoices

Preplan support for:
- legal/business name;
- billing address;
- tax/VAT/GST identifier;
- country/jurisdiction;
- invoice email;
- PO/reference fields where enterprise requires;
- tax-exclusive/inclusive display strategy;
- tax calculation provider or manual tax decision;
- invoice retention/download.

Tax determination is jurisdiction-specific and must be revalidated before commercial launch.

## Add-ons and grants

Possible add-ons:
- extra storage;
- extra platform credits;
- seat packs;
- priority concurrency;
- advanced publishing/account bundles.

Admin/support grants require:
- reason;
- actor;
- amount/entitlement;
- expiry;
- case/ticket reference;
- audit record.

## Billing UI

User-facing areas:
- plan and current entitlements;
- usage dashboard by meter;
- available/reserved/expiring credits;
- provider-funded vs BYOK usage;
- invoices/receipts;
- payment method;
- billing profile/tax fields;
- upgrade/downgrade/cancel;
- estimated impact before changing plan;
- payment-failure recovery;
- support contact.

Admin/support areas:
- subscription snapshot;
- entitlement resolution trace;
- ledger timeline;
- grants/adjustments;
- failed webhook/reconciliation view;
- no unaudited balance edits.

## Vendor boundary

The selected billing vendor may manage checkout, payment methods, subscriptions, invoices, taxes and/or usage billing. Canonical product state must still preserve:
- effective entitlements;
- product usage events;
- reservations/settlements;
- internal credit ledger where required;
- external mapping IDs;
- reconciliation state.

Current research note (August 2026): Stripe documents Entitlements for feature access and usage-based billing/credits. Stripe currently recommends Metronome for many new advanced usage-based integrations. This is mutable vendor guidance and not an architectural dependency.

## Reconciliation

Scheduled reconciliation compares:
- internal subscription/entitlement state;
- billing-provider subscription/invoice state;
- usage/credit state;
- failed/unprocessed webhooks.

Mismatches become cases; do not silently overwrite ambiguous canonical state.

## Security and privacy

- payment card data should remain with compliant payment provider where possible;
- never log payment secrets;
- billing webhooks use separate secrets and rotation;
- billing admin actions require privileged roles and audit;
- invoices/tax records have defined retention;
- billing contact data follows privacy lifecycle.

## Launch decision

Architecture supports paid commercialization, but launch may choose:
- `BILLING_ENABLED`;
- `INVITE_ONLY_NO_BILLING`;
- `FREE_BETA_BYOK_ONLY`.

The actual launch mode must be recorded before public launch. Even when billing is deferred, entitlement enforcement must exist conceptually so beta behavior does not become permanent architecture.

## Acceptance criteria

This pack is planning-complete when implementation can determine without chat context:
- plan/entitlement/limit representation;
- BYOK/platform-funded behavior;
- usage/credit reservation and settlement;
- failure/refund/downgrade behavior;
- subscription/payment lifecycle;
- billing UI/admin surfaces;
- security/reconciliation rules;
- launch-without-billing behavior;
- vendor abstraction boundary.
