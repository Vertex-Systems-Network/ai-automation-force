# M12 — Multi-Platform Publishing, Social Automation and Analytics

## Objective

Implement provider-neutral distribution from one approved master into platform-specific variants, durable scheduling, official API publishing, verification, analytics ingestion and bounded community automation.

## Entry criteria

- P0 complete.
- M01–M11 accepted.
- Explicit M12 consent.
- Current official APIs/scopes/app review/policies revalidated for each target platform.

## Dependencies

`M10 masters + M11 auth/RBAC/UI + social publishing/community specs -> M12`

## Work packages

### M12-WP1 / SOC1 — Platform capability registry and account connections
Initial target registry:
- YouTube;
- TikTok;
- Instagram;
- Facebook;
- X;
- LinkedIn;
- Pinterest;
- Threads;
- Vimeo;
- Dailymotion;
- Likee `EVALUATION/MANUAL_HANDOFF` until official public publishing path verified;
- future official API-capable networks.

Capability states:
`DIRECT_PUBLISH | DRAFT_UPLOAD | SCHEDULE_SUPPORTED | SYSTEM_SCHEDULED_DIRECT | MANUAL_HANDOFF | READ_ANALYTICS_ONLY | EVALUATION | UNSUPPORTED | DISABLED`

Implement OAuth/token/scopes/account status/last-evidence metadata.

### M12-WP2 / SOC2 — Canonical PublishPackage and variants
- campaign;
- target account/platform;
- source master;
- aspect/length derivative;
- title/caption/description/hashtags;
- thumbnail/cover;
- captions/subtitles;
- audience/kids/synthetic-media flags;
- visibility/privacy;
- schedule/timezone;
- approval/rights state;
- external IDs.

Platform variant planner uses canonical rules and media renderer; source master remains unchanged.

### M12-WP3 — Durable scheduler and idempotent publication lifecycle
States:
`DRAFT -> NEEDS_APPROVAL -> SCHEDULED -> PUBLISHING -> PROCESSING -> PUBLISHED`
plus failure/manual states.

- native schedule where supported;
- otherwise durable Temporal schedule/wait + direct publish;
- restart-safe;
- ambiguous result reconciliation before retry;
- per-target idempotency;
- successful targets never duplicated because another target failed.

### M12-WP4 / SOC3 — Tier-1 adapters
Implement and contract-test official supported routes for:
- YouTube;
- TikTok;
- Instagram professional accounts;
- Facebook Page/Reels;
- X.

Each adapter exposes current constraints, auth/scopes, processing, errors, analytics, delete/edit capabilities and app-review requirements.

### M12-WP5 / SOC4 — Extended adapters
- LinkedIn;
- Pinterest;
- Threads;
- Vimeo;
- Dailymotion;
- other verified networks through registry.

Unsupported actions downgrade to draft/manual handoff, not browser/private-endpoint automation.

### M12-WP6 — Publication review/UI and approvals
- target/account selection;
- side-by-side platform previews;
- metadata edit/adaptation;
- cost/rights/audience/disclosure checks;
- schedule calendar/timezone;
- approval flow;
- per-target progress/failure/retry;
- external URLs.

### M12-WP7 / SOC5 — Analytics ingestion and normalization
Preserve raw platform definitions while normalizing categories:
- views/impressions/reach;
- watch time/retention/completion;
- reactions/likes;
- comments/replies;
- shares/reposts/saves;
- clicks/CTR;
- followers/subscribers attributable;
- restrictions/removal/status.

Idempotent time-window sync, source metric name/version retained.

### M12-WP8 — Community ingestion and AI-assisted replies
Implement according to `SOCIAL-COMMUNITY-AUTOMATION.md`:
- platform capability check;
- comment/mention ingestion;
- classification/risk;
- `AI_DRAFT_REVIEW` default;
- hard no-auto categories;
- optional `AUTO_LOW_RISK` only explicit policy;
- rate/spam controls;
- moderation/support escalation;
- manual handoff where API missing.

### M12-WP9 — Learning feedback and reporting
- campaign/platform performance dashboards;
- link metrics to source project/content/variant attributes;
- generate hypotheses;
- memory candidates;
- no blind automatic prompt/policy mutation;
- future changes pass AI evaluation framework.

### M12-WP10 — Acceptance
Representative campaign publishes through configured test/private accounts on supported tier-1 adapters and proves:
- independent target state;
- one-target failure no duplicate others;
- token expiry/reconnect;
- scheduled/restart recovery;
- analytics round trip;
- community injection/hard-risk no-auto reply;
- Likee/unverified platform remains evaluation/manual.

## Expected modules/files

- social platform registry/connections;
- publish package/variant services;
- scheduler/workflows;
- adapter packages;
- publishing UI;
- analytics adapters/data;
- community automation services/UI;
- contract/E2E fixtures.

## Data/migration impact

Adds SocialConnection, PublishCampaign/Package/Target/Attempt, PlatformPost, analytics snapshots, CommunityItem/replies/moderation, scheduling and disclosure records.

## API/UI impact

Full publishing/social account/calendar/analytics/community interfaces and APIs.

## Security/cost/rights impact

- OAuth tokens encrypted/server-side;
- official APIs only;
- public publishing permission/approval;
- platform audience/synthetic-media/rights checks;
- rate/spam protections;
- comments untrusted prompt-injection input;
- no same-account/platform automation beyond authorized scopes.

## Test/acceptance

Apply Master QA social/community/event/security sections with fake adapters plus bounded private/test official accounts.

## Rollout/rollback

Per-platform feature flags/kill switches. First publish to newly connected account can require explicit approval. Adapter/policy versions can be disabled without losing canonical package/history. External posts require compensating delete/edit, not code rollback assumptions.

## Exit criteria

One approved project can create correct per-platform variants, schedule/publish independently across multiple verified official platforms, reconcile failures, ingest analytics and support policy-bounded community workflows with full lineage.

## Non-goals

- unofficial/private endpoint automation;
- promise that every named social platform has a publish API;
- blind autonomous replies by default;
- cross-platform metric definitions treated as identical;
- social ads buying/management unless a future explicitly preplanned product scope is approved.
