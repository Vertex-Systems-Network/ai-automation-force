# M07 — Storyboard, Timeline and Rhythm Engine

## Objective

Implement the provider-neutral editorial planning layer from Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take, with storyboard, timeline tracks, audio/beat markers, continuity states, keyframes, non-destructive edits and OpenTimelineIO mapping.

## Entry criteria

- P0 complete.
- M01–M06 accepted.
- Explicit M07 consent.

## Dependencies

`M05 content + M06 audio + M04 entities -> M07`

## Work packages

### M07-WP1 — Hierarchy services
- Act/Chapter, Sequence, Scene, Shot, Take repositories/services;
- stable order/time relationships;
- duration aggregation;
- validation against project ceiling;
- long-form pagination/loading boundaries.

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
- approval status.

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

### M07-WP6 — Keyframe/reference strategy
- first-frame;
- end-frame;
- mid keyframes;
- character/style/world references;
- approved asset version pinning;
- image-generation strategy integration;
- no provider-specific state as canonical timeline data.

### M07-WP7 — OTIO interchange and versioned edits
- map approved editorial structure to OpenTimelineIO;
- import supported editorial timing/metadata;
- namespaced AI metadata;
- version snapshots;
- undo/redo-safe operation model;
- optimistic conflict handling.

### M07-WP8 — Acceptance
Create a 10-minute representative project from approved content/audio:
- hierarchical storyboard;
- editable timeline;
- beat/audio alignment;
- continuity in/out;
- references/keyframes;
- OTIO export/import round trip within supported semantics;
- no provider video spend.

## Expected modules/files

- hierarchy/editorial services;
- rhythm/timing package;
- timeline/track models;
- continuity-state package;
- OTIO adapter;
- storyboard/timeline APIs;
- fixtures/tests.

## Data/migration impact

Adds hierarchy nodes, track/clip/marker/timing data, continuity states, reference links and editorial versions/operations.

## API/UI impact

Adds storyboard/timeline read/write/version APIs. Full rich editor UI arrives M11, but the API/state model is fixed here.

## Security/cost/rights impact

- referenced assets tenant/right checked;
- no generation spend required;
- edit permissions/version conflict model compatible with future RBAC;
- sensitive media remains object references.

## Test/acceptance

- hierarchy/duration invariants;
- shot reorder/time edits;
- audio/beat alignment;
- continuity state propagation;
- first/end frame links;
- optimistic conflicts;
- OTIO round trip;
- long list/query performance fixtures.

## Rollout/rollback

Editorial operations/version snapshots are non-destructive. OTIO import creates a new version rather than overwriting approved state without review.

## Exit criteria

A 10-minute project can be fully planned and edited as a provider-neutral storyboard/timeline with rhythm, audio markers, continuity and keyframes before any video-generation spend.

## Non-goals

- real video generation;
- final FFmpeg master;
- full M11 visual timeline UI;
- professional NLE feature parity;
- provider-specific clip limits defining project structure.
