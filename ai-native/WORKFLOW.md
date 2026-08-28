# `next` Workflow — Autonomous Runbook

This is the canonical execution procedure for a normal content-generation run.

## 0. Start

On command `next`:

- create a run identifier such as `RUN-YYYYMMDD-HHMMSS`;
- load repository policy and memory;
- confirm no prior run is left in an ambiguous approved-but-unindexed state;
- determine the next stable content ID.

## 1. Load state

Read:
- `AGENTS.md`
- `config/content-policy.yaml`
- `memory/state.json`
- `memory/content-index.json`
- `memory/fingerprint-index.json`
- recent content packages
- recent research records

Build a portfolio summary by age band, content type, topic, objective, tone, and recent frequency.

## 2. Research

Use current web research when available and useful. Research is for discovering opportunities and constraints, never for copying a competitor.

Research checklist:
- current platform or provider capability changes relevant to production;
- current kids/family platform-quality guidance if publishing implications matter;
- seasonal/calendar opportunities;
- search/interest signals where available;
- educational or developmental topic opportunities;
- portfolio gaps in this repository.

For factual or child-development claims, prefer reliable primary or institutional sources.

Save a concise research decision record with source URLs/titles, date accessed, findings, and what was intentionally not copied.

## 3. Choose portfolio target

Select age band and content type using:
- configured strategic priority;
- underserved portfolio cells;
- recency balance;
- age-appropriate opportunity;
- production feasibility;
- originality headroom.

Avoid repeating the same type or topic merely because the previous item performed well; diversity is a portfolio constraint.

## 4. Generate candidates

Generate at least 3 candidates. Each candidate needs:
- title
- one-line premise
- hook
- age band
- content type
- objective
- entertainment value
- learning/emotional value
- duration target
- creative mechanism
- risk notes

Do not write full content yet.

## 5. Duplicate gate

For every candidate, compare against `memory/content-index.json`, fingerprints, and repository content.

Check:
1. exact title/slug collision;
2. normalized title similarity;
3. same topic + same creative device;
4. same story conflict/resolution;
5. same central metaphor;
6. same chorus/refrain concept;
7. distinctive phrase overlap;
8. same learning objective within an overly similar treatment;
9. same characters/situation if that reuse is not intentionally serialized;
10. future semantic similarity score when vector search is implemented.

Candidate outcome:
- `CLEAR`
- `CLEAR_WITH_DIFFERENTIATION`
- `REJECT_DUPLICATE`
- `REJECT_DERIVATIVE`

Select the strongest cleared candidate.

## 6. Write content

Write using the target age policy.

General rules:
- short, clear language appropriate to the band;
- coherent structure;
- meaningful creative value;
- no manipulative fear, dangerous imitation, or inappropriate material;
- no real-person voice imitation;
- no copyrighted character borrowing;
- no unverified factual teaching.

Format-specific rules:

### Song
Include title, concept, lyrical structure, verses/chorus/bridge if suitable, repetition logic, movement/call-and-response opportunities, pronunciation notes, and musical-performance intent.

### Lullaby
Prioritize calm imagery, predictable language, low cognitive load, reassuring tone, and gentle repetition. Avoid instructions that could be unsafe for sleep contexts.

### Poem/rhyme
Maintain readable rhythm and age-appropriate imagery. Do not force rhyme at the expense of meaning or grammar.

### Story/bedtime story
Use a clear beginning, middle, and resolution. Define character goal, obstacle, attempt, emotional turn, resolution, and takeaway without becoming preachy.

### Educational narration
Define one primary learning objective, factual sources if needed, simple examples, and a recap.

### Guided imagination
Clearly distinguish imagination from fact; keep directions calm and non-risky.

## 7. Quality gates

Run every gate in `ai-native/QUALITY-GATES.md`.

If any mandatory gate fails:
- revise once if the issue is local and fixable;
- otherwise discard and return to candidate selection;
- never approve with unresolved mandatory failures.

## 8. Compile Gemini audio handoff

Use `ai-native/prompts/GEMINI-AUDIO-HANDOFF.md`.

Always include:
- exact approved text;
- target listener age;
- female voice direction unless content specification overrides it;
- naturalness requirements;
- pace, articulation, warmth, energy, pauses, emotional arc;
- pronunciation notes;
- section-level delivery directions;
- prohibitions against celebrity/real-person imitation;
- no ad-libbing that changes factual meaning;
- output naming/version guidance.

For musical content, explicitly label whether the handoff is intended as spoken performance, rhythmic chant, sung interpretation, or a guide vocal. Do not claim a model can generate a final song arrangement unless the selected provider/model actually supports that workflow.

## 9. Final duplicate recheck

Before repository save, compare the completed text again against approved memory. This catches accidental convergence introduced during writing.

## 10. Save package

Path:

`content/<age-band>/<content-type>/<content-id>-<slug>/`

Required files:
- `content.md`
- `metadata.json`
- `audio-prompt.md`
- `qa.json`
- `research.md`

## 11. Update memory

Only after the package is approved:
- append/update `memory/content-index.json`;
- add fingerprints to `memory/fingerprint-index.json`;
- update `memory/state.json` with last completed ID/run/date;
- append research summary to `memory/research-index.json` if useful.

Memory write is the completion boundary. If memory update fails, the run is not complete.

## 12. Report

The run report should be concise and include:
- content ID and title;
- age band and type;
- why it was chosen;
- duplicate-check result;
- QA status;
- repository paths;
- audio readiness;
- recommended next downstream action.
