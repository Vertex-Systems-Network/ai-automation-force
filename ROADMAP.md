# Lullabies AI-Native Studio Roadmap

## Phase 1A — Content OS Foundation

Status: implemented as repository architecture.

Includes:
- persistent AI operating contract
- one-word `next` workflow
- autonomous age/type selection
- current/evergreen research stage
- memory bank
- duplicate and derivative detection design
- content-generation prompt contract
- child-safety and quality gates
- speech/music audio router
- detailed Gemini TTS handoff
- detailed Lyria music handoff
- canonical content metadata schema
- repository classification rules

## Phase 1B — Executable Orchestrator

Goal: make `next` executable without relying on a human to manually copy each step between tools.

Recommended implementation:
- Python 3.12+ package under `studio/`
- CLI entry point: `lullabies next`
- provider adapters:
  - research/search adapter
  - LLM planning/writing adapter
  - Gemini TTS adapter
  - Lyria adapter
  - Git/repository persistence adapter
- local `.env` / GitHub Actions secrets for credentials; never commit secrets
- JSON Schema validation before save
- deterministic content ID allocator
- memory reconciliation on startup
- lexical duplicate detector
- semantic/vector duplicate detector
- retry/idempotency layer
- dry-run mode
- audit/status commands
- unit tests and fixture catalogue

Execution modes:
1. AI-agent mode — a capable agent reads `AGENTS.md` and runs the repository workflow.
2. CLI mode — `lullabies next` runs the same state machine programmatically.
3. Future scheduled mode — GitHub Actions/manual workflow dispatch, only after cost and publishing controls are configured.

No paid model call should occur without credentials and explicit spend policy.

## Phase 2 — Audio Rendering OS

Goal: turn every `audio-ready` package into a rendered and QA-checked audio artifact.

### Speech route
- Gemini TTS
- exact script checksum before render
- female voice selection stored in metadata
- WAV/PCM or provider output capture
- normalize to delivery master format
- transcript comparison against canonical script
- pronunciation QA
- silence/pause QA
- clipping/loudness checks
- store render manifest and provider/model version

### Music route
- Lyria full-song generation for songs/sung lullabies
- exact approved lyrics in prompt
- female singer profile
- track structure/BPM/key/instrumentation contract
- lyric fidelity check
- audio quality check
- originality-risk review of generated melody/style
- render versioning; never overwrite the only approved render

Recommended states:
`audio-ready -> audio-generated -> audio-qa-passed`

## Phase 3 — Visual IP and Video Planning

Do this before mass video generation.

### 3A. Visual/Character Bible
Create:
- brand art direction
- canonical color system
- character sheets
- front/side/back views
- expressions
- clothing/accessory rules
- environment/world rules
- prohibited mutations
- age-appropriate visual safety rules

Store canonical references in `visual-bible/`.

### 3B. Storyboard compiler
Convert approved content + audio into:
- scene list
- timestamps
- shot type
- subject/action
- background
- continuity state
- reference images
- camera motion
- text/caption need
- negative constraints
- expected transition

Recommended package artifact:
`video-plan.json`

### 3C. Video generation router
At foundation-research time, Google's Gemini API documentation recommends Gemini Omni Flash as the default video-generation/editing path for coherence, multimodal reasoning, and character consistency, while Veo 3.1 is useful for specific controls such as video extension, first/last-frame control, reference-image direction, and legacy Veo workflows.

Provider/model names must be re-verified before implementation.

Use:
- short deterministic scenes rather than one giant prompt;
- canonical character references;
- audio timeline as the timing source;
- continuity checks after every scene;
- regenerate only failed scenes;
- assemble only QA-passed clips.

### 3D. Video assembly
Recommended deterministic post-production layer:
- FFmpeg-based assembly
- master audio sync
- clip trim/extension rules
- captions/subtitles
- safe-zone handling
- intro/outro only when brand policy allows
- loudness normalization
- 16:9 master and optional 9:16 derivative
- checksum and render manifest

Recommended states:
`audio-qa-passed -> video-planned -> scenes-generated -> video-assembled -> video-qa-passed`

## Phase 4 — YouTube Publishing OS

Publishing remains human-gated until explicitly enabled.

### Metadata compiler
Generate:
- title
- description
- tags where useful
- category
- language
- playlist target
- thumbnail brief
- child-directed audience review
- synthetic-media disclosure review where applicable

### Upload implementation
Use the YouTube Data API with OAuth and resumable upload.

The upload record should explicitly support:
- `status.privacyStatus`
- `status.selfDeclaredMadeForKids`
- `status.containsSyntheticMedia` when applicable
- scheduled publication only after QA/approval

Default first upload state should be `private` or `unlisted`, not public.

Unverified API projects can face public-upload restrictions, so API-project compliance/audit status must be checked during implementation.

### Publishing gates
Before public release:
- final visual/audio QA
- copyright/IP review
- Made-for-Kids designation review
- title/thumbnail truthfulness
- no keyword stuffing
- no misleading educational claim
- no unsafe visual imitation
- upload metadata verified
- human approval until autonomous publishing is explicitly enabled

## Phase 5 — Analytics Learning Loop

Ingest performance after publication:
- impressions
- click-through rate
- average view duration
- retention curve
- repeat viewing where available
- traffic source
- search terms where available
- age/type/topic cohort comparisons

Use analytics to improve portfolio selection, not to blindly clone successful content.

Memory should record:
- what worked
- what underperformed
- hypotheses
- experiments
- saturation/fatigue signals

## Phase 6 — Localization

For each approved canonical item:
- preserve original content ID lineage
- create language variant ID/version
- adapt meaning, rhyme, meter, examples, and cultural references
- rerun safety/factual/originality checks
- rerender speech/music using the language-appropriate female voice profile
- create localized metadata and captions

Do not use literal translation for lyrics when it breaks meter, rhyme, naturalness, or cultural fit.

## Phase 7 — Multi-platform/IP Expansion

Possible future outputs:
- YouTube Shorts
- music streaming
- podcast/audio feeds
- ebooks/storybooks
- printables
- learning app
- games
- character licensing

All future formats should reference the same canonical content/IP records rather than creating disconnected copies.

## Immediate next milestone

Implement Phase 1B executable orchestrator and create the first single `next` run in dry-run mode. Once one content package can be generated, memory-checked, schema-validated, and stored reliably, enable real audio rendering as Phase 2.
