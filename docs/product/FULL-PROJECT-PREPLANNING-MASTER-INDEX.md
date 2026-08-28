# Full Project Preplanning Master Index

## Status

`FULL_PROJECT_PREPLANNING_IN_PROGRESS`

No executable development may start while this index contains unresolved first-time planning gaps.

## Purpose

Turn the entire product into a preplanned implementation program before coding resumes. The goal is not merely a roadmap; it is implementation-ready architecture, product behavior, UI/UX, options, data, security, AI governance, APIs, operations and acceptance criteria for the whole platform.

Mutable external facts will still be revalidated at implementation time, but no major product system should need to be invented during coding.

## Readiness classes

- `READY` — canonical spec exists and is sufficiently detailed for implementation after consent.
- `NEEDS_EXPANSION` — architecture exists but requires additional option/state/edge-case detail.
- `MISSING` — dedicated canonical spec has not yet been written.
- `DECISION_REQUIRED` — product must explicitly choose support/non-support before development.

## Existing ready or substantially ready areas

| Area | Status | Canonical source |
|---|---|---|
| Platform scope | READY | `ai-native/PLATFORM-SCOPE.md` |
| Engineering rules | READY | `ai-native/ENGINEERING-CONTRACT.md` |
| Development consent | READY | `ai-native/DEVELOPMENT-CONSENT-GATE.md` |
| Project options/wizard | READY | `docs/product/PROJECT-OPTIONS.md`, `NEW-PROJECT-WIZARD.md` |
| Content formats | READY | `CONTENT-TYPE-BIBLE.md` |
| Character/entity locking | READY | `CHARACTER-LOCK-SYSTEM.md` |
| Image generation/reuse | READY | `IMAGE-GENERATION-REUSE-SYSTEM.md` |
| Audio | READY | `AUDIO-PRODUCTION-BIBLE.md`, `ai-native/AUDIO-ROUTER.md` |
| Visual/cinematic direction | READY | `VISUAL-CINEMATIC-BIBLE.md` |
| Storyboard/shot planning | READY | `STORYBOARD-SHOT-SPEC.md` |
| Timeline/sequence engine | READY | `TIMELINE-SEQUENCE-ENGINE.md` |
| Long-form production | READY | `LONG-FORM-3H-PRODUCTION.md` |
| Provider contracts/failover | READY | `PROVIDER-CONTRACT-AND-RECOVERY.md`, `FREE-TIER-ROUTER.md` |
| Continuity QA | READY | `CONTINUITY-QA-SPEC.md` |
| Asset/media library | READY | `ASSET-MEDIA-LIBRARY.md` |
| Rights/provenance | READY | `RIGHTS-CONSENT-PROVENANCE.md` |
| Review/approval | READY | `REVIEW-APPROVAL-WORKFLOW.md` |
| Localization/dubbing | READY | `LOCALIZATION-DUBBING-SYSTEM.md` |
| Memory/learning | READY | `MEDIA-MEMORY-LEARNING-SYSTEM.md` |
| Prompt registry | READY | `PROMPT-REGISTRY-SYSTEM.md` |
| AI agent roles | READY | `AI-AGENT-ROLES.md` |
| Analytics learning | READY | `ANALYTICS-LEARNING-SYSTEM.md` |
| Public landing/auth/onboarding architecture | READY | `PUBLIC-LANDING-AUTH-ONBOARDING.md`, `AUTH-ONBOARDING-EDGE-CASES.md` |
| Landing visual content | READY | `LANDING-PAGE-VISUAL-CONTENT-MAP.md` |
| Public web launch planning | READY | `PUBLIC-WEB-LAUNCH-PLAN.md` |
| Authenticated web IA | READY conceptually | `WEB-APP-IA.md` |
| Social publishing architecture | READY conceptually | `MULTI-PLATFORM-SOCIAL-AUTOMATION.md` |
| Technology stack | READY | `docs/architecture/TECH-STACK.md` |
| GitHub↔Linear sync | READY | `docs/operations/GITHUB-LINEAR-SYNC.md` |
| Daily provider scout | NEEDS_EXPANSION/runtime verification | `docs/operations/DAILY-PROVIDER-SCOUT.md` |

## Predevelopment planning packs still required

### Pack A — Commercial SaaS and entitlements
Status: `MISSING`

Must define:
- product editions/plans;
- free/trial strategy;
- BYOK vs platform-funded provider usage;
- feature entitlement matrix;
- seats/workspaces/projects limits;
- generation credits/meters/ledger;
- storage/concurrency/resolution limits;
- social account limits;
- plan enforcement/degraded behavior;
- checkout/subscription/invoice/payment-failure lifecycle;
- credits/refunds/adjustments;
- VAT/tax/invoice fields;
- billing support/admin workflow;
- exact launch mode if billing is deferred.

Target canonical spec:
`docs/product/COMMERCIAL-PLANS-ENTITLEMENTS-BILLING.md`

### Pack B — AI safety, agent security and evaluation
Status: `MISSING`

Must define:
- untrusted input boundaries;
- prompt injection controls;
- tool least privilege;
- memory/retrieval poisoning controls;
- excessive-agency limits;
- privileged action approvals;
- AI decision ledger;
- explain/dry-run/undo behavior;
- golden fixtures;
- model/prompt/provider regression tests;
- adversarial/red-team suite;
- canary/promotion/rollback thresholds;
- user memory governance.

Target canonical specs:
- `docs/security/AI-AGENT-THREAT-MODEL.md`
- `docs/quality/AI-EVALUATION-REGRESSION-FRAMEWORK.md`
- `docs/product/AI-DECISION-LEDGER-AND-MEMORY-CONTROLS.md`

### Pack C — Full design system and product interaction model
Status: `NEEDS_EXPANSION`

Must define:
- visual design tokens;
- component taxonomy;
- status/color semantics;
- forms/tables/media controls;
- dark/light;
- responsive behavior;
- keyboard/focus/accessibility;
- AI command center;
- command palette/search;
- notifications center;
- account/security pages;
- all global empty/error/loading/offline/conflict states;
- UI localization and RTL;
- screenshot/demo design system for landing.

Target canonical specs:
- `docs/product/WEB-DESIGN-SYSTEM.md`
- `docs/product/AI-COMMAND-CENTER.md`
- `docs/product/NOTIFICATIONS-AND-INBOX-UX.md`

### Pack D — Multi-user workspace, RBAC and collaboration
Status: `MISSING`

Must define:
- workspace lifecycle;
- ownership transfer;
- roles/permission matrix;
- invitations/removal;
- custom role stance;
- resource scoping;
- comments/mentions/annotations;
- share links;
- reviewer access;
- approval delegation;
- tenant audit logs;
- concurrency/version conflicts;
- enterprise SSO/SAML/SCIM decision.

Target canonical spec:
`docs/product/WORKSPACE-RBAC-COLLABORATION.md`

### Pack E — Notifications, event bus and communications
Status: `MISSING`

Must define:
- canonical domain event taxonomy;
- internal event transport contract;
- in-app notifications;
- transactional email;
- push/mobile;
- webhook notifications;
- preferences/digests;
- rate limiting/deduplication;
- deliverability/bounces/unsubscribe;
- security alerts;
- budget/quota/generation/provider/publish/approval events.

Target canonical specs:
- `docs/architecture/EVENTS-NOTIFICATIONS-ARCHITECTURE.md`
- `docs/product/TRANSACTIONAL-COMMUNICATIONS.md`

### Pack F — Public/developer API and outgoing webhooks
Status: `DECISION_REQUIRED`

Must explicitly decide whether external customers get programmable APIs.

If yes, define:
- auth/API keys/OAuth;
- scopes;
- rate limits;
- idempotency;
- pagination/errors/versioning;
- webhooks;
- SDK strategy;
- developer docs/portal;
- API metering/entitlements;
- deprecation policy.

If no for v1, define internal-only API boundary and future compatibility constraints.

Target canonical spec:
`docs/product/DEVELOPER-API-WEBHOOKS.md`

### Pack G — Storage, uploads, delivery and archival
Status: `NEEDS_EXPANSION`

Must define:
- multipart/resumable upload;
- direct signed uploads;
- checksum/probe/quarantine;
- derivative generation;
- proxy strategy;
- CDN/range streaming;
- signed downloads;
- temp cleanup;
- archival/restore;
- retention classes;
- account deletion/export impact;
- FFmpeg/parser sandbox and resource ceilings.

Target canonical spec:
`docs/architecture/MEDIA-STORAGE-UPLOAD-DELIVERY.md`

### Pack H — Auth hardening, security and privacy lifecycle
Status: `MISSING`

Must define:
- password/session/device rules;
- MFA/passkeys;
- bot/abuse protections;
- KMS/secrets/encryption;
- secret rotation/revocation;
- webhook validation/replay protection;
- SSRF-safe URL fetching;
- malware/malformed media handling;
- tenant isolation;
- SAST/dependency/container/SBOM/license scans;
- data classification;
- account/project export/delete;
- retention;
- backup deletion semantics;
- privacy/data residency/subprocessors;
- legal launch dependency matrix.

Target canonical specs:
- `docs/security/SECURITY-ARCHITECTURE.md`
- `docs/security/DATA-PRIVACY-LIFECYCLE.md`
- `docs/legal/PUBLIC-LAUNCH-LEGAL-REQUIREMENTS.md`

### Pack I — Observability, environments, deployment and disaster recovery
Status: `MISSING`

Must define:
- logs/traces/metrics;
- request/run/job IDs;
- dashboards;
- SLOs/error budgets;
- alerts/on-call;
- incident response;
- postmortems;
- dev/staging/prod topology;
- IaC;
- worker scaling/resource isolation;
- DB PITR/backups;
- object-store durability;
- RPO/RTO;
- DR drills;
- feature flags/canary/rollback;
- migration/release sequence;
- CI runner policy;
- release/changelog/versioning.

Target canonical specs:
- `docs/operations/OBSERVABILITY-SLO-INCIDENTS.md`
- `docs/operations/DEPLOYMENT-ENVIRONMENTS-IAC.md`
- `docs/operations/BACKUP-DR-RECOVERY.md`
- `docs/operations/RELEASE-MANAGEMENT.md`

### Pack J — Support, admin and moderation operations
Status: `MISSING`

Must define:
- internal support console;
- user/workspace lookup;
- account suspension/restoration;
- job/provider diagnostics;
- controlled replay/retry;
- billing adjustments;
- abuse/moderation cases;
- data export/delete support;
- admin impersonation stance;
- admin action audit;
- help center/support channels;
- escalation rules.

Target canonical spec:
`docs/operations/SUPPORT-ADMIN-MODERATION.md`

### Pack K — Mobile product
Status: `MISSING`

Must define:
- mobile user goals;
- navigation;
- auth/session;
- push notifications;
- deep links;
- project status;
- approvals;
- take/keyframe/character review;
- provider/cost alerts;
- publishing approval;
- safe editable fields;
- offline/degraded behavior;
- media playback/upload policy;
- explicit non-goals.

Target canonical spec:
`docs/product/MOBILE-APP-SPEC.md`

### Pack L — Product analytics and experimentation
Status: `NEEDS_EXPANSION`

Separate platform product analytics from social/content performance.

Must define:
- acquisition/onboarding funnel;
- activation;
- feature adoption;
- generation/provider failure funnels;
- retention;
- latency/performance experience metrics;
- experiment framework;
- privacy/consent;
- event naming/versioning;
- internal dashboards.

Target canonical spec:
`docs/product/PRODUCT-ANALYTICS-EXPERIMENTATION.md`

### Pack M — Social community/replies and moderation stance
Status: `DECISION_REQUIRED`

Publishing is planned, but community automation needs an explicit stance:
- comments/replies ingestion;
- AI-assisted reply drafts;
- auto-reply allowed or prohibited;
- moderation queues;
- sentiment/topic classification;
- block/report/escalation;
- platform policy differences;
- human approval thresholds.

Target canonical spec:
`docs/product/SOCIAL-COMMUNITY-AUTOMATION.md`

### Pack N — Full milestone implementation decomposition
Status: `MISSING except M1 and M12 partial`

Every milestone M1–M15 must have:
- objective;
- entry criteria;
- work packages;
- dependency graph;
- files/modules expected;
- data/migrations;
- security/cost/rights impact;
- test matrix;
- rollout/rollback;
- exit criteria;
- explicit non-goals.

Target directory:
`docs/milestones/M01/` through `docs/milestones/M15/`

### Pack O — Full QA/release acceptance matrix
Status: `MISSING`

Must define cross-project test strategy for:
- unit;
- integration;
- contracts;
- E2E;
- provider fakes;
- spend-free fixtures;
- Temporal replay/idempotency;
- DB migration rollback;
- FFmpeg fixtures;
- browsers/devices/accessibility;
- performance/load/long-form;
- security/adversarial;
- AI evals;
- social test accounts;
- billing webhooks;
- backup restore/DR;
- release gates.

Target canonical spec:
`docs/quality/MASTER-QUALITY-ACCEPTANCE-MATRIX.md`

## Mandatory planning sequence

Recommended order to close the remaining preplanning program:

1. Pack B — AI security/evaluation/governance
2. Pack H — security/privacy/auth hardening
3. Pack A — commercial/entitlements/billing
4. Pack D — workspace/RBAC/collaboration
5. Pack C — design system/AI command/product UX
6. Pack E — events/notifications/communications
7. Pack G — storage/uploads/delivery
8. Pack I — observability/deployment/DR/release
9. Pack J — support/admin/moderation
10. Pack F — developer/public API decision
11. Pack K — mobile app
12. Pack L — product analytics/experimentation
13. Pack M — community automation stance
14. Pack O — master QA/acceptance
15. Pack N — full M1–M15 implementation decomposition
16. Final end-to-end gap audit

The order can be parallelized for documentation, but development remains blocked until all packs are closed.

## Final gate checklist

Development consent must not be requested until all are true:

- [ ] all Packs A–O are `READY` or explicit `NOT_SUPPORTED` decisions;
- [ ] all major UI routes/options/states are documented;
- [ ] all external adapter contracts have fallback/error behavior;
- [ ] all persistent data domains have ownership/lifecycle rules;
- [ ] all privileged AI actions have authority/approval rules;
- [ ] all commercial limits/entitlements have a source of truth;
- [ ] all security/privacy/DR requirements are documented;
- [ ] mobile/public API/community decisions are explicit;
- [ ] M1–M15 each have implementation work packages and acceptance gates;
- [ ] master QA matrix exists;
- [ ] final audit reports no material first-time planning gap;
- [ ] `checkpoints/LATEST.md` says `FULL_PROJECT_PLANNING_READY_FOR_CONSENT`.

Only after this checklist is complete may a Development Consent Brief be presented for executable work.
