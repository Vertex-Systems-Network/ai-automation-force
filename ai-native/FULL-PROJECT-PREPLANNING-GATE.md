# Full Project Preplanning Gate

## Operator requirement

No new executable development may begin or resume until the entire foreseeable product has been preplanned end-to-end.

This gate is stricter than milestone-local readiness. A milestone being individually development-ready is not sufficient to start implementation while major product areas still require first-time architecture/product planning.

## Goal

Before development resumes, the repository must contain enough canonical documentation that an implementation team can build Milestones 1–15 without needing to invent a missing product system, user flow, permission model, business rule, operational policy, AI-governance rule, data lifecycle or platform contract during coding.

Implementation-time revalidation of mutable external facts is expected and does not count as deferred product planning. Examples include current provider API versions, model availability, pricing, OAuth scopes, app-review rules, platform terms, SDK versions, browser support, tax/legal facts and security advisories.

## Global development rule

Until this gate is satisfied, repository state is:

`FULL_PROJECT_PREPLANNING_IN_PROGRESS`

and executable development remains blocked even if an older milestone-specific brief says `PLANNING_READY_FOR_CONSENT`.

When every required planning pack reaches its acceptance criteria and the final audit finds no material first-time planning gap, repository state may become:

`FULL_PROJECT_PLANNING_READY_FOR_CONSENT`

Only then may the operator be asked for executable development consent.

A generic `continue`, `next`, `resume`, `start`, or milestone-local readiness claim does not bypass this gate.

## Definition of fully preplanned

A product area is fully preplanned only when its canonical documentation defines, as applicable:

- purpose and ownership;
- user personas and actors;
- user-facing options and defaults;
- UI routes/screens/states;
- API/service/module boundaries;
- data entities and ownership;
- state machines and transitions;
- permissions/authorization;
- AI-autonomous decisions and limits;
- human approval/escalation rules;
- external integrations and adapter contracts;
- validation and error behavior;
- retry/recovery/idempotency;
- cost/budget/entitlement effects;
- security/privacy/rights requirements;
- observability/audit requirements;
- notifications/events;
- accessibility/localization requirements;
- test/evaluation/acceptance criteria;
- migration/backfill/rollback strategy;
- failure/degraded/offline behavior;
- lifecycle/retention/deletion behavior;
- launch/operational requirements;
- explicit out-of-scope decisions.

A heading in a roadmap is not enough.

## Required preplanning domains

The final preplanning program must cover all of the following before development:

### Product and media core
- platform scope and personas;
- project creation/options/presets;
- content intelligence/research/originality;
- characters/entities/worlds/props/styles;
- image generation/editing/reference reuse;
- audio/music/dialogue/SFX;
- storyboard/timeline/shot/take model;
- image/video generation routing;
- continuity/generated-media QA;
- deterministic assembly/rendering;
- long-form production up to configured three-hour limit;
- localization/dubbing/captions;
- asset/media library;
- rights/provenance/consent;
- review/approval.

### AI-native control plane
- agent roles and authority;
- orchestration/`next` semantics;
- prompt registry/versioning;
- memory/retrieval/originality;
- AI decision ledger/explainability;
- user memory inspection/correction/forget controls;
- tool permission model;
- prompt-injection and memory-poisoning defenses;
- model/provider promotion/canary/rollback rules;
- golden evaluation datasets and regression gates;
- adversarial/red-team test plan;
- human override/undo/dry-run/retry-scoped behavior.

### Provider/integration platform
- provider-neutral contracts;
- one authorized account/connection per provider by default;
- cross-provider failover without quota circumvention;
- capability registry;
- quota/cost/licensing/rights metadata;
- secrets lifecycle;
- webhooks/polling/reconciliation;
- provider onboarding/disconnect/reconnect;
- manual-handoff routes;
- current-fact evidence/revalidation policy.

### Public website and acquisition
- landing/features/use-cases/how-it-works/providers/pricing-ready pages;
- feature visuals/demo data;
- SEO/discoverability;
- conversion events;
- accessibility/performance/responsive behavior;
- trust/legal pages;
- signup/login/reset/verification;
- anti-abuse/bot handling;
- transactional email UX.

### Auth, account and workspace
- identity/account linking;
- sessions/devices;
- MFA/passkeys decision;
- workspace lifecycle;
- owner/admin/producer/editor/reviewer/viewer/billing/publishing roles;
- invitations/member lifecycle;
- project/asset/provider/social-account scoping;
- comments/mentions/review links;
- approval delegation;
- audit logs;
- enterprise SSO/SAML/SCIM position.

### Web UI/UX
- complete information architecture;
- design system/tokens/components;
- dashboard;
- projects;
- project wizard;
- AI command center;
- search/command palette;
- character/entity libraries;
- content/script editor;
- image workspace;
- audio workspace;
- storyboard;
- timeline;
- scene/shot/take inspector;
- assets;
- queue/jobs;
- providers/costs;
- QA/review;
- publishing;
- analytics;
- billing/account/security;
- notifications;
- admin/support;
- loading/empty/error/offline/conflict/permission states;
- desktop/tablet/mobile responsive rules;
- accessibility and localization/RTL.

### Mobile
- mobile personas and scope;
- navigation;
- monitoring;
- approvals;
- take/character/keyframe review;
- notifications;
- provider/cost alerts;
- publishing approval;
- offline/deep-link/push/auth behavior;
- deliberate non-goals for professional timeline editing.

### Social distribution
- YouTube;
- TikTok;
- Instagram;
- Facebook;
- X;
- LinkedIn;
- Pinterest;
- Threads;
- Vimeo;
- Dailymotion;
- Likee/manual evaluation policy;
- future platform registry;
- derivatives/metadata;
- durable scheduling;
- direct vs draft vs manual publishing;
- idempotency/reconciliation;
- analytics normalization;
- comments/community automation position;
- account/scopes/review requirements.

### Commercial SaaS
- free/trial/paid plans;
- entitlement model;
- BYOK vs platform-funded generation;
- included usage/credits;
- meters/ledger;
- storage/concurrency/resolution/social-account/seat limits;
- overage policy;
- checkout/subscriptions;
- invoices/payment failures/dunning;
- upgrade/downgrade/cancel/refund;
- taxes/VAT;
- promo/coupon/credit adjustments if supported;
- billing UI;
- billing webhooks/idempotency;
- commercial audit/support flows.

### Notifications and communications
- canonical event taxonomy;
- in-app notifications;
- transactional email;
- optional push/mobile;
- outgoing customer webhooks if enabled;
- preferences/digests;
- quiet hours if supported;
- security alerts;
- budget/quota/provider/publish/approval/job events;
- deliverability/bounce/unsubscribe behavior.

### Developer/public API
- explicit decision whether customer-facing API is offered;
- REST/OpenAPI surface;
- auth/API keys/OAuth clients;
- scopes/rate limits/idempotency;
- pagination/errors/versioning;
- outgoing webhooks;
- SDK policy;
- developer portal/docs;
- API metering/billing if applicable;
- deprecation/version migration policy.

### Storage/media delivery
- resumable/multipart uploads;
- signed direct-to-object-storage paths;
- MIME/probe/checksum/quarantine;
- image/audio/video derivatives;
- proxy generation;
- CDN/range streaming;
- signed delivery URLs;
- lifecycle/retention/temp cleanup;
- archival/restoration;
- user export/delete impact;
- media parser/FFmpeg sandbox/resource limits.

### Security/privacy/legal
- threat model;
- auth/session security;
- secrets/KMS/encryption/rotation;
- SSRF protection;
- webhook verification/replay prevention;
- malware/media parser isolation;
- tenant isolation;
- audit/event integrity;
- dependency/secret/SAST/container/SBOM/license scanning;
- data classification;
- retention/deletion/export;
- backup deletion semantics;
- privacy/cookie policy requirements;
- acceptable use/content moderation;
- subprocessors/data residency position;
- rights/synthetic-media/platform disclosure requirements.

### Observability/operations
- structured logs/traces/metrics;
- request/run/job/workflow IDs;
- SLOs/error budgets;
- dashboards/alerts;
- incident/on-call/escalation;
- runbooks/postmortems;
- dev/staging/prod environment model;
- IaC/deployment topology;
- worker/resource isolation/autoscaling;
- DB backups/PITR/restore drills;
- object-storage durability/versioning;
- RPO/RTO/disaster recovery;
- feature flags/canary/rollback;
- migrations/release sequencing;
- CI runner policy;
- release/versioning/changelog strategy.

### Support/admin/moderation
- internal admin console;
- user/workspace lookup;
- provider/account diagnostics;
- job replay/retry tools with permissions;
- billing support adjustments;
- abuse/moderation cases;
- account suspension/restoration;
- data export/delete support;
- customer support/help-center flows;
- impersonation/admin-access audit rules.

### Quality/testing/release acceptance
- unit/integration/contract/E2E strategy;
- provider fakes and spend-free fixtures;
- Temporal replay/idempotency tests;
- DB migration/rollback tests;
- FFmpeg/media fixtures;
- browser/device/accessibility matrix;
- load/performance/long-form tests;
- security/adversarial tests;
- AI regression/evaluation gates;
- social sandbox/test-account strategy;
- billing webhook/idempotency tests;
- backup restore/DR tests;
- release acceptance matrix per milestone.

## Preplanning completion rule

The project may leave `FULL_PROJECT_PREPLANNING_IN_PROGRESS` only when:

1. every domain above has a canonical spec or an explicit documented non-goal;
2. all user-facing option matrices are enumerated;
3. all milestones M1–M15 have implementation work-package breakdowns, dependencies, acceptance gates and rollback strategy;
4. all major cross-cutting services have architecture contracts;
5. UI/UX routes and global states are mapped;
6. AI security/evaluation/governance are documented;
7. commercial/billing/entitlements are documented even if initial release chooses a free/BYOK mode;
8. security/privacy/operations/DR are documented;
9. public API/mobile/support decisions are explicit;
10. a final gap audit reports no material first-time planning gap.

## Relationship to development consent

Full preplanning does not itself authorize development.

After this gate is satisfied, the operator must still explicitly approve executable development under `ai-native/DEVELOPMENT-CONSENT-GATE.md`.

Therefore the sequence is:

`FULL_PROJECT_PREPLANNING_IN_PROGRESS`
→ `FULL_PROJECT_PLANNING_READY_FOR_CONSENT`
→ explicit operator development consent
→ executable development.
