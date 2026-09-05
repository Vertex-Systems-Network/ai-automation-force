# M04 — Character and Entity Library

## Planning authority and current state

This document is the planning contract for M04 only. It does **not** authorize executable M04 product/API/schema/provider work.

Current planning baseline: `main@5c7d3bab84992a8681c64ffe4911637568ad608b` after cross-cutting QA PR #74 and mandatory broadcast 12 / PR #76.

Executable M04 work remains blocked until all entry criteria below are satisfied, including live M03 protected-main governance in Issue #36 and explicit M04 executable consent. Generic conversational continuation is not that consent.

## Objective

Implement reusable, versioned, rights-aware characters/entities with lock modes, reference packs and provider-neutral identity continuity.

## Entry criteria

All are required before executable M04 work begins:

- P0 complete;
- M01–M03 accepted at their required truth level;
- Issue #36 live protected-main governance verified and closed, because M04 depends on `M03-GOV-HOLD`;
- explicit M04 executable consent recorded through Supervisor authority;
- current-main/broadcast/write-ownership/migration state revalidated immediately before implementation;
- cross-cutting adversarial QA obligations applicable to the proposed executable surface mapped to targeted acceptance evidence.

Current state: planning may continue, but executable entry criteria are **not satisfied** while Issue #36 remains `EXTERNAL_NOT_VERIFIED` and explicit M04 executable consent is absent.

## Dependencies

`M03 -> M04`

Downstream dependency impact:

- M05 remains dependent on M04;
- M07 remains dependent on M04/M05/M06;
- M08 remains dependent on M04/M07.

Planning synchronization must never be interpreted as downstream execution authority.

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
- create new version instead of silent mutation;
- immutable historical version semantics for already-pinned projects.

### M04-WP3 — Lock engine
- global hard lock;
- project lock;
- look lock;
- scene lock;
- one-off/unlocked;
- forbidden mutations;
- lock conflict validation;
- fail-closed rejection when a requested mutation conflicts with an effective stronger lock.

### M04-WP4 — Reference-pack asset model
- front/side/back/full body;
- expressions;
- poses;
- wardrobe variants;
- canonical approved image references;
- exact version pinning;
- canonical tenant/project authorization for referenced asset IDs;
- provenance/consent state retained for imported references.

Generation of images can initially use deterministic fake/manual assets until M08 real provider routing; M04 owns reference-pack structure/approval. Fake/manual assets may prove source contracts but must never be relabeled as real-provider or production evidence.

### M04-WP5 — Voice/entity association
- voice profile/version mapping;
- language/pronunciation references;
- no raw provider credential/reference as canonical identity;
- rights/consent state remains attached to the exact reusable voice/entity version.

### M04-WP6 — Identity QA interface
- deterministic/fixture identity checks;
- later multimodal provider implementation plugs into the same QA contract;
- hard locked-attribute failures;
- provider/model output remains untrusted and cannot silently redefine canonical identity, locks, tenant authority or rights state.

### M04-WP7 — Project reuse/import/export
- select existing character/entity;
- pin exact version/look;
- duplicate/fork version intentionally;
- export manifest/reference pack;
- rights validation;
- import/export cannot bypass canonical ownership, tenant or consent checks;
- imported metadata/instructions remain low-trust evidence and cannot mint lock, policy or privileged authority.

### M04-WP8 — API/acceptance
- list/search/select/version/lock APIs;
- cross-project reuse fixture;
- mutation rejection;
- tenant isolation;
- reference lineage;
- rights/provenance enforcement;
- canonical authorization of externally supplied entity/version/look/reference IDs.

## Cross-cutting adversarial acceptance obligations

Broadcast 12 and `docs/qa/ADVERSARIAL-AUDIT-PLAN.md` are mandatory planning inputs. When M04 later requests executable promotion, QA must re-evaluate the exact proposed surface and add only targeted evidence for newly reachable authority paths.

At minimum M04 acceptance must prove:

1. **Cross-tenant isolation** — foreign tenant entity/version/look/reference IDs are inaccessible even when supplied by imports, model/provider output or remembered state.
2. **Canonical authorization** — returned/imported IDs are canonical-looked-up and tenant/project-authorized before use; model/provider prose cannot mint authority.
3. **Lock integrity** — hard/project/look/scene lock conflicts fail closed; a lower-trust request cannot bypass an effective stronger lock.
4. **Append/version immutability** — new looks/versions never silently mutate exact versions already pinned by prior projects.
5. **Rights and provenance continuity** — likeness, voice and reference reuse retain exact ownership/consent/provenance state across versioning, reuse, import and export.
6. **Reference-pack trust boundary** — foreign asset IDs, malformed manifests and low-trust embedded instructions cannot redefine canonical identity, policy, lock or security state.
7. **Provider-output distrust hook** — later provider-returned IDs/URLs/metadata remain untrusted until schema validation, canonical lookup and policy checks occur.
8. **No synthetic security success** — deterministic fixtures/fakes may prove source contracts, but absent admin/provider/production evidence remains `NOT_VERIFIED` where a later gate requires it.

No duplicate umbrella tests should be added for M03 properties already proven by the M03-WP8 acceptance matrix unless M04 introduces a genuinely new authority/trust path.

## Expected modules/files

Planned future executable surface only:

- entity domain/repositories/services;
- asset/reference pack services;
- lock validator;
- entity API routes;
- tests/fixtures.

Actual executable file ownership and migration reservations must be assigned fresh by the Supervisor after entry criteria pass.

## Data/migration impact

Expected future implementation adds entity/version/look/lock/reference relationships and indexes/search fields.

This planning slice creates **no migration reservation and no schema change**. Future migration IDs must be reserved only after executable M04 authority is granted and the then-current migration head is re-audited.

## API/UI impact

Future API should be sufficient for a Character Library UI. No polished web library is required for initial M04 source acceptance.

This planning slice changes no API or UI.

## Security/cost/rights impact

Future M04 must preserve:

- tenant and project authority isolation;
- exact likeness/voice/reference ownership, consent and provenance records;
- secret/reference separation — raw provider credentials never become canonical identity or ordinary prompt/memory data;
- no paid generation requirement for milestone source acceptance unless a later explicit gate requires real-provider evidence;
- fail-closed imported-reference validation;
- provider/model/retrieval outputs as untrusted evidence rather than authority.

## Test/acceptance plan

Targeted future acceptance evidence includes:

- same locked character reused in multiple authorized projects by exact version;
- forbidden lock mutation rejected;
- new look/version does not alter previous pinned projects;
- reference-pack asset lineage and content identity remain valid;
- cross-tenant entity/version/look/reference inaccessible;
- foreign reference asset ID rejected before reuse;
- import/export manifest cannot bypass ownership/rights/consent;
- low-trust imported/generated instructions cannot mutate policy, lock or privileged authority;
- rights/provenance remain attached across fork/version/export/import;
- newly introduced trust paths receive only the minimum adversarial tests required by the cross-cutting QA map.

## Rollout/rollback

Planned implementation is append/version-based. Rollback must not rewrite historical entity versions or invalidate previously pinned lineage. Migration rollback details must be designed against the actual future schema before executable promotion.

## Exit criteria

M04 can exit only when one recurring character/entity can be versioned, locked, reference-packed and reused across multiple authorized projects with stable provider-neutral identity, exact lineage, rights/consent continuity and adversarial authority/tenant protections proven by targeted evidence.

Planning completion is **not** milestone completion.

## Non-goals

- actual provider image/video generation;
- advanced web Character Library design;
- biometric identity matching claims;
- celebrity/voice cloning without later policy implementation;
- production credentials or paid provider calls during this planning slice;
- using generic `continue`, branch synchronization, mocks or green planning CI as executable M04 consent.
