# M10 — Deterministic Assembly and Final Rendering

## Objective

Implement deterministic FFmpeg-based media assembly so approved multi-provider image/video/audio assets become reproducible masters, captions, proxies and aspect variants without manual timeline reconstruction.

## Entry criteria

- P0 complete.
- M01–M09 accepted.
- Explicit M10 consent.
- Current FFmpeg/security codec stack revalidated.

## Dependencies

`M06 audio + M07 editorial timeline + M09 approved takes -> M10`

## Work packages

### M10-WP1 — Render-plan compiler
Compile canonical timeline/editorial state into a deterministic RenderPlan:
- clips/trim in/out;
- transitions;
- overlays;
- track routing;
- audio stems;
- captions;
- target duration;
- aspect/resolution/FPS/codec preset;
- source asset hashes/versions.

### M10-WP2 — Video assembly primitives
- concat;
- trim;
- scale/crop/pad;
- frame-rate conversion when required;
- transitions/filtergraphs;
- image still duration/motion-safe placement;
- overlays/titles only from validated templates;
- handling missing/failed source.

### M10-WP3 — Audio master integration
- dialogue/narration/music/SFX track alignment;
- ducking;
- loudness normalization;
- fades;
- channel/sample conversion;
- sync checks;
- final mix + stems/alternate mixes when preset requires.

### M10-WP4 — Captions/subtitles
- sidecar formats;
- burn-in option;
- font/style templates;
- safe-area positioning;
- language variants;
- timing validation;
- UTF/RTL text support where rendering stack permits.

### M10-WP5 — Output presets and platform variants
Canonical presets:
- source/master archival;
- 16:9 landscape;
- 9:16 vertical;
- 1:1 square;
- 4:5 portrait;
- preview/proxy;
- thumbnail/poster/contact sheet.

Preset config versioned. M12 may add platform-specific constraints without rewriting renderer core.

### M10-WP6 — Incremental/scoped renders
- scene/sequence preview;
- changed-shot-only intermediate rebuild;
- cache approved unchanged segments;
- final concat/reassembly;
- invalidation based on source/version/render settings;
- long-form chunking.

### M10-WP7 — Render manifests, idempotency and validation
Manifest records:
- render ID;
- exact source asset IDs/hashes;
- timeline version;
- FFmpeg/tool version;
- command/filtergraph normalized representation;
- preset;
- output hash/metadata;
- duration;
- validation/QA;
- logs/errors.

Repeated same idempotent render request can reuse valid output according to cache policy.

### M10-WP8 — Acceptance
Representative project:
- multi-provider approved clips;
- narration/music/SFX;
- captions;
- transitions;
- landscape + vertical outputs;
- proxy/master;
- deterministic manifest;
- partial shot replacement triggers scoped rerender;
- worker crash/retry no corrupted canonical output.

## Expected modules/files

- render-plan compiler;
- FFmpeg worker/activity package;
- preset registry;
- caption/subtitle package;
- render cache/invalidation;
- render APIs/status;
- deterministic media fixtures.

## Data/migration impact

Adds RenderPlan/RenderJob/RenderManifest, output/derivative links, preset versions and cache/invalidation metadata.

## API/UI impact

Adds render/preview/export/status APIs. Rich export/preset UI later M11.

## Security/cost/rights impact

- FFmpeg isolated/resource-limited;
- no raw shell injection;
- source rights/approval checked before final render;
- rendering compute/storage/egress tracked;
- subtitles/text escaped/validated;
- final output inherits provenance/rights lineage.

## Test/acceptance

- trim/concat/transitions;
- audio mix/loudness;
- caption timing/Unicode;
- aspect variants;
- corrupted source;
- resource timeout/cancel;
- incremental invalidation;
- output hash/manifest;
- long-form chunk fixture;
- worker restart.

## Rollout/rollback

Renderer/preset/tool versions pinned. New FFmpeg/preset versions can run side-by-side; historical manifests preserve reproducibility. Source/approved assets are never overwritten.

## Exit criteria

A multi-provider project renders reproducibly from canonical timeline state into validated master and derivative outputs, and changing one failed/replaced shot does not require manual reconstruction or unnecessary full regeneration.

## Non-goals

- generative video creation;
- professional compositor/NLE replacement;
- public social publishing;
- final rich web editor;
- uncontrolled user-provided arbitrary FFmpeg commands.
