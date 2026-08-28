# Free-Tier Provider Router

## Goal

Use legitimate free AI capacity first without sacrificing continuity, licensing safety, reproducibility, or provider terms.

This router is designed for a multi-provider production system. It must not assume that a consumer website's free plan is an API, and it must not bypass quotas by creating or rotating accounts.

## Core distinction

Every provider capability is classified as one of:

- `api_free` — official API has a usable free tier and automation is supported;
- `api_paid` — official API requires paid usage;
- `web_free_manual` — consumer web/app has free credits but no verified free API route; can be used only as a manual handoff unless an approved browser automation path is explicitly permitted by provider terms;
- `web_paid_manual`;
- `unavailable`.

A free web-app credit balance must never be represented as free API capacity.

## Provider selection order

For every generation task:

1. determine required capability;
2. determine continuity requirements;
3. determine final-use license requirement;
4. load current provider registry and quota state;
5. refresh stale provider facts from official sources;
6. eliminate providers that cannot satisfy the task;
7. prefer `api_free` candidates;
8. if none are available, return an approved `web_free_manual` handoff when it is useful;
9. otherwise select the cheapest approved paid API only if paid spend has been authorized;
10. otherwise pause that render without losing production state.

## Hard constraints

Never:
- create multiple accounts to evade a provider's free limits;
- rotate identities/accounts to bypass quotas;
- scrape or automate a consumer UI when terms/API access do not permit it;
- remove a watermark in violation of a provider's plan terms;
- treat personal-use output as commercially licensed output;
- publish an asset whose license status is unresolved;
- lose the generation history when switching providers.

## Dynamic provider registry

Each provider/model entry stores:

- provider ID;
- model ID;
- capability: text | image | tts | music | video | video-edit | video-extend;
- access class;
- API availability;
- free quota amount/type;
- quota reset rule;
- current remaining quota when measurable;
- duration limits;
- resolution limits;
- watermark status;
- commercial-use status;
- automation status;
- image-to-video support;
- first-frame support;
- last-frame/end-frame support;
- reference-image support;
- native extension support;
- reference-video support;
- audio input support;
- native audio support;
- current terms/source URLs;
- `verified_at` timestamp;
- confidence/status: verified | partial | conflict | stale.

Provider facts must be refreshed before production when they are older than the configured freshness window or when a request fails due to capability/quota changes.

## Current verified baseline — 2026-08-28

This baseline is guidance, not a permanent promise. The runtime must re-check official sources.

### Google Gemini Flash TTS

- official API;
- current Gemini 3.1 Flash TTS free tier exists;
- suitable for automated female narration;
- free-tier data may be used to improve provider products;
- rate limits apply.

Classification: `api_free` for supported free-tier TTS usage.

### Google Lyria 3

- official API;
- full music generation;
- current Gemini API pricing shows no free tier for Lyria 3;
- use only after paid spend is approved, or select another approved music provider/free manual route.

Classification: `api_paid`.

### Google Veo 3.1

- official API;
- current API output is 8-second video;
- supports Veo-generated-video extension;
- supports first/last-frame generation;
- supports up to three reference images;
- current Gemini API pricing shows no free tier.

Classification: `api_paid`.

### Runway

- consumer Free plan currently includes 125 one-time credits;
- free videos are watermarked;
- the consumer web credits are explicitly separate from API credits;
- API generations are paid credits.

Classification: `web_free_manual` for free consumer experiments; API is `api_paid`.

### Pika

- consumer pricing currently advertises a $0 tier with monthly video credits and limited resolutions/models;
- API is separately priced;
- current official pages contain changing/possibly conflicting commercial-use language between pricing and FAQ, therefore commercial status must be re-verified before final publication.

Classification: `web_free_manual`; final commercial use blocked while license status is unresolved.

### Kling AI

- official site currently advertises a free Basic plan with limited usage/features;
- paid benefits include stronger output options and extension-related capabilities;
- exact free allocation/capability can change and must be queried at runtime;
- do not assume consumer credits are API credits.

Classification: `web_free_manual` unless an official API free allocation is independently verified.

### Hailuo AI

- official consumer service includes a free mode with watermark/queue limits and new-user promotional credits;
- developer/API billing is separate;
- promotional amounts can change.

Classification: `web_free_manual` unless official free API capacity is independently verified.

### Luma Dream Machine

- current Free plan supports limited draft generation with watermarks;
- free-plan outputs are documented as personal-use only;
- do not use Free-plan outputs as monetized production masters.

Classification: `web_free_manual`, experiment/reference only for commercial project workflows.

## Quota ledger

Maintain a local/project ledger for every provider:

- quota snapshot timestamp;
- quota source;
- free balance;
- expected reset date/time;
- last successful call;
- last failed call;
- failure reason;
- credits consumed;
- paid cost consumed;
- generation IDs;
- provider account alias (non-secret);
- secret key reference name only, never the secret itself.

## Cost policy

Default project mode: `FREE_FIRST`.

Meaning:
- use legitimate free API capacity first;
- use manual free web handoffs only when the operator accepts the manual step;
- paid usage must not happen silently;
- when free capacity is exhausted, preserve the exact checkpoint and wait for quota reset or human authorization for a paid fallback.

Optional future policies:
- `FREE_ONLY`
- `FREE_FIRST`
- `BUDGET_CAPPED`
- `QUALITY_FIRST`

## History is provider-independent

Provider switching must never reset project history. All providers write to the same canonical generation ledger and asset manifest so the next model receives the same story, shot, character, timeline and continuity state.
