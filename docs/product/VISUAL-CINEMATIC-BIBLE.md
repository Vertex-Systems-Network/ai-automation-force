# Visual & Cinematic Bible

## Purpose

Define provider-neutral visual direction so the platform can create coherent shots across multiple AI image/video providers while preserving character identity, world rules, style, camera language and editorial continuity.

Visual direction is canonical project state. Provider prompts are derived implementations.

## Visual medium

Supported high-level media include:
- live-action realistic;
- photoreal cinematic;
- stylized 3D animation;
- 2D animation;
- storybook illustration;
- hand-drawn/cartoon;
- anime-inspired generic style without imitating protected franchises/artists;
- stop-motion/clay-like;
- miniature/toy world;
- motion graphics;
- mixed media;
- abstract/visualizer;
- documentary illustration;
- custom.

## Realism level

Optional scale:
- symbolic/graphic;
- highly stylized;
- stylized;
- semi-realistic;
- realistic;
- photoreal.

Character/version locks constrain how far realism/style may change across a project.

## Canonical style profile

A StyleProfile may include:
- style ID/version;
- visual medium;
- realism level;
- palette;
- contrast;
- saturation;
- texture/material language;
- line/shape language;
- environment detail level;
- character proportion language;
- lighting philosophy;
- lens/perspective philosophy;
- motion philosophy;
- prohibited mutations/styles;
- reference asset IDs;
- provider-specific adapter notes as derived metadata.

## Color & palette

Define where useful:
- primary colors;
- secondary colors;
- neutrals;
- accent colors;
- skin/fur/material colors for canonical identities;
- day/night variants;
- scene-specific deviations;
- forbidden palette changes.

Color continuity is important for recurring characters, wardrobe, signature props and branded/series worlds.

## Lighting profiles

Examples:
- soft daylight;
- golden hour;
- moonlit night;
- high-key studio;
- low-key cinematic;
- practical/interior warm;
- cool ambient + warm key;
- magical glow;
- overcast natural;
- dramatic silhouette;
- documentary naturalistic.

Lighting state should include source direction and motivation when continuity matters.

## Composition

Options include:
- centered;
- rule-of-thirds;
- symmetrical;
- negative-space;
- leading-lines;
- layered depth;
- flat graphic;
- wide environmental;
- character-dominant;
- product/object-dominant;
- dynamic diagonal;
- custom.

Composition must account for aspect-ratio derivatives and caption-safe zones where required.

## Shot sizes

Canonical vocabulary:
- extreme wide / establishing;
- wide / full;
- medium wide;
- medium;
- medium close-up;
- close-up;
- extreme close-up;
- insert/detail;
- over-the-shoulder;
- two-shot;
- group shot;
- POV;
- aerial/overhead.

## Camera angles

- eye level;
- high angle;
- low angle;
- top-down;
- worm's-eye;
- Dutch angle when intentionally justified;
- profile;
- three-quarter;
- over-shoulder;
- POV.

## Lens / perspective intent

Provider-neutral categories:
- ultra-wide environmental;
- wide;
- natural/normal;
- portrait/telephoto;
- macro/detail;
- shallow-focus portrait;
- deep-focus environment;
- orthographic/graphic where applicable.

Do not depend on exact physical lens simulation unless the selected provider supports it reliably.

## Camera movement

- static/locked;
- pan;
- tilt;
- push/dolly in;
- pull/dolly out;
- truck left/right;
- pedestal up/down;
- orbit;
- crane/jib;
- stabilized follow;
- handheld controlled;
- zoom;
- rack focus/focus transition;
- aerial/drone-like;
- object/character POV motion;
- generative bridge where justified.

Movement has direction, speed, easing and start/end state.

## Blocking & screen direction

For every continuity-sensitive scene track:
- character screen side;
- entering/exiting direction;
- eyeline;
- facing direction;
- body pose;
- hand/object occupancy where material;
- relative positions;
- camera side/axis.

Do not casually cross screen direction/180-degree axis without an intentional transition or establishing reset.

## Character visual state

Every recurring appearance should resolve:
- Character ID;
- CharacterVersion ID;
- Look ID;
- wardrobe;
- accessories;
- hair/fur;
- age/species appearance;
- expression/emotion;
- pose/action;
- reference assets;
- prohibited mutations.

Provider output is compared to this state, not accepted as the new canon automatically.

## Environment state

Track where relevant:
- World ID;
- Location ID;
- time of day;
- weather;
- season;
- lighting;
- set dressing;
- recurring background landmarks;
- spatial layout;
- recurring props;
- damage/change state after story events.

## Prop state

Recurring props may have:
- Prop ID/version;
- visual references;
- holder/location;
- condition;
- orientation;
- story importance;
- continuity constraints.

## Motion design

Character/object motion categories:
- idle/subtle;
- walk/run;
- dance/action choreography;
- gesture;
- object manipulation;
- facial reaction;
- environmental motion;
- vehicle motion;
- camera-only motion;
- transition movement.

Specify primary action and avoid overloading a short generative shot with multiple conflicting actions.

## Visual pacing

Profiles:
- very gentle;
- gentle;
- balanced;
- energetic;
- fast;
- cinematic dynamic;
- music-synced;
- dialogue-led;
- montage;
- custom.

Pacing influences shot duration and motion intensity, not only generation prompt wording.

## Transition language

Supported editorial intents:
- hard cut;
- match cut;
- action cut;
- reaction cut;
- insert cut;
- J-cut/L-cut audio transition;
- dissolve;
- fade;
- wipe only when stylistically justified;
- motion match;
- object match;
- color match;
- beat cut;
- generative bridge;
- scene reset/establishing transition.

## Text/graphics policy

Specify:
- no text generated inside AI imagery by default unless needed;
- captions/titles preferably rendered deterministically in post;
- logo/brand usage must use canonical assets;
- AI-created gibberish/watermarks/logos are QA failures.

## Visual reference strategy

Preferred reference hierarchy:
1. canonical character/look reference;
2. canonical world/location reference;
3. canonical style reference;
4. first/end keyframe;
5. adjacent approved frame when appropriate;
6. provider-specific derived reference representation.

Do not rely on text-only generation for strict identity continuity if reference-capable routes exist within policy.

## Cinematic scene coverage

When dialogue/narrative requires editorial flexibility, plan coverage such as:
- establishing;
- master/two-shot;
- character A coverage;
- character B coverage;
- reaction;
- insert/detail;
- cutaway/B-roll;
- transition/exit.

Not every scene needs all coverage. AI Director chooses based on narrative/editorial value and budget.

## Audience-aware visual behavior

Child-directed projects may constrain:
- intensity;
- threat/scare level;
- visual clutter;
- flashing/rapid cuts;
- malformed/disturbing imagery tolerance;
- readable action;
- emotional safety.

General/adult projects can support broader cinematic intensity but remain subject to universal platform/safety rules.

## Visual QA

Critical checks:
- canonical identity;
- apparent age/species;
- anatomy/object integrity;
- wardrobe/look;
- important props;
- environment/world;
- unwanted text/logos/watermarks;
- safety/rights.

Continuity checks:
- screen direction;
- camera position;
- lighting;
- palette;
- movement direction;
- start/end frame compatibility;
- object/character location;
- scene state.

Aesthetic checks:
- composition;
- focus;
- motion quality;
- style match;
- cinematic readability;
- artifact severity.

## Acceptance criteria

The visual system is development-ready when a shot can be fully described using canonical entities/style/camera/action/state, translated to different providers, and evaluated without treating any provider's internal state as the project memory.