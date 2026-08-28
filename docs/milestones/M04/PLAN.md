# M04 — Character and Entity Library

## Objective

Implement reusable, versioned, rights-aware characters/entities with lock modes, reference packs and provider-neutral identity continuity.

## Entry criteria

- P0 complete.
- M01–M03 accepted.
- Explicit M04 consent.

## Dependencies

`M03 -> M04`

## Work packages

### M04-WP1 — Entity repositories/services
- Character, CharacterVersion, Look;
- Location/World;
- Prop;
- Style;
- VoiceProfile references;
- ownership/rights.

### M04-WP2 — Character creation/versioning
- human/non-human categories;
- body/face/hair/eyes/palette/wardrobe/accessories;
- personality/movement/voice metadata;
- create new version instead of silent mutation.

### M04-WP3 — Lock engine
- global hard lock;
- project lock;
- look lock;
- scene lock;
- one-off/unlocked;
- forbidden mutations;
- lock conflict validation.

### M04-WP4 — Reference-pack asset model
- front/side/back/full body;
- expressions;
- poses;
- wardrobe variants;
- canonical approved image references;
- version pinning.

Generation of images can initially use fake/manual assets until M08 real provider routing; M04 owns reference-pack structure/approval.

### M04-WP5 — Voice/entity association
- voice profile/version mapping;
- language/pronunciation references;
- no raw provider credential/reference as canonical identity.

### M04-WP6 — Identity QA interface
- deterministic/fixture identity checks;
- later multimodal provider implementation plugs into same QA contract;
- hard locked-attribute failures.

### M04-WP7 — Project reuse/import/export
- select existing character/entity;
- pin exact version/look;
- duplicate/fork version intentionally;
- export manifest/reference pack;
- rights validation.

### M04-WP8 — API/acceptance
- list/search/select/version/lock APIs;
- cross-project reuse fixture;
- mutation rejection;
- tenant isolation;
- reference lineage.

## Expected modules/files

- entity domain/repositories/services;
- asset/reference pack services;
- lock validator;
- entity API routes;
- tests/fixtures.

## Data/migration impact

Adds entity/version/look/lock/reference relationships and indexes/search fields.

## API/UI impact

API sufficient for future Character Library UI. No polished web library required yet.

## Security/cost/rights impact

- tenant isolation;
- likeness/voice/right records;
- no paid generation required to accept milestone;
- imported references require provenance/consent state.

## Test/acceptance

- same locked character reused in multiple projects by exact version;
- forbidden mutation rejected;
- new look/version does not alter previous projects;
- reference pack assets lineage valid;
- cross-tenant entity inaccessible.

## Rollout/rollback

Append/version-based. Rollback code/migrations without rewriting historical entity versions.

## Exit criteria

One recurring character can be versioned, locked, reference-packed and reused across multiple projects with stable provider-neutral identity and rights lineage.

## Non-goals

- actual provider image/video generation;
- advanced web Character Library design;
- biometric identity matching claims;
- celebrity/voice cloning without later policy implementation.
