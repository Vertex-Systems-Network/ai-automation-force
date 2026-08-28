# Storyboard & Shot Planning Specification

## Purpose

Convert approved script/audio/content into a provider-neutral visual execution plan that is editable, resumable, cost-aware and continuity-safe before expensive image/video generation begins.

Storyboard planning is a deterministic planning stage. It does not imply provider spend.

## Hierarchy

Canonical hierarchy:

`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take`

The storyboard primarily plans Scenes and Shots. Takes are generated attempts/alternatives for an already planned Shot.

## Scene record

A Scene plan should include:
- Scene ID;
- parent Sequence ID;
- title/slug;
- narrative purpose;
- source script/audio range;
- target duration;
- characters and pinned versions/looks;
- World/Location;
- recurring props;
- time of day/weather;
- emotional state in/out;
- continuity state in/out;
- dialogue/narration/music segments;
- scene pacing;
- required coverage;
- transition in/out;
- risk notes;
- estimated generation complexity/cost class.

## Shot record

A planned Shot should include:
- Shot ID;
- Scene ID;
- order;
- start time;
- target editorial duration;
- source audio/script segment;
- shot purpose;
- shot size;
- camera angle;
- lens/perspective intent;
- camera movement;
- character IDs/versions/looks;
- character blocking/pose/action;
- Location/World state;
- props and state;
- lighting;
- composition;
- primary motion;
- secondary motion;
- first-frame reference intent;
- end-frame reference intent;
- optional mid-keyframe intent;
- continuity constraints;
- negative constraints;
- transition intent;
- audio events;
- provider capability requirements;
- generation priority;
- QA critical dimensions.

## Shot purpose vocabulary

Suggested values:
- establish;
- introduce character;
- action;
- dialogue speaker;
- reaction;
- emotional beat;
- reveal;
- insert/detail;
- cutaway;
- B-roll;
- transition;
- performance;
- dance/action cue;
- educational demonstration;
- atmosphere;
- montage beat;
- closing beat;
- custom.

## Shot duration

Editorial shot duration is independent from provider generation duration.

Examples:
- desired editorial shot 2.8 sec from a 5 sec generated take -> trim;
- desired 10 sec shot with provider max 8 sec -> use extension, multiple controlled segments or alternative coverage;
- desired 20 sec static illustrated beat -> use still/parallax/animation strategy rather than forcing a 20 sec generative video call.

The planner chooses the least risky production method that preserves creative intent.

## Keyframes

### First frame
Defines entry state:
- composition;
- character identity/look;
- position;
- environment;
- camera;
- lighting;
- props;
- incoming continuity.

### End frame
Defines desired exit state when useful:
- motion destination;
- camera endpoint;
- pose;
- object state;
- transition compatibility.

### Mid keyframe
Use only when the action or transformation is complex enough that beginning/end constraints are insufficient.

Keyframes should be canonical assets or derived references with lineage.

## Coverage planning

For dialogue/narrative scenes AI Director decides whether the scene needs:
- establishing shot;
- master shot;
- two/group shot;
- singles;
- over-the-shoulder;
- reaction shots;
- inserts;
- cutaways;
- transition/exit shot.

Coverage should be sufficient for editing but not generated wastefully.

## Music-driven planning

For songs/music videos align shots to:
- sections;
- phrase boundaries;
- beats/bars when useful;
- musical accents;
- lyric ideas;
- chorus/refrain repetition;
- instrumental sections;
- energy changes.

Avoid a mechanical cut on every beat unless the creative treatment explicitly requires it.

## Narration-driven planning

Use:
- sentence/phrase boundaries;
- semantic ideas;
- pauses;
- reveals;
- examples;
- emotional changes.

Visuals may lead, support or intentionally contrast narration, but must remain coherent.

## Dialogue-driven planning

Track:
- speaker;
- listening character;
- eyeline;
- screen direction;
- reaction timing;
- overlap/interruption;
- lip-sync requirement;
- camera axis.

Do not switch arbitrary camera positions that break spatial understanding.

## Long-form planning

For episodes/movies, do not load the entire 3-hour script/state into every shot-planning prompt.

Use scoped context:
- global canon summary;
- current character canon;
- current Act/Sequence goals;
- current Scene source text;
- adjacent scene continuity;
- relevant prior state changes.

Persist summaries/checkpoints at Act/Sequence/Scene boundaries.

## Continuity state

Each continuity-sensitive Shot stores incoming/outgoing state for:
- character positions;
- direction/facing;
- pose/action;
- expression/emotion;
- wardrobe/look;
- held props;
- object state;
- camera position/movement;
- lighting/time;
- environment changes.

This state is the bridge across providers.

## Transition planning

Transitions are editorial intent, not necessarily generated inside the video model.

Prefer deterministic post-production for:
- cut;
- dissolve;
- fade;
- J/L audio cuts;
- simple wipes/graphics;
- beat cuts.

Use generative transition/bridge only when the visual transformation itself is part of the content.

## Generation strategy classification

Each Shot can recommend one of:
- still image + deterministic movement;
- text-to-image then image-to-video;
- reference-image generation;
- image-to-video;
- first/end-frame video;
- native extension;
- video-to-video;
- reference video;
- pure text-to-video when continuity-insensitive;
- deterministic motion graphics;
- manual/imported asset.

The provider router may select a compatible implementation but must not violate canonical shot constraints.

## Risk classification

High-risk shots include:
- many recurring characters;
- close face + fast movement;
- object handoff;
- precise lip sync;
- complex choreography;
- camera orbit around multiple characters;
- text/signage inside scene;
- transformation with strict identity;
- continuity-critical action bridge.

High-risk shots may receive more references, shorter generation segments, higher-quality provider routing or human review depending on policy.

## Shot QA plan

Before generation define hard gates relevant to that shot:
- identity;
- specific prop;
- action completion;
- screen direction;
- end state;
- lip sync;
- safety;
- no text/logo;
- style match.

Secondary scored dimensions:
- composition;
- lighting;
- natural motion;
- artifact severity;
- cinematic quality.

## Regeneration

A failed Take does not invalidate the Shot plan automatically.

Flow:
`Shot -> Attempt/Take -> QA fail -> diagnose -> modify provider/prompt/reference/strategy -> new Take`

If repeated failures indicate the Shot itself is infeasible, AI Director may propose a revised Shot plan. Material story/edit change should be versioned and reviewed according to policy.

## Acceptance criteria

Storyboard planning is development-ready when a complete project can reach a provider-neutral shot list with timing, continuity, visual/audio intent, generation requirements and QA criteria before any provider call is made.