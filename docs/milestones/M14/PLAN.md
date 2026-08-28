# M14 — Long-Form Hardening to 3 Hours

## Objective

Prove and harden the complete platform for progressively larger 30/60/90/120/180-minute projects, including workflow history, scoped AI context, database/timeline performance, provider outages, quota waits, storage growth, cost caps, incremental renders and recovery.

## Entry criteria

- P0 complete.
- M01–M13 accepted.
- Explicit M14 consent.
- Representative providers/sandboxes and infrastructure capacity available.

## Dependencies

`M01–M13 -> M14`

## Work packages

### M14-WP1 — Long-form fixture and workload suite
Create canonical synthetic/controlled projects at:
- 30 minutes;
- 60 minutes;
- 90 minutes;
- 120 minutes;
- 180 minutes.

Include multi-act/sequence/scene hierarchy, recurring characters, audio, subtitles, multiple providers and publish variants without requiring every test to spend real provider credits.

### M14-WP2 — Workflow-history hardening
- Temporal workflow history size monitoring;
- continue-as-new/version patterns;
- child scene/sequence workflow partitioning;
- replay across releases;
- queue/fan-out control;
- cancellation/approval waits;
- recovery after worker/service restarts.

### M14-WP3 — AI context and memory scoping
- act/sequence/scene summaries;
- canonical continuity summaries;
- relevant-character/world retrieval;
- avoid placing entire 3-hour script/timeline in every prompt;
- retrieval provenance;
- context/token budgets;
- summary versioning/regression tests.

### M14-WP4 — Database/query/index performance
- hierarchy pagination;
- shot/take/asset history queries;
- timeline ranges;
- memory/vector lookup;
- approval/activity/audit queries;
- analytics queries;
- indexes/partitioning only where measured;
- connection pool/load tests.

### M14-WP5 — Web timeline virtualization and review scale
- thousands of shots/clips/assets;
- virtualized storyboard/timeline;
- proxy-first media;
- incremental loading;
- search/filter;
- navigation across acts/sequences;
- stable edit/conflict behavior;
- browser memory/interaction budgets.

### M14-WP6 — Provider outage/quota/cost resilience
Scenarios:
- provider unavailable mid-act;
- quota exhausted;
- one account disconnected;
- paid fallback approval;
- budget cap reached;
- long wait then resume;
- provider capability/model removed.

Canonical project resumes/switches without restarting completed work.

### M14-WP7 — Storage/archive and incremental rendering
- large asset counts/storage;
- proxy lifecycle;
- archive/restore older acts/takes;
- scene/sequence render cache;
- changed-shot invalidation;
- chunked final assembly;
- final master validation;
- export/backup impact.

### M14-WP8 — Performance/load/capacity
Measure:
- API latency under long-project queries;
- workflow queue lag;
- DB CPU/IO/connections;
- object storage/egress;
- FFmpeg CPU/disk;
- web memory/render time;
- provider concurrency;
- event/notification volume;
- cost estimation accuracy.

Define measured operating limits/alerts before production launch.

### M14-WP9 — Chaos/recovery and DR long-project scenarios
- kill workers during sequence generation;
- DB transient failover;
- storage timeout;
- event consumer outage;
- render worker OOM;
- deployment rollback while workflows active;
- restore/reconcile representative long project from backup.

Verify no duplicate accepted assets/cost/publications.

### M14-WP10 — 180-minute acceptance and limits publication
Acceptance uses a controlled 180-minute project plan/workload and proves:
- hierarchy/timeline usable;
- workflows restart/resume;
- scoped AI context;
- provider fallback;
- cost/budget controls;
- partial regeneration;
- incremental render;
- storage/recovery;
- final output manifest.

Record measured limits and recommended project complexity guidance.

## Expected modules/files

Primarily hardening/optimization/tests across existing API/workers/web/storage/timeline/render packages plus long-form fixture suites and operational dashboards.

## Data/migration impact

Only evidence-driven indexes/partitioning/schema optimizations. No new fundamental product domains should be invented in M14.

## API/UI impact

Performance/virtualization/pagination improvements without breaking existing contracts. Long-form navigation enhancements follow preplanned UI model.

## Security/cost/rights impact

- no relaxed security for performance;
- bounded real-provider test spend;
- long-retention/storage costs measured;
- rights/provenance remain per asset/project;
- large-context data minimized.

## Test/acceptance

Apply Master QA long-form/performance/resilience/DR sections at all target durations.

## Rollout/rollback

Optimizations feature-flagged where risky. Index/query changes tested under representative load. Workflow compatibility retained for in-flight long projects.

## Exit criteria

The platform demonstrably supports orchestrated projects up to 180 minutes without requiring a single-model 3-hour generation, with recoverable workflows, usable timeline, bounded context/cost, incremental rendering and measured production capacity.

## Non-goals

- unlimited project duration;
- one-call 3-hour AI generation;
- active-active multi-region;
- arbitrary professional studio-scale concurrent productions beyond measured capacity;
- new product features unrelated to hardening.
