# M11 — Web Application, Public Landing, Auth and SaaS Control Surface

## Objective

Implement the public marketing site, account/auth/onboarding, workspace/RBAC, full authenticated web product, design system, AI Command Center, notifications, billing/usage/settings and the complete 2-minute vertical-slice user experience.

## Entry criteria

- P0 complete.
- M01–M10 accepted.
- Explicit M11 consent.
- Current Next.js/React/auth/passkey/accessibility/browser baselines revalidated.

## Dependencies

`M01–M10 product/backend contracts + Packs A/C/D/E/H -> M11`

## Work packages

### M11-WP1 — Design-system implementation
- semantic tokens/theme;
- typography/spacing/components;
- form/data/media/status components;
- responsive workstation/desktop/tablet/narrow modes;
- accessibility foundations;
- localization/RTL infrastructure.

### M11-WP2 — Public landing/marketing site
- hero/value proposition;
- feature/use-case sections;
- product visual/mockup inventory;
- providers/character/image/video/audio/timeline/publishing story;
- pricing-ready section based on enabled commercial mode;
- trust/safety/FAQ;
- SEO metadata/schema/sitemap;
- performance/accessibility;
- signup/login CTAs.

Use real screenshots with synthetic data once available; conceptual visuals cannot masquerade as live evidence.

### M11-WP3 — Authentication/account security
- signup/login/logout;
- email verification;
- forgot/reset password;
- Google/Apple where enabled;
- passkeys/MFA;
- sessions/devices;
- account linking/collision handling;
- step-up auth;
- abuse/rate protection;
- account export/delete entry points.

### M11-WP4 — Onboarding/workspace bootstrap
- welcome/goals;
- audience/content defaults;
- language/timezone;
- provider connection or skip;
- budget/routing defaults;
- initial workspace;
- preset/demo/first project;
- resumable onboarding;
- zero-provider empty state.

### M11-WP5 — App shell, dashboard, project wizard
- workspace switcher;
- global nav/search/command palette;
- dashboard/active jobs/action-required;
- projects list/search;
- complete New Project Wizard and presets;
- project overview/progress/history.

### M11-WP6 — Core production workspaces
Implement UI for:
- content/script;
- Character/Entity Library;
- assets;
- image generation/candidates/reuse;
- storyboard;
- timeline/editor;
- audio;
- shots/takes comparison;
- QA/continuity;
- render/export;
- cost/quota.

Use virtualized/proxy media patterns for large projects.

### M11-WP7 — AI Command Center and notifications
- global typed commands;
- next/explain/dry-run/generate/retry/compare/repair/undo where supported;
- cost/scope/authority preview;
- active jobs;
- in-app inbox;
- notification preferences/digests;
- transactional communication integration;
- security/publishing/budget/provider alerts.

### M11-WP8 — Workspace/RBAC/collaboration
- members/invites/roles;
- project access;
- comments/annotations/mentions;
- review links;
- approvals/delegation;
- audit log;
- conflict/version UX;
- custom roles UI only if enabled entitlement.

### M11-WP9 — Billing/entitlements/settings/admin-visible controls
- plan/entitlement view;
- usage/credits;
- billing profile/invoices/payment recovery when billing enabled;
- upgrade/downgrade/cancel;
- provider/social/default settings;
- security/privacy/data settings;
- launch mode can support invite/free beta without paid checkout.

### M11-WP10 — E2E/accessibility/performance acceptance
Critical E2E:
`Landing -> Signup -> Verification -> Onboarding -> First Project -> Character/Reference -> Generate -> Review -> Timeline -> Render/Export`

Also:
- team invite/review;
- budget approval;
- account/session security;
- billing mode where enabled;
- mobile/narrow review fallback;
- WCAG 2.2 AA core flows;
- browser matrix;
- public landing performance/SEO checks.

## Expected modules/files

- `apps/web/`
- shared `packages/web-ui/` where justified;
- generated API client/contracts;
- auth/account UI;
- public marketing routes;
- app routes/modules;
- Playwright/component tests;
- localization resources.

## Data/migration impact

Implements operational users/workspaces/members/invites/preferences/sessions/notification/billing mappings already preplanned. No new first-time business model may be invented during UI coding.

## API/UI impact

This is the principal web UI milestone. API gaps discovered are fixed only if they conform to preplanned contracts; materially new product architecture returns to governance rather than being improvised.

## Security/cost/rights impact

- full auth/RBAC/tenant/step-up controls;
- no provider secrets in client;
- entitlement/budget/publishing approvals enforced server-side;
- rights/QA state visible before export/publish;
- secure signed media access.

## Test/acceptance

Apply Master QA web/auth/accessibility/RBAC/billing/AI command/storage/provider/media sections.

## Rollout/rollback

Feature flags allow staged module rollout. Auth/billing/security changes Class C release-managed. Public site may launch before full paid/product availability only under explicit launch mode and truthful feature claims.

## Exit criteria

A user can operate the full approved 2-minute media-production vertical slice from the web UI, from landing/signup through project creation, media generation/review and final export, with secure account/workspace/cost/notification behavior.

## Non-goals

- native mobile app (M13);
- full public API launch (M13);
- every enterprise SSO/custom-role feature unless enabled scope;
- unrestricted professional NLE parity;
- public social automation before M12.
