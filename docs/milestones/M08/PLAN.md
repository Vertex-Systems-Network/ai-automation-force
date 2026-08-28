# M08 — Hybrid Image and Video Router

## Objective

Implement provider capability adapters and HYBRID_SMART routing for image/video generation so canonical requests can move across legitimate free/paid providers without losing character, scene, continuity, cost or history state.

## Entry criteria

- P0 complete.
- M01–M07 accepted.
- Explicit M08 consent.
- Current provider APIs, scopes, prices, rights and limits revalidated from official sources.

## Dependencies

`M02 workflows + M03 assets + M04 entities + M07 shot/reference plans -> M08`

## Work packages

### M08-WP1 — Runtime provider capability registry
Canonical capability records for:
- text-to-image;
- image editing/inpaint/outpaint;
- image-to-image/reference/style controls;
- text-to-video;
- image-to-video;
- first/end frame;
- character/reference features;
- max duration/resolution/aspect;
- async/poll/webhook;
- moderation;
- cost/free quota evidence;
- commercial/right posture;
- last verified timestamp.

### M08-WP2 — Provider connection and credential model
- one authorized connection/account per provider by default;
- server-side secret handles;
- token/API-key lifecycle;
- status/scopes;
- funding source;
- test/revoke/reconnect;
- no multiple-account quota-rotation design.

### M08-WP3 — Canonical generation request/attempt contract
`GenerationRequest` contains:
- asset/shot intent;
- prompt version;
- reference asset IDs;
- first/end frame;
- character/world/style locks;
- duration/aspect/resolution;
- motion/camera;
- negative/forbidden constraints;
- budget/funding;
- rights requirement.

Every provider maps into this contract and returns normalized Attempt state/cost/output refs/errors.

### M08-WP4 — Initial image adapters
Implement a small approved set, chosen at execution after current API audit. Required adapter behaviors:
- capability discovery/config;
- submit;
- async status where applicable;
- normalized outputs;
- edit/reference support;
- cost/quota/error mapping;
- cancellation when supported;
- fake adapter for tests.

Do not integrate every provider discovered.

### M08-WP5 — Initial video adapters
At least two providers capable of executing the same canonical representative shot through supported official APIs/authorized flows.

Normalize:
- text/image-to-video;
- reference/first/end frame where supported;
- duration/resolution;
- job status;
- output download;
- error/moderation/cost.

### M08-WP6 — Routing engine
Default `HYBRID_SMART` utility considers:
- capability fit;
- expected quality;
- continuity fit;
- historical acceptance;
- rights confidence;
- expected accepted-output cost;
- retry risk;
- speed/queue;
- legitimate free quota;
- watermark/manual-labor penalties;
- workspace provider policy.

Modes:
- FREE_ONLY
- FREE_FIRST
- HYBRID_SMART
- BUDGET_CAPPED
- QUALITY_FIRST

### M08-WP7 — Quota/fallback/recovery and cross-provider handoff
Flow:
`Provider A -> quota/failure/QA-retry condition -> preserve canonical request/reference state -> Provider B -> normalize -> QA`

Rules:
- successful prior shots remain untouched;
- one provider’s hidden state is never required;
- approved references/first/end frames bridge providers;
- same-provider account rotation to evade quotas prohibited;
- consumer web credits are not automated unless provider officially supports the authorized mechanism;
- ambiguous external completion reconciled before retry.

### M08-WP8 — Cost/rights/acceptance
- estimate/reserve/settle usage;
- provider cost records every attempt, including failure where cost incurred;
- rights/commercial-use gate;
- watermark/output eligibility;
- representative image generation + one shot switch across at least two video providers;
- all attempts/history retained.

## Expected modules/files

- provider registry/runtime snapshot service;
- image/video adapter packages;
- router/scoring service;
- generation workflows/activities;
- provider connection/secret integration;
- cost/quota normalization;
- contract/fake-provider tests.

## Data/migration impact

Adds provider connections/capability snapshots, generation requests/attempts, quota/cost observations, provider references and routing decisions.

## API/UI impact

Adds provider connection/status, generation request, attempts, comparison/cost/fallback APIs. Provider admin/full UI later M11.

## Security/cost/rights impact

- credentials secret-managed;
- current ToS/API evidence required;
- no quota circumvention;
- budget reservation before paid work;
- rights/commercial-use requirement can exclude provider;
- outputs validated/downloaded into canonical storage.

## Test/acceptance

- fake adapters cover every normalized failure class;
- token/quota/rate-limit;
- malformed/partial output;
- cost settlement/idempotency;
- router scoring deterministic for fixture state;
- fallback preserves references;
- two-provider same-shot acceptance;
- no duplicate paid request after replay;
- provider unavailable produces manual/wait/fallback path.

## Rollout/rollback

Adapters/model versions feature-flagged and release-gated. Provider can be disabled globally without corrupting canonical projects. Router reverts to prior registry/scoring version.

## Exit criteria

The same canonical shot/reference package can be generated through at least two approved providers and switch safely on failure/quota while retaining full provider-neutral state, cost, rights and attempt history.

## Non-goals

- every market provider;
- guaranteed pixel-identical cross-provider output;
- quota evasion/multi-account rotation;
- full multimodal continuity scoring (M09);
- final render assembly (M10).
