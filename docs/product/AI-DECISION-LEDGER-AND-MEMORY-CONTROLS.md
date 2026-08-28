# AI Decision Ledger and Memory Controls

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define what the platform must record when AI makes material decisions and how users/operators inspect, correct, pin, forget and govern AI memory.

The goal is not to expose hidden chain-of-thought. The goal is to expose useful decision evidence, inputs, policy checks, alternatives and outcomes without storing or revealing private internal reasoning traces.

## Material decisions

A `DecisionRecord` is required when AI chooses or recommends something that can materially affect:
- project structure;
- content concept/script/lyrics;
- character/look/voice;
- provider/model;
- generation retry/fallback;
- paid spend;
- asset approval/rejection;
- continuity repair;
- publishing target/time/metadata;
- localization;
- analytics-driven future behavior;
- memory promotion;
- moderation/escalation;
- privileged tool action.

Trivial formatting or deterministic transformations do not require a full decision record.

## Decision record

Fields:
- `decision_id`
- `workspace_id`
- `project_id` optional
- `decision_type`
- `agent_role`
- `agent_version`
- `prompt_version`
- `model_provider/model/version`
- `policy_profile_version`
- `input_artifact_ids`
- `retrieved_memory_ids`
- `external_evidence_ids`
- `constraints_applied`
- `candidate_summary[]`
- `selected_candidate`
- `selection_factors[]`
- `confidence_band`
- `uncertainties[]`
- `estimated_cost/latency` where relevant
- `approval_requirement`
- `approval_record_id` optional
- `downstream_action_ids[]`
- `human_override` optional
- `outcome/evaluation` optional
- timestamps

Never persist raw secrets or hidden reasoning traces.

## User-facing explanation model

UI may show concise explanations such as:
- “Selected Runway because Kling quota is exhausted and this shot requires image-reference control.”
- “Rejected Take 4 because face identity score failed hard continuity threshold.”
- “Suggested this concept because recent portfolio memory shows three similar bedtime stories already exist.”

Allowed explanation content:
- facts/constraints;
- evidence references;
- selected vs rejected alternatives;
- policy/entitlement/budget gates;
- uncertainty;
- next safe action.

Do not present fabricated certainty or hidden chain-of-thought.

## AI command behavior

Every material command supports applicable modes:
- `EXPLAIN` — show decision evidence/constraints.
- `DRY_RUN` — plan actions, costs, providers and approvals without side effects.
- `EXECUTE` — perform authorized actions.
- `RETRY_FAILED_SCOPE` — retry only failed items, preserving successful state.
- `COMPARE_ALTERNATIVES` — generate/planning alternatives without replacing approved state.
- `UNDO` — invoke a defined compensating/revert action where supported.

A command declares whether undo is:
- `NATIVE_REVERSIBLE`
- `COMPENSATING_ACTION`
- `SOFT_DELETE_RESTORE`
- `NOT_REVERSIBLE`

## Memory classes

### Canonical policy memory
Version-controlled rules/configuration. Highest authority after system/operator policy.

### User preference memory
Explicit user choices/preferences, scoped to user/workspace/project.

### Approved project memory
Approved characters, styles, facts, decisions and creative canon.

### Observational memory
Facts observed from generation/provider/workflow history.

### Failure memory
Known failures, bad prompts/providers/settings and remediation outcomes.

### Performance memory
Analytics/cost/quality trends.

### Hypothesis memory
Unconfirmed suggestions inferred from analytics/research. Cannot automatically become policy.

### External evidence memory
Research/source snapshots with provenance/freshness.

## Memory lifecycle

`CANDIDATE -> VALIDATED -> ACTIVE -> SUPERSEDED | EXPIRED | REVOKED | DELETED`

Promotion rules vary by class. Examples:
- user preference may activate from explicit user setting;
- character canon activates after approval/lock;
- provider capability evidence requires source validation/freshness;
- analytics hypothesis requires evaluation before changing production policy.

## Scope hierarchy

Memory scopes:
- global product policy;
- workspace;
- project;
- content series/universe;
- character/entity;
- user preference.

Narrower memory must not silently override higher-authority product/security policy.

## Memory inspection UX

User/operator can view:
- memory statement/summary;
- type;
- source/provenance;
- scope;
- created/updated;
- confidence/status;
- where it was used;
- dependent decisions/projects when practical;
- expiry;
- correction/forget controls if authorized.

## Correct memory

Correction creates a new version/record and marks old memory superseded where history must remain auditable.

Examples:
- wrong character eye color;
- incorrect brand pronunciation;
- outdated provider capability;
- user preference changed.

Dependent future work uses new memory; already approved historical outputs do not silently rewrite.

## Forget/delete memory

When user has authority and law/policy permits:
- remove from active retrieval immediately;
- mark pending deletion where dependent systems require asynchronous cleanup;
- remove embeddings/index entries;
- propagate deletion to backups according to privacy lifecycle policy;
- preserve only legally/security-required audit metadata when applicable and documented.

`forget` must not merely hide a UI row while leaving active retrieval unchanged.

## Pin/lock memory

Users can pin allowed project/creative facts:
- character attributes;
- pronunciation;
- brand facts;
- series canon;
- preferred provider policy where allowed.

Pinned memory has explicit scope/version and requires privileged override to change. Security/product policies remain higher priority.

## Contradictions

When memories conflict:
- do not silently merge incompatible facts;
- identify scope, recency, authority and approval state;
- choose deterministic precedence where defined;
- otherwise surface `CONFLICT_REQUIRES_REVIEW`.

## Retrieval controls

Retrieval must consider:
- tenant/workspace authorization;
- scope;
- memory class;
- status;
- recency/freshness;
- relevance;
- confidence;
- poisoning/trust level;
- rights/privacy restrictions.

Embedding similarity alone never grants authority.

## User override

Human override records:
- original AI decision;
- selected override;
- actor;
- reason optional/required by action class;
- whether override should become a user/project preference memory;
- impact on future evaluation.

Do not automatically learn every override as a permanent global preference.

## Decision history UI

Project-level timeline supports filtering by:
- agent;
- decision type;
- provider;
- approval state;
- cost impact;
- human override;
- failed/recovered;
- publication effect.

A user should be able to answer:
- why was this provider used?
- why did this shot regenerate?
- why did the system block publishing?
- what memory influenced this concept?
- who approved this spend/publish action?

## AI learning governance

Performance observations do not directly mutate canonical policy.

Loop:
`Observation -> Hypothesis -> Evaluation -> Approved change -> Versioned policy/prompt/memory`

## Privacy/security

- decision records use references rather than copying entire sensitive documents;
- secrets are redacted;
- tenant authorization applies to every memory retrieval;
- security-sensitive decision logs have access controls;
- retention follows data classification;
- deleted user data is excluded from future model/retrieval context according to privacy lifecycle.

## Acceptance criteria

Planning is complete when implementation can determine:
- which decisions are logged;
- what explanation the user sees;
- how dry-run/retry/undo work;
- memory classes and lifecycle;
- scope/precedence/conflict rules;
- inspect/correct/pin/forget behavior;
- human override learning rules;
- privacy/security constraints.
