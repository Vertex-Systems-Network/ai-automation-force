# M13 — Mobile and Public API Product

## Objective

Ship the mobile companion and, when launch gates are satisfied, expose the already-versioned backend as a supported public developer API with API credentials, webhooks, SDKs and developer documentation.

## Entry criteria

- P0 complete.
- M01–M12 accepted.
- Explicit M13 consent.
- Current Expo/React Native/app-store/auth/API-security requirements revalidated.

## Dependencies

`M11 web/auth/workspace + M12 publishing + Pack F/K -> M13`

## Work packages

### M13-WP1 — Mobile application scaffold
- Expo/React Native TypeScript app;
- navigation;
- generated API client;
- environment/config;
- secure storage;
- theme/localization/accessibility foundations;
- error/offline handling.

### M13-WP2 — Mobile auth/session/security
- login/signup where appropriate;
- Google/Apple;
- MFA/passkeys where supported;
- secure token/session lifecycle;
- workspace switch;
- biometric/app-lock option;
- session/device management;
- reauth/step-up for sensitive actions.

### M13-WP3 — Mobile project/status/review
- Home/active jobs;
- project overview/progress;
- storyboard review;
- character/keyframe/take viewers;
- image/video/audio proxy playback;
- comments;
- approval center;
- stale-version approval protection.

### M13-WP4 — Mobile alerts/publishing/control
- push notifications;
- deep links;
- provider/cost/budget alerts;
- retry/cancel eligible jobs;
- publication review/approve/schedule/status;
- lightweight safe edits only.

### M13-WP5 — Mobile upload/offline/degraded
- signed/resumable image/audio/video reference upload;
- camera/photo permissions contextually;
- cached recent state;
- stale/offline indicators;
- online-only privileged actions;
- reconciliation on app resume.

### M13-WP6 — Public API credential/scopes layer
When public API launch enabled:
- personal/workspace API credentials;
- hashed secret storage;
- scopes;
- expiry/rotation/revoke;
- rate limits;
- audit;
- entitlement gating;
- optional third-party OAuth app foundation only if included launch scope.

If public API remains launch-disabled, first-party API contracts still stay versioned and this WP can deliver internal credential scaffolding without external exposure.

### M13-WP7 — Outgoing webhooks
- subscription management;
- allowlisted events;
- signed deliveries;
- replay/idempotency guidance;
- retries/dead-letter/disable policy;
- delivery history/test event;
- SSRF-safe endpoint validation.

### M13-WP8 — SDKs and developer portal
- TypeScript SDK first;
- Python SDK second;
- OpenAPI reference;
- auth/scopes;
- async jobs;
- media upload;
- errors/pagination/idempotency;
- webhooks;
- sandbox/fake provider examples;
- changelog/deprecation/status/support.

### M13-WP9 — Public API launch controls
- feature/entitlement flag;
- sandbox/test environment;
- abuse/rate monitoring;
- API product usage analytics;
- documentation/version stability review;
- support process;
- no public API exposure until security/operational gate passes.

### M13-WP10 — Acceptance
Mobile E2E:
- auth/MFA;
- open project;
- media review;
- approve current version;
- stale approval rejection;
- push/deep link;
- provider/budget alert;
- publication approval;
- offline cached state;
- session revoke.

API E2E if enabled:
- create credential;
- scoped request;
- idempotent generation job;
- signed upload;
- webhook delivery/signature;
- revoke credential;
- cross-tenant denial.

## Expected modules/files

- `apps/mobile/`
- public API credential/webhook modules;
- generated SDK packages;
- developer docs portal/static docs;
- mobile/API E2E tests.

## Data/migration impact

Adds mobile push/device metadata, API credentials/scopes, webhook subscriptions/deliveries, developer app records if OAuth apps enabled.

## API/UI impact

Mobile consumes same API. Public API may be enabled through entitlement/launch gate; no parallel duplicate backend.

## Security/cost/rights impact

- mobile secure storage;
- push payload privacy;
- deep links reauthorize;
- API key least privilege/rate limiting;
- webhook signing/SSRF controls;
- generation/publication still obey budget/rights/approval.

## Test/acceptance

Apply Master QA mobile/API/webhook/security/tenant/accessibility matrices.

## Rollout/rollback

Mobile staged through internal/beta/store tracks. API public flag can remain off or roll back without breaking first-party clients. SDK/API deprecations follow version policy.

## Exit criteria

Mobile safely monitors/reviews/approves core production and publishing, and the backend can operate as a documented, secured public API product when launch-enabled without duplicated business logic.

## Non-goals

- full desktop timeline editor on mobile;
- raw provider secrets on devices;
- offline autonomous generation/publishing;
- public OAuth ecosystem if not launch-enabled;
- unlimited/unmetered public API.
