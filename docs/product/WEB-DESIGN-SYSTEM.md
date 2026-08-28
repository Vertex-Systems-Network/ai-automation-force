# Web Product Design System

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define the interaction and visual-system contract for the public site and authenticated production application so implementation does not invent component behavior screen-by-screen.

This document defines tokens, component families, responsive behavior, accessibility, states and product-wide interaction rules. Exact brand art direction may be refined before visual implementation without changing these contracts.

## Product surfaces

The design system serves:
- public marketing/landing pages;
- authentication and onboarding;
- authenticated desktop web app;
- tablet review flows;
- admin/support tooling where shared components are appropriate;
- landing-page product mockups/screenshots.

Mobile-native design is specified separately.

## Foundations

### Color tokens

Use semantic tokens rather than raw colors in component code:
- `bg.canvas`
- `bg.surface`
- `bg.elevated`
- `bg.inverse`
- `text.primary`
- `text.secondary`
- `text.muted`
- `text.inverse`
- `border.default`
- `border.strong`
- `accent.primary`
- `accent.secondary`
- `status.info`
- `status.success`
- `status.warning`
- `status.danger`
- `status.pending`
- `focus.ring`

Brand color values remain replaceable design tokens.

Status color is never the sole carrier of meaning; pair with icon/text/pattern.

### Typography

Token families:
- display;
- heading 1–6;
- body large/default/small;
- label;
- caption;
- mono/code/data;
- numeric/metric.

Rules:
- readable line length for content-heavy panels;
- tabular numerals for cost/time metrics where useful;
- minimum accessible sizes for controls;
- locale-compatible fallback font stack;
- support Turkish/English and future RTL/Unicode scripts.

### Spacing and sizing

Use a consistent spacing scale. Layout must not use empty dummy elements solely to create spacing.

Tokens include:
- space scale;
- control heights;
- radius scale;
- border widths;
- shadow/elevation levels;
- icon sizes;
- content max widths;
- sidebar/panel widths;
- timeline track sizing.

## Theme model

Support:
- `LIGHT`
- `DARK`
- `SYSTEM`

Generated media itself is never color-inverted by theme.

Theme changes preserve status semantics and contrast requirements.

## Responsive breakpoints and modes

Do not design only by pixel breakpoints. Use interaction modes:

### Wide workstation
- persistent left navigation;
- multi-panel timeline/storyboard inspectors;
- side-by-side take comparison;
- dense tables when appropriate.

### Standard desktop/laptop
- collapsible nav;
- inspector drawers;
- reduced multi-column density.

### Tablet/review mode
- prioritize playback, review, approval, comments, project status;
- complex timeline controls simplify/reflow;
- touch target sizes increase.

### Narrow/mobile web fallback
- supports authentication, status, simple review/approval and settings;
- does not promise full professional timeline editing;
- direct users to native mobile/desktop surface where needed.

## Application shell

Authenticated app shell contains:
- workspace switcher;
- global navigation;
- project breadcrumb/context;
- global search/command trigger;
- notifications/inbox;
- current usage/cost indicator when relevant;
- account menu;
- optional active-jobs indicator.

Navigation groups:
- Dashboard
- Projects
- Characters/Entities
- Assets
- Publishing
- Analytics
- Providers
- Settings

Project workspace navigation:
- Overview
- Brief/Script
- Characters/World
- Storyboard
- Timeline
- Audio
- Shots/Takes
- QA
- Costs
- Publish
- History

## Component taxonomy

### Navigation
- sidebar/nav item;
- breadcrumbs;
- tabs;
- segmented controls;
- stepper/wizard;
- command palette;
- pagination/load-more;
- context menu.

### Inputs
- text/email/password;
- textarea/rich text where justified;
- number/duration/currency;
- select/multi-select;
- combobox/search select;
- checkbox/radio/switch;
- slider/range;
- tags;
- provider/account picker;
- character/entity picker;
- asset picker;
- date/time/timezone;
- file/media upload;
- prompt/AI instruction editor.

### Feedback
- inline validation;
- banners;
- toast;
- status badge;
- progress bar/ring;
- job stepper;
- skeleton;
- empty state;
- error/retry state;
- conflict state;
- quota/budget warning;
- approval-needed state.

### Data display
- table/data grid;
- card/list;
- metric/stat;
- timeline event;
- audit/decision record;
- cost breakdown;
- provider status;
- version comparison.

### Media
- image viewer;
- video player;
- audio player/waveform;
- storyboard card;
- keyframe strip;
- take comparison;
- before/after image comparison;
- caption/subtitle view;
- timeline clip/track;
- frame/timecode display;
- media metadata/provenance panel.

### Actions
- primary/secondary/tertiary/destructive buttons;
- split action/dropdown;
- approve/reject;
- generate/regenerate;
- lock/unlock;
- compare;
- retry failed scope;
- publish/schedule;
- download/export;
- archive/delete/restore.

## Button/action hierarchy

Rules:
- one clear primary action per local task context when practical;
- destructive actions visually and semantically distinct;
- paid/spend-impact actions show cost/credit estimate when available;
- public publishing actions show target account/privacy/audience state;
- disabled buttons include accessible reason/tooltips when non-obvious;
- long-running actions immediately return job state rather than frozen UI.

## Form behavior

All forms define:
- initial/default values;
- required/optional;
- validation timing;
- dependent-field visibility;
- unsaved-change behavior;
- server-error mapping;
- optimistic vs confirmed save strategy;
- keyboard behavior;
- help text;
- permission/entitlement disabled state.

Wizard forms persist resumable draft state.

## Global state patterns

Every screen/module must account for:

### Loading
- initial load skeleton where layout predictable;
- local progress for actions;
- background jobs remain navigable.

### Empty
Explain:
- what the area is;
- why empty;
- next safe action;
- optional example/demo.

### Error
Classes:
- retryable network;
- permission;
- entitlement;
- validation;
- provider unavailable;
- partial failure;
- stale/conflict;
- system error.

Never show raw provider/server errors without normalized user-safe context.

### Offline/degraded
- read cached/recent safe data where feasible;
- block side effects requiring server truth;
- queue only actions explicitly designed for offline replay;
- show reconnect state.

### Stale/version conflict
For collaborative/versioned resources:
- detect stale edits;
- preserve local draft;
- offer reload/compare/merge where supported;
- do not silently overwrite newer approved state.

### Permission/entitlement
Distinguish:
- insufficient role;
- plan entitlement missing;
- resource locked;
- approval required;
- provider/account disconnected.

## Timeline/editor UX principles

- non-destructive editing;
- timecode always unambiguous;
- zoom/pan keyboard/mouse behavior documented;
- snapping can be toggled;
- locked/approved clips visually distinct;
- failed/missing media visible in timeline;
- audio/video tracks have clear mute/solo/lock state;
- generation state is separate from editorial state;
- undo/redo history for editor-safe operations;
- long timelines virtualize/render efficiently;
- AI suggestions preview before destructive replacement.

## Storyboard UX

Storyboard cards show:
- shot number;
- frame/reference;
- duration;
- character/entity chips;
- camera/action summary;
- continuity status;
- generation/approval status;
- provider/take state;
- cost when relevant.

Bulk operations must declare scope before execution.

## Provider/cost UX

Provider screen distinguishes:
- connected/authorized;
- capability;
- free/quota state where knowable;
- paid/BYOK funding source;
- health/degraded;
- rights/commercial status;
- last capability verification.

Cost UI distinguishes:
- estimate;
- reserved;
- provider actual cost;
- customer billable usage;
- refunded/released.

## Account and security UX

Screens:
- profile;
- email/password;
- connected login methods;
- MFA/passkeys when enabled;
- active sessions/devices;
- security history;
- notification preferences;
- language/timezone;
- data export;
- account deletion;
- billing;
- workspace membership.

Sensitive changes require reauthentication according to security spec.

## Settings information architecture

Workspace settings:
- General
- Members/Roles
- Providers
- Social Accounts
- Defaults/Presets
- Budget/Usage
- Publishing Policy
- Notifications
- Security
- Billing
- API/Webhooks when enabled
- Data/Privacy

Project settings remain scoped and cannot silently change workspace/global policy.

## Accessibility

Target WCAG 2.2 AA for core web experience where applicable.

Requirements:
- semantic HTML;
- keyboard-operable controls;
- visible focus;
- no keyboard traps;
- accessible names/descriptions;
- status changes announced appropriately;
- sufficient contrast;
- captions/transcripts for product media where relevant;
- motion-reduction preference;
- drag/drop alternatives;
- timeline functions have non-pointer alternatives for critical operations;
- touch targets appropriate in touch modes.

## Localization and RTL

UI strings externalized from code.

Support:
- locale-aware date/time/number/currency;
- timezone explicit in scheduling;
- text expansion;
- pluralization;
- RTL layout mirroring where applicable;
- media timeline direction remains semantically time-left-to-right unless product research intentionally changes it; text controls can be RTL.

No important state embedded only inside English images.

## Design tokens for status

Canonical statuses map consistently across modules:
- draft/neutral;
- queued/pending;
- running/info;
- needs review/warning;
- approved/success;
- failed/danger;
- blocked/danger or warning depending severity;
- archived/muted.

Provider-specific statuses map to canonical semantics before display.

## Confirmation and destructive UX

Use confirmation proportional to impact:
- reversible low-risk: immediate + undo toast;
- costly generation: estimate + execute;
- public publish: review target/metadata/visibility + approval policy;
- destructive irreversible: explicit confirmation and recovery impact;
- account/workspace deletion: reauth + typed/strong confirmation + retention/deletion explanation.

## Landing/demo visual system

Marketing product visuals must reuse actual product tokens/component language. Before real implementation:
- conceptual mockups are clearly product concepts;
- synthetic/demo data only;
- no fake customers/metrics;
- later replace with real screenshots when stable.

## Performance UX

- route transitions avoid blank screens;
- media thumbnails/proxies before full masters;
- virtualized large lists/timelines;
- progressive job status;
- background work survives navigation;
- avoid blocking entire project UI for one failed shot/provider.

## Acceptance criteria

Pack C design-system portion is ready when implementation has deterministic guidance for:
- tokens/theme;
- shell/navigation;
- component families;
- forms/actions;
- media/timeline patterns;
- loading/empty/error/offline/conflict states;
- cost/provider/account/security UX;
- responsive modes;
- accessibility/localization/RTL;
- marketing/demo visual consistency.
