# Persistent Memory Bank and Duplicate Prevention

## Purpose

The memory bank prevents the AI from behaving like every run is a new chat. It is the durable record of what has been researched, created, approved, rejected, and learned.

The repository, not conversation history, is the canonical memory source.

## Memory files

### `memory/state.json`
Stores execution state:
- schema version
- next content sequence
- last completed content ID
- last completed run ID
- last completion time
- current/incomplete run if applicable

### `memory/content-index.json`
Compact catalogue of every approved content item.

Each entry should contain enough information for fast duplicate screening without opening every package:
- id
- title
- normalized title
- slug
- age band
- content type
- language
- primary topic
- secondary topics
- premise
- hook
- learning/emotional objective
- creative device
- key characters
- setting
- refrain/recurring phrase summary
- ending/resolution summary
- tags
- package path
- created/approved timestamps
- fingerprints

### `memory/fingerprint-index.json`
Machine-oriented duplicate hints:
- normalized-title hash
- premise hash
- hook hash
- phrase hashes
- future embedding/vector IDs

Hashes are accelerators, not the only duplicate test. Semantic comparison remains required.

### `memory/research-index.json`
Tracks meaningful research decisions so the AI does not repeatedly rediscover the same insight or mistake research repetition for content novelty.

## Duplicate detection model

Duplicate prevention has four levels.

### Level A — Exact identity

Reject:
- same content ID
- same slug
- same normalized title
- exact text/lyrics/script reuse unless explicitly versioning the same canonical work

### Level B — Near lexical similarity

Compare:
- titles
- hooks
- chorus/refrain
- distinctive phrases
- plot summaries

When code automation is implemented, use normalized n-gram/Jaccard or equivalent lexical checks.

### Level C — Semantic concept similarity

The AI must compare meaning, not only words.

Example of a probable duplicate:
- Old: a shy moon learns to glow by asking star friends for help.
- New: a timid moon discovers confidence after stars encourage it.

Different wording, materially same premise and resolution.

Example of acceptable reuse of a broad topic:
- Existing: counting five ducks crossing a pond.
- New: a bakery rhythm game teaching counting backward from ten.

Both teach counting, but the creative device and learning treatment are materially different.

### Level D — Portfolio fatigue

Even when not a strict duplicate, reject or defer concepts that overuse recently repeated combinations such as:
- same animal repeatedly
- same bedtime setting
- same lesson
- same musical energy
- same conflict/resolution pattern
- same age/type cell too often

The goal is a diverse catalogue, not merely unique strings.

## Candidate similarity decision

For each candidate, record:

- closest prior IDs
- title similarity assessment
- premise similarity assessment
- hook/refrain similarity assessment
- objective overlap
- creative-device overlap
- decision
- required differentiation if any

Allowed decisions:
- `CLEAR`
- `CLEAR_WITH_DIFFERENTIATION`
- `REJECT_DUPLICATE`
- `REJECT_DERIVATIVE`
- `DEFER_PORTFOLIO_FATIGUE`

## Final-text recheck

A concept can pass early screening but converge toward old content while being written. Therefore the complete approved text must be checked again immediately before save.

## Rejected concepts

Future implementation should maintain a rejected/deferred concept log. Rejected concepts should not pollute the approved catalogue, but their core fingerprints should be retained when useful so the AI does not propose the same rejected idea every run.

## Memory update transaction

The correct sequence is:

1. create package in draft state;
2. run final QA and duplicate recheck;
3. mark package approved;
4. update content index;
5. update fingerprints;
6. update state pointer;
7. verify all references resolve.

If steps 4–7 fail, the run is not complete. On the next run, the agent must reconcile approved package directories against memory before generating new work.

## Recovery rule

At startup, compare:
- approved content directories
- content index
- state pointer

If an approved directory exists but is absent from memory, recover/index it first.

If memory points to missing content, mark state inconsistent and repair before creating new approved content.

## Future vector memory

When automation code is added, introduce embeddings for:
- title + premise
- full content
- hook/refrain
- objectives

Store vector IDs separately from canonical content so the system can change embedding providers/models without rewriting content history.

A vector match is evidence, not an automatic verdict. The AI should still explain why a concept is or is not materially duplicative.
