# New Project Wizard Specification

## Purpose

The New Project Wizard converts creative intent into a complete provider-neutral project configuration without forcing the operator to understand individual AI provider limitations.

The wizard must support both quick creation and advanced production control. Every option can either be explicitly selected by the operator or delegated to AI where allowed.

## Modes

### Quick / AI Assisted
Operator supplies minimum intent; AI fills the remaining fields and explains materially important decisions.

Minimum inputs:
- project title or working title;
- audience or `AI Decide`;
- content format or `AI Decide`;
- duration or duration range;
- language;
- character strategy.

### Guided
Wizard presents all major production decisions with recommended defaults.

### Advanced
Expose all project, cast, visual, audio, timeline, provider, cost and review settings.

## Wizard sequence

### Step 1 — Project Intent
Fields:
- title / working title;
- optional creative brief;
- objective: entertainment / education / emotional / promotional / narrative / custom;
- language;
- optional target platform(s);
- optional reference/seed assets;
- AI autonomy level.

AI may suggest title, objective and project structure, but must preserve explicit operator intent.

### Step 2 — Audience
Choose:
- Baby
- Toddler
- Preschool
- Child
- Preteen
- Teen
- Family
- General
- Adult
- Custom
- AI Decide

Child-directed selection activates the relevant age/safety policy profile. `General` and `Adult` do not disable universal safety/rights rules.

Optional:
- exact age range;
- family co-viewing;
- learning level;
- content sensitivity profile.

### Step 3 — Cast / Generation Profile
Separate dimensions:
- cast age: baby / child / teen / adult / senior / mixed / non-human;
- gender presentation: male / female / mixed / unspecified / non-human;
- target human count;
- target non-human count;
- ensemble vs protagonist-led;
- narrator-only / on-screen cast / both;
- AI Decide toggle.

UI may provide convenience presets: `Kids`, `Adults`, `Men`, `Women`, `Mixed`, but backend must store separate dimensions.

### Step 4 — Content Format
Select registered content format:
- song;
- lullaby;
- poem;
- rhyme;
- story;
- bedtime story;
- educational video;
- guided imagination;
- explainer;
- music video;
- dialogue scene;
- short film;
- episode;
- series episode;
- cinematic sequence;
- movie;
- documentary;
- compilation;
- trailer/teaser;
- short/social;
- custom;
- AI Decide.

Format-specific options appear conditionally; see `CONTENT-TYPE-BIBLE.md`.

### Step 5 — Duration
Current product target:
- minimum 60 seconds;
- maximum 10,800 seconds / 3 hours.

Input modes:
- exact duration;
- range;
- preset;
- `AI Decide within range`.

Suggested presets:
- 1 minute;
- 2 minutes;
- 3 minutes;
- 5 minutes;
- 10 minutes;
- 15 minutes;
- 30 minutes;
- 60 minutes;
- 90 minutes;
- 120 minutes;
- 180 minutes.

Duration may influence format recommendations, pacing, act structure, cost estimate, shot count and provider routing, but provider clip limits must never silently change the creative target duration.

### Step 6 — Character Strategy
Choose:
- Existing Locked Character(s);
- Create New + Lock;
- Existing + New;
- One-off Characters;
- No Recurring Character;
- AI Decide.

When using existing characters, show:
- canonical character;
- active version;
- available looks;
- lock state;
- rights state;
- prior project usage.

When creating new characters, the character creation flow occurs before final project activation so recurring identity can be locked before production.

### Step 7 — World / Location / Props
Choose existing or create new:
- world/universe;
- main locations;
- recurring props;
- time period;
- season/weather;
- world rules;
- AI Decide.

For short simple content this step may remain lightweight; for episodic/movie projects it becomes important canonical continuity state.

### Step 8 — Visual Direction
Select or delegate:
- visual medium/style;
- genre treatment;
- realism level;
- palette;
- lighting profile;
- composition profile;
- camera/lens profile;
- motion profile;
- pacing;
- transition profile;
- text/graphics policy;
- reference images/styles.

See `VISUAL-CINEMATIC-BIBLE.md`.

### Step 9 — Audio Direction
Select or delegate:
- narration required;
- singer required;
- dialogue required;
- preferred voice gender/presentation;
- recurring voice assignments;
- music required;
- background music behavior;
- SFX/ambience;
- language/accent/pronunciation;
- lip-sync requirement;
- stems requirement;
- AI Music Director toggle.

See `AUDIO-PRODUCTION-BIBLE.md`.

### Step 10 — Timeline / Editing
Options:
- pacing profile;
- average shot length target;
- beat-sync for music;
- dialogue-led timing;
- cinematic dynamic pacing;
- montage allowance;
- transition preference;
- B-roll allowance;
- scene handles/overlap;
- strict continuity level;
- desired coverage level;
- AI Director autonomy.

### Step 11 — Output
Options:
- aspect ratio;
- resolution target;
- FPS;
- master container;
- subtitles/captions;
- vertical derivative;
- thumbnail/poster-frame requirement;
- audio-only derivative;
- clean/with-text variants where needed.

### Step 12 — Provider & Budget Policy
Choose:
- FREE_ONLY;
- FREE_FIRST;
- HYBRID_SMART;
- BUDGET_CAPPED;
- QUALITY_FIRST.

Optional:
- project budget cap;
- per-shot cap;
- daily/monthly cap references;
- preferred providers;
- blocked providers;
- allow manual-free handoff;
- latency preference;
- privacy/data-use restrictions.

The operator should not be required to choose individual providers per shot unless desired.

### Step 13 — Review / Approval Policy
Choose review level:
- AI-first with human final master approval;
- human approval after script/audio/storyboard;
- human approval after every scene;
- human approval after every generated take;
- custom checkpoints.

Locked identity, unresolved rights, public publishing and unconfigured paid spend retain hard approval gates regardless of convenience settings.

### Step 14 — Summary & Preflight
Before project creation display:
- audience;
- cast;
- format;
- duration;
- selected/created characters;
- visual/audio direction;
- estimated structural complexity;
- estimated shot range;
- estimated provider/cost policy;
- safety/rights gates;
- AI-autonomous decisions;
- operator overrides;
- likely production stages.

AI should flag contradictions before creation, e.g. a 180-minute project with `single simple rhyme` or strict character continuity with `text-only generation`.

## AI Decide behavior

`AI Decide` is permission to select a value, not permission to ignore constraints.

The AI must:
1. inspect explicit project intent;
2. inspect relevant audience/policy;
3. inspect repository memory and available canonical assets;
4. choose a production-appropriate value;
5. store the resolved value, not only `AI Decide`;
6. record the reason where materially important;
7. never override a locked operator selection without approval.

## Validation rules

Project creation must reject or block:
- duration outside configured range;
- custom content type without a custom name/definition;
- character reuse without resolvable canonical character/version;
- child-directed content without applicable policy profile;
- provider policy that authorizes spend without configured budget authorization;
- public publishing as an implicit project-creation side effect;
- unresolved required consent/license for imported real-person/voice assets.

## Save states

Wizard supports:
- Draft;
- Preflight Failed;
- Ready for Planning;
- Cancelled/Archived.

Creating a project does not automatically spend provider credits.

## Acceptance criteria

The wizard specification is implementation-ready when a future UI/API can reproduce the same canonical project record regardless of Quick, Guided or Advanced mode, and AI-autonomous choices are explicitly resolved and auditable.
