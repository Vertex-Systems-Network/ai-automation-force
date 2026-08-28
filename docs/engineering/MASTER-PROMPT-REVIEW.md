# Master Engineering Prompt Review

## Verdict

The supplied `AI-Native Production Development — Master Engineering Prompt` is a strong general engineering baseline and should be retained as a policy layer, but it is not sufficient by itself for this media-production platform.

Its strongest qualities are:
- architecture before implementation;
- evidence-based research;
- preservation of existing work;
- security throughout the lifecycle;
- risk-based testing;
- explicit failure/resilience thinking;
- data integrity;
- observability;
- living documentation;
- repository-backed AI memory;
- meaningful Git history;
- checkpoint/resume protocols;
- change impact analysis;
- dependency discipline;
- production readiness review;
- no fake completion;
- autonomous low-risk decisions;
- explicit Definition of Done.

These principles remain mandatory.

## Gaps for this project

### 1. It is generic software-engineering guidance
It does not define this product's domain model:
- projects;
- acts/sequences/scenes/shots/takes;
- characters;
- locations/worlds;
- props;
- voices;
- audio stems;
- keyframes;
- timelines;
- providers;
- generation attempts;
- rights/provenance;
- costs/quotas;
- publishing;
- analytics.

These are now covered by the project architecture/docs and must be loaded with the engineering contract.

### 2. It does not define durable long-running execution
A three-hour film may involve thousands of external jobs and may pause for minutes, days, quota resets or human approvals.

The project therefore requires:
- durable workflows;
- idempotent activities;
- resumable checkpoints;
- job locks;
- retries with budgets;
- circuit breakers;
- partial pipeline recovery;
- provider webhooks/polling;
- cancellation/version semantics.

### 3. It does not define provider independence
AI providers must be replaceable. Core business logic must describe required capabilities rather than embedding Veo/Kling/Runway/Gemini-specific assumptions.

### 4. It does not define free/paid economics
Every external generation can have:
- free API quota;
- manual free web credits;
- paid API pricing;
- different success rates;
- different licensing;
- watermark/privacy implications;
- retry costs.

The system must optimize expected accepted-output cost under policy, not blindly choose cheapest nominal calls.

### 5. It does not define media continuity
Long-form production needs explicit character/world/camera/timeline state and reference/keyframe control. Chat memory or provider hidden state is not acceptable continuity infrastructure.

### 6. It does not define rights/provenance as a hard state
An asset can pass visual QA yet still be blocked from publication due to unresolved commercial rights, watermark restrictions or consent/provenance issues.

### 7. Internet research needs risk classification
The original instruction can be interpreted as researching too broadly or changing dependencies whenever new information appears.

For this project research should be classified:
- current provider/pricing/model facts: refresh frequently;
- security advisories: refresh frequently and escalate;
- stable architecture fundamentals: research when materially needed;
- dependencies: update through controlled maintenance;
- new AI products: discover daily but do not automatically integrate just because they are new.

### 8. Commit/checkpoint rules need automation awareness
Automated scouts should not make noisy commits when nothing material changed. Production artifacts/jobs should not use Git commits as the runtime transaction mechanism once the application database exists.

### 9. Automatic self-modification needs guardrails
An AI that researches a new API must not automatically rewrite security, schema, budget, publishing or architecture code and merge it without an independent gate.

Use change classes:
- Class A: research/evidence snapshots — safe auto-merge after validation;
- Class B: high-confidence provider registry facts — conditional auto-merge after schema/evidence validation;
- Class C: architecture/docs proposals — PR, human/independent review required;
- Class D: executable code/schema/security/budget/publishing behavior — PR with full CI + review, no blind autonomous merge.

## Redundancy in the supplied prompt

Several sections reinforce the same principle (verification, no fake completion, DoD, final verification, production readiness). This redundancy is helpful for human readability but expensive for repeated AI context.

Recommended implementation:
- preserve a human-readable full engineering constitution;
- maintain a shorter machine/agent startup contract that references the constitution;
- use schemas/checklists/tests to enforce rules instead of repeating every rule in every prompt.

## Project-specific additions required

The adapted engineering contract must add:
- repository/application source-of-truth rules;
- provider capability abstraction;
- durable workflow policy;
- character/entity locking;
- timeline hierarchy;
- media provenance;
- cost/quota policy;
- prompt/version registry;
- generated-asset QA;
- deterministic post-production;
- AI research/update governance;
- app/API compatibility rules;
- provider contract tests;
- media fixture tests;
- long-form scalability tests;
- public publishing gates;
- child-directed safety profile when applicable.

## Final use

Do not paste the long general prompt into every provider call.

Use it as the project's engineering constitution:
`ai-native/ENGINEERING-CONTRACT.md`

Then individual tasks load only the relevant project docs and concise task-specific prompt/context.

This reduces token waste while making the policy more enforceable and durable.