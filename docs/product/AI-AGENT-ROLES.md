# AI Agent Role Catalogue

## Purpose

Define the specialized AI responsibilities inside the platform. These are logical roles, not necessarily separate models/processes. One capable model may execute multiple roles, but role boundaries keep prompts, authority, inputs, outputs and QA auditable.

No role may silently bypass safety, rights, budget, locked-identity or development-consent policies.

## 1. Orchestrator / Production Manager

Owns:
- current project/workflow state;
- next eligible unit of work;
- dependency ordering;
- handoffs between specialized roles;
- block/retry/escalation decisions;
- checkpoint creation.

May not:
- rewrite approved creative assets without versioning;
- spend outside authorized policy;
- publish publicly without required gate.

Inputs: project state, jobs, policy, approvals, provider health.
Outputs: next job/task, reason, dependencies, status transitions.

## 2. Research Intelligence Agent

Owns:
- current/evergreen topic research;
- opportunity discovery;
- factual/background research;
- audience/platform research;
- provider capability research when specifically assigned.

Requirements:
- prefer primary/official evidence for mutable technical/platform facts;
- attach sources/date/confidence;
- distinguish fact from hypothesis.

## 3. Portfolio / Content Strategist

Owns:
- what should be created next;
- format selection when AI-controlled;
- portfolio balance;
- series/character reuse opportunity;
- fatigue/saturation avoidance;
- target objective.

Uses memory and analytics but may not clone successful prior work.

## 4. Originality / Memory Agent

Owns:
- exact/near duplicate detection;
- concept similarity;
- refrain/lyric overlap;
- plot/creative-device overlap;
- character/situation saturation;
- prior failed/rejected idea retrieval.

Outputs a clear decision plus closest prior references and differentiation requirements.

## 5. Writer / Script Agent

Owns:
- lyrics;
- poem/rhyme text;
- story/script/screenplay;
- narration;
- dialogue;
- structural beats.

Must work from format bible, audience profile, locked canon and originality decision.

Approved text becomes versioned canonical source for downstream production.

## 6. Story Editor

Owns:
- coherence;
- pacing at narrative level;
- character motivation;
- scene purpose;
- redundant beats;
- age/audience appropriateness;
- ending/payoff quality.

Does not silently replace approved text; proposes a new version when material edits are needed.

## 7. Casting / Character Director

Owns:
- selecting existing vs new characters;
- recommending cast composition;
- assigning character versions/looks;
- preserving canonical identity;
- mapping voices to characters;
- flagging rights/consent gaps.

Locked character changes require versioning and applicable approval.

## 8. Visual Director / Art Director

Owns:
- visual medium;
- art/style profile;
- palette;
- production design;
- world/location treatment;
- lighting language;
- composition rules;
- consistency rules;
- negative visual constraints.

Outputs provider-neutral visual direction, not vendor-specific prompt fragments only.

## 9. Cinematography Agent

Owns per scene/shot:
- framing/shot size;
- lens/perspective intent;
- camera height/angle;
- camera motion;
- blocking/eyeline/screen direction;
- depth/focus intent;
- coverage requirements.

Must prioritize editorial continuity over novelty.

## 10. Storyboard / Shot Planner

Converts script/audio into:
- scenes;
- shots;
- shot timing;
- action;
- characters/location/props;
- first/mid/end keyframes;
- transitions;
- coverage;
- continuity state.

Does not call video providers directly unless operating under an approved generation job.

## 11. Music Director

Owns:
- whether music is required;
- genre/mood;
- BPM/tempo;
- key/scale where useful;
- instrumentation;
- song structure;
- energy curve;
- singer profile;
- instrumental bed behavior;
- transitions/stings.

For songs it compiles provider-neutral music intent plus exact approved lyrics.

## 12. Voice / Dialogue Director

Owns:
- narrator selection;
- character voice assignments;
- delivery style;
- pace;
- emotion;
- pronunciation;
- pauses;
- multi-speaker timing;
- lip-sync timing metadata.

Real-person impersonation or unauthorized cloning is not permitted.

## 13. Sound Designer

Owns:
- ambience;
- Foley/SFX;
- transitions;
- room/environment bed;
- sound motif;
- event synchronization;
- silence decisions.

Maintains independent assets/stems where practical.

## 14. Provider Router

Owns:
- capability matching;
- free/paid/manual route selection;
- quality/continuity/history weighting;
- quota/cost/license constraints;
- fallback chain.

It optimizes expected accepted-output cost/quality, not lowest nominal price.

Provider Router cannot override hard budget, rights or safety blocks.

## 15. Prompt Compiler

Translates canonical intent into provider/model-specific request format.

Inputs:
- canonical creative state;
- provider capability contract;
- prompt template/version;
- references/keyframes;
- negative constraints.

Outputs:
- versioned provider request;
- parameter map;
- prompt hash;
- expected output contract.

Provider-specific prompt is derived state, not canonical project memory.

## 16. Generation Supervisor

Owns execution attempt lifecycle:
- submit;
- poll/webhook reconcile;
- receive output;
- validate media payload;
- record cost/quota;
- attach provenance;
- send to QA.

It never marks a returned file canonical merely because the API succeeded.

## 17. Continuity Agent

Owns comparison against:
- locked characters/looks;
- prior/next shot state;
- world/location/props;
- lighting/style;
- camera/screen direction;
- movement/end frame.

Outputs hard-fail decisions and scored secondary dimensions.

## 18. Media QA Agent

Owns generated media quality checks:
- malformed anatomy/objects;
- unwanted text/logo;
- visual artifacts;
- audio clipping/noise;
- lyric/script fidelity;
- timing/lip sync;
- safety;
- content-policy fit.

QA dimensions are specialized by asset type.

## 19. Editor / Post-Production Planner

Owns:
- chosen takes;
- cut points;
- J/L cuts;
- transitions;
- B-roll use;
- music/voice/SFX timeline;
- captions/graphics;
- render plan.

Deterministic execution should use FFmpeg/OTIO rather than generative reinvention.

## 20. Rights / Provenance Agent

Owns:
- provider terms evidence;
- commercial-use state;
- source asset ownership;
- real-person consent records;
- watermark/publication restrictions;
- asset lineage completeness.

Unresolved material rights issue => publication block.

## 21. Budget / Cost Controller

Owns:
- project/run/shot budget availability;
- estimated retry-adjusted cost;
- reservation/reconciliation;
- free-credit usage;
- overspend prevention;
- provider cost history.

Does not authorize budgets; it enforces configured authorization.

## 22. Publishing Agent

Owns:
- title/description/metadata;
- thumbnail brief;
- captions;
- audience flags;
- synthetic-media review;
- private upload;
- scheduling/publication after approvals.

Public publishing remains gated by policy.

## 23. Analytics / Learning Agent

Owns:
- performance ingestion;
- cohort comparison;
- retention/CTR patterns;
- character/format/pacing correlations;
- experiment hypotheses;
- portfolio feedback.

It learns patterns rather than instructing the Writer to duplicate existing winners.

## 24. Localization Director

Owns:
- language adaptation;
- lyrical meter/rhyme adaptation;
- cultural fit;
- voice/dubbing selection;
- subtitle/caption variants;
- translated metadata.

Each language variant maintains lineage to the canonical source.

## 25. Security / Safety Reviewer

Cross-cutting role that may block:
- unsafe child content;
- privacy violations;
- malicious/untrusted file/URL handling;
- unauthorized identity use;
- secret exposure;
- unsafe publishing behavior.

## Role arbitration

When role recommendations conflict:
1. hard safety/security/rights/budget rules win;
2. locked operator decisions win over AI preferences;
3. canonical approved project/character/content state wins over provider output;
4. Orchestrator resolves remaining scheduling conflicts;
5. material creative conflict is surfaced for review rather than silently choosing an irreversible path.

## AI autonomy levels

Suggested project-level presets:
- `ASSISTED` — AI suggests; operator approves major creative stages;
- `BALANCED` — AI autonomously handles routine decisions; operator reviews configured checkpoints;
- `HIGH_AUTONOMY` — AI executes all reversible production decisions within policy, with hard gates preserved;
- `CUSTOM` — per-role authority controls.

Autonomy never means bypassing locked identity, rights, security, budget or publication gates.

## Acceptance criteria

The role catalogue is implementation-ready when every future workflow activity can identify an owner role, required inputs, allowed decisions, resulting artifact/state and the policy that can block it.
