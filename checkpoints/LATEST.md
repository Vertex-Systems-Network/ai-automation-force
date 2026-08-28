# Latest Checkpoint

Current planning phase: **P0 — Full Project Preplanning Gate**

Status: **FULL_PROJECT_PREPLANNING_IN_PROGRESS**

## Operator requirement

No new executable development in M1–M15 may begin or resume until the entire foreseeable product is preplanned end-to-end.

Canonical global gate:
`ai-native/FULL-PROJECT-PREPLANNING-GATE.md`

Canonical master index:
`docs/product/FULL-PROJECT-PREPLANNING-MASTER-INDEX.md`

Development consent remains separately governed by:
`ai-native/DEVELOPMENT-CONSENT-GATE.md`

The previous M1 state `PLANNING_READY_FOR_CONSENT` is superseded by this stricter global preplanning gate. M1 remains technically well-scoped, but it is not authorized to start until P0 exits.

## Meaning of complete preplanning

Before development, the project must already define the foreseeable:
- product/media systems;
- AI roles, authority, memory, evaluation and security;
- all user-facing options/defaults;
- complete web UI/UX and design system;
- auth/account/workspace/RBAC/collaboration;
- provider/API/social integrations and fallback contracts;
- billing/entitlements/usage metering;
- notifications/events/transactional communications;
- public/developer API stance;
- mobile product;
- storage/uploads/CDN/delivery/archival;
- security/privacy/legal/data lifecycle;
- observability/SLOs/deployment/backups/DR/releases;
- support/admin/moderation;
- product analytics/experimentation;
- social community automation stance;
- master QA/evaluation/release acceptance;
- implementation-ready work-package decomposition for M1–M15.

Mutable external facts such as provider API versions, current pricing, OAuth scopes, app-review rules, ToS and SDK versions may be revalidated at implementation time, but no major product architecture or business rule should need first-time invention during coding.

## Existing mature core

The repository already has strong planning for:
- project creation/options/presets;
- content formats/research/originality;
- characters/entities/locks;
- image generation/editing/reuse/image-to-video handoff;
- audio/music/dialogue/SFX;
- visual/cinematic direction;
- storyboard/timeline/shot/take hierarchy;
- long-form production up to three hours;
- provider-neutral routing/failover/cost policy;
- continuity/generated-media QA;
- assets/provenance/rights;
- review/approval;
- localization/dubbing;
- memory/learning/prompt registry/AI agent roles;
- public landing/features/visual inventory;
- signup/login/verification/reset/onboarding;
- authenticated web IA;
- multi-platform social publishing and analytics architecture;
- daily provider scouting;
- GitHub↔Linear planning sync.

## P0 planning backlog

Linear P0 gate issue:
- `ABD-149` — Complete full-project preplanning before any development

Existing deep-audit gaps moved under P0:
- `ABD-142` — commercial plans/entitlements/usage metering/billing
- `ABD-143` — AI-agent security/threat model/evaluation framework
- `ABD-144` — design system/AI command center/notifications/account UX
- `ABD-145` — workspace/RBAC/invitations/collaboration
- `ABD-146` — security/privacy/secrets/uploads/webhooks/data lifecycle
- `ABD-147` — observability/SLOs/incidents/backups/DR/releases
- `ABD-148` — notifications/events/public API/uploads/support-admin

Additional explicit P0 packs:
- `ABD-150` — mobile product specification
- `ABD-151` — product analytics/experimentation
- `ABD-152` — social community automation/moderation stance
- `ABD-153` — developer API/webhooks/SDK decision
- `ABD-154` — media storage/resumable uploads/delivery/archival
- `ABD-155` — master QA/evaluation/release acceptance matrix
- `ABD-156` — decompose M1–M15 into implementation-ready work packages

M1/WP1 (`ABD-128`) is explicitly blocked by `ABD-149`.

## Preplanning packs A–O

Tracked in `docs/product/FULL-PROJECT-PREPLANNING-MASTER-INDEX.md`:

A. Commercial SaaS/entitlements/billing
B. AI safety/agent security/evaluation
C. Full design system/product interaction model
D. Workspace/RBAC/collaboration
E. Notifications/events/communications
F. Public/developer API decision
G. Storage/uploads/delivery/archival
H. Auth hardening/security/privacy/legal
I. Observability/environments/deployment/DR/release
J. Support/admin/moderation
K. Mobile product
L. Product analytics/experimentation
M. Social community automation stance
N. Full M1–M15 implementation decomposition
O. Master QA/release acceptance matrix

## Exit condition

P0 may close only when:
- all Packs A–O are `READY` or explicit `NOT_SUPPORTED` decisions;
- every major UI route/options/state is documented;
- all privileged AI actions have authority/approval rules;
- all persistent data domains have ownership/lifecycle rules;
- all commercial limits/entitlements have a canonical source of truth;
- security/privacy/DR/operations are implementation-ready on paper;
- mobile/public API/community decisions are explicit;
- M1–M15 each have work packages, dependencies, tests, rollback and exit criteria;
- master QA matrix exists;
- final end-to-end audit reports no material first-time planning gap.

Only then set status to:

`FULL_PROJECT_PLANNING_READY_FOR_CONSENT`

and present a Development Consent Brief. Full preplanning does not itself authorize development.

## GitHub ↔ Linear

GitHub remains canonical for architecture/policy/specs/evidence/checkpoints. Linear mirrors P0 planning tasks, roadmap milestones, dependencies and status.

Recurring sync remains enabled every six hours for planning/status/documentation only and must preserve this P0 block.
