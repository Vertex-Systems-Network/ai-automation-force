# Prompt Registry & Prompt Versioning Specification

## Purpose

Treat production prompts as versioned software assets rather than disposable chat text. The registry must preserve task intent, compatible providers/models, variables, tests, performance history and change rationale.

## Core principles

- Canonical project state is separate from provider-specific prompt text.
- Prompts are generated from structured inputs and versioned templates.
- Production prompts are never silently overwritten.
- Provider prompt tuning must not mutate canonical characters/content/style.
- Prompt changes are evaluated with fixtures/history before broad use where practical.

## Prompt classes

Initial classes:
- research;
- portfolio/content selection;
- originality judge;
- content writer;
- story/script editor;
- character creator;
- character reference compiler;
- visual/art direction;
- storyboard/shot planner;
- keyframe generation;
- image generation;
- video generation;
- video continuation/extension;
- TTS/narration;
- dialogue voice;
- music/song generation;
- ambience/SFX;
- continuity QA;
- media QA;
- metadata/publishing;
- localization;
- analytics/hypothesis;
- provider scout.

## Prompt record

Every registered prompt/template should store:
- Prompt ID;
- semantic version;
- task class;
- purpose;
- input schema;
- required variables;
- optional variables/defaults;
- compatible provider families/models;
- output schema/contract;
- system/developer/user template sections where relevant;
- safety/negative constraints;
- examples/fixtures;
- changelog;
- status: draft/evaluation/active/deprecated;
- created/updated metadata.

## Semantic versioning

Suggested:
- MAJOR — output/behavior contract changes materially;
- MINOR — compatible capability/quality improvement;
- PATCH — wording/bugfix without intended contract change.

Jobs record exact prompt version/hash used.

## Structured input

Do not compose critical prompts by arbitrary string concatenation from hidden chat history.

Prompt compiler receives typed canonical data such as:
- Project profile;
- ContentVersion;
- CharacterVersion/Look;
- Scene/Shot state;
- style profile;
- provider capability;
- references;
- policy constraints;
- requested output schema.

## Provider adaptation

Base canonical prompt intent may have provider-specific adapters for:
- supported parameter vocabulary;
- prompt length;
- negative prompts;
- reference syntax;
- camera/motion language;
- audio/music controls;
- JSON/structured output support.

Provider adaptation creates a derived compiled request. It does not become the new canonical creative state.

## Exact-content protection

For approved scripts/lyrics/dialogue:
- mark exact text blocks as immutable unless the task is explicitly editing them;
- instruct generation model not to rewrite where exact fidelity is required;
- QA output against canonical text/audio.

## Character consistency protection

Visual/video prompts should reference canonical IDs/versions/looks and include:
- identity summary;
- reference assets;
- scene-specific state;
- prohibited mutations;
- continuity in/out state.

Do not rely on repeating long prose descriptions as the only identity mechanism when provider references are available.

## Prompt performance history

Track by prompt version + provider/model + task class:
- attempts;
- accepted rate;
- failure reasons;
- average retries;
- average cost;
- continuity score;
- QA score;
- latency;
- known problematic inputs.

History informs evaluation but does not automatically rewrite active prompts without governed change.

## Evaluation fixtures

Create reusable test fixtures for representative cases:
- single locked character;
- multi-character dialogue;
- child-directed song;
- cinematic motion shot;
- first/end-frame continuation;
- multilingual narration;
- malformed provider output;
- high-risk continuity shot.

Prompt evaluation should compare contract adherence and QA, not only subjective preference.

## Prompt change workflow

1. identify issue/opportunity;
2. create new prompt version;
3. document rationale;
4. validate schema/template rendering;
5. run offline fixtures where possible;
6. run controlled provider tests only within authorization/cost policy;
7. compare outcomes;
8. activate/deprecate version;
9. preserve older version/history.

## Security

Treat content inserted into prompts as untrusted where applicable.

Protect against:
- prompt injection from fetched research/web content;
- provider responses attempting to alter system policy;
- secrets inserted into prompt logs;
- malicious uploaded text overriding role instructions.

External source text is data, not authority.

## Prompt scope/context minimization

Use the smallest sufficient context:
- current task;
- relevant canon;
- relevant adjacent continuity;
- relevant memory/research;
- explicit constraints.

Avoid huge multi-hour prompt payloads when a scene/shot-level summary is sufficient.

## Output contracts

Where reliable provider/model support exists, prefer structured outputs for planning/metadata roles. Otherwise parse/validate defensively and reject malformed contracts.

Creative media prompts still require normalized metadata around the free-form creative request.

## Deprecation

Deprecated prompt versions remain resolvable for historical jobs/audit. New jobs should not use deprecated versions unless reproducing/diagnosing prior behavior.

## Acceptance criteria

Prompt system is development-ready when every production attempt can identify the prompt/template version and structured inputs that produced it, and prompt improvements can be rolled out/reverted without silently changing historical or canonical project state.