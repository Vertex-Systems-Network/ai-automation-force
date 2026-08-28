# Audio Production Bible

## Purpose

Define provider-neutral audio production behavior for narration, dialogue, songs, background music, ambience, SFX and final mixing. The operator should be able to specify high-level intent while the AI Audio Director resolves production details within policy.

## Audio modes

Supported primary modes:
- narration;
- dialogue;
- song/full music;
- chant/rhythmic speech;
- narration + background music;
- dialogue + score;
- ambience-only;
- SFX/Foley;
- instrumental music;
- mixed production.

## Canonical audio plan

Every audio-bearing project may define:
- master language;
- speaker/character voice assignments;
- singer assignments;
- narration strategy;
- dialogue strategy;
- music strategy;
- ambience strategy;
- SFX strategy;
- pronunciation dictionary;
- timing/beat map;
- stems required;
- target loudness/output format;
- lip-sync requirement;
- localization/dubbing intent.

Provider-specific model IDs are derived routing decisions, not canonical audio identity.

## Narration

Options:
- single narrator;
- alternating narrators;
- character narration;
- documentary/neutral;
- bedtime/gentle;
- energetic/educational;
- cinematic/dramatic;
- custom.

Voice attributes:
- gender presentation;
- age presentation;
- timbre;
- warmth/brightness;
- pace;
- diction;
- accent/language variant;
- emotional range;
- breathiness/energy;
- prohibited styles.

Default for legacy kids workflow may remain adult female-presenting, warm/natural, unless project profile overrides it.

## Dialogue

Dialogue requires:
- character ID;
- character version;
- voice profile ID;
- text;
- speaker turn;
- start/end timing where available;
- emotion;
- intensity;
- pace;
- interruption/overlap rules;
- pronunciation notes;
- lip-sync marker requirement.

Recurring character voices must remain version-pinned. A provider-specific voice ID may change while the canonical VoiceProfile remains constant.

## Song / Full Music

AI Music Director resolves where operator has not explicitly locked values:
- genre;
- subgenre;
- BPM/tempo;
- time feel/time signature where relevant;
- key/scale where useful;
- instrumentation;
- singer profile;
- backing vocals;
- energy curve;
- song structure;
- intro/outro behavior;
- instrumental breaks;
- dynamics;
- children-participation/call-response where appropriate;
- mix intent.

Exact approved lyrics are canonical. Provider should not silently rewrite lyrics.

## Instrumental Background Music

Background score/music bed must be planned independently from narration/dialogue so it can be regenerated or remixed without replacing voice.

Music-bed plan:
- emotional purpose;
- intensity curve;
- instrumentation;
- tempo or free-time;
- entry/exit points;
- loopability if needed;
- dialogue-safe frequency/arrangement notes;
- transition/sting points;
- ducking expectations.

## Chant / Rhythmic Speech

Used for:
- rhymes;
- educational repetition;
- actions/movement;
- call-and-response;
- spoken rhythmic content.

Specify:
- cadence;
- beat emphasis;
- tempo target;
- repetition map;
- pauses;
- group/solo voice behavior.

## Ambience

Examples:
- bedroom night;
- forest;
- city;
- school;
- ocean;
- spaceship;
- room tone;
- crowd;
- weather.

Ambience should maintain scene continuity and be stored as separate track/stem when practical.

## SFX / Foley

Each effect should have:
- event ID;
- scene/shot reference;
- semantic label;
- start time;
- duration;
- intensity;
- spatial intent;
- source/generation provenance.

Examples: footsteps, door, sparkle, vehicle, object impact, animal sound, magical cue.

Avoid using sound effects that are needlessly startling for young-child profiles.

## Music and narrative timing

Master audio may become the editorial clock where appropriate.

For songs:
- BPM;
- beat grid;
- bars;
- sections;
- lyric phrase timing;
- key musical events.

For narration:
- sentence boundaries;
- semantic pauses;
- scene-change pauses;
- emphasis markers.

For dialogue:
- speaker turns;
- interruptions;
- reactions;
- silence;
- room tone.

## Stems

Preferred canonical stems when applicable:
- narration;
- dialogue by character or dialogue bus;
- lead vocal;
- backing vocals;
- music/instrumental;
- ambience;
- SFX;
- optional percussion/score sub-stems when provider supports them.

If a provider only returns a mixed master, record that limitation in provenance.

## Mixing rules

Deterministic post-production should handle:
- trim/alignment;
- voice/music ducking;
- fades;
- crossfades;
- bus gain;
- loudness normalization;
- peak limiting;
- channel/layout conversion;
- final encoding.

Generative AI should not be used to recreate a mix when deterministic mixing can preserve approved stems.

## Audio QA

### Speech/narration
Check:
- exact script fidelity;
- missing/extra words;
- pronunciation;
- pacing;
- unnatural pauses;
- clipping/distortion;
- wrong voice assignment;
- audience/style fit.

### Song
Check:
- lyric fidelity;
- section order;
- intelligibility;
- singer profile;
- musical coherence;
- unwanted imitation/rights risk;
- clipping;
- duration fit;
- inappropriate emotional/tonal behavior for audience.

### Dialogue
Check:
- correct speaker;
- timing;
- voice identity;
- emotion;
- cross-talk errors;
- lip-sync timing metadata;
- pronunciation.

### Final mix
Check:
- speech intelligibility;
- music not masking dialogue;
- no clipping;
- consistent loudness;
- no missing stem/event;
- scene transitions;
- final duration alignment.

## Regeneration strategy

Do not regenerate entire master for a localized defect when separable stems exist.

Examples:
- one pronunciation error -> regenerate affected utterance;
- one SFX missing -> generate/add SFX only;
- music too loud -> remix, do not regenerate voice;
- bad chorus -> regenerate/version music track or section where provider capability permits;
- wrong character voice -> regenerate only affected dialogue lines/scene.

## Voice/identity rights

Do not imitate a real identifiable person without applicable authorization. Imported voice samples require rights/consent provenance where material. Provider commercial-use terms are independent from identity consent.

## Localization

Each localized audio version should preserve:
- semantic meaning;
- character identity;
- emotional intent;
- timing intent;
- song meter/rhyme where applicable;
- pronunciation dictionary;
- source-version lineage.

Literal translation is not sufficient for lyrics when it breaks meter/rhyme/naturalness.

## Acceptance criteria

Audio planning is development-ready when every spoken/music/dialogue asset can be traced from canonical text/intent through voice/music direction, provider attempt, QA result, approved stem/master and deterministic final mix without relying on provider chat history.