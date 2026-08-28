# Public Landing Page, Authentication & Onboarding Specification

## Purpose

Define the public-facing marketing website and the account entry flow for the AI-native media production platform.

The public surface must explain the complete product clearly enough that a visitor can understand what it creates, how the AI production system works, why provider-independent continuity matters, and how to start an account without exposing internal/provider secrets.

Canonical flow:

`Public Landing -> Feature Education -> Signup/Login -> Account Verification -> Onboarding -> Workspace/Defaults -> Create First Project -> App Dashboard`

The marketing site and authenticated production app may share the same Next.js application/repository, but they are separate product surfaces with separate navigation, performance, security and content requirements.

---

## 1. Public information architecture

Recommended public routes:

- `/` — main landing page
- `/features` — complete feature overview
- `/features/characters`
- `/features/image-generation`
- `/features/video-generation`
- `/features/audio`
- `/features/storyboard-timeline`
- `/features/provider-routing`
- `/features/continuity-qa`
- `/features/long-form`
- `/features/publishing-analytics`
- `/use-cases` — songs, stories, episodes, movies, educational, social, etc.
- `/how-it-works`
- `/pricing` — only when plans/pricing are defined
- `/providers` — supported/evaluation provider explanation without implying unsupported guarantees
- `/security` or `/trust` — security/privacy/rights overview when implementation facts exist
- `/docs` or help center later
- `/about` / company details when applicable
- `/contact`
- `/login`
- `/signup`
- `/forgot-password`
- `/reset-password`
- `/verify-email`
- legal pages: Terms, Privacy, Cookie Policy, Acceptable Use as required before public launch

Do not publish claims about provider capabilities, pricing, uptime, free quotas or commercial rights unless current evidence supports them.

---

## 2. Header/navigation

Public header should support:

Left:
- brand/logo;
- Features;
- Use Cases;
- How It Works;
- Providers;
- Pricing when available;
- Docs/Resources later.

Right:
- Login;
- primary `Start Creating` / `Sign Up` CTA.

Mobile:
- accessible menu;
- persistent primary signup CTA where practical;
- no overloaded mega-menu.

Authenticated users visiting the marketing site may see `Open App` instead of Signup as the primary CTA.

---

## 3. Landing page section architecture

### 3.1 Hero

Purpose: explain the product in one screen.

Hero content should communicate:
- AI-native media production, not one-shot generation;
- images, audio and video in one production system;
- recurring character consistency;
- multiple AI providers through one workflow;
- short-form through long-form projects;
- provider-independent project memory/continuity.

Primary CTA:
- `Start Creating`

Secondary CTA:
- `See How It Works`

Hero visual:
- high-quality product UI composition showing project/storyboard/timeline/character reference/provider status;
- may be a real product screenshot once implementation exists;
- before the product exists, use a clearly conceptual product mockup rather than a fabricated live screenshot.

Optional supporting micro-copy:
- no provider-specific lock-in;
- reusable characters and references;
- controlled image-to-video workflow;
- hybrid free/paid routing subject to configured provider access.

Avoid absolute promises such as `perfect consistency` or `zero-cost unlimited generation`.

### 3.2 What the platform creates

Visual cards for:
- Songs & music videos
- Poems & rhymes
- Stories & bedtime stories
- Educational/explainer videos
- Shorts/social content
- Episodes & series
- Cinematic sequences
- Short films
- Documentaries
- Movies / long-form projects up to the configured product limit

Each card should have:
- representative visual;
- concise description;
- typical workflow/output;
- link to relevant feature/use case page.

### 3.3 AI production workflow

Show a visual horizontal/vertical pipeline:

`Idea/Research -> Script/Content -> Characters/World -> Images/References -> Audio -> Storyboard -> Shots -> Provider Routing -> Continuity QA -> Edit/Render -> Review -> Publish -> Learn`

The visual must make clear that generation is orchestrated and stateful rather than `prompt -> random video`.

### 3.4 Character Library & Character Lock

Show:
- character card/library;
- canonical version;
- look/wardrobe variants;
- reference pack;
- voice association;
- lock indicator;
- reuse across multiple projects.

Feature message:
`Create once. Lock the identity. Reuse consistently.`

Do not promise identical pixels across models/providers; describe continuity as controlled and QA-enforced.

### 3.5 Image Generation & Reuse

Show the documented image pipeline:
- generate character/reference candidates;
- approve canonical image;
- create scene/keyframe images;
- use approved image as image-to-video / first-frame / end-frame / style / location reference;
- store lineage in Asset Library.

Suggested visual pair:
1. Character/reference sheet UI;
2. Keyframe -> generated video shot flow.

Feature message:
`Generate images once, approve them, and turn them into reusable production controls.`

### 3.6 Storyboard & Timeline

Show:
- scene hierarchy;
- shot cards;
- keyframes;
- audio markers;
- timeline tracks;
- selected takes;
- scene/shot status.

Feature message:
`Plan before spending generation credits.`

### 3.7 Multi-provider AI routing

Show provider-neutral routing diagram/UI:
- connected providers;
- capability status;
- quota/availability;
- free/paid policy;
- retry/fallback route;
- same canonical shot request translated to another provider.

Example provider names may be shown only when actually supported/evaluated and with current factual status.

Core explanation:
- one authorized connection/account per provider by default;
- multiple different providers may be connected;
- provider outage/quota/capability failure can trigger eligible cross-provider failover;
- no same-provider account rotation to evade quotas;
- character/keyframe/scene state remains canonical outside providers.

### 3.8 Continuity & QA

Show side-by-side candidate review:
- approved vs rejected take;
- character identity score/status;
- wardrobe;
- props;
- location;
- lighting;
- camera direction;
- unwanted text/logo;
- rights/provenance state.

Message:
`A provider returning a file does not mean the shot is approved.`

### 3.9 Audio Production

Show:
- script/lyrics;
- narrator/character voices;
- music direction;
- stems;
- waveform/timing;
- ambience/SFX;
- mix/QA.

Explain separate routes for speech, dialogue, music, songs and cinematic mixes.

### 3.10 Long-form production

Explain how longer media is produced through:
- Act -> Sequence -> Scene -> Shot -> Take;
- scoped context;
- resumable jobs;
- incremental renders;
- continuity memory;
- deterministic assembly.

Do not imply one AI model generates a continuous three-hour film in one call.

### 3.11 Asset Library

Show reusable assets:
- characters;
- images;
- worlds;
- props;
- audio;
- keyframes;
- video takes;
- masters.

Explain versioning, canonical/rejected states and lineage.

### 3.12 Review & Approval

Show configurable review gates:
- script;
- character lock;
- images;
- audio;
- storyboard;
- scenes/shots;
- final master;
- public publishing.

AI autonomy presets can be explained without implying safety/rights/budget gates are bypassed.

### 3.13 Publishing & Analytics

Show planned product lifecycle:
- final master;
- metadata;
- thumbnail;
- captions;
- private-first verification where appropriate;
- publishing approval;
- analytics;
- learning feedback.

Platform availability should be labelled according to actual implementation status.

### 3.14 Use-case showcase

Use tabs/cards such as:
- Kids / family media
- General entertainment
- Educational
- Creators
- Agencies/studios
- Series / recurring IP
- Long-form filmmaking

Kids-specific policy should be described as a safety/content profile, not as the only platform scope.

### 3.15 Why this architecture

Comparison without attacking competitors:

Traditional one-model workflow:
- provider-specific state;
- repeated prompting;
- inconsistent character/reference behavior;
- manual stitching;
- limited recovery.

Platform workflow:
- canonical project state;
- reusable assets;
- provider routing;
- QA gates;
- history/cost/provenance;
- resumable production.

### 3.16 FAQ

Initial FAQ topics:
- What can I create?
- Can I use my own characters/images/audio?
- Can I create new characters and keep them consistent?
- Which providers can I connect?
- What happens when a provider is unavailable or quota is exhausted?
- Does switching provider guarantee an identical result? (No; continuity is controlled and QA-checked.)
- Can I create long videos/movies?
- Are free providers supported?
- How are provider costs handled?
- Are my provider keys exposed to the browser? (No.)
- Can I review before generation/publishing?
- How does image-to-video work?
- Can I localize/dub content?
- How are rights/provenance tracked?

### 3.17 Final CTA

Strong final CTA:
- `Start Your First Project`
- secondary: `Explore Features`

Do not require payment merely to create an account unless pricing policy later requires it.

---

## 4. Product imagery system for the marketing site

Landing page visuals are first-class marketing assets.

### Visual asset categories

- product UI screenshots;
- conceptual UI mockups before implementation;
- generated example character sheets;
- image-to-video flow examples;
- storyboard/timeline examples;
- provider routing diagram;
- continuity QA comparison;
- audio workspace visual;
- project wizard visual;
- final output thumbnails/posters;
- lightweight animations/video loops where useful.

### Truthfulness rule

Before a feature is implemented:
- label visuals as concept/preview where there is a risk of implying live functionality;
- do not fabricate real customer names/logos/testimonials;
- do not fabricate usage counts, savings percentages, uptime or performance metrics.

After implementation:
- prefer real product screenshots captured from controlled demo data;
- keep screenshots synchronized with current UI.

### Image quality/delivery

Plan for:
- AVIF/WebP where supported;
- responsive `srcset`/sizes;
- lazy loading below the fold;
- explicit width/height to avoid layout shift;
- meaningful alt text;
- dark/light screenshot treatment according to final design system;
- mobile-specific crops where needed;
- poster image for autoplay preview video;
- no text embedded in screenshots when HTML copy can remain accessible/searchable.

### Suggested marketing screenshot/demo dataset

Create a safe synthetic demo project specifically for marketing captures, e.g.:
- one recurring fictional character;
- one world/location;
- character reference images;
- storyboard frames;
- 12–20 planned shots;
- provider routing status;
- QA comparison;
- final short master.

This avoids exposing user/private projects in marketing screenshots.

---

## 5. Landing page conversion behavior

Primary conversion event:
- signup started;
- signup completed;
- onboarding completed;
- first project created.

Secondary events:
- feature section viewed;
- feature/use-case page opened;
- demo/video played;
- provider section viewed;
- pricing viewed when available;
- login;
- contact/demo request later.

Analytics must respect privacy/cookie requirements and should not be installed in a way that blocks basic page usability.

---

## 6. Signup / registration

### Entry methods

Initial recommended account methods:
- email + password;
- Google sign-in when configured;
- Apple sign-in where product/platform strategy justifies it;
- additional identity providers can be added later through the auth layer.

Do not require every social provider in the first implementation.

### Signup fields

Minimum:
- name/display name;
- email;
- password for password-based registration;
- terms/privacy acceptance where legally required.

Avoid collecting unnecessary profile information during signup.

Optional information belongs in onboarding rather than registration.

### Password requirements

Implementation should follow current security best practice at development time, including:
- strong server-side password hashing;
- breached/common-password protection if practical;
- secure reset flow;
- rate limiting;
- no plaintext password logging/storage.

Exact auth library/provider versions must be revalidated before implementation.

### Registration states

- signup form;
- submitting;
- account exists;
- invalid input;
- email verification required;
- verification sent;
- verified;
- social sign-in continuation;
- auth-provider failure;
- rate limited;
- account disabled/blocked where applicable.

### Email verification

Recommended before enabling sensitive/account-level actions.

Flow:
`Signup -> Verification message -> Verify token -> Account active/onboarding`

Verification tokens must be single-purpose, time-bound and safely stored/validated.

### Duplicate identities

When the same verified email appears through password and social auth, use a deliberate account-linking policy rather than silently creating duplicate user identities.

---

## 7. Login

Support:
- email/password;
- configured OAuth/social providers;
- remember/session behavior according to security policy;
- password reset;
- resend verification where appropriate.

Login UI states:
- invalid credentials;
- unverified email;
- rate-limited;
- provider unavailable;
- account disabled;
- session expired;
- safe redirect back to intended application page after authentication.

Avoid revealing whether sensitive accounts exist through overly specific error messages where account enumeration would be a concern.

---

## 8. Forgot/reset password

Flow:
`Forgot Password -> generic acknowledgement -> secure reset link/token -> new password -> invalidate/reset relevant sessions according to policy -> login/app`

Requirements:
- rate limiting;
- expiring one-time token;
- safe generic response;
- no password in URL/logs;
- audit event;
- invalidate/reset token after use.

---

## 9. Onboarding after signup

Onboarding is separate from account creation.

Suggested flow:

### Step 1 — Welcome / intent
Ask what the user plans to create:
- songs/music videos;
- stories;
- educational content;
- shorts;
- episodes;
- films/movies;
- mixed;
- explore first.

This can seed defaults without limiting the account.

### Step 2 — Default audience/language
Optional defaults:
- primary language;
- common audience profile;
- default content formats.

All remain editable per project.

### Step 3 — Provider connections
Options:
- connect now;
- skip and explore;
- configure provider later.

Explain:
- credentials stay server-side;
- one authorized connection/account per provider by default;
- multiple different providers may be connected;
- connecting a provider does not automatically spend credits.

Do not request unnecessary provider secrets before the user chooses to connect that provider.

### Step 4 — Budget/routing defaults
Optional:
- FREE_ONLY;
- FREE_FIRST;
- HYBRID_SMART;
- BUDGET_CAPPED;
- QUALITY_FIRST.

No paid-spend authorization should be inferred merely from signup.

### Step 5 — First project
Offer:
- `Create New Project`;
- `Use a Preset`;
- `Explore Demo Project`.

A safe synthetic read-only demo project can reduce empty-state friction.

### Step 6 — Onboarding complete
Route to:
- app dashboard;
- first project wizard;
- demo depending on selected action.

---

## 10. Account model planning

Core identities:
- User;
- AuthIdentity / credential method;
- EmailVerification state;
- Session;
- PasswordReset token/event;
- Account preferences;
- Workspace/organization later or initially single-user workspace abstraction.

Recommended future-safe architecture:
- every user belongs to at least one Workspace, even if the first UX calls it simply `My Workspace`;
- projects/assets/provider connections belong to Workspace rather than raw User where practical;
- this avoids painful migration when teams/agency accounts are added.

Detailed RBAC/team roles remain a separate milestone specification before multi-user development.

---

## 11. Provider credential boundary

Provider credentials:
- are entered only in authenticated settings/onboarding;
- are sent over TLS;
- are never rendered back in full after save;
- never live in frontend source/local storage;
- are encrypted/secret-managed server-side according to deployment architecture;
- are scoped to the owning workspace/account;
- have connection test/status and revoke/replace flow;
- must never be written to ordinary application logs or Git.

Marketing website must not collect provider API keys.

---

## 12. Account security planning

Before auth implementation, the dedicated development brief must cover:
- session strategy;
- CSRF where relevant;
- XSS/input validation;
- rate limits;
- brute-force protection;
- email verification;
- password hashing;
- OAuth state/PKCE/nonce as applicable;
- secure cookies;
- logout/session invalidation;
- audit events;
- provider-token encryption;
- account deletion/export policy;
- privacy/retention;
- optional 2FA/passkeys milestone decision.

Auth/security implementation requires separate explicit development consent when its milestone begins.

---

## 13. SEO/content architecture

Public marketing pages should support:
- unique title/meta description;
- canonical URL;
- Open Graph/social metadata;
- semantic headings;
- structured data only where factually appropriate;
- sitemap/robots;
- crawlable feature copy;
- fast server-rendered content;
- accessible internal linking;
- localization-ready public routes later.

Authenticated application pages should generally not be indexed.

Do not hide primary landing copy inside canvas/video/images.

---

## 14. Performance requirements

Landing page must not become a heavy product demo that destroys Core Web Vitals.

Plan for:
- server-rendered/static marketing content where appropriate;
- optimized images;
- deferred video/demo loading;
- minimal critical JS;
- lazy feature visuals below fold;
- no unnecessary provider SDKs on public pages;
- CDN/cache strategy later;
- responsive loading.

Authentication pages should remain especially lightweight and resilient.

---

## 15. Accessibility requirements

Public/auth pages must include:
- keyboard navigation;
- visible focus;
- semantic forms/labels;
- accessible validation messages;
- sufficient contrast;
- reduced-motion consideration;
- captions/transcripts for meaningful demo video;
- alt text for informative feature images;
- no critical information communicated only through animation/color.

---

## 16. Footer

Recommended groups:
- Product: Features, Use Cases, How It Works, Providers, Pricing later;
- Resources: Docs/Help/Status/Blog later;
- Company: About/Contact;
- Legal: Privacy, Terms, Cookie, Acceptable Use;
- account CTA/login.

Only show links/pages that actually exist or clearly mark coming-soon material internally, not as dead public links.

---

## 17. Launch content truth states

Every marketing feature should internally carry a launch state:
- `LIVE` — implemented and available;
- `BETA` — implemented but limited/evaluation;
- `PLANNED` — documented but not publicly claimed as available unless clearly labelled;
- `INTERNAL` — not marketed.

The landing page should be generated from/checked against these truth states before launch to avoid marketing features that are not actually available.

---

## 18. Acceptance criteria

This public/auth plan is development-ready when:
- a visitor can understand the platform without reading internal docs;
- each major product feature has a landing section/visual plan;
- signup/login/reset/verification states are defined;
- onboarding routes users into a first project without requiring immediate provider spend;
- provider credentials remain server-side;
- marketing imagery cannot be confused with fabricated customer/product evidence;
- SEO/performance/accessibility requirements are explicit;
- auth security details are required to be revalidated and separately briefed before implementation;
- public marketing claims can be reconciled against actual feature launch state.

Executable implementation remains blocked by the repository Development Consent Gate until an applicable development scope is explicitly approved.