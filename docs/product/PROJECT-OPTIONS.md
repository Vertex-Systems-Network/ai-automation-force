# Project Options and Production Taxonomy

## Purpose

Define the complete operator-facing project configuration for the AI-native media studio. The UI may expose simple presets, but canonical storage must keep dimensions separate so future providers, workflows, analytics, and mobile clients do not inherit ambiguous fields.

## 1. Project creation flow

Recommended order:

1. Project identity
2. Audience profile
3. Cast/generation profile
4. Character strategy
5. Content format
6. Genre / creative treatment
7. Duration
8. Language
9. Visual style
10. Audio strategy
11. Timeline / pacing strategy
12. Output settings
13. Provider/cost policy
14. Review policy

The operator can choose `AI Decide` for most fields. Explicit operator selections override autonomous choices unless they violate hard safety/licensing rules.

## 2. Audience profile

Do not store `kids`, `adult`, `man`, `woman`, `both` in one field. These represent different concepts.

Canonical dimensions:

### Audience class
- `baby`
- `toddler`
- `preschool`
- `child`
- `preteen`
- `teen`
- `general`
- `adult`
- `family`
- `custom`

For child-directed projects, use age bands in the child-safety/content policy.

### Cast age composition
- `none`
- `baby`
- `child`
- `teen`
- `adult`
- `senior`
- `mixed`
- `non-human`
- `custom`

### Cast gender composition
- `none`
- `male`
- `female`
- `mixed`
- `unspecified`
- `non-human`
- `custom`

UI presets may display:
- Kids
- Adults
- Men
- Women
- Mixed

but must translate them into the canonical dimensions above.

## 3. Character source strategy

Before generation, the operator or AI selects one of:

- `locked-existing` — select one or more existing canonical characters;
- `new-and-lock` — create new characters, QA them, then lock before production;
- `mixed` — reuse existing characters and create additional new locked characters;
- `one-off` — create temporary characters for a single project, still with project-level continuity records;
- `no-character` — landscapes, abstract visuals, product/object stories, etc.;
- `ai-decide`.

A long-form project must never generate an important recurring character independently shot-by-shot without a canonical character record.

## 4. Character archetype registry

Initial extensible character types:

Human:
- baby
- toddler
- boy
- girl
- teen-boy
- teen-girl
- adult-man
- adult-woman
- senior-man
- senior-woman
- family/group

Non-human:
- realistic-animal
- anthropomorphic-animal
- fantasy-creature
- friendly-monster
- robot
- toy/mascot
- object-character
- vehicle-character
- nature-character
- alien/fictional-creature
- custom

The registry is extensible. Provider prompts must use canonical character IDs rather than free-text identity descriptions as the primary source of truth.

## 5. Content format

Core formats:
- song
- sung-lullaby
- spoken-lullaby
- poem
- rhyme
- story
- bedtime-story
- guided-imagination
- educational-video
- explainer
- music-video
- dialogue-scene
- short-film
- episode
- series-episode
- movie
- documentary
- cinematic-sequence
- compilation
- trailer/teaser
- short/social-short
- custom

Format and creative treatment are separate. A `movie` can be cinematic animation, musical, documentary-style, fantasy, comedy, etc.

## 6. Creative treatment / genre

Initial registry:
- cinematic
- animated-2d
- animated-3d
- stylized-3d
- realistic-live-action
- storybook
- stop-motion-inspired
- clay-inspired
- paper-cut-inspired
- sketch/illustrative
- educational-clean
- musical
- adventure
- fantasy
- science-fiction
- mystery
- comedy
- emotional/drama
- bedtime/gentle
- documentary
- nature
- historical
- action
- dance/performance
- surreal
- abstract
- custom

Do not expose presets that intentionally imitate a living artist or protected franchise style.

## 7. Duration model

Canonical unit: milliseconds or integer seconds; never store human strings as the source of truth.

Supported product duration:
- hard minimum default: 60 seconds
- recommended short default: 120 seconds
- hard maximum: 10,800 seconds (3 hours)

Presets:
- 1 minute
- 2 minutes
- 3–5 minutes
- 5–10 minutes
- 10–30 minutes
- 30–60 minutes
- 60–90 minutes
- 90–120 minutes
- 120–180 minutes
- custom

Long-form generation does not mean one provider call. Projects above short-form thresholds use hierarchical structure and resumable shot production.

## 8. Language

Project fields:
- source language
- narration language
- dialogue language(s)
- lyric language
- subtitle language(s)
- metadata language
- localization targets
- accent/dialect preference
- pronunciation dictionary

Canonical content and localized variants preserve lineage. Lyrics are adapted for meter/rhyme, not blindly translated.

## 9. Visual controls

Project-level controls:
- aspect ratio: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, custom
- target resolution: draft, 720p, 1080p, 1440p, 4K where supported
- frame rate: 24, 25, 30, 50, 60, custom where technically valid
- visual style ID
- palette
- lighting language
- texture / realism level
- camera grammar
- lens preference
- depth-of-field preference
- motion intensity
- animation intensity
- world/location IDs
- prop IDs
- reference images/videos
- first-frame/end-frame strategy
- typography/subtitle style
- safe zones
- watermark policy

Shot-level controls may override project defaults.

## 10. Camera controls

Support provider-neutral camera intent:
- shot size: extreme-wide, wide, medium-wide, medium, medium-close, close, extreme-close
- angle: eye-level, high, low, top-down, dutch, over-shoulder, POV
- lens intent: ultra-wide, wide, normal, portrait/telephoto, macro
- movement: static, pan, tilt, dolly, truck, pedestal, orbit, crane, handheld, steadicam-like, zoom, rack-focus
- movement speed
- subject tracking
- gaze direction
- screen direction
- composition anchor
- focus target

Provider adapters translate this intent into provider-specific prompts/settings.

## 11. Audio controls

Project may use:
- narration only
- music only
- dialogue
- song
- narration + music bed
- dialogue + music + SFX
- full cinematic mix

Controls:
- narrator/singer/cast voice IDs
- gender presentation where requested
- speaking pace
- emotional direction
- music genre
- BPM/tempo
- key when useful
- instrumentation
- dynamic range
- music ducking
- sound effects
- ambience
- silence strategy
- lip-sync requirement
- pronunciation dictionary
- loudness target
- stems retention

`AI Decide` is the default for creative musical details unless the operator overrides them.

## 12. Pacing, rhythm and sequence controls

Every project has a pacing profile:
- very-gentle
- gentle
- balanced
- energetic
- fast
- cinematic-dynamic
- music-synced
- dialogue-led
- custom

Timing controls include:
- target average shot length
- min/max shot length
- beat markers
- dialogue sentence boundaries
- chorus/verse markers
- scene-change density
- motion intensity curve
- emotional intensity curve
- transition density
- quiet/rest moments
- hook window
- climax window
- ending resolution

The timeline engine may optimize these values while preserving the selected profile.

## 13. Transition controls

Supported intent:
- hard cut
- match cut
- action cut
- J-cut/L-cut audio transition
- cross dissolve
- fade
- dip to color
- wipe when stylistically justified
- morph/generative transition
- camera-motion match
- object/shape match
- audio/beat-synced cut
- scene bridge

Do not overuse generative transitions. Continuity and story rhythm have priority over novelty.

## 14. Provider / cost controls

Execution mode:
- FREE_ONLY
- FREE_FIRST
- HYBRID_SMART
- BUDGET_CAPPED
- QUALITY_FIRST

Optional project caps:
- per attempt
- per shot
- per minute
- per project
- daily
- monthly

Provider controls:
- allow list
- deny list
- prefer list
- API-only
- allow manual free handoffs
- commercial-use required
- no-watermark required
- privacy/data-use constraints

## 15. Review controls

Approval modes:
- fully manual per stage
- manual at character lock + final master
- manual before paid spend + public publish
- policy-driven autonomous production with final publish gate
- custom

Hard safety/licensing blocks cannot be bypassed by a low-friction review mode.

## 16. Export / delivery controls

- master container/codec
- web delivery encode
- audio master
- subtitle formats
- thumbnail
- poster frame
- chapter markers
- platform derivatives
- 16:9 / 9:16 / 1:1 variants
- project manifest
- provenance manifest
- prompt/provider history
- checksum

## 17. Extensibility rule

Taxonomies are registry-driven rather than hard-coded into UI logic. New character types, formats, genres, providers, resolutions, languages, and output targets can be added through versioned registries and schemas without rewriting the core orchestrator.