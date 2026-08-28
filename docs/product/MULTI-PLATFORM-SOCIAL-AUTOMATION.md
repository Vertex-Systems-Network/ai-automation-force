# Multi-Platform Social Publishing & Automation System

## Purpose

Define a provider-neutral publishing, scheduling, analytics and recovery layer for social/media platforms that expose legitimate APIs or approved upload interfaces.

The system must never assume every platform supports the same media types, scheduling controls, metadata, permissions or automation level.

Canonical flow:

`Approved Master -> Platform Variant Planner -> Publish Package -> Platform Capability Check -> Policy/Permission Gate -> Schedule/Publish Job -> Platform Adapter -> Verify -> Store PlatformPost -> Analytics Sync -> Learning Memory`

## Core principles

1. One canonical project/master can create many platform-specific derivatives without changing the source master.
2. Platform APIs are adapters, not the system of record.
3. Each platform has dynamic capability/permission evidence and can be enabled, draft-only, manual-only or disabled.
4. Public publishing is always policy-gated; account connection alone does not authorize autonomous posting.
5. A failed platform publish never invalidates the approved master or other platform publications.
6. Platform-specific limits, scopes, review requirements and terms are revalidated before adapter enablement and periodically afterwards.
7. Never automate undocumented private endpoints, browser scraping or credential/session abuse to mimic an API.

## Platform capability states

Every platform/account route must resolve to one of:

- `DIRECT_PUBLISH` — official API permits direct publishing for the connected account/app/scopes.
- `DRAFT_UPLOAD` — official API can upload media/content for user review/finalization in the native platform.
- `SCHEDULE_SUPPORTED` — platform API itself supports scheduled publication for the required content/account type.
- `SYSTEM_SCHEDULED_DIRECT` — platform lacks native scheduling but the platform allows direct publish; our scheduler waits then calls the publish API at the approved time.
- `MANUAL_HANDOFF` — system prepares files/metadata/checklist but a human completes publishing.
- `READ_ANALYTICS_ONLY` — connection supports analytics/reading but not publication.
- `EVALUATION` — official capabilities/app approval are still being verified.
- `UNSUPPORTED` — no legitimate supported route for the requested automation.
- `DISABLED` — administratively or policy disabled.

Capability is evaluated per account, app approval, content type and permission state, not only per brand name.

## Initial platform registry

### Verified official publishing/upload paths as of 2026-08-28

- YouTube — video upload through YouTube Data API; OAuth; metadata/privacy; resumable/retryable upload patterns.
- TikTok — Content Posting API supports Direct Post and Upload-to-Draft flows; video and current photo support; account/app scopes and creator-info UX requirements apply.
- Instagram — official Instagram Platform supports content publishing for eligible professional accounts; images, videos/Reels and carousels are available subject to account type, permissions and current Meta rules.
- Facebook — official Meta APIs support Page publishing paths including Reels/video routes subject to Page access and permissions.
- X — X API supports post creation plus image/GIF/video media upload; current access is pay-per-use and account/app permissions apply.
- LinkedIn — Posts API supports organic text, image, video, document, article, multi-image and other supported post types subject to member/organization permissions and current version headers.
- Pinterest — official API supports creating image/video Pins and boards with write scopes.
- Vimeo — official API supports authenticated video upload and management; upload access may require app/account approval.
- Dailymotion — official API v2 supports authenticated video upload, creation and publication.
- Threads — official Threads API supports publishing/media workflows; exact supported content/account behavior is capability-registry driven and revalidated before enablement.

### Evaluation/manual until official publishing evidence is verified

- Likee — do not automate private/unofficial endpoints. Keep `EVALUATION` or `MANUAL_HANDOFF` until an official public publishing API/partner path is verified and approved.
- Any other social network without verified official publishing documentation follows the same rule.

### Extensible candidates

The registry is intentionally open for API-capable networks such as Snapchat/public-profile products, Bluesky/AT Protocol, Mastodon-compatible services, additional video hosts, regional social networks and future platforms. Each adapter must pass the same capability, rights, security and QA gates before enablement.

## Social account/connection model

Recommended canonical records:

### SocialPlatform
- platform ID/key;
- display name;
- official developer/docs evidence;
- adapter version;
- capability status;
- supported account types;
- supported media/content types;
- auth type;
- required scopes;
- app-review requirements;
- quota/rate-limit metadata;
- upload limits;
- scheduling capabilities;
- analytics capabilities;
- webhook capabilities;
- commercial/policy notes;
- last verified timestamp;
- enabled/evaluation/disabled state.

### SocialConnection
- stable connection ID;
- workspace ID;
- platform ID;
- external account/channel/page/profile ID;
- display account name;
- account type;
- token/credential reference (secret-managed, never raw in normal DB/UI logs);
- granted scopes;
- token expiry/refresh state;
- connection health;
- publishing capability state;
- analytics capability state;
- moderation/disclosure settings;
- created/updated/last-verified timestamps.

One workspace may connect multiple distinct platforms and, where the platform legitimately allows it, multiple owned pages/channels/profiles. Quota-evasion account rotation is never a design goal.

## Publish package

Canonical `PublishPackage` should contain:
- Project/ContentVersion/FinalMaster IDs;
- target platform connection;
- platform-specific media asset derivative IDs;
- title/headline;
- caption/body;
- description;
- hashtags/keywords;
- mentions when resolvable and permitted;
- thumbnail/cover/poster;
- alt text/accessibility text;
- language/locale;
- audience/privacy setting;
- category/topic;
- made-for-kids or equivalent audience flags when applicable;
- synthetic/AI disclosure fields where required/configured;
- location/tagging where supported and authorized;
- interaction settings when supported;
- comments/duet/stitch/remix settings where supported;
- schedule time/timezone;
- campaign/series identifiers;
- UTM/tracking URL policy;
- rights/provenance clearance;
- approval state;
- idempotency key.

The canonical package preserves intent; adapters drop/transform fields that a platform does not support and must report that mapping explicitly.

## Platform Variant Planner

Before publishing, create optimized derivatives per platform without mutating the master.

Possible variants:
- 16:9 long video;
- 9:16 vertical short/Reel/TikTok;
- 1:1 or 4:5 feed crop;
- shorter trailer/teaser;
- image cover/carousel frames;
- subtitle-burned vs clean caption-track variant;
- platform-specific thumbnail/poster;
- audio-safe normalized derivative;
- duration-limited cut;
- alternate opening hook;
- text/caption-safe crop.

The planner uses actual current platform constraints from the capability registry, not hard-coded assumptions in creative logic.

## Metadata adaptation

A Metadata/Distribution Agent may transform the same canonical publication intent into platform-native copy.

Examples:
- YouTube: title, description, tags/keywords where relevant, category, thumbnail, privacy, audience settings.
- TikTok: caption/title, privacy and interaction options returned by current creator-info/capability rules.
- Instagram/Facebook: caption, Reel/feed choice, carousel composition, cover, location/tagging where supported.
- X: concise post/thread copy, media attachment, link policy.
- LinkedIn: professional commentary, article/document/video variants, organization/member author choice.
- Pinterest: board, Pin title/description/link, image/video Pin.

Do not auto-spam identical text everywhere. Preserve campaign meaning while adapting syntax, length, hashtags and CTA to each platform.

## Scheduling architecture

Canonical scheduler owns the desired publish time even when the platform has its own native scheduling.

Schedule states:
- `DRAFT`
- `AWAITING_APPROVAL`
- `APPROVED`
- `SCHEDULED`
- `READY_TO_PUBLISH`
- `PUBLISHING`
- `PROCESSING_PLATFORM`
- `PUBLISHED`
- `PARTIAL_SUCCESS`
- `FAILED_RETRYABLE`
- `FAILED_FINAL`
- `CANCELLED`
- `EXPIRED_TOKEN`
- `MANUAL_ACTION_REQUIRED`

Rules:
- use platform-native scheduling when officially supported and operationally preferable;
- otherwise keep a durable internal scheduled job and call direct publish at the approved time;
- never rely on a browser tab or frontend timer;
- timezone stored explicitly;
- DST changes handled using timezone-aware schedule data;
- rescheduling is versioned/audited;
- cancellation must attempt to cancel native scheduled posts where supported;
- missed schedule due to outage becomes a policy decision: publish-late, wait-for-window or require review.

## Multi-platform campaign

A single campaign may target many accounts/platforms:

`Campaign -> PublishPackages[] -> PublishJobs[] -> PlatformPosts[]`

Campaign can define:
- common launch window;
- staggered times;
- per-platform copy;
- per-platform derivative;
- region/language variants;
- embargo;
- review requirements;
- priority;
- retry deadline;
- analytics cohort ID.

Failure on one target must not cause duplicate reposts to targets that already succeeded.

## Idempotency and duplicate prevention

Every publish job requires a deterministic idempotency key based on approved package/version/target.

Before retry:
- inspect local attempt history;
- use platform status/publish IDs where available;
- confirm whether the previous request already created a post;
- retry only if duplication risk is controlled.

Store:
- platform publish/upload ID;
- external post/media ID;
- canonical URL when available;
- processing state;
- attempt timestamps;
- API/request correlation IDs where safe;
- failure category;
- response evidence required for audit.

## Retry/recovery

Failure classes:
- network/transient;
- rate limited;
- platform outage;
- processing delay;
- token expired/refresh failed;
- revoked permission;
- missing app review/access;
- invalid media specification;
- rejected metadata;
- policy/moderation rejection;
- quota exhausted;
- duplicate/ambiguous result;
- manual confirmation required.

Recovery rules:
- exponential/backoff retry only for retry-safe classes;
- honor platform retry/reset guidance;
- refresh tokens through legitimate OAuth flows;
- regenerate only the required media derivative when format validation fails;
- never silently broaden privacy/audience permissions to force success;
- never publish via undocumented endpoints if official API denies access;
- manual handoff retains the same package/lineage and final external-post verification.

## Pre-publish gates

A package cannot become publishable until required gates pass:
- final master approved;
- target-specific derivative QA passed;
- rights/commercial-use clearance;
- audience/child-directed flags resolved;
- real-person/voice consent resolved where required;
- caption/metadata review according to project policy;
- account connection healthy;
- scopes/permissions valid;
- platform capability evidence fresh;
- publishing approval satisfied;
- embargo/schedule valid;
- no unresolved policy/security block.

## Human approval modes

- `MANUAL_EVERY_POST`
- `APPROVE_CAMPAIGN_ONCE`
- `APPROVE_PLATFORM_VARIANTS`
- `AUTOMATED_WITH_FINAL_PUBLISH_GATE`
- `POLICY_DRIVEN_AUTOPUBLISH` — only if explicitly enabled in a later approved policy/milestone.

Default planning stance remains conservative: public publishing requires approval until policy explicitly authorizes otherwise.

## Analytics ingestion

After publication, adapters may ingest available official metrics such as:
- views/impressions;
- reach;
- watch time;
- average view duration;
- retention points where available;
- likes/reactions;
- comments/replies;
- shares/reposts;
- saves/bookmarks;
- clicks/CTR;
- follows/subscribers attributed where available;
- completion rate;
- traffic source/audience geography where permitted;
- post status/removal/restriction signals.

Normalize into canonical metrics while retaining raw platform metric names/version/source.

Never compare metrics across platforms as if definitions are identical without normalization/context.

## Comments/community automation

Separate from publishing.

Possible future adapter capabilities:
- ingest comments/replies;
- moderation queue;
- sentiment/topic clustering;
- suggested replies;
- auto-reply only under explicit policy and platform rules;
- spam/toxicity triage;
- escalation to human;
- FAQ/help routing.

Do not enable autonomous public replies merely because publishing is authorized.

## Provider/platform scout integration

The daily external-capability scout should eventually track social platform API changes as a separate source class:
- API versions;
- deprecated endpoints;
- scopes;
- app-review requirements;
- media limits;
- publishing modes;
- rate limits;
- pricing/access changes;
- analytics fields;
- webhook changes;
- synthetic-media disclosure requirements;
- policy/terms changes.

Scout findings update evidence/research and can propose adapter changes; executable adapter/code changes remain consent-gated.

## Security

- OAuth/credentials server-side only;
- tokens encrypted/secret-managed;
- minimum required scopes;
- CSRF/state/PKCE where appropriate;
- token refresh rotation handled safely;
- revoke/disconnect support;
- no raw tokens in Git/logs/analytics/client storage;
- workspace ownership isolation;
- audit log for connection, publish, reschedule, cancel and delete actions;
- webhook signature verification when platform supports it;
- user-provided webhook/media URLs treated as untrusted.

## Deletion/edit lifecycle

Where official APIs permit:
- edit supported fields;
- delete/unpublish;
- update thumbnail/metadata;
- change privacy;
- archive where supported.

Never pretend all platforms support edits after publication. Capability registry determines allowed actions.

A deleted external post remains in internal audit history as a tombstoned PlatformPost record rather than erasing publication lineage.

## Product UI surfaces

Publishing workspace should include:
- connected accounts;
- capability/permission status;
- content calendar;
- campaign composer;
- platform variants preview;
- approval queue;
- scheduled queue;
- publish progress;
- failures/retries;
- manual handoffs;
- external links;
- analytics;
- token/connection health;
- provider/platform evidence freshness.

## Acceptance criteria

This system is development-ready conceptually when:
- any approved master can produce per-platform PublishPackages and derivatives;
- platforms can express different automation levels without hacks;
- scheduling is durable and timezone-safe;
- direct/draft/manual publishing all share one lineage model;
- duplicate publishing is prevented through idempotency/status reconciliation;
- failed targets retry independently;
- public publishing remains approval/policy gated;
- analytics can flow back into canonical learning memory;
- unsupported platforms such as an unverified Likee route remain manual/evaluation rather than using unofficial automation.

## Current implementation boundary

This document is planning/architecture only. No social adapter, OAuth flow, scheduler, publishing job, webhook, platform upload or analytics integration is authorized by this document alone. Executable development requires the applicable development-consent milestone.