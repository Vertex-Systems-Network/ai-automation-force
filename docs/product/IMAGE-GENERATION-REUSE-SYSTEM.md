# Image Generation & Reuse System

## Purpose

Define a provider-neutral image-generation layer that can create, approve, lock, reuse and version still-image assets before and during video production.

Images are not disposable prompt outputs. Approved images become canonical or derived production assets that may drive character identity, worlds, props, storyboards, keyframes, thumbnails and image-to-video generation.

The system must support both AI-generated and imported images through the same asset/provenance/QA pipeline.

## Core principle

Use images when they improve control, continuity, cost efficiency or editorial planning.

Do not force image generation before every video shot. The Image Planner decides whether a shot/project benefits from a canonical still reference.

Canonical project state remains provider-independent. Provider-specific reference IDs or sessions are derived implementation details.

## Image generation modes

Project or workflow option:

- `AUTO` — AI decides where still references materially improve the production.
- `CHARACTER_FIRST` — generate/approve character reference packs before recurring use.
- `KEYFRAME_FIRST` — generate approved shot/scene keyframes before video generation.
- `SCENE_FIRST` — generate one or more canonical scene/location frames before shot production.
- `ALL_SHOTS_KEYFRAMED` — every continuity-sensitive shot gets an approved first/key frame.
- `DIRECT_VIDEO_ALLOWED` — image stage may be skipped for continuity-insensitive shots when provider capability/quality is sufficient.
- `MANUAL` — operator explicitly chooses which images to generate/use.

Default recommendation: `AUTO`, with mandatory character/reference generation when a recurring locked identity does not yet have an adequate canonical reference pack.

## Image asset purposes

Supported purposes include:

### Character identity
- canonical hero/reference portrait;
- front/side/back reference;
- full-body reference;
- expression sheet;
- pose/action sheet;
- wardrobe/look variants;
- age/state variants when intentionally versioned;
- character + signature prop reference;
- multi-character lineup for scale/relationship guidance.

### World/location
- establishing reference;
- room/set layout;
- exterior/interior variants;
- day/night/weather variants;
- recurring landmark reference;
- production-design reference.

### Props/objects
- canonical object reference;
- front/back/side views;
- held/use-state reference;
- condition/damage-state variants.

### Style
- visual style reference;
- palette reference;
- material/texture reference;
- lighting reference;
- composition reference.

### Storyboard/editorial
- storyboard frame;
- scene board;
- first frame;
- midpoint keyframe;
- end/target frame;
- transition bridge frame;
- poster frame;
- thumbnail;
- cover/key art.

### Video generation control
- image-to-video source;
- first-frame anchor;
- last/end-frame target where provider supports it;
- character/reference-image input;
- style-reference input;
- scene/location reference;
- adjacent-shot continuity anchor;
- video-extension handoff frame.

## Canonical image lifecycle

`planned -> briefed -> generation-ready -> generated-candidate -> image-qa -> approved -> registered -> canonical-or-derived -> downstream-in-use`

Failure states:
- `rejected-quality`
- `rejected-identity`
- `rejected-style`
- `rejected-rights`
- `blocked-provider`
- `blocked-quota`
- `blocked-budget`
- `manual-handoff`

An API returning a file does not make the image canonical.

## Image Planner

The Image Planner decides:
- whether an image is required;
- image purpose;
- required canonical entities;
- source references;
- aspect ratio/resolution;
- composition;
- camera/viewpoint;
- style/lighting;
- text-free requirement;
- number of candidates;
- required QA strictness;
- whether approval is automatic or human-gated;
- downstream intended use.

Examples:

`need: locked recurring character, full body, neutral pose, front view, consistent wardrobe, transparent/clean background preferred`

`need: shot SHT-000123 first-frame keyframe, 16:9, characters CHR-000001@v2 + CHR-000004@v1, location LOC-000008, warm sunset, medium-wide, screen direction left-to-right`

## Image generation request contract

Provider-neutral request should include where relevant:
- request/job ID;
- image purpose;
- project/scene/shot IDs;
- content/audience policy;
- character/version/look IDs;
- world/location/prop/style IDs;
- canonical reference asset IDs;
- positive visual intent;
- prohibited mutations/negative constraints;
- aspect ratio;
- target dimensions/resolution class;
- camera/composition;
- lighting/palette;
- seed/reference-strength controls when provider exposes them;
- candidate count;
- commercial-use requirement;
- watermark policy;
- budget/quality policy;
- expected output contract.

Provider adapters translate this request into provider-specific API payloads.

## Image provider router

Use the same provider-independent routing philosophy as video/audio.

Router considers:
- text-to-image support;
- image editing support;
- character/reference-image support;
- style-reference support;
- multi-reference capability;
- output resolution;
- aspect ratio;
- transparency where applicable;
- inpainting/outpainting/edit capability;
- quality history;
- identity consistency history;
- latency;
- free quota;
- paid cost;
- commercial rights;
- watermark;
- current provider health;
- retry-adjusted expected accepted-output cost.

Current provider facts remain in the dynamic provider registry and are refreshed by the provider scout rather than hard-coded into this document.

## Multi-provider failover

Default account policy remains one authorized account/connection per provider unless provider/business rules explicitly support another legitimate organization/workspace structure.

Multiple different providers may be connected simultaneously.

If the selected image provider becomes unavailable, quota-exhausted, budget-blocked, rate-limited or repeatedly fails QA:
1. preserve the canonical ImageGenerationRequest;
2. preserve all character/world/style locks;
3. preserve reference asset IDs and hashes;
4. record the failed attempt;
5. re-score eligible providers;
6. compile the same canonical intent for the next provider;
7. generate new candidates;
8. run the same image QA;
9. approve only acceptable output.

Do not rotate multiple same-provider accounts to evade free-tier/quota limits.

Cross-provider output is not expected to be pixel-identical. The system preserves canonical intent and uses QA to minimize identity/style drift.

## Image QA

### Hard checks
- correct locked character identity/version/look;
- correct apparent age/species;
- no missing/extra required characters;
- no prohibited character mutation;
- anatomy/object integrity;
- required prop identity/state;
- required location/world identity;
- no unwanted text/logo/watermark;
- safety/content-policy compliance;
- rights/provenance complete enough for intended use.

### Continuity checks
- wardrobe/accessories;
- hair/fur/eyes/colors;
- proportions;
- palette/style;
- lighting direction;
- environment layout;
- screen direction;
- pose/action state;
- prop holder/location;
- adjacent keyframe compatibility.

### Aesthetic/technical checks
- composition;
- focus/readability;
- crop/safe area;
- resolution;
- aspect ratio;
- artifacts;
- intended camera viewpoint;
- thumbnail/poster readability where relevant.

Critical identity/safety/rights failures are hard failures.

## Candidate selection

The system may generate multiple candidates when allowed by policy.

Candidate selection flow:
`candidates -> technical validation -> identity/continuity QA -> aesthetic score -> rights check -> best acceptable candidate -> approval`

Rejected candidates remain generation-history records.

Do not automatically promote the visually prettiest candidate if it violates continuity or locked identity.

## Canonical reference packs

For recurring characters, locations and important props, approved image sets should form versioned reference packs.

Example character pack:
- `CHR-000001@v2 / LOOK-000003`
- hero portrait;
- full body front;
- profile;
- three-quarter;
- back;
- neutral expression;
- happy/sad/surprised expressions;
- signature wardrobe;
- palette reference;
- scale/reference metadata.

Reference packs are reusable across projects when rights/project policy allows.

Changing the pack never silently mutates the locked CharacterVersion. A material identity change creates a new version/look.

## Image editing/regeneration

Supported logical operations:
- full regenerate;
- edit instruction;
- inpaint region;
- outpaint/extend canvas;
- background replacement;
- wardrobe/look change through an approved new look;
- expression/pose variation;
- lighting/time-of-day variation;
- aspect-ratio adaptation;
- style-safe derivative;
- cleanup/upscale when provider/tool policy allows.

Edits create new Asset lineage. Never overwrite the only approved canonical original.

## Image -> video handoff

When an approved image will drive video:

1. resolve Shot + character/world/style state;
2. resolve approved image Asset ID and hash;
3. mark intended role: `first_frame`, `reference`, `end_frame`, `style_reference`, etc.;
4. compile provider-neutral motion/action/camera intent;
5. select video provider based on required image-conditioning capability;
6. pass provider-specific reference representation;
7. record video attempt lineage to the image asset;
8. run video QA against both canonical entities and the source image;
9. approve only if motion output preserves required identity/state.

The source image remains immutable canonical evidence even when video providers internally transform it.

## First/end-frame strategy

For strict continuity:
- generate/approve the starting image/keyframe;
- generate/approve the intended end image when useful;
- use both when the provider supports first+last frame control;
- otherwise use the first frame/reference plus explicit target-state metadata;
- after approved video generation, extract/approve the final frame as the continuity anchor for the next shot when appropriate.

Do not blindly chain provider output without canonical checks.

## Long-form strategy

For long projects, do not generate a unique still for every frame.

Prefer reusable hierarchical image assets:
- character reference packs;
- world/location references;
- scene hero keyframes;
- shot keyframes only where continuity/control warrants them;
- transition anchors at scene/sequence boundaries;
- poster/thumbnail assets separately.

The Image Planner can increase keyframe density for difficult scenes and reduce it for simple continuity-insensitive shots.

## Cost strategy

Image generation can be used as a lower-cost control/validation step before expensive video calls when it materially reduces failed video attempts.

Routing should consider expected accepted-video cost, not merely image call cost.

Example:
`approved character+scene keyframe -> image-to-video`
may be preferable to several failed text-to-video attempts when strict identity is required.

But do not generate unnecessary stills when direct video has equal expected quality and lower total cost.

## Asset library integration

Every generated/imported image is registered in the Asset & Media Library with:
- Asset ID;
- purpose/type;
- canonical/candidate/rejected state;
- dimensions/MIME/size/hash;
- provider/model/attempt;
- prompt/version;
- parent/reference IDs;
- character/world/scene/shot links;
- QA;
- rights/provenance;
- storage URI;
- downstream usage links.

## Invalidation rules

Changing an upstream locked reference may make derived assets stale.

Examples:
- CharacterVersion change -> character keyframes/video takes using old version remain historical and new work must use new version;
- approved Look change -> affected planned keyframes marked stale;
- Location revision -> scene keyframes may need refresh;
- StyleProfile change -> not-yet-approved image/video assets re-evaluated;
- source image replacement -> dependent video attempts remain historical but new generations use the new selected image.

Invalidate the smallest affected scope rather than rebuilding the whole project.

## Operator/UI controls

Future UI should expose:
- generate image;
- upload/import image;
- select purpose;
- choose Auto vs manual provider policy;
- candidate grid/compare;
- approve/reject;
- regenerate/edit;
- lock as canonical reference;
- create new version/look;
- assign to character/location/prop/style/scene/shot;
- use as first frame;
- use as end frame;
- use as video reference;
- show lineage/downstream usage;
- show provider/cost/rights/QA state.

## AI roles

Logical responsibilities:
- Visual Director — canonical art/style intent;
- Image Planner/Reference Director — decides which still assets are needed and their purpose;
- Prompt Compiler — compiles provider-specific image request;
- Provider Router — selects provider/model;
- Generation Supervisor — executes/records attempts;
- Image QA/Continuity Agent — validates identity/style/technical quality;
- Asset Manager — registers approved/rejected lineage;
- Storyboard/Shot Planner — consumes approved keyframes;
- Video Router/Generation Supervisor — uses approved images for image-conditioned video.

These roles may be implemented by shared models/workers; role boundaries are logical/auditable.

## Current provider research note — 2026-08-28

Current official documentation confirms that provider capabilities are already broad enough for this abstraction:
- Google recommends current Gemini image-generation (Nano Banana family) for generation/editing; older Imagen path is deprecated.
- Runway exposes image generation and model-routing APIs in addition to video/audio routing.
- Luma documents text-to-image plus character, image and style references and image-to-image operations.

These facts are volatile and must be refreshed through the provider registry/scout at implementation/runtime rather than treated as permanent constants.

## Acceptance criteria

The Image Generation & Reuse System is development-ready when the platform can:
1. decide whether a still image is needed;
2. create a provider-neutral image brief;
3. generate/import candidate images through eligible providers;
4. QA and approve one without mutating locked canon;
5. register the image with full lineage/provenance;
6. reuse it as a canonical character/world/style/keyframe/reference asset;
7. feed it into image-to-video/first-frame/end-frame/reference workflows;
8. fail over providers without losing canonical intent;
9. preserve historical attempts and downstream dependency links;
10. invalidate only affected downstream work when the selected image changes.
