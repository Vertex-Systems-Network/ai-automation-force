# Operator Commands

The repository is designed so normal operation requires minimal prompting.

## `next`

Primary command.

Meaning: autonomously execute one complete Phase 1 content run from repository state.

The agent must:
- load state;
- research;
- choose age band/type/topic;
- check memory;
- write;
- QA;
- prepare Gemini audio handoff;
- save package;
- update memory;
- report completion.

The operator should not need to restate prior decisions.

## `next <N>`

Future batch command. Generate up to N independent approved content packages sequentially, with memory updated after every item. Do not generate concepts in parallel without memory synchronization because that can create cross-run duplicates.

Until batch automation code is implemented, interpret this conservatively and preserve the same per-item gates.

## `next --type <type>`

Optional override for a specific registered content type while retaining autonomous topic/age selection where appropriate.

## `next --age <age-band>`

Optional target age-band override.

## `next --language <language>`

Optional language override. Localization must be adaptation, not naive literal translation, especially for rhyme/song meter.

## `status`

Read-only summary of:
- last completed item;
- next sequence;
- catalogue counts by age/type;
- incomplete run if any;
- memory consistency;
- current phase capability.

## `audit`

Run repository/content-system audit without generating new content. Check:
- memory consistency;
- broken package references;
- schema completeness;
- duplicate risks;
- policy drift;
- missing QA;
- stale provider configuration;
- future workflow gaps.

## `research`

Refresh opportunity research and save a research snapshot without producing new content.

## `recheck <content-id>`

Re-run duplicate, safety, factual, and metadata QA on an existing package without silently changing the approved canonical text.

## `audio <content-id>`

Compile or refresh the Gemini audio handoff for an approved content item. If the configured model has changed, preserve the content text and version only the provider-specific audio prompt.

## Future commands

Reserved for later phases:
- `render-audio <content-id>`
- `video-plan <content-id>`
- `render-video <content-id>`
- `publish <content-id>`
- `analyze <content-id>`
- `localize <content-id> <language>`

These commands must not be treated as implemented until their phase documentation and safety gates exist.
