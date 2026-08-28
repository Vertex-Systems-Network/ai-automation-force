# Timeline, Sequence and Rhythm Engine

## Goal

Support smooth productions from approximately one minute to three hours without relying on a single generative call or a fragile chain of extensions.

The canonical timeline is provider-independent and editable like a simplified non-linear editor.

## 1. Hierarchy

Long-form project structure:

`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take -> Frame/Audio segment`

Short projects may omit Act/Chapter and begin at Scene/Shot while using the same schema.

### Project
Global story, duration, audience, cast, style, language, format, budget, output settings.

### Act/Chapter
Large narrative or program segment. Useful for movies, compilations and long educational programs.

### Sequence
A related set of scenes pursuing one dramatic/musical/instructional objective.

### Scene
Continuous place/time/story unit.

### Shot
Smallest canonical visual generation unit.

### Take
One provider generation attempt for a shot. Many takes may exist; only one becomes canonical.

## 2. Timeline tracks

Support parallel tracks:
- primary video
- B-roll/overlay video
- narration
- dialogue by character
- lead vocal
- background vocals
- music
- ambience
- SFX
- captions/subtitles
- titles/graphics
- markers
- beat grid
- emotion curve
- continuity state

Generative providers produce assets; the timeline owns timing.

## 3. Master timing source

Choose one:
- audio-led: songs, narration, podcasts, poems
- script/dialogue-led
- picture-led
- music/beat-led
- mixed

Songs should usually lock approved master audio before final shot timing. Dialogue films may lock dialogue blocks first and refine picture timing around performance.

## 4. Rhythm model

Store a pacing profile plus a time-varying curve.

Signals:
- average shot duration
- min/max shot duration
- words per minute
- dialogue density
- BPM and musical beat/bar grid
- motion intensity
- visual novelty rate
- emotional intensity
- transition density
- silence/rest density
- camera movement density

The system should prevent monotonous equal-length AI clips. Provider maximum clip duration is an implementation constraint, not the artistic rhythm.

## 5. Beat-aware segmentation

For music:
- detect/know BPM
- store beats/bars
- preserve verse/chorus/bridge boundaries
- align important cuts/motions to musically meaningful positions when appropriate
- allow deliberate off-beat cuts for creative reasons
- avoid cutting every beat mechanically

For narration/story:
- use sentences, clauses, pauses and story beats
- keep action readable before cutting
- allow reaction shots and breathing space

## 6. Smooth sequence rules

Adjacent shots maintain explicit continuity:
- character ID/version
- wardrobe/look
- pose/action end state
- prop state
- environment
- time of day
- lighting direction
- screen direction
- camera side / 180-degree logic where applicable
- motion vector
- gaze
- weather/particles
- audio ambience

Every shot stores `incoming_state` and `outgoing_state`. The next shot either inherits the outgoing state or declares an intentional transition.

## 7. Keyframe strategy

Use canonical keyframes before expensive video generation when continuity matters.

Per shot:
- first frame/reference
- optional midpoint control/reference
- optional target/end frame
- canonical character refs
- location/world refs
- prop refs
- composition sketch/reference when useful

Provider adapters decide how many references can be supplied while the canonical plan remains unchanged.

## 8. Shot generation strategies

Router options:
1. provider-native extension for true same-shot continuation
2. first + last frame controlled generation
3. first-frame image-to-video
4. reference images + image/video generation
5. reference-video/video-to-video
6. text-to-video only for continuity-insensitive material

A 3-hour project may contain thousands of shots. Completed shots are immutable checkpoints unless intentionally revised.

## 9. Transition planner

Select transitions based on narrative function, not random decoration.

Types:
- cut
- match cut
- action match
- audio J/L cut
- dissolve
- fade
- motion match
- shape/object match
- generative bridge
- location establishing bridge
- montage transition

Transition plans specify required overlap/head/tail handles so editing can choose the cleanest cut point.

## 10. Handles and overlap

Generated shots should optionally include head/tail handles beyond the final cut duration.

Example:
- requested final shot: 5.0 sec
- generated usable source: 6–8 sec when provider allows
- editor chooses a stable in/out point

For cross-provider continuity, generate a small logical overlap around the handoff and cut on the best matching frame.

## 11. Continuity QA

Before a take becomes canonical compare with:
- character references
- scene state
- planned first/end frames
- previous canonical shot
- next planned keyframe when available

Score identity, wardrobe, environment, props, style, camera, action, temporal transition, anatomy/object integrity, unwanted text/logos and safety.

Critical continuity failures reject the take.

## 12. Long-form memory windows

Do not send a 3-hour script into every generation call.

Build scoped context:
- project bible
- current act/sequence summary
- current scene state
- adjacent shot states
- relevant character/location/prop records
- exact current audio/script segment

This reduces prompt drift, token cost and accidental contradictions.

## 13. Story continuity memory

Maintain structured facts:
- plot events completed
- unresolved goals
- character knowledge
- relationship state
- inventory/props
- location/time
- injuries/changes if appropriate to content policy
- promises/setups/payoffs
- recurring visual motifs

A long movie must not rely on a language model remembering all previous prose implicitly.

## 14. Deterministic assembly

Use FFmpeg/media tooling for:
- trimming
- concatenation
- overlays
- audio mixing
- fades/transitions
- subtitles
- loudness normalization
- resizing/cropping
- final encodes

The canonical edit decision list/render manifest should make a final master reproducible from approved assets.

## 15. Revision model

Edits are non-destructive:
- revise one shot
- revise one scene
- replace music
- change subtitle language
- switch provider
- re-render output format

Do not invalidate unrelated approved shots.

## 16. UI target

Future UI should provide:
- storyboard view
- timeline view
- scene/shot inspector
- character/location sidebar
- audio waveform
- beat markers
- provider/take history
- QA badges
- cost per shot/scene/project
- lock indicators
- compare takes
- regenerate selected shot only
- ripple timing with explicit confirmation
- version history

## 17. Three-hour scalability rule

The system supports up to 10,800 seconds as a project target by orchestration and hierarchical timeline management. No requirement implies a single model must generate a three-hour continuous file. Provider limits are hidden behind shot jobs, checkpoints and deterministic assembly.