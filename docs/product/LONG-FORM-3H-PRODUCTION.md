# Long-Form Production Specification — Up to 3 Hours

## Purpose

Define how the platform plans, generates, validates, assembles and recovers long-form projects up to the current configured maximum of 10,800 seconds / 3 hours.

Three-hour support means orchestration/timeline/storage/context capability. It does not mean one AI model generates a continuous three-hour file in one call.

## Hierarchical production model

Use:
`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take`

Recommended long-form checkpoints:
- Project canon;
- Act summary/state;
- Sequence summary/state;
- Scene continuity state;
- Shot state.

## Context strategy

Never send the full multi-hour project history into every AI call.

Each scoped AI job receives only relevant context:
- global project premise/style/audience;
- locked character/world canon;
- current Act/Sequence objective;
- current Scene script and continuity;
- adjacent Scene/Shot state;
- material historical changes referenced by current action.

## Canon summaries

Persist structured summaries at boundaries:

### Project canon
- premise/logline;
- audience/format;
- visual/audio style;
- global character/world definitions;
- immutable rules;
- final objective.

### Act/Chapter state
- goals;
- character state changes;
- unresolved plot threads;
- key locations/props;
- emotional trajectory;
- timeline bounds.

### Sequence state
- immediate objective;
- start/end state;
- important events;
- characters/location/props;
- continuity handoff.

### Scene state
- precise blocking/state;
- dialogue/action;
- incoming/outgoing continuity;
- selected shots/takes.

## Planning passes

Long-form should be planned progressively:
1. premise/logline;
2. synopsis;
3. Act/chapter structure;
4. sequence beats;
5. scene list;
6. scene scripts;
7. scene storyboard;
8. shot plans;
9. generation.

Avoid generating thousands of shot prompts before the script/scene architecture is stable.

## Duration budgeting

Allocate target duration hierarchically:
- Project total;
- Act totals;
- Sequence totals;
- Scene totals;
- Shot editorial durations.

Validation should catch major drift before rendering.

## Incremental production

Generate by bounded production unit, typically Scene or Sequence.

Example:
`Plan Scene -> keyframes -> shots -> QA -> assemble scene -> scene QA -> checkpoint -> next scene`

This reduces recovery cost compared with waiting for an entire movie to finish before validation.

## Incremental rendering

Maintain:
- shot masters;
- scene masters/proxies;
- sequence previews;
- project timeline.

Changing one Shot should invalidate only affected Scene/transition/render regions where possible.

Do not re-render unrelated completed hours unnecessarily.

## Workflow history

Durable orchestrator may need history compaction/continue-as-new or equivalent strategy for thousands of long-running activities. Exact Temporal implementation belongs to development, but planning requires bounded workflow history and persisted domain state outside transient worker memory.

## Shot count scaling

Do not hard-code one shot every provider max duration.

Shot count derives from creative pacing.

A 90-minute movie might contain hundreds to more than a thousand shots depending on treatment; a calm story may have far fewer. UI/backend queries must paginate/virtualize accordingly.

## Provider routing at scale

Route per Shot or logical generation unit.

Long-form router additionally considers:
- provider rate/concurrency limits;
- budget remaining by Act/Scene;
- accepted-output rate;
- batch opportunity;
- quota reset;
- consistency drift over project;
- provider changes over long production time.

Provider registry facts may need refresh during a project that takes days/weeks.

## Cost forecasting

Before production estimate at multiple levels:
- Shot expected cost;
- Scene budget;
- Act budget;
- Project expected range;
- retry reserve.

Update forecasts using actual accepted-output history.

Large project should not consume whole budget early because opening scenes happened to retry heavily without raising a budget signal.

## Character continuity over long duration

Never depend on the first generated shot remaining in context.

Use canonical character versions/looks plus state changes.

If a character intentionally changes wardrobe/age/injury/state:
- create explicit Look/state version;
- define start/end story range;
- prevent accidental use outside that range.

## World continuity

Track evolving state:
- location condition;
- time/day progression;
- weather;
- objects moved/destroyed;
- plot-relevant environmental changes.

Persist state updates at Scene/Sequence boundaries.

## Audio long-form strategy

Maintain separate tracks/stems for:
- dialogue;
- narration;
- score;
- ambience;
- SFX;
- songs.

Use scene/sequence cues and deterministic final mix. Do not regenerate whole-film audio for one dialogue fix.

## QA strategy

Use layered QA:
- Take QA;
- adjacent Shot continuity;
- Scene QA;
- Sequence continuity summary;
- Act narrative/continuity QA;
- final project QA.

This catches local defects early while still reviewing global coherence.

## Recovery

Persist enough state so recovery can identify:
- last completed unit;
- in-flight provider job;
- approved/rejected assets;
- remaining budget;
- locks;
- current canon summaries;
- next eligible unit.

Crash/provider outage must not restart completed Scenes/Shots.

## Archival/export

Long-form project should support an audit/export manifest containing:
- project/version;
- canon references;
- timeline/OTIO;
- final asset references/hashes;
- rights/provenance summary;
- provider/cost summary;
- publication records.

## Scaling acceptance ladder

Do not call 3-hour support production-ready after a 2-minute demo.

Validate progressively:
- 2 minutes;
- 5–10 minutes;
- 30 minutes;
- 60 minutes;
- 90 minutes;
- 120 minutes;
- 180 minutes.

At each stage test:
- workflow recovery;
- query performance;
- storage;
- cost controls;
- context scoping;
- render invalidation;
- continuity;
- UI virtualization where available.

## Acceptance criteria

Long-form architecture is development-ready when a 3-hour Project can be represented, scoped, resumed, budgeted and incrementally rendered without any subsystem requiring the whole film to fit in one prompt, one provider job, one database row or one monolithic render operation.