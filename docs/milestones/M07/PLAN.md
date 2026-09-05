# M07 — Storyboard, Timeline and Rhythm Engine

## Planning authority and current state

This document is the planning contract for M07 only. It does **not** authorize executable M07 product/API/schema/provider work.

Current planning baseline: `main@fc3382689431e811f2c3c2007e53ccd216e8bb31`, after cross-cutting adversarial QA plus M04–M06 planning promotions and broadcast-15 reconciliation.

Executable M07 work remains blocked until M04, M05 and M06 are accepted at the executable truth levels required by the milestone chain, explicit M07 executable consent is recorded, and then-current governance, branch/write ownership, migration and downstream-provider boundaries are revalidated. Planning completion, branch synchronization, green planning CI, deterministic fakes or generic conversational continuation is not executable consent.

## Objective

Implement the provider-neutral editorial planning layer from Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take, with storyboard, timeline tracks, audio/beat markers, continuity states, keyframes, non-destructive edits and OpenTimelineIO mapping, while ensuring generated/imported editorial data cannot bypass canonical tenant/project authority, version lineage, rights/provenance, hierarchy invariants or approval/security boundaries.

## Entry criteria

All are required before executable M07 work begins:

- P0 complete;
- M01–M06 accepted at their required executable truth levels;
- explicit M07 executable consent recorded through Supervisor authority;
- current main, broadcast, dependency, write ownership and migration state revalidated immediately before implementation;
- Issue #36/live repository-governance requirements satisfied where they remain part of the accepted upstream milestone chain;
- cross-cutting adversarial QA obligations applicable to the exact proposed M07 surface mapped to targeted evidence;
- current OpenTimelineIO/import/export assumptions revalidated against the implementation surface before interoperability becomes executable authority.

Current state: planning may continue, but executable M07 entry criteria are **not satisfied**. M04/M05/M06 planning promotions do not satisfy executable dependencies, and no explicit M07 executable consent is recorded.

## Dependencies

`M04 entities + M05 content + M06 audio -> M07`

Downstream impact:

- M08 depends on executable M04 and executable M07 completion;
- planning completion or synchronization does not satisfy M08 executable dependency gates.

## Work packages

### M07-WP1 — Hierarchy services
- Act/Chapter, Sequence, Scene, Shot, Take repositories/services;
- stable order/time relationships;
- duration aggregation;
- validation against project ceiling;
- long-form pagination/loading boundaries;
- imported/generated hierarchy IDs and parent relations require canonical project authorization and schema validation;
- impossible hierarchy, cross-project parents, cyclic relations, negative/overflow timing and ceiling violations fail closed before downstream execution.

### M07-WP2 — Shot planner/storyboard
- shot purpose/type/size;
- characters/entities;
- action/blocking;
- environment/props;
- camera/lens/movement;
- lighting/style;
- intended duration;
- dialogue/audio links;
- transition intent;
- generation notes;
- approval status;
- generated scene/shot text remains advisory evidence and cannot mint approval, publish, budget, tool or security authority;
- all referenced entities/assets/audio resolve through canonical tenant/project authority rather than trusting generated/provider IDs.

### M07-WP3 — Timing/rhythm engine
Timing modes:
- audio-led;
- script-led;
- picture-led;
- music-led.

Represent:
- beats/bars/verse/chorus/drop;
- narrative beats;
- pauses/reactions;
- emotional curve;
- pacing targets;
- handles/overlap;
- transition timing.

Timing imported from models/providers/editors is input evidence only. Canonical duration ceilings, clip bounds and monotonic timeline invariants remain deterministic product authority.

### M07-WP4 — Timeline tracks
Canonical tracks:
- video;
- dialogue;
- music;
- SFX/ambience;
- captions;
- markers/beats;
- emotion/continuity metadata.

Support clip timing, trims, gaps, overlays and linked media references without embedding binaries.

Rules:
- linked media IDs are canonical object references, tenant/project authorized on use;
- foreign provider IDs/URLs or model-returned references cannot become timeline authority without canonical resolution;
- provider-specific hidden state is never required to interpret canonical timeline truth;
- clip operations preserve rights/provenance/version references rather than copying unverified metadata into stronger classes.

### M07-WP5 — Continuity in/out state
Per shot:
- incoming character/entity state;
- pose/position/screen direction;
- wardrobe/accessories;
- environment/props;
- time/lighting;
- camera/action state;
- outgoing state;
- first/end frame references.

Continuity state is versioned evidence, not a model-owned authority surface. Later generated suggestions cannot silently mutate pinned character/entity/reference versions or approved prior-shot continuity.

### M07-WP6 — Keyframe/reference strategy
- first-frame;
- end-frame;
- mid keyframes;
- character/style/world references;
- approved asset version pinning;
- image-generation strategy integration;
- no provider-specific state as canonical timeline data;
- reference asset/version lineage, ownership/rights and project scope remain explicit;
- unknown/foreign provider-returned reference IDs are rejected until canonical lookup proves authority.

### M07-WP7 — OTIO interchange and versioned edits
- map approved editorial structure to OpenTimelineIO;
- import supported editorial timing/metadata;
- namespaced AI metadata;
- version snapshots;
- undo/redo-safe operation model;
- optimistic conflict handling;
- imported OTIO/external metadata remains untrusted until schema, project ownership, referenced-asset authority, duration/hierarchy invariants and supported-semantics validation pass;
- unsupported/unknown metadata cannot create privileged actions or silently mutate approved state;
- import creates a new reviewable version and never destructively overwrites an approved timeline;
- stale optimistic writes fail safely rather than silently winning over a newer approved version.

### M07-WP8 — Acceptance
Create a 10-minute representative project from approved content/audio:
- hierarchical storyboard;
- editable timeline;
- beat/audio alignment;
- continuity in/out;
- references/keyframes;
- OTIO export/import round trip within supported semantics;
- no provider video spend;
- no cross-tenant/foreign reference acceptance;
- no silent approved-version overwrite;
- no generated/imported text or metadata authority escalation.

## Cross-cutting adversarial acceptance obligations

`docs/qa/ADVERSARIAL-AUDIT-PLAN.md` is a mandatory planning input. When M07 later requests executable promotion, QA must re-evaluate the exact reachable authority surface and add only targeted missing evidence.

At minimum M07 acceptance must prove:

1. **Generated editorial text cannot grant authority** — model/provider/imported text cannot create tool, publish, approval, budget, account or security authority.
2. **Canonical tenant/project reference authorization** — entity, asset, audio, keyframe, first/end-frame and other reference IDs are canonical-looked-up and tenant/project authorized before use.
3. **Provider state is not canonical timeline truth** — provider IDs, URLs, hidden job state or model-returned metadata cannot become the only source of timeline/reference authority.
4. **Pinned lineage survives edits** — later edits preserve exact character/entity/asset/audio/reference versions and cannot silently rewrite approved prior versions.
5. **Malformed/generated structures fail closed** — invalid hierarchy, timing, duration, schema, reference or continuity structures are rejected before downstream execution.
6. **OTIO/import data is untrusted** — imported external structures and metadata require supported-semantics, schema, ownership, hierarchy, timing and reference validation before becoming canonical.
7. **Approved state is non-destructive** — import/edit operations create reviewable versions; approved timelines are not silently overwritten.
8. **Optimistic conflicts fail safely** — stale writes cannot silently replace a newer approved version or reference lineage.
9. **Rights/provenance remain attached** — referenced media/entity/voice assets retain ownership, rights/consent and provenance continuity through storyboard/timeline versions.
10. **No synthetic downstream success** — deterministic planning fixtures prove contracts only; no video/provider/publish/production truth is inferred from planning CI.

Do not add duplicate umbrella tests for already-proven lower-layer M03 asset isolation or M04–M06 planning statements unless M07 introduces a newly reachable authority/trust path.

## Expected modules/files

Planned future executable surface only:

- hierarchy/editorial services;
- rhythm/timing package;
- timeline/track models;
- continuity-state package;
- OTIO adapter;
- storyboard/timeline APIs;
- fixtures/tests.

Actual executable write ownership and migration reservations must be assigned fresh by the Supervisor after entry criteria pass.

## Data/migration impact

Expected future implementation may add hierarchy nodes, track/clip/marker/timing data, continuity states, reference links and editorial versions/operations.

This planning slice creates **no migration reservation and no schema change**. Future migration IDs must be reserved only after executable M07 authority exists and the then-current migration head is audited.

## API/UI impact

Future implementation may add storyboard/timeline read/write/version APIs. Full rich editor UI arrives M11, but the API/state model is fixed here.

This planning slice changes no API or UI.

## Security/cost/rights impact

Future M07 must preserve:

- referenced asset/entity/audio/keyframe canonical tenant/project authorization;
- exact version/reference lineage and rights/provenance continuity;
- no generation/video-provider spend required for M07 source acceptance;
- edit permissions/version conflict model compatible with future RBAC;
- sensitive media remains object references rather than embedded secret-bearing payloads;
- imported/generated metadata remains low-trust until deterministic validation;
- provider/model text cannot elevate approval/publish/tool/security authority.

## Test/acceptance plan

Targeted future evidence includes:

- hierarchy/duration invariants and invalid-parent/cycle/ceiling rejection;
- cross-project/foreign asset/entity/audio/reference ID denial;
- shot reorder/time edits with exact pinned lineage preservation;
- audio/beat alignment and duration-bound validation;
- continuity state propagation without silent identity/version mutation;
- first/end frame links using canonical authorized assets;
- generated malformed timeline/storyboard structure rejection;
- optimistic stale-write conflict rejection;
- OTIO round trip for supported semantics;
- malicious/foreign OTIO references and authority-like metadata rejection;
- import creates a new version rather than overwriting approved state;
- long list/query performance fixtures.

## Rollout/rollback

Editorial operations/version snapshots are non-destructive. OTIO import creates a new version rather than overwriting approved state without review. Rollback selects an earlier valid version; it does not erase lineage/audit evidence or silently repoint pinned references.

## Exit criteria

M07 can exit only when a representative project can be fully planned and edited as a provider-neutral storyboard/timeline with rhythm, audio markers, continuity and keyframes while preserving canonical tenant/project authority, supported import semantics, version lineage, rights/provenance and fail-closed validation before any video-generation spend.

Planning completion is **not** executable milestone completion.

## Non-goals

- real video generation;
- final FFmpeg master;
- full M11 visual timeline UI;
- professional NLE feature parity;
- provider-specific clip limits/state defining canonical project structure;
- production credentials or paid provider calls during this planning slice;
- using generic `continue`, branch synchronization, mocks or green planning CI as executable M07 consent.
