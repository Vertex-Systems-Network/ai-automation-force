# M08 — Hybrid Image and Video Router

## Planning authority and current hold

This document is currently a **planning-only contract**. It does not authorize provider SDK integration, schema/API/product/test implementation, migrations, credentials, paid calls, media generation, publication, security-setting mutation, or production data access.

Executable M08 remains blocked until all then-current gates are satisfied, including:

- executable M04 acceptance;
- executable M07 acceptance;
- explicit M08 executable consent;
- Issue #36/live protected-main governance where required by the accepted dependency chain;
- fresh collision-free write ownership and migration reservation where required;
- current provider APIs, authentication/scopes, prices/quotas, model availability, commercial rights/licensing, moderation and output-use restrictions revalidated from official sources.

Planning completion, deterministic fakes, green planning CI, branch synchronization, or generic conversational continuation cannot satisfy those executable gates.

## Objective

Plan provider capability adapters and HYBRID_SMART routing for image/video generation so canonical requests can later move across legitimate free/paid providers without losing character, scene, continuity, cost, rights, provenance, authority or history state.

## Entry criteria for later executable work

- P0 complete.
- Required M01–M07 executable dependencies accepted, including executable M04 and M07.
- Explicit M08 executable consent.
- Live governance and repository entry gates satisfied.
- Current provider APIs, scopes, prices, quotas, model capabilities, moderation, rights/licensing and output restrictions revalidated from official sources.
- Write ownership and any required migration IDs reserved from the then-current repository state.

## Dependencies

`M02 workflows + M03 assets + M04 entities + M07 shot/reference plans -> M08`

M07 planning/reference completion is not executable M07 acceptance. Every M07-supplied asset/entity/reference/version identifier remains subject to canonical tenant/project authorization and pinned-version/rights/provenance validation before later M08 execution.

## Cross-cutting trust boundary

M08 introduces a high-risk external provider boundary. Future execution must preserve these invariants:

1. **Provider/model output is untrusted evidence.** Returned IDs, URLs, filenames, MIME/type claims, dimensions, metadata, JSON, moderation labels, transcripts/OCR and natural-language instructions require schema validation and canonical policy checks before use.
2. **Returned IDs never grant authority.** Every entity, asset, shot, audio, keyframe, reference, version, connection or provider-returned resource ID must be looked up canonically and re-authorized for the active workspace/project.
3. **Generated/imported text cannot mint privilege.** Prompts, provider output, embedded media text, OCR/transcripts or model recommendations cannot create tool, publish, budget, approval, account or security authority.
4. **Secrets remain references.** Raw API keys, OAuth tokens, signing credentials and provider secrets stay in server-side secret resolution and must not enter ordinary prompts, model memory, generated artifacts, manifests, decision ledgers or logs.
5. **Rights/provenance survive routing.** Cross-provider fallback or regeneration must preserve exact reference/version lineage, ownership, consent, likeness/voice rights and commercial-use eligibility.
6. **Retries/fallbacks are bounded.** Attempt count, elapsed time, provider fan-out and money require explicit ceilings, idempotency, circuit-breaking and budget reservation.
7. **Ambiguous completion fails closed.** If an external request may have completed but acknowledgement is lost, reconcile before retrying, switching provider or settling spend; do not create duplicate paid generation.
8. **Unknown capability cannot be silently substituted.** Unsupported/unknown operations fail explicitly or require an authorized alternative; a provider/model may not infer a privileged substitute.
9. **Canonical storage is the trust anchor.** Provider-hosted URLs/hidden state are temporary evidence only. Eligible outputs are validated, downloaded and recorded through canonical asset authority before later reuse.
10. **Source acceptance is not production truth.** Fakes may prove contracts; missing live provider/admin/production evidence remains NOT_VERIFIED until an explicit later gate requires and obtains it.

## Work packages

### M08-WP1 — Runtime provider capability registry

Plan canonical capability records for:

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
- watermark/output-use restrictions;
- capability source/provenance and last verified timestamp.

Rules:

- capability evidence is provider/model/version scoped and freshness-stamped;
- unknown/stale capability is not equivalent to supported;
- provider marketing prose or model-generated descriptions are not canonical capability authority;
- execution later revalidates material volatile fields rather than freezing discovery-time assumptions indefinitely.

### M08-WP2 — Provider connection and credential model

Plan:

- one authorized connection/account per provider by default;
- server-side secret handles only;
- token/API-key lifecycle;
- non-secret readiness/status/scopes;
- funding source;
- test/revoke/reconnect;
- workspace/project authorization boundaries;
- no multiple-account quota-rotation design.

Raw secret values must not be persisted in canonical generation requests/attempts, prompts, manifests or logs.

### M08-WP3 — Canonical generation request/attempt contract

`GenerationRequest` later contains only canonically authorized/pinned inputs such as:

- workspace/project/asset/shot intent;
- prompt version;
- reference asset/version IDs;
- first/end frame references;
- character/world/style locks with pinned version lineage;
- duration/aspect/resolution;
- motion/camera;
- negative/forbidden constraints;
- budget/funding ceiling and authority reference;
- rights/consent/commercial-use requirement;
- stable idempotency/business-operation key.

Every provider maps into this contract and returns normalized Attempt evidence:

- provider/model/version and connection reference;
- request fingerprint/idempotency lineage;
- submitted/started/finished timestamps;
- normalized status/error class;
- observed quota/rate/cost evidence;
- provider references as non-authoritative provenance;
- output candidates pending validation/canonical ingest;
- ambiguity/reconciliation state;
- actual settled cost when known.

Provider IDs/URLs must never become the canonical operation key or bypass tenant/project authorization.

### M08-WP4 — Initial image adapters

Later executable work may integrate a small approved set selected only after a fresh official API audit. Required adapter behaviors:

- capability discovery/config;
- submit;
- async status where applicable;
- normalized outputs;
- edit/reference support;
- cost/quota/error mapping;
- cancellation when supported;
- strict schema/type/size/output validation;
- canonical ingest handoff;
- fake adapter for deterministic source tests.

Do not integrate every provider discovered. Unknown/unsupported capability must fail explicitly rather than silently selecting another privileged operation.

### M08-WP5 — Initial video adapters

Later executable acceptance requires at least two approved providers capable of executing the same canonical representative shot through supported official APIs/authorized flows.

Normalize:

- text/image-to-video;
- reference/first/end frame where supported;
- duration/resolution;
- job status;
- output download;
- error/moderation/cost;
- provider/model/version provenance;
- ambiguous/lost-ack reconciliation.

Provider output metadata remains untrusted until validated and canonically ingested.

### M08-WP6 — Routing engine

Default `HYBRID_SMART` utility may later consider only authorized/canonical evidence:

- capability fit and freshness;
- expected quality;
- continuity fit;
- historical acceptance from tenant-authorized evidence;
- rights/commercial-use confidence;
- expected accepted-output cost;
- retry/ambiguity risk;
- speed/queue/rate-limit evidence;
- legitimate free quota;
- watermark/manual-labor penalties;
- workspace provider policy;
- budget authority and remaining reservation;
- provider/connection circuit state.

Modes:

- FREE_ONLY
- FREE_FIRST
- HYBRID_SMART
- BUDGET_CAPPED
- QUALITY_FIRST

Routing output is a recommendation/decision record, not new authority. It cannot override budget, rights, tenant, publish, security or explicit consent gates.

### M08-WP7 — Quota/fallback/recovery and cross-provider handoff

Planned flow:

`Provider A -> known retry-safe quota/failure/QA condition -> preserve canonical request/reference state -> authorized Provider B -> normalize -> validate -> QA`

Rules:

- successful prior shots remain untouched;
- one provider’s hidden state is never required;
- approved canonical references/first/end frames bridge providers;
- every bridged reference is re-authorized and pinned to exact lineage/version;
- same-provider account rotation to evade quotas is prohibited;
- consumer web credits are not automated unless provider officially supports the authorized mechanism;
- retries/fallbacks/fan-out/time/cost are bounded;
- paid retries require remaining budget reservation/authority;
- a permanent rights/policy/authorization failure is not converted into a retryable provider-selection problem;
- ambiguous external completion reconciles before retry/fallback and may not trigger duplicate paid work;
- circuit-open/unavailable state yields wait/manual/authorized fallback, never uncontrolled fan-out.

### M08-WP8 — Cost/rights/acceptance

Later executable work must:

- estimate/reserve/settle usage idempotently;
- record cost evidence for every attempt where cost may be incurred, including failures;
- fail closed when budget authority/reservation is insufficient;
- enforce current rights/commercial-use/consent requirements before dispatch and before canonical reuse;
- enforce watermark/output eligibility;
- preserve provider/model/version, input reference lineage and output provenance;
- demonstrate representative image generation and one authorized shot switch across at least two video providers;
- retain all attempt/reconciliation/history evidence without granting provider output canonical authority.

## Expected modules/files for later executable work

- provider registry/runtime snapshot service;
- image/video adapter packages;
- router/scoring service;
- generation workflows/activities;
- provider connection/secret integration;
- cost/quota normalization;
- canonical output validation/ingest handoff;
- contract/fake-provider tests.

This planning slice creates none of those executable surfaces.

## Data/migration impact for later executable work

Expected future data may include provider connections/capability snapshots, generation requests/attempts, quota/cost observations, provider references, routing decisions and reconciliation state.

No migration is reserved or authorized by this planning document. Any future migration IDs must be reserved only after executable authority exists and the then-current migration head/write ownership is re-audited.

## API/UI impact for later executable work

Potential future surfaces include provider connection/status, generation request, attempts, comparison/cost/fallback APIs. Provider admin/full UI remains later M11.

No API/UI change is authorized by this planning slice.

## Security/cost/rights impact

Future implementation must ensure:

- credentials are secret-managed and resolved outside ordinary provider/model-visible state;
- current ToS/API/rights/licensing evidence is required at executable entry and revalidated when stale/materially changed;
- no quota circumvention;
- budget reservation before paid work and bounded spend through retries/fallbacks;
- rights/consent/commercial-use requirements can exclude a provider/model/output;
- returned IDs/URLs/metadata/instructions are untrusted;
- cross-tenant/project references are denied canonically;
- output validation/download/canonical ingest precedes accepted reuse;
- provider/model output cannot grant publish, budget, account or security authority;
- generated media/OCR/transcript instructions remain low-trust evidence.

## Test/acceptance obligations for later executable promotion

Targeted tests must be added only when M08 execution is authorized. They must include at least:

- fake adapters for every normalized failure class;
- unknown/stale capability fails closed;
- foreign tenant/project/entity/asset/reference/provider-returned IDs rejected;
- provider URLs/metadata cannot bypass canonical ingest/authorization;
- token/quota/rate-limit handling;
- malformed/partial/mismatched media output fails closed;
- embedded/generated instruction text cannot mutate provider/tool/publish/budget/security authority;
- raw secrets absent from prompts, artifacts, manifests, attempt/decision ledgers and logs;
- budget reservation, settlement and idempotency;
- router scoring deterministic for fixture state;
- routing cannot override rights/budget/authority policy;
- fallback preserves canonical pinned references/version/rights/provenance;
- ambiguous completion reconciles before retry/fallback;
- no duplicate paid request after worker replay/lost acknowledgement;
- bounded retry/fallback/fan-out/circuit-breaker behavior under persistent 429/500/timeout faults;
- provider unavailable produces manual/wait/authorized-fallback path;
- representative same-shot execution through two approved providers only when real-provider evidence is explicitly authorized/required;
- deterministic fakes/source tests never relabeled as production/provider truth.

Existing M03 lower-layer asset/private-delivery evidence should be reused rather than duplicated; M08 adds tests only for new provider/router trust boundaries.

## Rollout/rollback for later executable work

Adapters/model versions are feature-flagged and release-gated. A provider/model may be disabled without corrupting canonical projects. Router registry/scoring versions are pinned so decisions remain reproducible, and rollback does not rewrite accepted attempt/history evidence.

## Exit criteria for later executable M08

M08 is executable-complete only when the same canonical, tenant-authorized, rights-valid shot/reference package can be processed through at least two approved providers and switch safely on a **known retry/fallback-safe** condition while retaining provider-neutral state, pinned lineage, rights/provenance, cost, authority, reconciliation and attempt history.

An ambiguous prior attempt must not be silently switched. Source mocks/fakes alone cannot prove live provider/admin/production truth where the later acceptance gate explicitly requires external evidence.

## Non-goals

- every market provider;
- guaranteed pixel-identical cross-provider output;
- quota evasion/multi-account rotation;
- trusting provider/model-returned IDs or URLs as canonical authority;
- allowing generated text/media to mint tool/publish/budget/security authority;
- full multimodal continuity scoring (M09);
- final render assembly (M10);
- any executable provider work during the current planning-only slice.
