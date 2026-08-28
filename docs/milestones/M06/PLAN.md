# M06 — Hybrid Audio OS

## Objective

Implement provider-neutral narration, dialogue, music/song generation, ambience/SFX, pronunciation, stems, deterministic mixing and audio QA so canonical content can reach an approved audio master with cost/provenance history.

## Entry criteria

- P0 complete.
- M01–M05 accepted.
- Explicit M06 consent.
- Current audio/TTS/music provider APIs/licensing revalidated.

## Dependencies

`M05 -> M06`

## Work packages

### M06-WP1 — Audio plan and director service
- choose `TTS | MUSIC | MIXED | DIALOGUE | NARRATION_WITH_BED`;
- voice/cast assignments;
- genre/mood/tempo/BPM/key/instrumentation;
- song/narration structure;
- ambience/SFX plan;
- mix/ducking/loudness targets;
- AI decision record and user overrides.

### M06-WP2 — Voice/TTS adapter contract
- canonical speech request/response;
- voice capability/locale/style;
- pronunciation/SSML-like controls where supported;
- streaming vs async output normalization;
- provider/model references;
- cost/rights metadata;
- fake adapter plus initial real adapters later within scope.

### M06-WP3 — Music/song adapter contract
- instrumental/full-song capability;
- lyrics handling;
- duration/structure/style controls;
- stems capability where available;
- commercial-use/right facts;
- provider-neutral generation attempts.

### M06-WP4 — Dialogue and character voice system
- character-version -> VoiceProfile-version;
- multi-speaker timing;
- line segmentation;
- emotion/style;
- language variants;
- no silent voice identity mutation.

### M06-WP5 — Pronunciation/localization
- pronunciation dictionary;
- names/brands/terms;
- locale-specific voice selection;
- transliteration where needed;
- human override/pin;
- pronunciation QA fixtures.

### M06-WP6 — SFX/ambience/stem management
- separate assets/tracks;
- loop/placement metadata;
- rights/provenance;
- fade/duck intent;
- no destructive mixing into source assets.

### M06-WP7 — Deterministic audio assembly
Using FFmpeg/media tools:
- align stems/voice/dialogue;
- trim/fade;
- ducking;
- loudness normalization;
- sample-rate/channel conversion;
- final master + preview;
- reproducible render manifest.

### M06-WP8 — Audio QA and acceptance
Checks:
- text/lyrics fidelity;
- pronunciation;
- voice/version consistency;
- timing/dropout/silence;
- clipping;
- loudness;
- channel/sample validity;
- stem alignment;
- rights/cost/provenance.

Acceptance outputs:
- one approved song audio master;
- one approved narrated story with background mix;
- full attempt/cost/QA history.

## Expected modules/files

- audio director/services;
- provider audio adapters;
- voice/pronunciation package;
- deterministic mix/render activities;
- audio QA;
- schemas/API routes;
- audio fixtures/tests.

## Data/migration impact

Adds AudioPlan, VoiceProfile/version associations, audio generation attempts, stems/tracks, pronunciation entries, mix manifests and audio QA records.

## API/UI impact

Adds audio plan/generate/status/preview/approve APIs. Full mixer UI later, but contracts support it.

## Security/cost/rights impact

- voice/likeness consent and provider licensing enforced;
- no unauthorized celebrity/person voice cloning;
- spend reservations per attempt;
- provider secrets server-side;
- generated/imported audio provenance retained.

## Test/acceptance

- fake TTS/music adapters;
- provider malformed/rate-limit/failure;
- deterministic mix fixtures;
- pronunciation/localization;
- character voice version pinning;
- clipping/loudness/dropout QA;
- retry/fallback no duplicate billing.

## Rollout/rollback

Provider/prompt/model changes versioned and canaried. Mix manifests allow deterministic re-render. Approved source/master assets are immutable/versioned.

## Exit criteria

A song and narrated story progress from canonical content through provider-neutral audio plans/generation to approved deterministic masters with complete rights, cost and QA history.

## Non-goals

- video generation;
- full DAW replacement;
- unrestricted voice cloning;
- final web mixer UI;
- live real-time voice chat.
