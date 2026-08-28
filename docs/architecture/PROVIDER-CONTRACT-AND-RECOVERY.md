# Provider Contract, Routing & Recovery Specification

## Purpose

Define the provider-neutral contract used by all AI generation providers and the recovery behavior when providers fail, throttle, exhaust quota, return malformed output or cannot satisfy continuity requirements.

Core rule: canonical project state describes **what is needed**; provider adapters decide **how that provider represents it**.

## Provider capability record

Each provider/model record should describe where applicable:
- provider/model ID;
- API vs manual-web access;
- availability state;
- supported media: text/image/audio/video;
- text-to-image/video;
- image/reference input;
- first/end frame support;
- reference video/video-to-video;
- native extension;
- native audio;
- max/min duration;
- supported resolutions/aspect ratios;
- supported languages/voices;
- concurrency/rate limits;
- free quota/credits;
- paid price dimensions;
- watermark behavior;
- commercial-use/license status;
- privacy/data-use notes;
- idempotency/webhook/poll behavior;
- official evidence URLs/date;
- operational health/history.

Provider facts are versioned and freshness-sensitive.

## Canonical GenerationRequest

A provider-neutral request should include:
- request/job/attempt ID;
- project/scene/shot/content/asset references;
- media kind;
- target duration;
- target aspect/resolution;
- canonical creative intent;
- character/version/look references;
- world/location/prop/style references;
- first/end/mid keyframes where used;
- camera/action/motion state;
- audio/text/lyrics/dialogue where relevant;
- negative constraints;
- hard QA requirements;
- optional preferences;
- privacy/license requirements;
- budget/cost ceiling;
- deadline/latency preference;
- idempotency key.

Canonical request must not contain only a raw prompt string.

## Provider adapter responsibilities

Adapter translates canonical request to provider API/UI semantics and returns normalized state.

Required adapter behavior:
- capability validation before submit;
- typed request mapping;
- parameter normalization;
- provider-specific prompt compilation;
- reference upload/registration where needed;
- request submission;
- provider generation ID capture;
- polling/webhook handling;
- response/error normalization;
- cost/quota capture where possible;
- output download/import;
- media integrity validation;
- provenance capture;
- cleanup/retention behavior;
- fixture/mock support;
- contract tests.

Provider adapter may not mutate locked canonical project/character state.

## Normalized result

Possible result classes:
- SUCCESS_OUTPUT_READY;
- ACCEPTED_ASYNC;
- WAITING_PROVIDER;
- RATE_LIMITED;
- QUOTA_EXHAUSTED;
- AUTH_FAILED;
- PAYMENT_REQUIRED;
- POLICY_REJECTED;
- CAPABILITY_MISMATCH;
- MALFORMED_RESPONSE;
- INVALID_MEDIA;
- PROVIDER_UNAVAILABLE;
- TIMEOUT;
- CANCELLED;
- UNKNOWN_RETRYABLE;
- UNKNOWN_PERMANENT.

Raw provider errors are preserved in secure logs, while normalized categories drive orchestration.

## Routing inputs

Router considers:
- required capability;
- hard quality/continuity requirements;
- character/reference compatibility;
- historical accepted-output rate;
- latency;
- provider health;
- free quota;
- nominal price;
- retry-adjusted expected cost;
- manual effort;
- watermark;
- commercial rights;
- privacy/data-use restriction;
- operator preferred/blocked providers;
- budget caps.

## Routing modes

- FREE_ONLY;
- FREE_FIRST;
- HYBRID_SMART;
- BUDGET_CAPPED;
- QUALITY_FIRST.

All modes use one canonical job pipeline.

## Expected accepted-output cost

Routing should estimate:

`expected accepted cost = nominal call cost + expected retry cost + manual labor penalty + failure/continuity penalty`

A zero-cost provider with low success rate is not automatically preferred over a paid provider with consistently accepted output.

## Fallback chain

Before submission, router may prepare ordered eligible routes:
1. preferred best-fit route;
2. same-provider alternative model/mode;
3. other provider with equivalent capability;
4. manual-free handoff when allowed;
5. block/wait for quota/budget/capability.

Fallback must preserve the same canonical GenerationRequest and continuity anchors, with provider-specific derived prompt regenerated for the new route.

## Retry policy

Retry only when failure class is plausibly transient or prompt/reference adjustment is justified.

Retry categories:
- network timeout;
- provider 5xx/outage;
- rate limit after appropriate wait;
- transient processing failure;
- recoverable malformed provider response;
- generation quality failure requiring new attempt.

Do not repeatedly retry:
- invalid credentials;
- unsupported capability;
- unresolved rights/license;
- hard budget block;
- permanent provider policy rejection;
- deterministic invalid request until request is corrected.

## Retry budgets

Every job/shot should have bounded retry policy:
- maximum provider retries;
- maximum quality retries;
- maximum total cost/credits;
- maximum wall-clock wait where applicable;
- maximum identical-strategy retries.

Repeated identical failures should trigger strategy/provider change or escalation, not infinite loops.

## Circuit breaker

Track provider/model health.

Open circuit after configured high failure rate or repeated infrastructure errors. While open:
- stop sending routine traffic;
- route eligible jobs elsewhere;
- periodically probe/re-evaluate;
- preserve blocked jobs/checkpoints.

Quality rejection alone should be separated from infrastructure outage metrics.

## Quota exhaustion

When free quota/credits expire:
- mark provider route unavailable until reset if reset known;
- preserve completed shots;
- keep canonical next shot/request;
- evaluate other free/paid routes under project policy;
- wait if FREE_ONLY and no route exists;
- never create extra accounts to evade quota.

## Manual-free handoff

For consumer web providers without legitimate automation path, create a handoff package:
- provider/mode;
- source/reference files;
- exact provider-specific prompt;
- settings/duration/aspect;
- expected filename;
- canonical shot/request ID;
- import instructions.

Imported output resumes the same integrity/QA/provenance pipeline.

## Malformed/invalid media

Before QA, output must pass media integrity checks:
- file exists and decodes;
- MIME/container expected;
- duration sane;
- resolution sane;
- checksum computed;
- no HTML/error page disguised as media;
- storage completed.

Invalid output is not a creative QA failure; classify as provider/media-integrity failure.

## Provider switch continuity

On switch:
- reuse canonical character/version/look;
- reuse first/end keyframes/references;
- reuse scene/shot continuity state;
- recompile provider-specific prompt;
- do not pass unsupported provider-specific hidden IDs as canonical state;
- record previous rejected attempts so router can avoid known failure patterns.

## Idempotency

Every external side-effect job needs a stable idempotency strategy where provider supports it, or internal reconciliation when it does not.

On worker restart:
- check persisted provider generation ID before resubmitting;
- reconcile pending result;
- avoid double charging/generation where possible.

## Cost reconciliation

Before paid call:
- estimate;
- verify authorization/caps;
- reserve estimated amount where architecture supports it.

After result:
- capture actual billable units/cost when available;
- reconcile reservation;
- record free credit consumption;
- expose discrepancy.

## Security

Provider adapters must:
- read secrets from environment/secret manager;
- never store secrets in Git;
- validate external URLs/domains where fetching is permitted;
- treat provider response text/files as untrusted;
- use signed/short-lived media access when possible;
- avoid logging tokens/request secrets.

## Acceptance criteria

Provider integration is development-ready only when a new provider can implement this normalized contract without changing canonical Project/Shot/Character schemas, and failures can switch/wait/retry without restarting completed production.