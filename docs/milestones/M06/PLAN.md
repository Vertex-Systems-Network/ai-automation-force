# M06 — Hybrid Audio OS

## Planning authority and current state

This document is the planning contract for M06 only. It does **not** authorize executable M06 product/API/schema/provider work.

Current planning baseline: `main@496cff2fe7aa4dbf5777b4a5b4cb5616a29ae432`, after cross-cutting adversarial QA plus M04/M05 planning promotion and broadcast-14 reconciliation.

Executable M06 work remains blocked until the milestone dependency chain is accepted at executable truth levels, explicit M06 executable consent is recorded, and then-current governance, branch/write ownership, migration and provider/licensing gates are revalidated. Planning completion, branch synchronization, green planning CI or generic conversational continuation is not executable consent.

## Objective

Implement provider-neutral narration, dialogue, music/song generation, ambience/SFX, pronunciation, stems, deterministic mixing and audio QA so canonical content can reach an approved audio master with cost/provenance history without allowing provider output, retrieved metadata, voice references or low-trust media to bypass rights, identity, approval, budget or security authority.

## Entry criteria

All are required before executable M06 work begins:

- P0 complete;
- M01–M05 accepted at their required executable truth levels;
- explicit M06 executable consent recorded through Supervisor authority;
- current audio/TTS/music provider APIs, commercial terms and licensing revalidated;
- current main, broadcast, dependency, write ownership and migration state revalidated immediately before implementation;
- Issue #36/live repository-governance requirements satisfied where they remain part of the accepted upstream milestone chain;
- cross-cutting adversarial QA obligations applicable to the exact proposed M06 surface mapped to targeted evidence.

Current state: planning may continue, but executable M06 entry criteria are **not satisfied**. Issue #36 remains `EXTERNAL_NOT_VERIFIED`, upstream executable milestone gates are not replaced by planning promotions, and no explicit M06 executable consent is recorded.

## Dependencies

`M01 -> M02 -> M03 -> M04 -> M05 -> M06`

Downstream impact:

- M07 depends on executable M04/M05/M06 completion;
- planning completion or synchronization does not satisfy M07 executable dependency gates.

## Work packages

### M06-WP1 — Audio plan and director service
- choose `TTS | MUSIC | MIXED | DIALOGUE | NARRATION_WITH_BED`;
- voice/cast assignments;
- genre/mood/tempo/BPM/key/instrumentation;
- song/narration structure;
- ambience/SFX plan;
- mix/ducking/loudness targets;
- AI decision record and user overrides;
- retrieved/provider/model suggestions remain advisory evidence and cannot grant approval, budget, rights or security authority.

### M06-WP2 — Voice/TTS adapter contract
- canonical speech request/response;
- voice capability/locale/style;
- pronunciation/SSML-like controls where supported;
- streaming vs async output normalization;
- provider/model references;
- cost/rights metadata;
- fake adapter plus initial real adapters later within separately authorized executable scope;
- provider-returned voice IDs, status, URLs, transcripts and metadata validated against canonical tenant/project/voice authority before use;
- provider output cannot bypass voice-profile rights or pinned version identity.

### M06-WP3 — Music/song adapter contract
- instrumental/full-song capability;
- lyrics handling;
- duration/structure/style controls;
- stems capability where available;
- commercial-use/right facts;
- provider-neutral generation attempts;
- provider-reported licensing or ownership facts remain untrusted until validated against retained policy/provenance evidence.

### M06-WP4 — Dialogue and character voice system
- character-version -> VoiceProfile-version;
- multi-speaker timing;
- line segmentation;
- emotion/style;
- language variants;
- no silent voice identity mutation;
- likeness/voice consent and permitted-use facts required before an identity-bound voice can become generation authority;
- pinned prior voice assignments are immutable/versioned rather than silently overwritten by provider recommendations or replacements.

### M06-WP5 — Pronunciation/localization
- pronunciation dictionary;
- names/brands/terms;
- locale-specific voice selection;
- transliteration where needed;
- human override/pin;
- pronunciation QA fixtures;
- provider/transcript guesses cannot silently overwrite pinned canonical pronunciation or identity facts.

### M06-WP6 — SFX/ambience/stem management
- separate assets/tracks;
- loop/placement metadata;
- rights/provenance;
- fade/duck intent;
- no destructive mixing into source assets;
- imported/generated audio remains tenant/project scoped and foreign provider asset IDs are rejected unless resolved through canonical authority;
- rights/consent/provenance continuity retained through derivatives and mix manifests.

### M06-WP7 — Deterministic audio assembly
Using FFmpeg/media tools:
- align stems/voice/dialogue;
- trim/fade;
- ducking;
- loudness normalization;
- sample-rate/channel conversion;
- final master + preview;
- reproducible render manifest;
- malformed media, parser/probe failures, invalid duration/channel/sample metadata and unexpected tool output fail closed rather than producing an approved master;
- source assets are not destructively mutated.

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
- rights/cost/provenance;
- voice/likeness consent continuity;
- canonical provider/asset identity validation;
- secret/log hygiene;
- bounded retry/fallback and duplicate-billing behavior.

Acceptance outputs:
- one approved song audio master;
- one approved narrated story with background mix;
- full attempt/cost/QA history;
- no stronger production/provider truth state than the evidence actually proves.

## Cross-cutting adversarial acceptance obligations

`docs/qa/ADVERSARIAL-AUDIT-PLAN.md` is a mandatory planning input. When M06 later requests executable promotion, QA must re-evaluate the exact reachable authority surface and add only targeted missing evidence.

At minimum M06 acceptance must prove:

1. **Voice rights/version authority cannot be bypassed** — provider output, retrieved metadata or a malicious prompt cannot select or mutate an identity-bound voice without canonical authorization, consent and pinned version checks.
2. **Provider output is untrusted** — returned IDs, URLs, transcripts, status, licensing claims and classifications require schema validation and canonical lookup before becoming decision input.
3. **Tenant/project isolation is canonical** — foreign voice/audio/stem/provider asset IDs are rejected rather than trusted because an external provider/model returned them.
4. **Audio parsing fails closed** — parser/probe/transcode errors, malformed audio and inconsistent duration/channel/sample facts cannot be relabeled as valid/approved.
5. **Secrets stay outside media artifacts** — raw provider/OAuth/signing credentials never enter prompts, generated metadata, manifests, ledgers, logs, transcripts, embeddings or ordinary audio records.
6. **Rights/provenance remain attached** — voice consent, imported audio/music/SFX rights, source provenance and derivative lineage remain visible through generation and mixing.
7. **Retries and cost are bounded** — attempts/fallbacks/fan-out use configured ceilings, idempotency and budget authority; retries cannot silently duplicate billable generations.
8. **Approval authority is deterministic** — provider/model text saying “approved”, “licensed” or “safe” cannot create canonical QA/rights/approval state.
9. **Versioned identity is immutable** — approved/pinned voice or audio source versions are not silently rewritten when new provider capabilities or recommendations appear.
10. **No synthetic production success** — deterministic fakes prove source contracts only; unavailable live provider/licensing/publish/admin evidence remains `NOT_VERIFIED` where required.

Do not add duplicate umbrella tests for already-proven lower-layer properties unless M06 creates a newly reachable authority/trust path.

## Expected modules/files

Planned future executable surface only:

- audio director/services;
- provider audio adapters;
- voice/pronunciation package;
- deterministic mix/render activities;
- audio QA;
- schemas/API routes;
- audio fixtures/tests.

Actual executable write ownership and migration reservations must be assigned fresh by the Supervisor after entry criteria pass.

## Data/migration impact

Expected future implementation may add AudioPlan, VoiceProfile/version associations, audio generation attempts, stems/tracks, pronunciation entries, mix manifests and audio QA records.

This planning slice creates **no migration reservation and no schema change**. Future migration IDs must be reserved only after executable M06 authority exists and the then-current migration head is audited.

## API/UI impact

Future implementation may add audio plan/generate/status/preview/approve APIs. Full mixer UI is later, but contracts should support it.

This planning slice changes no API or UI.

## Security/cost/rights impact

Future M06 must preserve:

- voice/likeness consent and provider licensing enforcement;
- no unauthorized celebrity/person voice cloning;
- immutable/versioned voice-profile identity;
- spend reservation plus bounded attempt/fallback/fan-out behavior;
- provider secrets server-side and excluded from generated artifacts/prompts/logs/ledgers;
- generated/imported audio provenance retained through derivatives;
- canonical tenant/project/provider-asset authorization;
- fail-closed media parsing/probing and approval semantics.

## Test/acceptance plan

Targeted future evidence includes:

- fake TTS/music adapters for source contracts only;
- provider malformed/rate-limit/failure/untrusted-metadata cases;
- foreign voice/audio/provider asset-ID rejection;
- malicious provider output attempting to override voice rights/version pinning;
- deterministic mix fixtures;
- malformed audio/parser/probe fail-closed behavior;
- pronunciation/localization and pinned override behavior;
- character voice version pinning and no silent identity mutation;
- clipping/loudness/dropout/channel/sample QA;
- rights/consent/provenance continuity through stems/mixes;
- raw secret exclusion from prompts/manifests/logs/ledgers;
- retry/fallback idempotency and no duplicate billing.

## Rollout/rollback

Future provider/prompt/model changes are versioned and canaried. Mix manifests allow deterministic re-render. Approved source/master and voice-profile versions are immutable/versioned. Provider or licensing changes must not silently rewrite historical truth; later corrections use explicit versions/state transitions with retained auditability.

## Exit criteria

M06 can exit only when a song and narrated story progress from canonical content through provider-neutral audio plans/generation to approved deterministic masters with complete rights, consent, cost, provenance and QA history, without provider-output authority escalation, cross-tenant asset trust, silent voice mutation, secret leakage or unbounded retries/cost.

Planning completion is **not** executable milestone completion.

## Non-goals

- video generation;
- full DAW replacement;
- unrestricted voice cloning;
- final web mixer UI;
- live real-time voice chat;
- production credentials or paid provider calls during this planning slice;
- using generic `continue`, branch synchronization, mocks or green planning CI as executable M06 consent.
