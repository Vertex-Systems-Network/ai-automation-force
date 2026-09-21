# AGENTS.md — Mandatory AI Operating Contract

This file is the first instruction source for any AI agent working in this repository.

## Mission

Operate this repository as a persistent, provider-agnostic AI-native media production platform with research intelligence, memory, originality control, reusable/locked entities, autonomous audio direction, editorial timelines, visual continuity, hybrid free/paid provider routing, cost control, production history, rights/provenance, publishing and analytics learning.

The initial business/content profile is child-directed media, but the core platform also supports general/adult-audience projects. Child-specific age and safety rules remain mandatory whenever a project is child-directed.

The repository is the canonical engineering/policy/history source during the current repository-first phase. Chat history and any individual provider history are secondary.

The normal operator command is `next`.

`next` does not always mean "write new content". It means inspect canonical project state and autonomously execute the highest-value safe next unit of work that is permitted by current policy and consent state.

## Compact durable resume layer

The canonical compact resume path is `ai-native/parallel/state/`.

On every start, `continue`, `next`, `resume`, interrupted session, tool failure, or message-delivery timeout, reconcile in this order before broad repository reading:

1. `ai-native/parallel/state/CURRENT-STATE.yaml`;
2. `ai-native/parallel/state/LAST-CHECKPOINT.md`;
3. exact current default/main branch and SHA;
4. accepted actionable OPEN Issues first;
5. accepted actionable OPEN PRs second;
6. active claims, merge/coordination queue, deterministic contract state, and `ai-native/parallel/state/RUNNER-BENCHMARK.yaml`;
7. only then read larger historical checkpoints when a specific fact or conflict requires them.

Compact state is a resume index only. It never overrides current repository/runtime evidence. Never repeat a merge, migration, provider call, deployment, destructive action, or other irreversible work merely because a previous user-facing message was not delivered.

Keep the compact layer bounded:
- `CURRENT-STATE.yaml` <= 12 KiB;
- `LAST-CHECKPOINT.md` <= 16 KiB;
- rolling `EXECUTION-JOURNAL.md` <= 32 KiB.

Before reporting a meaningful milestone as complete, blocked, verifying, or waiting, reconcile the compact state, rolling journal when a meaningful transition occurred, coordination queue when changed, and Runner Benchmark when changed. If durable state cannot be written, do not claim full completion.

## One operator turn = one logical milestone

By default, one operator `continue`/`resume` turn performs one bounded logical engineering milestone. Do not chain a broad audit, multiple unrelated implementations, repeated CI polling, merge, post-merge audit, and unrelated next task into one turn.

Security/incident work may contain tightly coupled actions only when splitting them would reduce safety.

## Remote-call and CI budget

Batch related read-only calls where supported and read only evidence required for the active milestone. Perform at most one consolidated CI/status refresh per milestone by default. Never tight-poll workflows, deployments, providers, or status endpoints, and never rerun a workflow merely because a chat/UI response timed out.

Before final exact-head CI observation, persist the milestone as `VERIFYING` or `WAITING_EXTERNAL` when remote checks are expected. If required CI is still running after the consolidated refresh, do not create another source commit solely to record that CI is pending. Record run IDs on the PR/Issue status surface when possible and end the milestone. A second same-turn refresh is allowed only after a material security/merge/incident/provider transition that makes it necessary for a safe decision; record the exception durably.

## Runner Benchmark

`ai-native/parallel/state/RUNNER-BENCHMARK.yaml` is the machine-readable registry for material remote/container/browser/runtime/full-regression/performance workloads.

Each runner task records a stable task ID, source Issue/PR/work package, command/workflow, exact source identity, environment/matrix/input/fixture identity, authorization state, security-critical and merge-blocking classification, expected runner time, deterministic dedup key, status, and immutable terminal evidence when available.

Runner registration never grants execution authority. Consumed, expired, historical, destructive, provider, production, deployment, release, or formal-runtime authority must never be inferred or silently reused.

## Mandatory user-facing engineering footer

Every engineering status/completion response must include all three of these evidence-based lines:
- repository name;
- current module progress bar and percentage;
- overall roadmap progress bar and percentage.

Progress must come from repository-defined lifecycle/milestone evidence, not conversational guessing. The default overall roadmap denominator is M0-M15 (16 milestones); a milestone counts as accepted only when its required acceptance/governance gates are satisfied. If a percentage cannot be supported, report the bar as `unknown` rather than inventing a number.

## Mandatory README progress reconciliation

The root README `Live development progress` section is the mandatory human-visible progress surface.

On every engineering start/resume/continue, and again before the final engineering response:

1. compare the README progress snapshot with exact live repository truth;
2. verify exact main SHA, active/open PRs and Issues, current module/status, evidence-based module percentage, accepted roadmap count/percentage, genuine blockers, and exact next action;
3. update README in the same integration cycle when the **material progress surface** changes: accepted milestone/governance state, active blocker/Issue, current module/status/percentage, accepted roadmap count/percentage, or exact next product action;
4. exact main/PR state is always verified live, but a README/progress bookkeeping PR does not require a second README-only PR merely to record the merge SHA or its own closure;
5. if repository work is already being submitted, the README progress delta is part of that same bounded branch/PR rather than a later cleanup task;
6. if the turn is strictly read-only and no material progress-surface fact changed, verify the snapshot as unchanged and do not manufacture percentage movement or a timestamp-only commit;
7. historical README tables never override this live snapshot or repository/runtime evidence.

A stale README progress snapshot is a reconciliation defect. Do not report a changed milestone/progress state as fully reconciled while knowingly leaving the README dashboard stale.

## Mandatory startup sequence

Before doing project work:

1. Read `README.md`, including `Current agent working instructions`.
2. Read `AGENTS.md`.
3. Read `ai-native/DEVELOPMENT-CONSENT-GATE.md`.
4. Read `ai-native/ENGINEERING-CONTRACT.md`.
5. Read `ai-native/MASTER-PLAN.md`.
6. For development/maintenance work, read `ai-native/parallel/MULTI-AGENT-PROTOCOL.md` and the relevant registries under `ai-native/parallel/`.
7. Read `docs/architecture/DEVELOPMENT-PLAN.md` when development is relevant.
8. Read `docs/architecture/TECH-STACK.md` when architecture/code is relevant.
9. Read `config/project-taxonomy.yaml`.
10. Read `config/execution-policy.yaml`.
11. Read `config/content-policy.yaml` for child/content-policy work.
12. Read `config/provider-registry.yaml`.
13. Read `config/update-policy.yaml` when provider research/self-update is relevant.
14. Read `ai-native/SYSTEM.md` and `ai-native/WORKFLOW.md` where applicable.
15. Read `ai-native/QUALITY-GATES.md` and `ai-native/MEMORY-BANK.md`.
16. Read `ai-native/AUDIO-ROUTER.md` when audio is relevant.
17. Read `ai-native/VIDEO-CONTINUITY.md` when visual/video work is relevant.
18. Read `ai-native/FREE-TIER-ROUTER.md` when provider routing/cost is relevant.
19. Read product docs for character/timeline/project-option work.
20. Read all machine-readable state/ledger files required for the current job.
21. Inspect current implementation, tests and recent relevant Git/PR history.
22. Determine the first incomplete or highest-value eligible job.
23. Perform the mandatory working-instruction audit below.
24. Before crossing from planning into executable development, verify that explicit operator consent exists for the exact development scope.

Never rely only on chat memory when repository/runtime state exists.

## Mandatory working-instruction audit

Every agent must perform this audit on every start or resume, including when the operator only says `continue`, `next`, or `resume`.

For development/maintenance work, compare the current repository state against the instructions under which the task previously operated. Check at minimum:
- this file and the root README summary;
- engineering and consent rules;
- `ai-native/parallel/MULTI-AGENT-PROTOCOL.md`;
- module ownership and active work claims;
- dependency graph and public contract ownership;
- shared-file rules;
- migration reservation when schema/data work is possible;
- relevant milestone/architecture docs;
- current main/branch/PR/checkpoint evidence.

The agent must determine whether the instructions it should follow have materially changed.

If a material instruction change exists:
1. update the affected canonical instruction/registry/task record before proceeding where permitted;
2. re-evaluate scope, owned paths, dependencies, migration reservation, contracts, required checks and consent;
3. stop or re-plan if the active assignment is no longer valid;
4. ensure the root README `Current agent working instructions` summary is updated in the same integration cycle;
5. record what changed and why in the relevant PR/checkpoint/integration record.

If there is no material change, do not churn README just to refresh a timestamp. Continue using the verified current instructions.

The README is a concise human-visible summary; canonical detailed rules remain in `AGENTS.md`, engineering/consent docs, and `ai-native/parallel/`.

## Parallel agent coordination

Parallel development is governed by `ai-native/parallel/MULTI-AGENT-PROTOCOL.md`.

Core rules:
- an agent may read the whole repository but may write only its claimed paths;
- task branches are named for work packages, not AI/model identity;
- overlapping active write claims are blocked until Integration Agent resolution;
- shared files and generated artifacts are centrally coordinated unless explicitly granted;
- migration identifiers are reserved before creation;
- consumers depend on stable public contracts rather than another agent's private implementation;
- every task pins an exact base commit when executable work starts;
- exact-head promotion CI remains required where repository policy requires it;
- parallel readiness never bypasses development consent.

## Mandatory development consent gate

`ai-native/DEVELOPMENT-CONSENT-GATE.md` is authoritative.

Research, audit, planning, architecture analysis and non-executable documentation may continue without development consent.

Executable development must not begin or resume until the operator explicitly approves a scoped Development Consent Brief.

A generic `continue`, `next`, `resume` or similar command is not development consent unless the operator explicitly authorizes implementation/code development.

When the next meaningful action is executable development and approval has not been given:

1. finish the planning/audit needed to define the scope;
2. prepare the Development Consent Brief required by the consent-gate document;
3. set/describe project state as `PLANNING_READY_FOR_CONSENT` where appropriate;
4. stop before implementation;
5. ask the operator for explicit consent.

Do not interpret prior consent for one milestone as blanket authorization for later milestones or materially expanded scope.

## Product model invariants

### Project configuration

Keep these dimensions separate:
- audience class;
- cast age composition;
- cast gender composition;
- character source/reuse strategy;
- content format;
- creative treatment/genre;
- duration;
- language;
- visual/camera/audio controls;
- pacing/rhythm;
- provider/cost policy;
- review/publishing policy.

Do not store `kids`, `adult`, `man`, `woman`, `both` as one ambiguous enum.

### Character/entity continuity

Recurring characters must be selected from a canonical library or created and locked before recurring use.

Never silently change a locked identity. Use versioned character/look/scene-state records.

Provider-specific reference IDs are derived implementation details, not the canonical identity.

### Timeline hierarchy

Long-form media uses:

`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take`

Provider clip limits do not define artistic shot duration or project duration.

Supported product duration is registry-driven, currently from 60 seconds up to 10,800 seconds (3 hours).

Long-form output is built through resumable shot jobs and deterministic assembly, not one giant model call.

## `next` contract

A normal `next` run must:
- load canonical repository/runtime state;
- detect incomplete, blocked, failed and ready jobs;
- choose the highest-value eligible job;
- refresh research/provider facts if stale and material;
- preserve idempotency and job history;
- execute only within safety, rights, licensing, cost and consent policy;
- route across free or paid providers using execution policy when that production scope is authorized;
- run mandatory QA;
- save canonical artifacts/manifests only after relevant gates pass;
- record rejected attempts as history;
- update state atomically;
- summarize completed work, remaining work and genuine blocks.

If the next job is executable development and no matching development consent exists, `next` must prepare the development brief and stop at the consent gate rather than implement.

If no production item is in progress, `next` may begin a content/project planning cycle according to project settings and portfolio policy, subject to consent whenever executable development is involved.

## Non-negotiable rules

### Audience/safety

When a project is child-directed, use configured age bands and child-safety/content policy. Never treat ages 0–12 as one audience.

For baby audio, design for parent-controlled listening rather than encouraging infant screen engagement.

General/adult-audience support does not disable universal safety, rights, platform or consent requirements.

### Originality

Do not copy, closely imitate or intentionally evoke protected songs, recordings, branded characters, celebrity voices, distinctive fictional universes, lyrics, melodies, plots or catchphrases.

A public-domain concept is not permission to copy a modern recording/arrangement.

### Memory before creation

Never create final canonical content before checking relevant memory/originality state. If state is corrupt or unavailable, repair/reconcile it before approval.

### Provider independence

No provider is the system of record. Switching provider must not reset project, content, audio, character, shot, timeline, continuity, cost, rights or QA history.

### Free + paid hybrid policy

Both free and paid providers may be used. Default mode is `HYBRID_SMART` unless configuration changes it.

- legitimate free capacity should be used when capability, quality, continuity and license are sufficient;
- free consumer web credits are not automatically free API capacity;
- manual-free provider handoffs are explicit jobs;
- paid calls occur only inside configured authorization/budget policy;
- never create/rotate accounts to evade quotas;
- never automate a provider contrary to terms;
- do not accept lower-quality output merely because it was free;
- optimize expected accepted-output cost, including retry/manual-labor risk.

### Audio architecture

Speech, music, dialogue and narration-with-background are distinct routes.

- speech -> speech/TTS provider;
- full song -> capable music model;
- narration + background -> separate voice + music stems then deterministic mix;
- dialogue -> versioned character voice assignments and scene timing;
- SFX/ambience -> independent assets/tracks where appropriate.

The AI may infer music/audio direction unless the operator/project overrides it.

### Visual continuity

Never assume different video providers share hidden generation state.

Use storyboard/timeline + canonical characters/entities + keyframes/references + scene/shot state + continuity QA.

### No mass-generation shortcut

Do not optimize output count at the expense of originality, coherence, continuity, rights, safety or platform quality.

## Engineering contract

All implementation/maintenance work must follow `ai-native/ENGINEERING-CONTRACT.md` and the development consent gate.

This includes architecture-first work, impact analysis, current official-source research when material, security, risk-based testing, durable workflows, provider abstraction, data/media integrity, provenance, observability, controlled dependencies, checkpoints and honest completion status.

## Daily provider self-update governance

The daily scout is controlled by:
- `.github/workflows/provider-scout.yml`;
- `automation/provider_scout.py`;
- `config/update-policy.yaml`;
- `config/provider-sources.json`.

It may auto-merge only permitted low-risk Class A/B changes after validation and repository rules, and only when those changes are explicitly classified as non-development under `ai-native/DEVELOPMENT-CONSENT-GATE.md`.

It must not blindly self-merge:
- new provider integrations;
- executable code changes;
- schemas/migrations;
- security/auth changes;
- budget behavior;
- publishing behavior;
- destructive changes.

A newly discovered provider starts disabled/evaluation-only until adapter, tests, license and capability validation exist and any required development consent has been granted.

## Lifecycle/history

Content/project lifecycle may progress through planning, writing, audio, storyboard, keyframes, shots, assembly, QA, publishing and analytics states. Do not mark a stage complete unless its gate actually passed.

Record successful and rejected attempts with relevant:
- run/job/project/content/asset/scene/shot/take IDs;
- provider/model;
- access tier;
- prompt version/hash;
- input/output hashes;
- generation ID;
- QA scores;
- rejection reason;
- quota/cost;
- rights/provenance;
- timestamps.

Failed history is valuable and must not be discarded merely because the asset was rejected.

## Change discipline

- Prefer additive, backwards-compatible changes.
- Version schemas, prompts and locked entities.
- Keep policies, prompts, research, machine state and automation code separated.
- Never commit secrets.
- Use deterministic IDs/checksums.
- Do not overwrite the only canonical approved asset/version.
- Do not silently weaken safety, licensing, cost, review or consent controls.

## Human escalation

Human/independent approval remains required when configured or materially necessary, especially for:
- any executable development scope not already explicitly approved;
- public publishing until policy explicitly enables otherwise;
- paid use without configured authorization/caps;
- destructive deletion of canonical history/assets;
- weakening child-safety or security controls;
- changing locked canonical character/brand identity;
- unresolved commercial-use/consent/license state;
- Class C/D automated self-update changes.

Routine research, planning, audits, non-executable documentation and analysis may proceed without unnecessary per-step questions. Executable implementation may proceed only inside an explicitly approved development scope.
