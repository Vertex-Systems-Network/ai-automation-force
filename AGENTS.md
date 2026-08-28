# AGENTS.md — Mandatory AI Operating Contract

This file is the first instruction source for any AI agent working in this repository.

## Mission

Operate this repository as an AI-native children's content studio with persistent memory, originality control, age-aware writing, child-safety QA, production-ready audio handoff, and resumable autonomous execution.

The normal operator command is `next`.

When the operator says `next`, do not ask what type of content to make unless repository state is genuinely corrupt or a required secret/credential is unavailable. The agent must inspect repository state, research, decide, produce, validate, classify, save, and update memory.

## Mandatory startup sequence

Before generating any content:

1. Read `README.md`.
2. Read `AGENTS.md`.
3. Read `config/content-policy.yaml`.
4. Read `ai-native/SYSTEM.md`.
5. Read `ai-native/WORKFLOW.md`.
6. Read `ai-native/QUALITY-GATES.md`.
7. Read `ai-native/MEMORY-BANK.md`.
8. Read all machine-readable files in `memory/`.
9. Inspect recent approved content and recent research records.
10. Determine the current pipeline state and next available content ID.

Never rely only on chat memory when repository state exists. The repository is the source of truth.

## `next` contract

A `next` run must perform the following autonomously:

- research current content opportunities and evergreen gaps;
- select a target age band using configured strategy and portfolio balance;
- select the best content type (song, lullaby, poem, rhyme, story, educational narration, guided imagination, bedtime story, or a future registered type);
- generate at least three candidate concepts before choosing one;
- run duplicate detection against memory and repository content before full writing;
- reject concepts that are too similar to previous work;
- write the complete original content;
- generate a production-grade Gemini TTS handoff prompt;
- run all quality gates;
- classify and save the package;
- update memory/index files only after the content passes all gates;
- summarize the run and recommend the next downstream action.

## Non-negotiable rules

### Age appropriateness

Do not treat 0–12 years as one audience. Use the configured age band and its language, duration, pacing, emotional complexity, educational scope, and safety constraints.

For `baby-audio`, design for parent-controlled listening rather than encouraging infant screen engagement.

### Originality

Do not copy, closely imitate, or intentionally evoke copyrighted children's songs, modern nursery arrangements, branded characters, celebrity voices, distinctive fictional universes, lyrics, melodies, plots, or catchphrases.

A public-domain concept is not permission to copy a modern recording or arrangement.

### No mass-generation behavior

Do not optimize for volume at the cost of coherence. Every approved item must have a clear purpose, beginning/middle/end where applicable, age-appropriate language, identifiable creative value, and an originality rationale.

### Research

When current data can improve topic selection, use current web research and record material sources in the research record. Prefer primary/official sources for platform rules, safety, health, education, and product capability claims.

### Memory before creation

Never create final content before checking the memory bank. If memory cannot be read, stop the approval step and repair memory first rather than silently creating untracked content.

### Female voice default

The default single-speaker audio direction is a warm, natural female voice appropriate to the target age band. This is a production preference, not permission to imitate any real person. Never request a celebrity or identifiable person's voice.

For songs, TTS may not be the best final musical renderer. Still produce the required Gemini audio handoff, clearly distinguishing spoken narration, rhythmic chant, and singing intent. If a chosen Gemini endpoint cannot reliably satisfy musical requirements, preserve the lyrics and performance specification and mark musical rendering as a downstream production task rather than fabricating capability.

## Content package requirement

Each approved content item must include:

- stable content ID
- title
- slug
- content type
- target age band
- target duration
- language
- objective
- entertainment goal
- learning/emotional goal where relevant
- concept summary
- full text/lyrics/script
- structure map
- pronunciation notes
- audio performance notes
- Gemini audio prompt
- safety review
- originality/duplicate review
- research provenance
- tags and classifications
- downstream video notes placeholder
- publishing status
- memory fingerprints

## State transitions

Allowed high-level states:

`idea -> researched -> uniqueness-cleared -> drafted -> qa-passed -> audio-ready -> approved`

Future states may append:

`audio-generated -> video-planned -> video-generated -> publish-ready -> published -> analyzed`

Do not mark a state complete unless its gate has actually passed.

## Failure behavior

If a gate fails:

1. record the failure reason;
2. revise once or generate a replacement candidate;
3. re-run affected gates;
4. do not update the approved memory catalogue until all mandatory gates pass.

If external research or a required provider is unavailable, use evergreen repository knowledge only when safe to do so and mark the limitation in the research record.

## Change discipline

- Prefer additive, backwards-compatible changes to the Content OS.
- Do not silently alter schemas after approved records exist.
- Version schemas and migrations when machine-readable structures change.
- Keep prompts, policies, memory, generated content, and automation code separated.
- Never place API keys or secrets in the repository.

## Human escalation

Human approval is required before:

- publishing to a public platform until the publishing policy explicitly enables autonomous publishing;
- spending money through an API/service;
- deleting approved content or memory history;
- changing a child-safety rule to be less strict;
- changing brand identity, canonical characters, or voice identity after those are locked.

Routine `next` content creation does not require per-item approval once the system is configured and the output remains inside these rules.
