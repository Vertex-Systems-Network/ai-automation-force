# Master Quality, Evaluation and Release Acceptance Matrix

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define one cross-project verification contract for application code, AI behavior, durable workflows, providers, media, billing, security, web/mobile UX, publishing and production operations.

A milestone or release cannot be called complete because code exists. Completion requires applicable evidence from this matrix.

## Quality principles

- test the exact artifact/commit being accepted;
- hard safety/security/data-integrity failures cannot be averaged away;
- external-provider tests have spend-free fakes plus limited real sandbox/integration evidence;
- long-running workflows are tested for replay/restart/idempotency;
- migrations test upgrade and recovery/compatibility;
- cross-tenant isolation is a hard gate;
- publishing/billing side effects must be idempotent/reconcilable;
- AI changes require evaluation/regression evidence;
- accessibility/performance/security are acceptance dimensions, not post-launch extras;
- `Not Verified` is better than inferred PASS.

## Test levels

### L0 — Static/contract
- formatting/lint;
- type checks;
- schema validation;
- OpenAPI diff;
- generated contract determinism;
- config validation;
- IaC validate/plan;
- dependency/secret/SAST scans.

### L1 — Unit
Pure domain/services/functions with fake dependencies.

### L2 — Component/integration
DB, object storage, Temporal test environment, media tools, event/outbox, auth components.

### L3 — Contract/adapter
Every external provider/social/billing/email adapter against fixtures/fake server plus current sandbox/official API when feasible.

### L4 — End-to-end
Representative user journeys across API/workflows/storage/UI.

### L5 — Non-functional
Performance/load, resilience, security, accessibility, long-form, DR.

### L6 — Production/canary acceptance
Synthetic monitoring, release canary, real environment health and bounded external integrations.

## Mandatory global hard gates

No production release when any applicable item fails:
- cross-tenant access/isolation;
- secret leakage;
- critical auth bypass;
- privilege escalation;
- duplicate payment/publish/cost settlement;
- destructive data-loss regression;
- database migration cannot safely progress/recover;
- AI privileged-action injection escape;
- unresolved critical security vulnerability;
- public publishing bypasses required approval;
- billing entitlement grants/revokes incorrectly in critical path;
- backup/restore health required for a stateful high-risk release is unavailable.

## Python backend baseline

Per affected package:
- Ruff/lint;
- strict type checks per project policy;
- pytest unit/integration;
- Pydantic/JSON Schema contract fixtures;
- property/invariant tests for critical domain rules;
- coverage is informative, not a substitute for scenario quality.

Hard-domain cases:
- invalid IDs/references;
- duration boundaries;
- tenant scope;
- state transitions;
- idempotency;
- money/credit arithmetic;
- timezone/date behavior;
- concurrency/version conflict.

## TypeScript web/mobile baseline

- TypeScript strict;
- lint;
- component/unit tests for complex state;
- generated API contract compile;
- E2E via Playwright for web critical journeys;
- mobile integration/E2E framework selected at implementation but scenarios are fixed here;
- no unhandled console/runtime errors in acceptance journeys.

## Database tests

### Schema/migration
- empty DB upgrade from initial;
- upgrade from previous supported production version;
- migration rerun/idempotency where relevant;
- downgrade only where explicitly supported;
- forward-recovery path tested when downgrade unsafe;
- constraints/indexes/FKs;
- long-running/backfill behavior;
- no table lock/downtime beyond release plan.

### Persistence round trips
- 2-minute song;
- 10-minute storyboard;
- 90-minute movie plan;
- 180-minute plan boundary;
- character/version/lock;
- asset/rights;
- job/attempt/QA/cost;
- publication/analytics;
- billing/entitlement/usage.

### Concurrency
- optimistic version conflict;
- duplicate requests;
- simultaneous approvals;
- credit reservation race;
- duplicate webhook/event.

## Tenant isolation suite

Required against every data plane:
- SQL/repository;
- object storage/signed URLs;
- vector/semantic retrieval;
- cache;
- Temporal/job lookup;
- provider/social account mapping;
- analytics/reporting;
- support/admin paths;
- share/review links;
- API credentials.

Synthetic Workspace A/B fixtures deliberately attempt cross-access.

## Temporal/durable workflow suite

- worker process killed and restarted;
- API restarts;
- activity timeout;
- provider 429/5xx;
- manual approval wait;
- cancellation;
- quota wait;
- retry ceiling;
- circuit breaker;
- continue-as-new/long history;
- workflow replay against old histories after code change;
- duplicate activity completion/webhook;
- 100-shot fan-out/join;
- no duplicate accepted asset/cost/publication after replay.

## Provider adapter contract matrix

Every image/video/audio/TTS/provider adapter tests:
- capability discovery/config;
- auth success/failure;
- request normalization;
- structured provider response mapping;
- async poll/webhook;
- rate limit/quota;
- timeout/network;
- provider 4xx/5xx;
- malformed response;
- partial output;
- moderation/policy refusal;
- cost/usage normalization;
- rights/commercial metadata;
- cancellation where supported;
- fallback eligibility;
- unknown model/capability fail closed.

Use fake provider to exercise all cases without spend.

Real provider acceptance uses small bounded fixtures and explicit test budget/credentials.

## Image generation/reuse QA

- candidate generation;
- image validation;
- character/reference identity;
- aspect/resolution;
- rights/provenance;
- edit creates new version;
- original not overwritten;
- approved image becomes first/end/reference input;
- cross-provider handoff preserves canonical references;
- rejected image excluded from approved downstream routing unless explicitly selected.

## Character/continuity QA

Fixtures cover:
- face identity;
- body/proportions;
- hair/eyes/skin/fur;
- wardrobe/accessories;
- environment/props;
- lighting/palette;
- screen direction;
- camera/action;
- temporal first/end state;
- multi-provider drift.

Hard locked-identity mutations reject/regenerate affected take only.

## Audio QA

- narration/TTS text fidelity;
- pronunciation dictionary;
- voice assignment/version;
- dialogue timing;
- music structure/BPM/key metadata where applicable;
- clipping;
- loudness normalization target;
- channel/sample-rate validity;
- silence/dropout;
- stem alignment;
- ducking;
- subtitle/transcript timing;
- localization/dubbing duration/lip-sync tolerance.

Exact loudness/output technical targets are defined per delivery preset and verified deterministically.

## FFmpeg/media suite

Small deterministic media fixtures test:
- probe;
- trim;
- concat;
- transitions;
- scale/crop/pad;
- aspect variants;
- audio mix/duck;
- subtitle burn/sidecar;
- thumbnail/poster;
- proxy;
- final encode;
- corrupted input;
- timeout/resource ceiling;
- cancellation/cleanup;
- reproducible manifest/hash where deterministic inputs/settings permit.

## Long-form tests

Project scales:
- 2 min;
- 10 min;
- 30 min;
- 60 min;
- 90 min;
- 120 min;
- 180 min.

Measure:
- DB query behavior;
- timeline virtualization;
- workflow history;
- context scoping;
- memory retrieval;
- object count/storage;
- incremental render;
- restart/recovery;
- partial regeneration;
- cost estimate/reservation;
- final assembly.

Three-hour support acceptance does not require one model call; it requires orchestrated project completion without architectural failure.

## Auth/security suite

Map tests to current security baseline (including OWASP ASVS-style controls where applicable):
- signup/login/reset/verify;
- account enumeration resistance;
- password/session rules;
- passkey/MFA;
- OAuth state/nonce/PKCE/link collision;
- CSRF/CORS;
- XSS/injection;
- SSRF;
- upload/malicious media;
- webhook signature/replay;
- rate limiting;
- step-up auth;
- session revoke;
- secret redaction;
- security headers;
- API key scopes;
- tenant isolation;
- admin privilege/audit.

## AI security/adversarial suite

Use Pack B fixtures:
- direct prompt injection;
- indirect web/document injection;
- social comment injection;
- image/audio embedded instruction;
- malicious tool output;
- memory poisoning;
- excessive agency;
- paid overspend attempt;
- publish without approval;
- secret extraction;
- cross-tenant ID;
- recursion/unbounded consumption.

Target for privilege/security hard failures: zero successful escapes in release suite.

## AI evaluation suite

Every changed prompt/model/provider/agent stack runs applicable:
- golden task fixtures;
- known failure regressions;
- adversarial suite;
- structured-output rate;
- quality rubrics;
- human preference/calibration where needed;
- cost/latency benchmark;
- baseline comparison;
- canary rules.

AI model judge cannot be sole hard-gate authority.

## Billing/entitlement suite

- plan entitlement resolution;
- trial overlay/expiry;
- upgrade/downgrade;
- seat/storage/concurrency limits;
- BYOK vs platform credit funding;
- reserve/settle/release/reverse usage;
- duplicate workflow/webhook no double charge;
- failed attempt policy;
- refund/credit adjustment;
- past-due/grace/restriction;
- invoice/payment webhook reconciliation;
- external billing outage;
- restore/reconciliation after DB PITR.

Use billing provider test mode/fake webhooks.

## Social publishing suite

Per platform adapter:
- account auth/scopes;
- capability state;
- metadata validation;
- media variant;
- direct vs draft/manual route;
- scheduling;
- publish request;
- external processing;
- verification;
- idempotent retry;
- token expiry;
- rate limit;
- rejection;
- deletion/edit if supported;
- analytics ingestion.

Cross-platform campaign failure on one target must not duplicate successful targets.

Real tests use private/test accounts and non-public defaults wherever possible.

## Community automation suite

- ingestion;
- classification;
- prompt injection block;
- hard-risk no-auto-send;
- low-risk allowlist;
- human edit/approval;
- rate/spam ceiling;
- duplicate event no duplicate reply;
- deleted source;
- platform capability missing -> manual;
- support/moderation escalation.

## Event/notification suite

- transactional outbox atomicity;
- duplicate/out-of-order event;
- schema versioning;
- consumer replay;
- dead-letter;
- notification recipient authorization;
- preference/digest;
- security mandatory messages;
- email escaping;
- bounce/suppression;
- push deep-link auth;
- webhook delivery signing/retry.

## Storage/upload suite

- signed upload authorization;
- multipart resume;
- wrong MIME/magic;
- oversized/malformed/malware fixture;
- hash/probe;
- proxy/derivative lineage;
- signed download tenant isolation;
- CDN/private access;
- temp cleanup;
- archive/restore;
- export;
- deletion propagation;
- egress/quota.

## Web UX E2E

Critical journeys:
1. Landing -> signup -> verify -> onboarding -> first project
2. Login/reset/passkey/MFA
3. Project wizard with conditional options
4. Character create/lock/reuse
5. Image candidates -> approve -> video reference
6. Storyboard/timeline review
7. Generation -> progress -> failed-scope retry
8. Take compare/approve
9. Cost/budget approval
10. Final render/export
11. Connect social -> publish package -> approve/schedule
12. Notifications/inbox/action
13. Billing upgrade/downgrade/payment failure when enabled
14. Team invite/role/comment/review
15. Data export/delete
16. AI Command Center explain/dry-run/execute/undo-compatible action.

## Web accessibility

Target WCAG 2.2 AA core routes.

Tests:
- automated accessibility scan;
- keyboard navigation;
- focus order/dialogs;
- screen-reader labels/announcements;
- contrast;
- zoom/reflow;
- reduced motion;
- drag/drop alternative;
- media captions/transcripts;
- RTL/localization layouts.

Automated scan does not replace manual critical-route testing.

## Browser/device matrix

Web current supported baseline is defined at implementation based on market/security support, but acceptance includes current major desktop versions of:
- Chrome/Chromium;
- Edge;
- Firefox;
- Safari/macOS;
plus representative tablet/narrow web for review flows.

Exact minimum versions are mutable support facts and revalidated per release policy.

## Mobile acceptance

Representative current supported iOS/Android versions/devices, including:
- auth/MFA;
- push/deep links;
- approval stale-version protection;
- media playback;
- workspace switching;
- offline stale view;
- session revoke;
- publication approval;
- accessibility/dynamic type.

## Performance/load

### API
Verify SLO latency under planned baseline load plus headroom.

### Workflows
Backlog/worker autoscaling under burst; no uncontrolled provider spend.

### DB
Query/index plans for large projects/assets/history.

### Web
Core Web Vitals/public landing and app interaction budgets defined during UI implementation but cannot regress beyond release thresholds.

### Timeline
Virtualization for thousands of shots/clips without loading all full media.

### Storage
Concurrent multipart uploads/downloads and CDN behavior.

## Resilience/chaos tests

Controlled non-production scenarios:
- kill API/worker;
- DB connection interruption;
- object store transient failure;
- provider outage/rate limit;
- event consumer down;
- email provider down;
- Temporal activity failure;
- network timeout;
- render worker OOM;
- deployment rollback.

Verify no duplicate side effects and safe recovery.

## Backup/DR acceptance

- monthly restore test;
- quarterly full recovery drill;
- RPO/RTO measured;
- object hash validation;
- external side-effect reconciliation simulation;
- deletion tombstone behavior after restore;
- failover/degraded mode.

## Release evidence bundle

Every milestone/release stores:
- exact commit/artifacts;
- tests run/results;
- known skipped/not-verified items;
- security/eval results;
- migrations;
- canary metrics;
- rollout/rollback status;
- known risks;
- approval records.

## Milestone acceptance template

Each milestone declares which matrix sections apply plus milestone-specific exit scenarios.

Status vocabulary:
- `PASS`
- `FAIL`
- `NOT_APPLICABLE`
- `NOT_VERIFIED`.

`NOT_VERIFIED` is never treated as PASS.

## Test data

Prefer:
- synthetic users/workspaces;
- generated/public-domain-safe media fixtures;
- fake providers;
- test billing/social accounts;
- deliberately malicious security fixtures isolated from production memory.

Production customer data only when authorized and minimized.

## CI cost control

Fast PR suite:
- static/unit/core integration/fakes/security basics.

Scheduled/nightly suite:
- heavier media;
- long workflow;
- provider sandbox bounded tests;
- browser matrix;
- AI evals.

Pre-release suite:
- full applicable acceptance.

No test suite may unexpectedly consume unbounded paid AI credits.

## Acceptance criteria

This master matrix is complete when every planned subsystem has:
- appropriate test levels;
- hard failure gates;
- representative end-to-end scenarios;
- security/AI/provider/media/billing/social checks;
- non-functional/DR coverage;
- evidence/status vocabulary;
- exact linkage into milestone exit criteria.
