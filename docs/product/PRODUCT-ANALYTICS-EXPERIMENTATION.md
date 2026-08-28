# Product Analytics and Experimentation

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define first-party product analytics for AI Automation Force separately from social/content-performance analytics. The goal is to understand acquisition, activation, reliability, feature adoption, retention and UX without leaking sensitive project content into analytics systems.

## Principles

- operational/business events are canonical sources where possible;
- analytics schemas are versioned;
- minimize personal/private content;
- no raw prompts/media sent to generic analytics by default;
- user/workspace identifiers are pseudonymous where practical;
- product analytics never becomes authorization/billing source of truth;
- experiments cannot bypass security, rights, entitlement or approval rules;
- AI/product improvements require evaluation, not blind metric optimization.

## Analytics domains

### Acquisition
- landing page visit;
- source/referrer/campaign where consent permits;
- feature/pricing/docs views;
- signup initiated/completed;
- login method chosen;
- invite acceptance.

### Onboarding
- verification complete;
- workspace created;
- goal/content type selected;
- provider connection started/succeeded/skipped;
- budget/routing defaults set;
- first project started/completed;
- onboarding abandoned/resumed.

### Activation
Canonical activation milestones:
1. account verified;
2. workspace ready;
3. first project created;
4. first approved/generated asset produced;
5. first final render/export completed.

Secondary activation:
- first social account connected;
- first publication verified;
- first recurring character locked.

### Feature adoption
- project wizard usage;
- character library;
- image generation/edit/reuse;
- audio routes;
- storyboard;
- timeline;
- AI Command Center;
- provider routing/fallback;
- QA/approval;
- publishing;
- localization;
- mobile;
- developer API.

Track meaningful completion/outcome, not just button clicks.

### Reliability/production funnel
- project plan -> generation requested;
- generation request -> provider attempt;
- attempt -> accepted/rejected;
- retry/fallback;
- QA pass/fail;
- render success/fail;
- publish success/fail.

Break down by normalized error class and product version while protecting tenant privacy.

### Cost/value funnel
- credits/usage consumed;
- provider cost;
- accepted-output cost;
- project completion;
- paid conversion/retention where lawful.

Do not expose one customer’s financial details to unrelated analytics users.

### Retention
Measure cohort return/activity by:
- account/workspace;
- creator/team type;
- plan;
- activated feature sets;
- first completed content type.

Possible windows:
- D1/D7/D30;
- weekly/monthly active workspaces;
- project recurrence;
- publication recurrence.

## Canonical analytics event

Fields:
- `analytics_event_id`
- `event_name`
- `event_version`
- `occurred_at`
- pseudonymous user/workspace ID;
- session ID if consent/policy permits;
- project ID hashed/pseudonymous if needed;
- product release/version;
- platform (`web | mobile | api`);
- locale/timezone class;
- plan/entitlement cohort;
- experiment assignments;
- structured safe properties.

Never put arbitrary prompt/script/project title as property by default.

## Event naming examples

- `signup.completed.v1`
- `onboarding.provider_connected.v1`
- `project.created.v1`
- `project.first_asset_approved.v1`
- `generation.completed.v1`
- `generation.failed.v1`
- `render.completed.v1`
- `publish.verified.v1`
- `command_center.dry_run_completed.v1`
- `approval.resolved.v1`

When canonical domain event already exists, analytics projection can derive from it instead of duplicate client event.

## Client vs server events

### Server-authoritative
Use server events for:
- signup/account state;
- project creation;
- generation/job result;
- billing/entitlement;
- publication;
- approvals;
- durable activation milestones.

### Client UX events
Use client events only for interaction insights such as:
- screen/view;
- wizard step interaction;
- search/command palette usage;
- UI error/display;
- onboarding abandonment hints.

Critical business metrics should not rely solely on browser analytics blockers.

## Funnel definitions

### Signup funnel
`Landing -> Signup Start -> Account Created -> Email Verified/OAuth Complete -> Workspace Created`

### First-value funnel
`Workspace -> Project Created -> Plan/Storyboard Ready -> First Generation -> First Approved Asset -> Final Render`

### Publishing funnel
`Social Connected -> Publish Package Created -> Approved -> Scheduled/Requested -> Published Verified`

Each step has explicit canonical event and time window.

## Product health metrics

- activation rate;
- time to first project;
- time to first accepted asset;
- project completion rate;
- generation failure/retry rate;
- provider fallback success;
- render completion rate;
- publish verification rate;
- human override/approval delay;
- API/web/mobile latency/error experience;
- weekly/monthly active workspaces;
- retention/churn;
- paid conversion when billing enabled.

## AI-native metrics

- `next` command success/actionability;
- dry-run -> execute conversion;
- AI recommendation acceptance/override;
- originality collision prevention;
- continuity QA catch/false-positive proxy;
- provider-router accepted-output cost;
- model/prompt version quality outcomes;
- memory correction/forget events;
- AI decision explanation views.

These metrics feed hypotheses, not automatic production-policy mutation.

## Privacy/consent

Separate:
- essential operational telemetry;
- product analytics;
- public-site marketing analytics/advertising.

Depending jurisdiction/settings, consent manager gates non-essential analytics.

Privacy controls:
- IP minimization/truncation where feasible;
- no raw secrets/private prompts/media;
- configurable retention;
- user/account deletion propagation;
- workspace privacy-mode support for enterprise if later required.

## Data model/warehouse stance

Initial stage can store selected product analytics in PostgreSQL/analytics tables or a privacy-conscious product analytics service.

At scale, an analytics warehouse may be added.

Canonical event definitions remain vendor-neutral; switching Mixpanel/PostHog/Amplitude/warehouse must not require redefining product metrics.

No analytics vendor is selected as a mandatory architecture dependency at planning stage; self-hosted/privacy/cost requirements can choose implementation within this contract.

## Dashboards

### Executive/product
- acquisition;
- activation;
- retention;
- paid conversion;
- active workspaces/projects;
- completed outputs.

### Onboarding
- step conversion/dropoff;
- provider connection success;
- first-value timing.

### Production reliability
- failure classes;
- retry/fallback;
- provider success;
- render/publish outcomes.

### Feature adoption
- active users/workspaces per module;
- adoption cohorts;
- feature-to-retention correlations as hypotheses.

### AI quality/cost
- accepted-output cost;
- override rates;
- eval/production correlations;
- provider/model mix.

## Experiment framework

Experiment record:
- experiment ID;
- hypothesis;
- owner;
- eligible population;
- variants;
- primary metric;
- guardrail metrics;
- start/stop criteria;
- assignment unit (`user | workspace`);
- exposure event;
- analysis plan;
- result/decision.

## Assignment

Use deterministic stable assignment so users/workspaces do not randomly switch variants across sessions.

Workspace-level assignment preferred for collaborative workflow features to avoid team members seeing incompatible product behavior.

## Experiment guardrails

Experiments cannot alter:
- security protections;
- tenant isolation;
- legal/rights gates;
- public publishing approval below minimum policy;
- billing accuracy;
- data deletion semantics;
- safety hard blocks.

Experiments affecting AI behavior also follow AI evaluation/canary framework.

## Experiment examples

Allowed examples:
- onboarding wizard copy/layout;
- default storyboard presentation;
- AI Command Center suggestion placement;
- optional provider recommendation UI;
- landing CTA.

Higher-risk AI routing experiments require offline evaluation and bounded canary, not ordinary UI A/B only.

## Feature flags vs experiments

- release flag = rollout/control;
- experiment flag = randomized/stable measurement;
- entitlement = contractual access;
- permission = authority.

Do not mix these concepts into one boolean system.

## Statistical/reporting stance

Predefine:
- primary metric before start;
- minimum sample/time where feasible;
- confidence/uncertainty reported;
- avoid repeated peeking/metric fishing;
- practical effect size considered, not only statistical significance;
- segmentation after the fact treated as exploratory.

Exact statistical technique may vary by experiment type but must be documented in result.

## Product feedback

Qualitative feedback sources:
- in-app feedback;
- support cases;
- rejection/override reasons;
- optional exit/cancel survey.

Do not treat support anecdotes as quantitative truth; link them as research evidence/hypotheses.

## Data quality

Monitor:
- schema validation;
- event duplicate rate;
- missing server events;
- client/server timestamp skew;
- late events;
- experiment assignment mismatches;
- analytics vendor delivery failures.

## Retention

Raw event retention should be finite and policy-driven; derived aggregates can persist longer if privacy-compatible.

Deletion/account lifecycle propagates according to Data Privacy spec.

## Testing

- canonical funnel event fires exactly once/idempotently where required;
- tenant-sensitive properties not exported;
- consent blocks marketing/product analytics where configured;
- server activation metrics work with client blockers;
- experiment assignment stable;
- guardrail/security cannot be experiment-disabled;
- deleted user excluded/anonymized according to policy;
- event version compatibility.

## Acceptance criteria

Implementation can determine:
- analytics domains/events;
- canonical funnels/activation;
- server vs client sources;
- AI/product health metrics;
- privacy/retention;
- dashboard structure;
- experiment assignment/guardrails;
- feature flag vs experiment vs entitlement distinction.
