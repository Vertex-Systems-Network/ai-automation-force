# Latest Checkpoint

Current checkpoint: `checkpoints/2026-08-28-documentation-core-complete.md`

Current milestone: **Milestone 1 — Core domain model and repository migration boundary**

Status: **PLANNING_READY_FOR_CONSENT**

Core product/AI documentation status:
- complete enough for staged implementation;
- tracked in `docs/product/DOCUMENTATION-COMPLETENESS-MATRIX.md`;
- includes project options/wizard, content types, AI roles, prompts, characters, audio, visual/cinematic, image generation + approval + reuse, image-to-video reference handoff, storyboard/timeline, provider routing/recovery, continuity QA, memory, assets, approvals, rights, localization, publishing, analytics, 3-hour long-form architecture, web IA, presets/admin;
- also includes public landing-page architecture, feature marketing content, feature visual/screenshot inventory, signup/registration, login, email verification, password reset, onboarding and the public -> authenticated app handoff;
- public-web launch planning now also covers SEO/discoverability, conversion funnels, pricing-ready structure, trust/legal dependencies, performance, accessibility, responsive behavior and launch gates;
- auth/onboarding edge-case planning covers duplicate identities, OAuth collisions, expired/used verification/reset tokens, resumable onboarding, provider connection failures, workspace bootstrap, rate limits and security-event requirements;
- multi-platform social/media publishing planning now covers official API-capable networks, per-platform derivatives/metadata, durable scheduling, direct publish vs draft upload vs manual handoff, idempotent retries, publication verification, analytics ingestion and learning feedback.

Image generation planning is canonical in `docs/product/IMAGE-GENERATION-REUSE-SYSTEM.md` and is exposed as an explicit New Project Wizard strategy. Approved still images may become reusable character/world/style/keyframe/reference assets and may drive first-frame/end-frame/image-to-video workflows while retaining provider-independent lineage and continuity state.

Public website/auth planning is canonical in:
- `docs/product/PUBLIC-LANDING-AUTH-ONBOARDING.md`;
- `docs/product/LANDING-PAGE-VISUAL-CONTENT-MAP.md`;
- `docs/product/PUBLIC-WEB-LAUNCH-PLAN.md`;
- `docs/product/AUTH-ONBOARDING-EDGE-CASES.md`.

The public product path is planned as:

`Landing -> Features/Use Cases -> Signup/Login -> Verification -> Onboarding -> Provider/Defaults Setup -> First Project -> App Dashboard`

The landing page must present major product features with purposeful product images/screenshots/mockups. Real product screenshots use safe synthetic demo data once implementation exists; conceptual pre-implementation visuals must not be presented as fabricated live-product/customer evidence.

## Multi-platform social publishing planning

Canonical architecture: `docs/product/MULTI-PLATFORM-SOCIAL-AUTOMATION.md`.

Planned capability model:
- `DIRECT_PUBLISH`;
- `DRAFT_UPLOAD`;
- `SCHEDULE_SUPPORTED`;
- `SYSTEM_SCHEDULED_DIRECT`;
- `MANUAL_HANDOFF`;
- `READ_ANALYTICS_ONLY`;
- `EVALUATION`;
- `UNSUPPORTED`;
- `DISABLED`.

Initial verified/evaluated platform scope includes:
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
- Likee as `EVALUATION/MANUAL_HANDOFF` until an official public publishing API/partner path is verified;
- additional API-capable social/media platforms through the same registry after official capability review.

The publishing layer is provider/platform neutral:

`Approved Master -> Platform Variant Planner -> Publish Package -> Capability/Permission Gate -> Durable Schedule/Publish Job -> Platform Adapter -> Verification -> PlatformPost -> Analytics -> Learning Memory`

Public publishing remains approval/policy gated. No undocumented private endpoints, browser automation or quota/permission circumvention are planned.

## Linear planning mirror

Linear project: **AI Automation Force**

Linear mirrors roadmap/planning/status while GitHub remains canonical for engineering policy, architecture, schemas, implementation/test evidence and checkpoints.

Roadmap milestones M0–M15 are mirrored in Linear.

Current M1 work-package chain:
- `ABD-128` — WP1 Contract freeze + generated schemas
- `ABD-129` — WP2 Full lineage fixtures/invariants
- `ABD-130` — WP3 Aggregate validation hardening
- `ABD-131` — WP4 Legacy CNT importer
- `ABD-132` — WP5 PostgreSQL persistence architecture
- `ABD-133` — WP6 Reversible migrations
- `ABD-134` — WP7 Persistence repositories + round trips
- `ABD-135` — WP8 Milestone verification/checkpoint

M12 is now **Multi-Platform Publishing & Analytics** with future consent-gated social work packages:
- `ABD-137` — SOC1 Platform capability registry + account connection model
- `ABD-138` — SOC2 Publish packages + variants + durable scheduler + idempotent recovery
- `ABD-139` — SOC3 Tier-1 adapters: YouTube, TikTok, Instagram, Facebook, X
- `ABD-140` — SOC4 Extended adapters: LinkedIn, Pinterest, Threads, Vimeo, Dailymotion + evaluation networks
- `ABD-141` — SOC5 Cross-platform analytics normalization + learning feedback

GitHub↔Linear synchronization policy is canonical in `docs/operations/GITHUB-LINEAR-SYNC.md`.

A recurring sync scheduler is enabled at a six-hour cadence. It may synchronize planning/status/documentation only, must be idempotent, must avoid duplicate noise, and must never treat synchronization as development consent.

Development consent policy: `ai-native/DEVELOPMENT-CONSENT-GATE.md`

Development brief awaiting operator approval: `docs/architecture/M1-DEVELOPMENT-CONSENT-BRIEF.md`

Detailed execution plan: `docs/architecture/M1-EXECUTION-PLAN.md`

M1 planned work packages:
1. contract freeze + generated schemas;
2. full lineage fixtures;
3. aggregate validation hardening;
4. legacy content importer boundary;
5. PostgreSQL persistence architecture;
6. reversible migration scaffold;
7. persistence repositories + short/long project round trips;
8. Milestone 1 verification.

Next executable action: WP1 only after explicit operator development consent.

A generic `continue`, `next`, or `resume` does not authorize development.

Do not start or modify executable code, schemas, migrations, dependencies, CI behavior, provider integrations, Temporal, generation pipelines, UI, authentication, publishing or later milestones without applicable development consent.
