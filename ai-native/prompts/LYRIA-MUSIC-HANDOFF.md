# Lyria Music Handoff Prompt

Use this template for `audio_mode: music`, especially songs and sung lullabies.

The final generated prompt should be detailed enough to paste into Google's current Lyria interface/API after the operator supplies credentials.

## Provider assumptions

- Verify current Lyria model availability before execution.
- Foundation preference for full tracks: `lyria-3-pro-preview`.
- Foundation preference for 30-second tests/previews: `lyria-3-clip-preview`.
- Use the exact approved lyrics from the content package.
- Do not ask Lyria to write replacement lyrics unless explicitly running a separate experimental draft outside the approved catalogue.

## Prompt compiler template

Create a complete original children's music track for the following approved content.

### CONTENT IDENTITY

Content ID: {{content_id}}
Target age: {{age_band}}
Language: {{language}}
Target duration: {{target_duration}}
Purpose: {{objective}}
Listener mood/outcome: {{listener_outcome}}

### MUSICAL IDENTITY

Genre / production family: {{genre}}
Tempo: {{bpm_or_tempo}}
Key / scale: {{key_or_scale}}
Mood: {{mood}}
Energy level: {{energy}}
Production density: {{production_density}}

Use original musical material. Do not imitate, quote, interpolate, or intentionally evoke a copyrighted children's melody, contemporary song, identifiable artist, film/TV theme, branded character song, or famous recording/arrangement.

### FEMALE SINGER PROFILE

Use an adult female lead singer with:
- warm, friendly, clean tone;
- clear child-friendly diction;
- comfortable, non-strained range;
- natural smile/brightness when the song is playful;
- gentle low-dynamic delivery when the song is a lullaby;
- emotionally expressive but never seductive, aggressive, harsh, frightening, or overly mature;
- no imitation of any known singer, actor, creator, celebrity, or existing children's character.

Vocal priority order:
1. lyric intelligibility;
2. age-appropriate warmth;
3. musicality;
4. expressiveness;
5. ornamentation only when it does not reduce clarity.

### INSTRUMENTATION

Primary instruments: {{primary_instruments}}
Secondary texture: {{secondary_instruments}}
Percussion: {{percussion}}
Bass: {{bass}}
Additional production notes: {{production_notes}}

For preschool/toddler content:
- keep arrangement uncluttered;
- avoid aggressive sub-bass, harsh distortion, startling transients, or chaotic sound effects;
- preserve vocal clarity above the instrumentation.

For lullabies:
- sparse and soft arrangement;
- gentle piano, acoustic textures, pads, bells, strings, or other age-appropriate sounds as specified;
- smooth dynamics;
- no sudden drum hits or abrupt transitions;
- avoid overstimulation.

### SONG STRUCTURE

{{structure_map}}

Respect the approved structural intent. Use section labels and timing guidance where useful.

Energy map:
{{section_energy_map}}

### EXACT APPROVED LYRICS

Use these lyrics as the canonical lyric source. Do not replace the message, add unrelated verses, introduce product references, or change educational facts.

Lyrics:

{{exact_lyrics}}

### REPETITION / PARTICIPATION

{{repetition_notes}}

If there is call-and-response, make the lead cue and child-response gap musically obvious while keeping the lead vocalist as the only required generated vocal identity unless additional backing vocals are explicitly requested.

### PRONUNCIATION

{{pronunciation_notes}}

Prioritize correct pronunciation over rhyme embellishment or vocal runs.

### MIX / MASTER INTENT

- lead vocal centered and intelligible;
- balanced music with no harsh frequency build-up;
- no clipped peaks;
- age-appropriate dynamics;
- clean ending suitable for video editing;
- avoid excessively loud mastering.

### DO-NOT-DO CONSTRAINTS

- no copyrighted melody imitation;
- no recognizable artist imitation;
- no celebrity/real-person voice imitation;
- no protected character voice;
- no lyric rewrite that changes facts or safety meaning;
- no scary, violent, sexualized, or adult-coded vocal styling;
- no brand/product insertion;
- no random spoken ad-libs that were not approved;
- no abrupt or startling sound design for younger age bands.

## Package metadata

Save beside the prompt:
- provider family: `lyria`
- preferred model
- prompt version
- content ID
- run ID
- target duration
- exact-lyrics fingerprint
- female vocal required: true
- intended genre/BPM/key
- output filename placeholder
- render status

## Music QA after rendering — Phase 2

Check:
- exact/near-exact lyric fidelity;
- pronunciation;
- intelligibility;
- no unsafe or inappropriate ad-libs;
- melody originality risk;
- vocal identity risk;
- arrangement age fit;
- loudness and clipping;
- section coherence;
- duration;
- file integrity.

A successful model response is not sufficient for production approval.
