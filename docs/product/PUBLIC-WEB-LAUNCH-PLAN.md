# Public Web Launch Plan

## Purpose

Define the launch-ready planning layer for the public marketing website that sits in front of the authenticated AI media production application.

This document complements `PUBLIC-LANDING-AUTH-ONBOARDING.md` and `LANDING-PAGE-VISUAL-CONTENT-MAP.md` by specifying content hierarchy, SEO/discoverability, conversion measurement, pricing-readiness, trust/legal requirements, performance, accessibility, and launch gates.

No executable implementation is authorized by this document.

---

## 1. Public product boundary

Canonical public-to-private flow:

`Marketing Site -> Signup/Login -> Verification -> Onboarding -> App`

Public routes explain and convert.
Authenticated routes create/manage projects, assets, provider connections and production jobs.

Provider secrets, workspace data, project history and private assets never belong on the public surface.

---

## 2. Landing page message hierarchy

The homepage should answer these questions in order:

1. What is this product?
2. What can I create with it?
3. Why is it different from a one-model generator?
4. How does character/image/video continuity work?
5. How does multi-provider routing help?
6. Can I control/review the process?
7. Can it handle long-form projects?
8. How do I start?

Recommended hierarchy:

- Hero
- Output/use-case gallery
- End-to-end production workflow
- Character + Image Generation/Re-use
- Storyboard + Timeline
- Multi-provider routing/failover
- Continuity QA
- Audio production
- Asset Library
- Long-form production
- Review/Approval
- Publishing/Analytics when live
- Use cases
- FAQ
- Final CTA

Do not present unimplemented features as live.

---

## 3. Core marketing positioning

The product should be positioned as an **AI-native media production system**, not merely an AI video generator.

Primary differentiators:

- provider-independent canonical project memory;
- reusable/locked characters and references;
- image generation + approval + re-use;
- image-to-video/keyframe workflows;
- multiple providers under one production routing layer;
- continuity and QA gates;
- audio + storyboard + timeline + assets in one workflow;
- resumable short- and long-form production;
- rights/provenance/cost history;
- controlled human/AI approvals.

Avoid unsupported claims such as:
- perfect continuity;
- unlimited free generation;
- zero manual review;
- identical output across providers;
- guaranteed commercial rights for every provider/model.

---

## 4. Content architecture by public route

### `/`
Primary conversion landing page.

### `/features`
Overview of all major capabilities.

### Feature detail pages
Recommended:
- Characters
- Image Generation & Re-use
- Video Generation
- Audio
- Storyboard/Timeline
- Provider Routing
- Continuity QA
- Long-form Production
- Asset Library
- Review/Approval
- Publishing/Analytics when live

Each feature page should include:
- problem;
- capability;
- workflow;
- UI/product visual;
- limitations/truthful constraints;
- CTA.

### `/use-cases`
Use-case hub.

Potential use cases:
- songs/music videos;
- children/family content;
- educational/explainer;
- social shorts;
- recurring series/IP;
- agency/studio production;
- cinematic short films;
- long-form movie planning/production;
- localization/dubbing.

### `/how-it-works`
Detailed production lifecycle.

### `/providers`
Explain provider-agnostic architecture and current supported/evaluation providers.

Provider facts must be generated from current provider registry/research and not stale hard-coded marketing copy.

### `/pricing`
Reserved for defined commercial plans.

Do not invent pricing before pricing/product strategy is approved.

### `/security` or `/trust`
Only claim controls that actually exist.

Topics may include:
- provider credential boundary;
- private project isolation;
- signed/private media access;
- rights/provenance;
- audit history;
- data handling;
- disclosure of sub-processors/providers where required.

### `/contact`
Support/contact or future sales/demo flow.

---

## 5. SEO and discoverability planning

Every public page should define:
- canonical URL;
- unique title;
- unique meta description;
- H1;
- clear semantic headings;
- index/noindex policy;
- Open Graph/Twitter/social preview metadata;
- structured data only when valid and appropriate;
- internal links;
- image alt text;
- breadcrumb structure on deep pages where useful.

Core topic clusters may include:
- AI media production platform;
- AI character consistency;
- AI image-to-video workflow;
- multi-provider AI video production;
- AI storyboard/timeline;
- AI video continuity;
- long-form AI video production;
- AI media asset management;
- AI audio/video production workflow.

Do not keyword-stuff or create thin near-duplicate feature pages.

Public content should remain accurate as provider/model capabilities change.

---

## 6. Dynamic provider marketing data

Provider names, capabilities, free/paid status, model availability and limits are volatile.

Marketing pages should not rely on manually copied static claims where machine-readable provider registry can safely supply status.

Recommended content classes:
- `Supported`
- `Evaluation`
- `Manual Handoff`
- `Temporarily Unavailable`
- `Deprecated/Removed`

The public site should expose only the subset appropriate for marketing.

Never expose:
- API keys;
- private account identifiers;
- quota secrets;
- internal provider failure details;
- provider pricing claims without current evidence.

---

## 7. Conversion funnel

Primary funnel:

`Landing View -> Signup Start -> Signup Complete -> Verified -> Onboarding Complete -> First Project Created`

Secondary funnel events:
- Features viewed;
- How It Works viewed;
- Demo played;
- Provider page viewed;
- Pricing viewed;
- Signup CTA clicked;
- Login clicked;
- First project preset selected;
- Provider connection started/completed.

Do not treat raw page views as the primary product-success metric.

---

## 8. Pricing-ready structure

Even before pricing exists, the public architecture should leave room for:
- Free/Trial plan;
- Creator/Individual;
- Pro;
- Team/Studio;
- Enterprise/custom;
- usage/credit-based components;
- provider-direct cost pass-through or BYO-provider-credentials model;
- storage/render allowances;
- feature/automation limits.

No pricing or entitlement logic should be implemented until the commercial model is explicitly approved.

Landing copy should avoid promising included provider credits unless they are actually part of the plan.

---

## 9. Trust and legal readiness

Before public launch define/verify as applicable:
- Terms of Service;
- Privacy Policy;
- Cookie Policy;
- Acceptable Use Policy;
- copyright/IP complaint path;
- user-content/provider processing disclosure;
- age/minimum-user requirements;
- children/family product policy where relevant;
- real-person likeness/voice rules;
- commercial-use/provenance disclosures;
- AI/synthetic media disclosure policy where relevant.

Legal copy must reflect actual product behavior and jurisdictions; templates are not a substitute for appropriate legal review.

---

## 10. Marketing analytics/privacy

Analytics design should support funnel measurement while minimizing unnecessary collection.

Track event names/IDs rather than raw sensitive prompt/project content.

Do not send:
- provider API keys;
- private prompts/scripts;
- private asset URLs;
- email verification tokens;
- password/reset data;
- internal project content

to marketing analytics.

Consent/cookie behavior must follow applicable legal requirements.

---

## 11. Performance requirements

Public pages should prioritize fast first-load and crawlability.

Plan for:
- server-rendered/static-rendered marketing routes where practical;
- optimized AVIF/WebP images;
- responsive image sizing;
- no large app bundles on pure marketing routes;
- lazy-loading below-fold visuals;
- preload only critical hero assets;
- poster-first demo video;
- reduced-motion fallback;
- fonts optimized/subset/licensed appropriately;
- no blocking analytics for basic page rendering.

The authenticated timeline/editor bundle should not be required to render the homepage.

---

## 12. Accessibility requirements

Public website must support:
- semantic headings;
- keyboard navigation;
- visible focus;
- accessible menu/dialog behavior;
- meaningful alt text;
- sufficient contrast;
- form labels/errors;
- reduced-motion support;
- captions/transcripts for meaningful video/audio;
- non-color-only state communication.

Marketing polish does not justify inaccessible interaction.

---

## 13. Responsive behavior

Desktop:
- immersive product visuals;
- multi-column feature layouts;
- detailed diagrams.

Tablet:
- simplified visuals;
- preserved CTA hierarchy.

Mobile:
- hero copy + product visual remains legible;
- feature screenshots crop intelligently;
- no tiny desktop UI shrunk to unreadable scale;
- mobile navigation is accessible;
- signup CTA remains easy to reach.

---

## 14. Demo strategy

Before real customer projects exist, use a safe synthetic demo project.

The same demo should power:
- landing screenshots;
- character references;
- image-generation candidates;
- storyboard;
- timeline;
- provider fallback example;
- QA comparison;
- final output preview.

This provides visual continuity and avoids fake customer evidence.

---

## 15. Content maintenance

Public content has two classes:

### Stable product content
Examples:
- architecture philosophy;
- character locks;
- image reuse;
- storyboard/timeline;
- workflow concepts.

### Volatile content
Examples:
- provider/model names;
- model capabilities;
- free quotas;
- prices;
- platform publishing rules.

Volatile content should have evidence freshness and maintenance ownership.

---

## 16. Launch phases

### Phase A — Private/Internal
- public pages may exist behind limited exposure;
- conceptual mockups allowed when labelled internally/appropriately;
- signup may be invite-only.

### Phase B — Beta
- real product screenshots;
- signup enabled;
- onboarding enabled;
- provider connection setup;
- controlled feature claims;
- Terms/Privacy live.

### Phase C — Public Launch
- production auth/security;
- monitoring;
- legal/trust pages;
- verified landing claims;
- optimized real screenshots;
- stable signup/reset/verification;
- support/contact path;
- analytics/privacy validated.

---

## 17. Public web acceptance criteria

Public web planning is development-ready when:
- landing structure is complete;
- feature/use-case route map is defined;
- every major feature has a truthful visual plan;
- signup/login/onboarding entry points are specified;
- pricing area can exist without invented pricing;
- SEO metadata/content ownership is defined;
- provider facts cannot silently become stale marketing claims;
- performance/accessibility/privacy requirements are explicit;
- legal/trust dependencies are known;
- conversion funnel and launch gates are defined.
