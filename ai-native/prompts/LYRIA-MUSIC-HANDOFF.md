# Lyria Music Handoff Prompt

Use this template for `audio_mode: music` and for instrumental background beds used by `audio_mode: speech_with_bed`.

The AI agent is the music director. The operator should not need to manually choose genre, instruments, BPM, key, energy curve, or production density for every content item.

## Provider assumptions

- Verify current Lyria model availability, tier and terms before execution.
- Full-track preference: `lyria-3-pro-preview` when available and allowed by the selected cost policy.
- Short test/previews: `lyria-3-clip-preview` when useful.
- Use exact approved lyrics for songs.
- For narration beds, explicitly request instrumental output with no lead vocal unless the content plan intentionally requires a non-lyrical vocal texture.
- Never ask Lyria to replace approved lyrics in a production render.

## Mandatory autonomous planning pass

Before writing the final provider prompt, analyze:
- content type;
- target age;
- learning/emotional objective;
- approved lyrics or narration arc;
- scene/section structure;
- duration;
- language and pronunciation;
- desired listener state;
- child-safety constraints;
- visual/editing needs when known.

Then autonomously choose and persist:
- genre / production family;
- BPM or tempo band;
- key/scale when useful;
- instrumentation level of specificity;
- primary instruments when narratively important;
- expected genre-default instrumentation when explicit listing adds no value;
- percussion style/density;
- bass profile;
- harmonic texture;
- female vocal profile for songs;
- section structure;
- energy curve;
- repetition/call-response behavior;
- mix priorities;
- ending behavior;
- prohibited sounds.

Do not leave unresolved placeholders in the final provider prompt. If a parameter is intentionally left to model discretion, state that explicitly, for example: `Use tasteful genre-appropriate supporting instrumentation at model discretion; keep the lead vocal dominant.`

## Prompt compiler — full song

Create a complete original children's song for the following approved content.

### CONTENT IDENTITY

Content ID: {{content_id}}
Target age: {{age_band}}
Language: {{language}}
Target duration: {{target_duration}}
Purpose: {{objective}}
Listener outcome: {{listener_outcome}}

### AUTONOMOUS MUSICAL DIRECTION

Genre / production family: {{resolved_genre}}
Tempo: {{resolved_bpm_or_tempo}}
Key / scale: {{resolved_key_or_scale_or_model_discretion}}
Mood: {{resolved_mood}}
Energy: {{resolved_energy}}
Production density: {{resolved_production_density}}

Instrumentation decision:
{{resolved_instrumentation_direction}}

The arrangement must support the educational/emotional goal rather than merely sounding fashionable. Use original musical material. Do not imitate, quote, interpolate, or intentionally evoke a copyrighted children's melody, contemporary song, identifiable artist, film/TV theme, branded character song, or famous recording.

### FEMALE SINGER PROFILE

{{resolved_female_singer_profile}}

Default constraints:
- adult female lead;
- warm, friendly, clean tone;
- clear child-friendly diction;
- comfortable non-strained range;
- emotionally appropriate to the content;
- never seductive, aggressive, harsh, frightening or overly mature;
- no imitation of any known singer, actor, creator, celebrity, or character.

Vocal priority:
1. lyric intelligibility;
2. age-appropriate warmth;
3. musicality;
4. expressiveness;
5. ornamentation only when clarity remains intact.

### SONG STRUCTURE

{{resolved_structure_map}}

Energy map:
{{resolved_section_energy_map}}

Use clear section labels where useful. Respect timing needs for later video editing.

### EXACT APPROVED LYRICS

Lyrics:

{{exact_lyrics}}

Treat these lyrics as canonical. Do not introduce unrelated verses, factual changes, brand references, adult-coded ad-libs, or unsafe wording.

### REPETITION / PARTICIPATION

{{resolved_repetition_notes}}

### PRONUNCIATION

{{pronunciation_notes}}

Prioritize correct pronunciation over vocal flourishes.

### MIX / MASTER INTENT

{{resolved_mix_plan}}

Always keep the lead lyric intelligible, avoid clipped peaks and harsh frequency build-up, and provide a clean ending suitable for editing.

### DO NOT DO

- no copyrighted melody imitation;
- no artist or celebrity imitation;
- no protected character voice;
- no unsafe lyric changes;
- no scary, violent, sexualized or adult-coded styling;
- no product insertion;
- no random unapproved spoken ad-libs;
- no abrupt/startling sound design for younger age bands.

## Prompt compiler — instrumental narration bed

Create an original instrumental background score for a children's narrated piece.

Content ID: {{content_id}}
Target age: {{age_band}}
Target duration: {{target_duration}}
Story / narration objective: {{objective}}
Emotional arc: {{resolved_emotional_arc}}

Musical direction:
- genre/texture: {{resolved_genre_or_texture}}
- tempo: {{resolved_bpm_or_tempo}}
- key/scale: {{resolved_key_or_scale_or_model_discretion}}
- instrumentation: {{resolved_instrumentation_direction}}
- density: {{resolved_production_density}}

Timeline / section cues:
{{resolved_music_bed_timeline}}

Critical constraints:
- instrumental by default; no lead lyrics;
- remain underneath a female narrator;
- do not compete with speech frequencies;
- thin the arrangement during important explanatory/emotional lines;
- no sudden transients, jump scares or aggressive bass for young listeners;
- use smooth transitions;
- create a clean intro and ending for deterministic mixing;
- use original music only;
- do not imitate identifiable artists, songs, film scores or children's franchises.

If ordinary genre instrumentation is sufficient, use tasteful genre-appropriate supporting instruments at model discretion. Explicitly include any instrument or musical event that is narratively important.

## Package metadata

Save beside every music prompt:
- provider family;
- preferred model;
- prompt version;
- content ID;
- run ID;
- target duration;
- exact-lyrics fingerprint when applicable;
- female vocal required;
- instrumental-only boolean;
- resolved genre/BPM/key;
- resolved instrumentation policy;
- quota/tier class;
- license class;
- output filename placeholder;
- render status.

## Music QA after rendering

Check:
- lyric fidelity when applicable;
- pronunciation;
- intelligibility;
- no unsafe/unapproved ad-libs;
- originality risk;
- vocal identity risk;
- age fit;
- arrangement fit;
- loudness/clipping;
- section coherence;
- duration;
- narration compatibility for music beds;
- file integrity.

A successful provider response is not production approval.
