# Audio Production Router

## Purpose

Do not send every content type to the same audio model. Route approved content to the audio system that matches the intended final artifact.

The operator's requirement is Google/Gemini-family audio production with a female voice as the default. The routing layer preserves that intent while distinguishing speech synthesis from full music generation.

## Route A — Speech / narration

Use for:
- story
- bedtime-story
- poem when spoken
- rhyme when spoken
- educational-narration
- guided-imagination
- spoken lullaby

Preferred provider family: Gemini TTS.

Current preferred model at foundation time:
- `gemini-3.1-flash-tts-preview`

Fallbacks:
- `gemini-2.5-pro-preview-tts`
- `gemini-2.5-flash-preview-tts`

Before API automation, verify currently supported model IDs in official Google documentation because preview model names can change.

### Prompt structure

Build every narration prompt with:
1. Audio Profile — voice identity/archetype without impersonation;
2. Scene — listener context and emotional environment;
3. Director's Notes — tone, pace, accent, articulation, energy, pauses, emotional progression;
4. Exact Script — frozen approved text;
5. Pronunciation Notes;
6. Prohibitions — no ad-libbing that changes meaning, no celebrity imitation, no inappropriate dramatic effects.

Default voice direction:
- female-presenting adult narrator;
- warm and natural;
- reassuring rather than exaggerated;
- clear articulation;
- emotionally expressive but not theatrical enough to distract from comprehension;
- age-band-specific pace.

Voice selection in API configuration must use an available prebuilt voice auditioned as female-presenting and appropriate for the project. Do not infer that a named voice is female unless verified/auditioned.

## Route B — Full musical audio

Use for:
- song
- sung lullaby
- musical rhyme
- musical learning track

Preferred provider family: Lyria through the Gemini API.

Current preferred full-track model at foundation time:
- `lyria-3-pro-preview`

Preview/short concept model:
- `lyria-3-clip-preview`

Before API automation, verify current model IDs and availability.

### Music prompt structure

Every full music prompt should specify:
- exact approved lyrics;
- target child age band;
- genre/style described generically, not as imitation of a living/identifiable artist;
- female singer profile;
- vocal timbre/range appropriate to children;
- BPM or tempo band;
- key/scale when musically useful;
- instrumentation;
- mood;
- production density;
- intro/verse/chorus/bridge/outro structure;
- duration target;
- section energy map;
- repetition/call-and-response instructions;
- pronunciation;
- no unsafe or startling sound design for young audiences;
- no copyrighted melody imitation;
- no celebrity voice/style imitation.

Default singer direction for children's songs:
- adult female voice;
- warm, friendly, clean timbre;
- clear consonants and vowels;
- comfortable non-strained range;
- cheerful energy when appropriate;
- avoid seductive, breathy, aggressive, raspy, or overly mature styling;
- no imitation of a known singer.

For lullabies:
- soft female vocal;
- low dynamic range;
- gentle tempo;
- sparse instrumentation;
- smooth transitions;
- no abrupt percussion/transients;
- avoid overstimulation.

## Route C — Rhythmic spoken chant

A rhyme or learning piece may be better as a rhythmic spoken performance without a full musical arrangement.

Default route: Gemini TTS with explicit rhythmic cadence instructions.

If instrumental backing is later required, render the speech and music separately or route to Lyria only when a full musical output is intended.

## Routing decision field

Every content package must include:

- `audio_mode`: `speech` | `music` | `chant`
- `audio_provider_family`: `gemini-tts` | `lyria`
- `preferred_model`
- `female_voice_required`: true by default
- `final_audio_prompt_path`

## Capability honesty

Never claim that TTS produced a full song arrangement. Never claim that a music model guarantees exact vocal identity or exact melody. Record actual provider/model used when audio is rendered.

Provider capability can change; the router is stable, provider configuration is versioned.
