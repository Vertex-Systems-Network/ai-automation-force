# Continuity QA Specification

## Purpose

Define how the platform validates continuity between generated assets, shots, scenes and recurring characters across one or many providers.

Continuity QA compares output against canonical project state, not provider memory.

## Continuity dimensions

### Character identity
Check:
- face/identity;
- apparent age;
- species;
- body proportions;
- hair/fur;
- eyes;
- skin/fur tone;
- signature features;
- voice assignment where audio is present.

### Character look
Check:
- wardrobe;
- accessories;
- hairstyle/look variant;
- color palette;
- scene-specific state;
- prohibited mutations.

### Spatial continuity
Check:
- screen side;
- facing direction;
- eyeline;
- character relative positions;
- held objects;
- exits/entries;
- camera axis;
- foreground/background relationships.

### Environment
Check:
- World/Location identity;
- set layout;
- recurring landmarks;
- time of day;
- weather;
- lighting source/direction;
- environment damage/change state;
- recurring background objects.

### Props
Check:
- prop identity;
- location/holder;
- condition;
- color/shape;
- story state;
- appearance/disappearance logic.

### Camera and visual style
Check:
- visual medium/style;
- palette;
- lighting;
- lens/perspective intent;
- camera movement direction;
- framing continuity;
- transition compatibility.

### Motion continuity
Check:
- action direction;
- velocity/intensity;
- start/end pose;
- object trajectory;
- camera movement;
- cut-on-action compatibility.

### Audio continuity
When applicable:
- voice identity;
- room tone/ambience;
- music section alignment;
- loudness shifts;
- dialogue timing;
- SFX continuity.

## Reference hierarchy

Continuity judge should prioritize:
1. locked canonical character/entity records;
2. approved canonical style/world/location records;
3. planned incoming/outgoing shot state;
4. canonical first/end keyframes;
5. adjacent approved shot frames/audio;
6. earlier provider output only when already approved and canonical.

Rejected takes are evidence/history but not reference canon.

## Hard failures

Examples:
- wrong character identity;
- character age/species mutation;
- critical wardrobe/look mutation where locked;
- missing/incorrect story-critical prop;
- unsafe/malformed anatomy severe enough to make output unusable;
- incorrect screen direction that breaks planned action;
- missing required end-state for next shot;
- wrong speaker/voice in dialogue;
- unwanted watermark/logo/text that violates output policy;
- unresolved rights/provenance where required.

Hard failures cannot be averaged away by a high aesthetic score.

## Secondary scoring

Suggested 0–100 dimensions:
- identity;
- look/wardrobe;
- environment;
- props;
- style;
- lighting;
- composition;
- camera;
- motion;
- transition compatibility;
- audio continuity;
- artifact cleanliness.

Thresholds may vary by shot risk/profile, but critical hard gates remain independent.

## Adjacent-shot QA

For Shot N -> Shot N+1 compare:
- outgoing state N;
- incoming state N+1;
- last approved frame/state N;
- first approved frame/state N+1;
- transition intent.

The result should classify:
- PASS;
- PASS_WITH_MINOR_NOTES;
- RETRY_TAKE;
- REVISE_SHOT_PLAN;
- HUMAN_REVIEW_REQUIRED.

## Same-shot extension QA

For provider-native extension:
- identity drift;
- background drift;
- camera/motion reset;
- object discontinuity;
- temporal jump;
- style degradation.

Repeated extension drift should cause strategy change instead of indefinite extension.

## Cross-provider QA

When switching providers, increase scrutiny on:
- identity;
- style;
- color/lighting;
- proportions;
- frame boundary;
- motion.

Provider switch itself is not a failure if canonical continuity passes.

## Long-form continuity memory

Do not compare every new shot with every prior frame in a multi-hour project.

Use scoped state:
- global character canon;
- world canon;
- current Act/Sequence state summary;
- current Scene continuity ledger;
- adjacent shot state;
- material historical state changes.

Persist continuity checkpoints at scene/sequence boundaries.

## Failure diagnosis

Continuity QA should return cause categories such as:
- IDENTITY_DRIFT;
- LOOK_DRIFT;
- LOCATION_DRIFT;
- PROP_DRIFT;
- SCREEN_DIRECTION_ERROR;
- CAMERA_RESET;
- MOTION_DISCONTINUITY;
- LIGHTING_DRIFT;
- STYLE_DRIFT;
- END_STATE_MISMATCH;
- AUDIO_IDENTITY_MISMATCH;
- LIP_SYNC_FAILURE;
- PROVIDER_ARTIFACT;
- UNSAFE_OUTPUT.

Diagnosis feeds retry strategy and provider history.

## Retry recommendation

Based on diagnosis, recommend one or more:
- same provider new seed/attempt;
- strengthen character references;
- use first/end-frame mode;
- shorten shot;
- simplify action;
- change provider/model;
- revise camera/action plan;
- create intermediate keyframe;
- split shot;
- human review.

Do not silently alter story intent to pass continuity.

## Canonicalization

Only QA-passed Take may become selected/canonical Shot media.

When a new Take supersedes an earlier approved Take:
- preserve prior Take/history;
- version selection/change;
- update downstream invalidation only where necessary.

## Acceptance criteria

Continuity QA is development-ready when every generated shot has an explicit canonical reference set, hard gates, diagnostic failure categories and a retry/revision path that does not require restarting unrelated completed shots.