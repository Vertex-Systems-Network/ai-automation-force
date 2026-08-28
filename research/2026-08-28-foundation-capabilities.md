# Foundation Research Snapshot — 2026-08-28

This record captures external capability/policy facts used to design the initial AI-Native Content OS. Future agents must re-verify provider model IDs and platform rules before implementing automation because preview capabilities can change.

## Google speech generation

Source: Google AI for Developers — Text-to-speech generation
https://ai.google.dev/gemini-api/docs/speech-generation

Findings used by the architecture:
- Gemini TTS supports single-speaker and multi-speaker speech generation.
- Natural-language prompting can control style, tone, accent, and pace.
- Google recommends thinking of advanced prompts in terms of an audio profile, scene, and director's notes.
- Current documented TTS model family includes Gemini 3.1 Flash TTS Preview and Gemini 2.5 TTS variants.
- TTS is suited to exact text recitation and fine-grained spoken performance; it should not be confused with full music generation.

Foundation speech preference recorded in config:
`gemini-3.1-flash-tts-preview`

This is a preference, not a permanent guarantee. Verify before API integration.

## Google music generation

Source: Google AI for Developers — Generate music with Lyria 3
https://ai.google.dev/gemini-api/docs/music-generation

Findings used by the architecture:
- Lyria 3 is available through the Gemini API family for music generation.
- Lyria 3 Clip produces short music clips.
- Lyria 3 Pro is intended for full-length songs with structured sections such as verses, choruses, and bridges.
- Prompts can specify genre, instruments, BPM, key/scale, mood, structure, duration, vocals, and lyrics.
- The model supports supplied lyrics and vocal-profile direction.

Foundation music preferences recorded in config:
- full song: `lyria-3-pro-preview`
- preview: `lyria-3-clip-preview`

Verify before API integration.

## YouTube kids/family quality

Source: YouTube Help — Best practices for kids & family content
https://support.google.com/youtube/answer/10774223

Findings incorporated into QA gates:
- high-quality content should be age-appropriate, enriching, engaging, and inspiring;
- learning, curiosity, creativity, imagination, life skills, and coherent narratives are positive principles;
- confusing/hard-to-follow mass-produced or auto-generated content is a low-quality risk;
- deceptively educational, sensational/misleading, heavily promotional, or bizarre use of children's characters can be low-quality signals;
- quality principles can affect recommendations and monetization.

System consequence:
AI is used for quality and production acceleration, not uncontrolled volume generation.

## YouTube Made for Kids classification

Source: YouTube Help — Determining if your content is Made for Kids
https://support.google.com/youtube/answer/9528076

Findings incorporated into future publishing policy:
- content directed to children through songs, stories, poems, characters, activities, early education, or other child-directed factors is likely to require Made-for-Kids consideration;
- creators are responsible for audience designation rather than relying only on YouTube automation.

System consequence:
Phase 4 publishing must include a per-item Made-for-Kids review and must not silently assume a general-audience classification.

## YouTube Kids eligibility

Source: YouTube Help — Content policies for YouTube Kids
https://support.google.com/youtube/answer/10938174

Finding:
YouTube Kids is a filtered subset with separate age-appropriateness and content-quality considerations. Publishing to YouTube does not guarantee YouTube Kids inclusion.

## Research principle

This research is used only for system architecture and opportunity/policy understanding. Competitor material must never be copied into generated content. Future topic research must abstract signals and preserve originality.
