# AI Evaluation and Regression Framework

## Status

`PREDEVELOPMENT_READY`

## Purpose

AI behavior is versioned software behavior. Model, prompt, retrieval, provider, routing or policy changes must not be promoted on subjective impressions alone.

This framework defines offline evaluation, adversarial testing, canary promotion, regression detection and rollback for the AI-native platform.

## Evaluation layers

### Layer 1 — Deterministic contract validation
- schema validity;
- required fields;
- canonical IDs;
- duration/format constraints;
- entitlement/budget/policy compliance;
- forbidden action attempts;
- idempotency invariants.

### Layer 2 — Task quality evaluation
Domain-specific rubric scores for:
- research quality/source grounding;
- concept originality;
- script/story quality;
- age/audience fit;
- character consistency;
- visual prompt/shot quality;
- continuity reasoning;
- audio/music direction;
- provider routing;
- social metadata adaptation;
- localization/dubbing;
- analytics hypothesis quality.

### Layer 3 — Safety/security evaluation
- prompt injection resistance;
- indirect injection;
- excessive agency;
- secret/data leakage;
- cross-tenant access attempts;
- harmful/rights-sensitive outputs;
- memory poisoning;
- tool misuse;
- unbounded resource/spend behavior.

### Layer 4 — End-to-end production evaluation
Representative projects execute against fake/sandbox providers to evaluate:
- planning completeness;
- workflow recovery;
- regeneration scope;
- continuity state;
- cost estimation;
- approvals;
- final manifests;
- publication package quality.

### Layer 5 — Online canary/production monitoring
Only after offline gates pass:
- limited traffic/workspaces;
- bounded spend;
- no expansion of permissions;
- compare acceptance, retry, cost, latency and human override rates;
- automatic rollback when hard thresholds breach.

## Version identity

Every evaluated AI behavior identifies:
- `agent_version`
- `prompt_version`
- `model/provider/version`
- `retrieval_policy_version`
- `tool_contract_version`
- `policy_profile_version`
- `evaluation_suite_version`
- relevant feature flags/config snapshot.

No result is reported as a generic “model score” without its stack identity.

## Dataset classes

### Golden fixtures
Stable representative cases with expected invariants and rubric targets.

Required golden suites:
- project wizard normalization;
- kids preschool song concept;
- general-audience story;
- 2-minute song pipeline;
- 10-minute storyboard;
- 90-minute movie plan;
- character lock/reference pack;
- cross-provider shot handoff;
- audio plan;
- localization case;
- publishing package adaptation;
- analytics-to-memory hypothesis.

### Failure regression fixtures
Real or synthetic examples for known past failures:
- face/wardrobe drift;
- malformed provider response;
- hallucinated capability;
- duplicate content concept;
- over-budget fallback;
- partial job duplication;
- bad subtitles/lip-sync timing;
- wrong audience metadata;
- social duplicate publish;
- stale API assumption.

A fixed bug adds a regression fixture when practical.

### Adversarial fixtures
Cover threat-model scenarios:
- direct/indirect prompt injection;
- malicious web page/doc/comment/image text;
- fake tool result;
- poisoned memory;
- cross-tenant ID;
- secret exfiltration request;
- “ignore approval” request;
- recursion/runaway retry;
- malicious metadata/caption.

### Human-preference evaluation set
Pairwise/ranked examples for subjective creative quality. Human preference must not override hard safety/rights/contract failures.

## Rubric model

Each rubric dimension declares:
- description;
- scale;
- hard minimum or informational threshold;
- evaluator type (`DETERMINISTIC | MODEL_JUDGE | HUMAN | HYBRID`);
- evidence required;
- confidence requirements.

Do not use one LLM judge score as sole release authority.

## Core metrics

### Quality
- task pass rate;
- hard-failure rate;
- rubric mean/percentile;
- human preference win rate;
- human override rate;
- regeneration rate;
- continuity acceptance rate;
- originality collision rate.

### Reliability
- valid structured-output rate;
- tool-call validation failure;
- workflow completion rate;
- retry count;
- duplicate side-effect rate (target zero);
- recovery success.

### Cost/performance
- accepted-output cost;
- cost per completed project/shot/minute;
- token/input/output usage;
- provider attempts per accepted asset;
- latency percentiles;
- queue time.

### Security/safety
- injection attack success rate (target zero for privileged escalation);
- unauthorized tool attempt block rate;
- cross-tenant leakage (target zero);
- secret leakage (target zero);
- policy hard-failure escape rate (target zero);
- excessive-agency escape rate (target zero).

## Model-judge rules

Model judges are allowed for semantic/creative scoring when:
- judge prompt/version is pinned;
- the judge does not evaluate its own output where avoidable;
- deterministic facts are checked separately;
- bias/variance is measured on a human-labeled calibration set;
- disagreements can route to human review;
- judge output includes rationale/evidence references in internal evaluation records.

## Promotion process

Proposed change examples:
- new model;
- new provider;
- prompt update;
- retrieval policy;
- temperature/generation parameters;
- agent logic;
- memory ranking;
- routing scoring.

Promotion sequence:

`Candidate -> Static/Contract Tests -> Golden Suite -> Failure/Adversarial Suite -> Cost Benchmark -> Human Review if required -> Canary -> Promote`

## Hard release gates

A candidate cannot promote when:
- a previously passing hard safety/security fixture fails;
- cross-tenant/secret leakage appears;
- idempotency/duplicate side effects regress;
- rights/content hard policy escapes;
- required structured contracts fail above defined tolerance;
- accepted-output cost exceeds configured release threshold without explicit business approval;
- critical continuity/project invariants regress.

## Relative quality gates

For subjective quality, define per-agent minimums and no-regression bands. Example policy:
- candidate must not reduce critical rubric dimensions by more than configured tolerance;
- cost/latency improvement cannot compensate for hard-quality failure;
- improvement in one content type does not justify degradation in another without scoped routing.

Exact numeric thresholds are set from baseline data before implementation/launch and versioned with the suite.

## Canary design

Canary rules:
- only eligible non-critical traffic initially;
- small bounded percentage/workspace allowlist;
- separate metrics by old/new stack;
- provider spend cap;
- no new privilege scope through canary;
- automatic stop conditions;
- rollback preserves project canonical state.

## Rollback

Every promoted AI stack retains:
- prior known-good version;
- prompt/config artifacts;
- routing compatibility;
- schema compatibility notes;
- rollback command/playbook.

If a provider/model disappears, rollback may mean route to another approved stack rather than an unavailable exact version.

## Evaluation data governance

Evaluation datasets store only necessary data. Rules:
- synthetic fixtures preferred for security/tenant cases;
- production examples require privacy/rights eligibility and redaction;
- no raw provider secrets;
- user content inclusion follows consent/data policy;
- retention/classification defined;
- adversarial fixtures clearly isolated from production memory.

## Continuous learning boundary

Production analytics can propose hypotheses/candidates but cannot silently change prompts/models/policies. Learning loop:

`Observe -> Hypothesis -> Candidate change -> Offline evaluation -> Approval/promotion -> Canary -> Production`

This prevents self-reinforcing autonomous drift.

## Required reports

Each evaluation run produces:
- candidate/baseline identities;
- suite/version;
- environment;
- result summary;
- hard failures;
- quality deltas;
- cost/latency deltas;
- security results;
- human-review results;
- recommendation (`REJECT | HOLD | CANARY | PROMOTE`);
- artifact links.

## Acceptance criteria

This pack is planning-complete when every AI/model/prompt/provider change has a defined:
- evaluation identity;
- dataset class;
- rubric/metric path;
- hard gate;
- promotion/canary process;
- rollback behavior;
- data-governance boundary.
