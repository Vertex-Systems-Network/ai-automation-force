# Provider Integration Roadmap

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define the provider program before implementation so Milestone 8 does not decide provider strategy from scratch while coding.

The platform remains provider-neutral. This roadmap defines candidate tiers, admission gates, adapter sequencing, capability expectations, fallback rules and revalidation requirements. Exact model IDs, prices, quotas, rate limits, licenses and API details are mutable facts and must be revalidated against official sources immediately before implementation or enablement.

## Core rules

1. Canonical project, character, image, audio, shot, timeline, cost, rights and QA state never lives only inside a provider.
2. One authorized account/connection per provider is the default product model. Same-provider account rotation to evade quota is prohibited.
3. Multiple different providers may be connected simultaneously.
4. Provider switching preserves canonical references, first/end frames, prompt/version, character/world/style locks, cost and attempt history.
5. A provider is never enabled merely because a website has a free tier.
6. Consumer-web credits and API capacity are distinct.
7. Only official APIs or explicitly permitted manual handoff paths are used.
8. Provider-specific output is accepted only after canonical QA/rights gates.
9. Failed attempts remain auditable.
10. No provider is a mandatory system-of-record dependency.

## Provider lifecycle

Every provider/capability moves through:

`DISCOVERED -> EVIDENCE_VERIFIED -> EVALUATION -> ADAPTER_READY -> TESTED -> ENABLED_LIMITED -> ENABLED -> DEGRADED | DISABLED`

A provider can be downgraded automatically when capability evidence becomes stale, credentials fail, rights posture changes, quality falls below threshold or health degrades.

## Admission gate

Before `ADAPTER_READY`:
- official programmable API or explicitly permitted authorized workflow verified;
- current terms/commercial-use position recorded;
- privacy/data handling reviewed;
- authentication method known;
- request/job/result lifecycle documented;
- input/output limits known;
- pricing/quota/rate-limit evidence recorded;
- cancellation/webhook/poll behavior known where applicable;
- moderation/error behavior understood;
- provider terms do not require quota circumvention or unsupported browser automation.

Before `ENABLED_LIMITED`:
- adapter contract tests;
- fake provider tests;
- malformed/partial result handling;
- cost normalization;
- rights/provenance capture;
- asset ingestion checks;
- retry/idempotency/reconciliation tests;
- representative QA benchmark;
- kill switch/feature flag.

Before broad `ENABLED`:
- bounded production canary;
- accepted-output cost observed;
- continuity/quality performance acceptable;
- no unresolved security/rights blocker.

## Capability vocabulary

Adapters advertise canonical capability keys including:
- `TEXT_TO_IMAGE`
- `IMAGE_TO_IMAGE`
- `IMAGE_EDIT`
- `INPAINT`
- `OUTPAINT`
- `STYLE_REFERENCE`
- `CHARACTER_REFERENCE`
- `MULTI_REFERENCE_IMAGE`
- `TEXT_TO_VIDEO`
- `IMAGE_TO_VIDEO`
- `FIRST_FRAME`
- `LAST_FRAME`
- `REFERENCE_VIDEO`
- `VIDEO_EXTEND`
- `VIDEO_EDIT`
- `NATIVE_AUDIO_VIDEO`
- `TTS`
- `VOICE_CLONE` only with rights/consent policy
- `SPEECH_TO_SPEECH`
- `MUSIC`
- `VOCALS`
- `SFX`
- `DUBBING`
- `UPSCALE_IMAGE`
- `UPSCALE_VIDEO`
- `AVATAR_VIDEO`

Provider-specific feature names are mapped to these canonical keys.

## Initial integration tiers

### Tier 1 — first implementation candidates

These are the preferred first programmable adapters because official API evidence is currently available and their capabilities cover the initial vertical slice.

#### Google Gemini / generative media
Planned roles:
- image generation/editing via current Gemini image models;
- video generation through current Gemini/Veo family;
- first/last-frame and reference-driven video when supported by current model;
- TTS;
- music via Lyria where commercially/API available;
- multimodal analysis/QA/research where appropriate.

Current planning evidence (August 2026): Google documents Gemini API generative media including current image models and Veo 3.1, with image-to-video, first/last frame and reference-image controls. Current model IDs must be revalidated before code.

#### Runway
Planned roles:
- text/image-to-video;
- image generation/editing where current API supports it;
- video-to-video/upscale;
- audio/TTS/SFX/dubbing/voice operations where enabled;
- provider comparison/cross-provider fallback.

Current official API exposes asynchronous media generation and a broad image/video/audio surface.

#### Luma
Planned roles:
- text/image generation;
- image-to-video;
- character/image/style references where current API supports them;
- additional video/reference capability after benchmark.

#### MiniMax / Hailuo
Planned roles:
- text-to-video;
- image-to-video;
- first/last-frame video;
- subject-reference video where current API supports it;
- possible speech/audio routes only after separate capability review.

Current official MiniMax API documents asynchronous video generation and Hailuo models, including first/last-frame workflows.

### Tier 2 — qualified expansion candidates

#### Pika
Planned roles:
- video/image/media generation through the official Pika API when access, pricing, terms and capability are current and approved;
- useful as a fallback/benchmark provider rather than mandatory core dependency.

Current Pika API documentation exposes REST media endpoints and API-key based jobs. Exact production capability must be revalidated during M08.

#### Kling
Status: `EVALUATION_CANDIDATE`.

Desired roles:
- text/image-to-video;
- image-conditioned/continuity workflows;
- video editing where current official programmable access supports it.

Planning rule: do not implement or enable a Kling adapter until official Open Platform/API documentation, credentials/access, terms, cost and exact capabilities are directly verified at implementation time. Public consumer-web availability is not sufficient evidence for automated API use.

### Tier 3 — specialist/future candidates

Examples may include:
- avatar/talking-head providers;
- specialist dubbing/voice providers;
- high-quality music/SFX providers;
- local/open models;
- enterprise/private inference providers.

They enter through the same admission gate and are not hard-coded by name into core orchestration.

## Image adapter sequencing

Recommended initial image path:
1. Google current image API as primary candidate;
2. Runway and/or Luma as alternate/reference-capable candidates;
3. additional providers only after benchmark demonstrates value.

Acceptance fixture set:
- recurring stylized character reference;
- realistic adult portrait with consent-safe synthetic identity;
- location/world reference;
- prop/product-like object;
- first-frame shot keyframe;
- edit/inpaint derivative;
- 16:9 and 9:16 variants.

Metrics:
- identity consistency;
- instruction adherence;
- reference adherence;
- artifact/text failure;
- latency;
- accepted-output cost;
- rights/watermark eligibility.

## Video adapter sequencing

Minimum M08 acceptance requires at least two independently programmable providers capable of the same representative canonical shot.

Recommended candidate order for evaluation:
1. Google current video generation path;
2. Runway;
3. MiniMax/Hailuo;
4. Luma;
5. Pika;
6. Kling after official API evidence/access verification.

The order is an evaluation priority, not a quality ranking and may change after fresh benchmarks.

Representative video fixtures:
- simple text-to-video shot;
- locked-character image-to-video;
- first-frame constrained motion;
- first+last-frame interpolation where supported;
- recurring location/reference shot;
- 9:16 social shot;
- difficult continuity shot requiring fallback.

## Audio provider program

Audio remains separate from video provider selection.

Routes:
- speech/TTS;
- character dialogue;
- music/song;
- background score;
- SFX/ambience;
- dubbing/localization;
- speech-to-speech/voice transformation where consent permits.

Google Gemini TTS/Lyria are planned candidates but not exclusive. Runway and specialist providers can be admitted through the same contract. Voice cloning requires explicit rights/consent records and cannot be silently inferred from an uploaded voice.

## Cross-provider handoff contract

When provider A cannot continue:
1. freeze the canonical `GenerationRequest` version;
2. persist provider A attempt/result/error/cost;
3. preserve approved source/reference assets and hashes;
4. preserve CharacterVersion/Look, World/Location, StyleProfile and Shot state;
5. preserve first/end frame and motion/camera intent;
6. re-score eligible providers;
7. compile provider B payload;
8. execute without replacing successful previous shots;
9. normalize output into canonical storage;
10. run the same QA/continuity/rights gate;
11. accept or continue bounded retry/fallback.

Cross-provider output is not guaranteed pixel-identical. The system targets continuity-equivalent accepted output.

## Account/quota policy

Default:
- one active authorized connection per provider/workspace funding context;
- legitimate organization/team structures may be supported if provider terms explicitly allow them;
- no account farming/rotation to bypass quotas;
- quota exhaustion is represented as state and triggers wait, manual handoff or a different provider;
- free web/manual routes remain explicit manual jobs unless an official API permits automation.

## Cost model

For every attempt track:
- provider;
- model/version;
- requested units;
- estimated cost;
- actual provider cost if known;
- platform/customer funding source;
- reserved/settled/released credits;
- failure/rejection reason;
- accepted-output status;
- effective accepted-output cost.

Routing optimizes expected accepted-output utility, not raw call price.

## Quality history

Provider/model performance is scoped by task type. Store aggregates for:
- acceptance rate;
- continuity pass rate;
- identity pass rate;
- retry rate;
- latency;
- cost;
- moderation rejection;
- outage/rate-limit frequency.

Do not globally label one provider as universally “best.”

## Rights and provenance

Every adapter must return/store enough metadata to construct a Rights/Provenance record:
- provider/model/version;
- request/attempt timestamp;
- source/reference asset lineage;
- commercial-use/watermark evidence snapshot/reference;
- generated output hash;
- provider task/request ID;
- user/provider funding context.

If rights evidence is insufficient for intended publication, asset may remain internal/review-only.

## Security

- credentials in server-side secret management;
- no provider API secret in browser/mobile/logs/prompts;
- provider callback/webhook verification;
- outbound URL/upload rules follow SSRF/media security spec;
- downloaded outputs pass asset validation/quarantine/probe;
- provider response text is untrusted;
- adapter has least-privilege network/tool access.

## Capability freshness

Canonical runtime registry stores:
- evidence URL/source ID;
- verified timestamp;
- freshness TTL;
- model/capability version;
- confidence;
- enablement state.

Stale material facts trigger refresh before new production routing when required by policy.

Daily Provider Scout may update research/evidence and high-confidence non-executable facts. It must not silently enable an adapter, change paid spend behavior or bypass development/release gates.

## Provider deprecation and replacement

When provider/model is deprecated:
- stop selecting it for new work before shutdown date;
- preserve historical attempts/assets;
- migrate configuration to replacement model through evaluation/canary;
- do not regenerate old accepted assets merely due to provider deprecation;
- workflows waiting on unavailable provider enter fallback/reconciliation path.

## UI/admin requirements

Provider management UI eventually shows:
- connection state;
- API/manual mode;
- funding source;
- capabilities;
- enabled/disabled/degraded;
- current quota/rate information where reliably available;
- cost class;
- rights/commercial status;
- last verified time;
- test connection;
- reconnect/revoke;
- per-provider workspace allow/deny;
- recent failures/health.

Router explanation shows why a provider was selected or skipped without exposing secrets/private reasoning.

## Testing matrix

Every adapter must pass:
- auth failure;
- quota/rate limit;
- timeout/network failure;
- malformed response;
- asynchronous pending/success/failure;
- duplicate/replayed activity;
- output missing/corrupt;
- moderation rejection;
- cost metadata absent/changed;
- cancellation where supported;
- cross-provider fallback;
- secret redaction;
- fake-provider spend-free tests.

## Implementation-time revalidation checklist

Before each provider adapter is coded/enabled, confirm from current official sources:
- official API still exists and account has authorized access;
- current endpoint/SDK/model IDs;
- auth and scopes;
- pricing/billing/quota/rate limits;
- supported inputs/outputs/durations/resolutions;
- reference/keyframe/edit features;
- content/moderation rules;
- commercial/rights/watermark terms;
- data retention/training/privacy terms;
- callback/webhook behavior;
- deprecations/shutdown dates.

This is fact refresh, not first-time architectural planning.

## Acceptance criteria

Provider integration planning is complete when implementation can proceed without inventing:
- provider lifecycle/admission gates;
- initial adapter candidate tiers;
- image/video/audio evaluation sequence;
- one-account-per-provider and quota policy;
- cross-provider handoff;
- cost/quality/provenance/security contracts;
- capability freshness/deprecation behavior;
- UI/admin requirements;
- adapter test/enablement gates.
