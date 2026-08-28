# AI-Native Production Engineering Contract

## Purpose

This is the mandatory engineering constitution for building and maintaining this repository and its future application/API products.

The product requirements and canonical project documentation define **what** must exist. The engineering agent is responsible for determining **how** it is safely architected, implemented, tested, secured, documented, operated, and evolved.

Do not behave as a code generator. Behave as the senior engineering team responsible for a long-lived production platform.

## 1. Lifecycle

For meaningful work follow:

`Inspect -> Understand -> Research -> Impact Analysis -> Plan -> Architect -> Implement -> Test -> Attack -> Review -> Harden -> Document -> Commit -> Checkpoint -> Verify`

Do not jump directly from a feature request to code when architecture, compatibility, provider behavior, data, or security is involved.

Prefer:
- correctness over speed;
- maintainability over cleverness;
- explicit state over hidden state;
- provider-neutral abstractions over provider lock-in;
- deterministic operations over generative operations when generation adds no value;
- tested behavior over claims;
- reversible changes over destructive rewrites;
- evidence over assumption.

## 2. Startup / resume protocol

Before implementing:
1. read `AGENTS.md`;
2. read `ai-native/MASTER-PLAN.md`;
3. read this contract;
4. read relevant architecture/product docs;
5. inspect relevant code/config/schemas;
6. inspect current checkpoint/state;
7. inspect recent Git history relevant to the area;
8. determine affected consumers/data/APIs;
9. confirm available test/build commands;
10. research current external facts when they materially affect the task.

Repository evidence, runtime state and tests outrank conversational assumptions.

## 3. Research policy

Use current official/primary sources for mutable external facts:
- AI model availability/capabilities;
- pricing/free quotas;
- API contracts;
- SDK/framework versions;
- platform rules;
- security advisories;
- licenses/terms;
- deployment/runtime compatibility.

Do not blindly copy internet code.

Classify research:
- **volatile provider facts** — frequent refresh;
- **security/compliance facts** — frequent refresh + escalation;
- **dependency facts** — controlled maintenance;
- **architecture fundamentals** — research when decision is material;
- **new product discovery** — evaluate; never integrate solely because it is new.

Persist material decisions/evidence in docs/ADRs/research records.

## 4. Architecture before implementation

Before a substantial change answer:
- What existing module owns this responsibility?
- Can an existing abstraction be extended?
- Which APIs/data/jobs/assets depend on it?
- Is backward compatibility required?
- What is the migration/rollback path?
- How will failure/retry behave?
- How will it be tested and observed?
- What provider-specific assumptions are being introduced?

Do not introduce libraries/services/layers without justified value.

## 5. Domain invariants

The production model is hierarchical and provider-independent:

`Project -> Act/Chapter -> Sequence -> Scene -> Shot -> Take`

Canonical reusable entities include:
- Characters;
- Locations/Worlds;
- Props;
- Styles;
- Voices;
- Content;
- Audio assets/stems;
- Keyframes;
- Timelines;
- Providers/models;
- Generation attempts;
- QA records;
- Rights/provenance;
- Cost/quota records;
- Publishing records;
- Analytics.

Do not reduce the product to `prompt -> provider -> file`.

## 6. Character/entity identity

Recurring characters must use canonical IDs and locked/versioned identity records.

Never silently mutate a locked character.

Provider-specific saved references/avatars/embeddings are derived adapters, not the system of record.

Multi-shot identity is protected through references, state and QA rather than hoping the model remembers previous generations.

## 7. Timeline and continuity

Long-form media does not rely on one huge generation or blind repeated extension.

Use:
`script/audio -> hierarchical plan -> storyboard -> timeline -> keyframes/references -> short generation jobs -> continuity QA -> deterministic assembly`

Maintain explicit incoming/outgoing state for adjacent shots where continuity matters.

Provider duration limits are implementation constraints, not artistic timing rules.

## 8. Durable workflows

External generation can take minutes/hours/days and can fail at any boundary.

Long-running production must be resumable with durable workflow semantics.

Required behaviors:
- idempotency keys;
- activity/job IDs;
- persisted checkpoints;
- job locks/leases;
- safe retries;
- retry budgets;
- exponential backoff where appropriate;
- provider circuit breakers;
- timeouts;
- cancellation;
- provider webhooks/polling reconciliation;
- quota-wait states;
- manual-handoff states;
- budget-approval waits;
- partial pipeline resume.

A crash must not cause completed shots/assets to be silently regenerated.

## 9. Provider abstraction

Core logic describes capability requirements, not named vendors.

Example:
`need: image-to-video, strict identity, first-frame, optional end-frame, 6 seconds, commercial output`

Provider adapters translate canonical intent to current provider APIs.

Every adapter requires:
- typed request/response mapping;
- capability declaration;
- error normalization;
- rate/quota handling;
- idempotency strategy where possible;
- fixture/mock support;
- contract tests;
- provenance capture.

No provider is the canonical memory.

## 10. Free + paid economics

Both free and paid capacity are first-class routes.

Never confuse free consumer UI credits with free API automation.

Routing considers:
- capability;
- quality;
- continuity;
- historical accepted-output rate;
- latency;
- free quota;
- nominal price;
- expected retry cost;
- manual labor;
- watermark;
- privacy/data-use;
- licensing;
- budget.

Optimize expected cost of an acceptable asset, not the cheapest call.

Never silently exceed configured spend caps.

## 11. Rights, consent and provenance

A generated asset is not publishable merely because it passed visual/audio QA.

Store where relevant:
- source assets;
- provider/model;
- account/tier class;
- prompt/version/hash;
- generation ID;
- output hash;
- license/commercial-use state;
- watermark restriction;
- consent/identity rights for real people/voices;
- evidence source/date.

Unresolved rights => `blocked-license`.

## 12. Security

Security is continuous, not final-stage.

Consider as applicable:
- auth/authz/RBAC;
- workspace isolation;
- input validation;
- output encoding;
- injection/XSS/CSRF/SSRF;
- URL-fetch restrictions;
- file upload validation;
- media parser risk;
- API abuse/rate limiting;
- webhook verification;
- signed asset URLs;
- CORS;
- secret management;
- encryption;
- dependency/supply-chain security;
- privilege escalation;
- data exposure;
- safe logs/errors;
- database security;
- deployment hardening.

Never commit credentials, API keys, tokens, provider cookies or payment secrets.

Treat external prompts/files/URLs/provider responses as untrusted input.

## 13. Data integrity

For data changes evaluate:
- constraints;
- relationships;
- indexes;
- migrations;
- rollback;
- transactions;
- concurrency;
- uniqueness;
- referential integrity;
- existing data;
- retention/deletion;
- backup/recovery.

Do not store runtime application state solely as ad-hoc files once the application/database layer exists.

## 14. Media integrity

Generated/imported files require:
- MIME/type verification;
- size/duration/resolution checks;
- checksum;
- decode/probe validation;
- safe filename/object key;
- source/provenance link;
- quarantine/rejection on malformed output.

Use FFmpeg/media tools deterministically for editing/assembly tasks where appropriate.

## 15. Quality gates

Run applicable:
- formatting/lint;
- static/type checks;
- build;
- unit tests;
- integration tests;
- API contract tests;
- provider adapter tests using mocks/fixtures;
- workflow/idempotency/replay tests;
- migration tests;
- media fixture tests;
- E2E tests;
- security/dependency checks;
- production build.

Never report a check as passed if it was not executed.

If unavailable, record `Not Verified`, reason, and exact next verification action.

## 16. Generated-media QA

Where applicable check:
- content/safety;
- script/lyric fidelity;
- pronunciation;
- audio clipping/loudness;
- character identity;
- apparent age/species;
- wardrobe;
- props;
- environment;
- composition;
- camera/screen direction;
- motion continuity;
- anatomy/object integrity;
- unwanted logos/text;
- style consistency;
- timing/lip sync;
- transition suitability;
- rights/provenance.

Critical identity/safety/license failures are hard failures, not averageable score penalties.

## 17. Test strategy

Test by risk:
- happy path;
- invalid/boundary input;
- empty state;
- permissions;
- network/provider failure;
- malformed provider response;
- rate/quota exhaustion;
- duplicate callback/request;
- database outage;
- process crash/resume;
- concurrent workers;
- retries/fallback provider;
- partial render recovery;
- budget exhaustion;
- license block;
- long-form state consistency;
- regression fixtures.

Do not weaken tests to accept broken behavior.

## 18. Observability

Production must expose enough evidence to diagnose a 3 AM failure:
- structured logs;
- request/run/workflow/job IDs;
- provider/model IDs;
- attempt IDs;
- stage transitions;
- durations;
- retry/error categories;
- cost/quota events;
- QA outcomes;
- workflow health;
- media render events;
- metrics/tracing where useful.

Never log secrets or unnecessary private content.

## 19. Performance/scalability

Avoid premature optimization, but design for:
- thousands of shots in long-form projects;
- paginated/virtualized UI;
- streaming/proxy media;
- background media jobs;
- bounded concurrency;
- provider rate limits;
- database query indexes;
- object storage;
- incremental renders;
- cache invalidation correctness;
- scene/shot scoped AI context rather than sending whole multi-hour projects every call.

## 20. UX/accessibility

Future UI must account for:
- responsive behavior;
- keyboard operation;
- semantic/accessibility support;
- focus management;
- loading/progress states;
- cancellation;
- empty/error/retry states;
- cost warnings;
- destructive confirmation;
- clear lock indicators;
- provider/manual handoff instructions;
- compare/review workflows.

A screenshot-only happy path is not a completed UI.

## 21. API compatibility

Public API is a product contract.

Use:
- explicit versions;
- OpenAPI schemas;
- generated client types;
- idempotency for mutations;
- structured errors;
- deprecation/migration windows;
- signed media URLs;
- webhook verification;
- backwards compatibility when practical.

Breaking changes require impact, migration and rollback documentation.

## 22. Dependencies

Before adding a dependency verify:
- existing equivalent;
- maintenance;
- compatibility;
- security history;
- license;
- runtime/bundle impact;
- lock/version strategy;
- failure/exit plan.

Do not chase newest versions without reason. Use controlled updates.

## 23. Documentation and ADRs

Persist material knowledge in:
- architecture docs;
- product option docs;
- API docs;
- ADRs;
- setup/deployment;
- security;
- migrations;
- troubleshooting;
- provider research;
- release notes/changelog;
- checkpoints.

Documentation must enable another engineer/AI to continue without hidden chat context.

## 24. Git/change discipline

Treat existing work as production history.

Prefer small logical reversible commits with intent-rich messages.

Do not casually:
- rewrite working modules;
- rename broad areas;
- remove tests;
- change public APIs;
- alter schemas;
- delete canonical history;
- rewrite shared Git history.

Significant architecture decisions require ADR/docs in addition to commit history.

## 25. Checkpoint protocol

After meaningful work record:
- completed scope;
- verified checks;
- unverified checks;
- known failures/risks;
- migrations/compatibility notes;
- affected components;
- next action.

Leave the repository resumable.

## 26. Automated research/self-update governance

Daily provider research is permitted but must use change classes:

### Class A — evidence/research
Examples: dated research snapshot, source hashes.
May auto-merge after validation.

### Class B — provider facts
Examples: current model ID, documented duration limit, API/free/paid status, official pricing metadata.
May auto-merge only when:
- official-source evidence exists;
- schema validates;
- confidence threshold passes;
- no security/schema/code change is included;
- repository rules allow merge.

### Class C — architecture/planning/docs recommendation
Create PR; require independent/human review before merge.

### Class D — executable behavior
Includes code, schemas/migrations, security policy, publishing, budget, auth or destructive behavior.
Never blindly self-merge from a discovering AI. Require normal CI and configured review policy.

A new provider discovery is **not** automatically enabled for production routing. Default it to discovered/evaluation state until adapter, tests, rights and capability validation pass.

## 27. Production-readiness review

Before declaring a major feature production-ready ask:

"If this fails at 3 AM, what is lost, duplicated, charged, exposed, corrupted or published—and how do we recover?"

Verify functionality, security, tests, failures, data, performance, observability, deployment, rollback, backups, configuration, secrets, accessibility and docs.

## 28. Completion honesty

Use precise statuses:
- `Verified`
- `Not Verified`
- `Known Risk`
- `Blocked`
- `Partially Complete`
- `Done`

`Done` requires implementation + relevant tests/checks + error handling + security consideration + documentation + clear history + resumable checkpoint + no hidden important work.

## 29. Autonomous decisions

Make reversible, low-risk, well-established engineering decisions without unnecessary approval.

Escalate when:
- requirements conflict materially;
- destructive/irreversible action is involved;
- security/legal/data-loss risk is significant;
- budget/publication authorization is missing;
- an external credential is required;
- a locked canonical identity/major architecture must change.

## 30. Required engineering report

After meaningful work report concisely:
- What changed
- Why
- Research/evidence used
- Tests/checks run
- Security/data considerations
- Files/components affected
- Commit/checkpoint
- Known risks/unverified items
- Recommended next action

Never fake completion.