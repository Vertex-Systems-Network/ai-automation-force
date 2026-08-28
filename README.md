# Lullabies — AI-Native Kids Content Studio

This repository is the source of truth for an AI-native children's content production system covering songs, poems, stories, lullabies, educational narration, and future video/publishing workflows.

## Core operating model

The repository is not only a content archive. It is the persistent memory and operating system used by an AI agent whenever the operator gives the command `next`.

`next` means:

1. Load repository instructions, configuration, memory, and prior content.
2. Research current opportunities and age-appropriate topics.
3. Select the best content type and target age band.
4. Check the memory bank and content catalogue for semantic, thematic, title, lyric, plot, hook, and learning-objective duplication.
5. Reject or substantially differentiate duplicates.
6. Create the content package.
7. Run child-safety, quality, originality, continuity, copyright-risk, and platform-policy gates.
8. Produce a detailed Gemini TTS audio-generation handoff with a female voice direction where appropriate.
9. Classify and save the approved package in the repository.
10. Update memory/indexes so the next run knows exactly what has already been created.
11. Report what was created and the recommended next production step.

## Phase 1 scope

Phase 1 builds the content intelligence and audio handoff layer:

- research and opportunity selection
- age classification
- autonomous content-type selection
- originality and duplicate prevention
- content writing
- Gemini TTS production prompts
- persistent memory bank
- quality and safety gates
- repository classification
- resumable `next` workflow

Video generation, automated publishing, channel analytics, thumbnails, localization, and performance-driven iteration are Phase 2+ and intentionally attach to this foundation rather than being mixed into the first implementation.

## Age bands

The system uses age-specific rules instead of treating all children as one audience:

- `baby-audio`: 0–12 months — parent-controlled lullaby/gentle audio use cases
- `toddler`: 1–2 years
- `preschool`: 2–5 years
- `early-primary`: 5–7 years
- `junior`: 7–9 years
- `preteen`: 9–12 years

The first recommended production focus is `preschool` unless research provides a strong reason to choose another configured band.

## Content types

Supported Phase 1 types:

- song
- lullaby
- poem
- rhyme
- story
- educational-narration
- guided-imagination
- bedtime-story

The AI chooses the type for normal `next` runs.

## Repository map

- `AGENTS.md` — mandatory instructions for any AI agent operating this repository
- `ai-native/SYSTEM.md` — architecture and state machine
- `ai-native/WORKFLOW.md` — detailed `next` execution workflow
- `ai-native/QUALITY-GATES.md` — non-negotiable acceptance gates
- `ai-native/MEMORY-BANK.md` — persistent memory and duplicate-detection design
- `ai-native/COMMANDS.md` — operator command contract
- `ai-native/prompts/` — reusable content and Gemini audio prompts
- `config/content-policy.yaml` — age bands, content types, voice defaults, and selection rules
- `memory/` — machine-readable persistent memory
- `content/` — approved content packages, classified by age/type/status
- `research/` — research snapshots and opportunity decisions

## Operating command

After this foundation is present, the normal operator command is simply:

`next`

The agent must resume from repository state rather than asking the operator to repeat prior decisions.
