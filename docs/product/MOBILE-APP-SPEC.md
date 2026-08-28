# Mobile Application Product Specification

## Status

`PREDEVELOPMENT_READY`

## Product decision

Build a React Native + Expo mobile companion focused on **monitoring, review, approvals, alerts and lightweight project control**. Do not duplicate the full professional desktop timeline editor in v1.

## Primary mobile users

- creator/owner checking production away from desktop;
- producer monitoring long jobs;
- reviewer approving/rejecting shots/assets/publishing;
- team/admin responding to provider/budget/security alerts;
- publisher reviewing scheduled/publication state.

## Navigation

Bottom-level primary navigation:
- Home
- Projects
- Inbox
- Approvals
- Account

Contextual routes:
- Project
- Character/Entity
- Asset/Take Viewer
- Job/Workflow
- Publish Campaign
- Usage/Cost
- Provider/Social Connection status

Tablet layouts may use split panes.

## Home

Shows:
- active projects;
- jobs currently running/waiting;
- approvals requiring user;
- failures/action required;
- upcoming publications;
- usage/budget summary;
- recent completed work.

No vanity dashboard overload; prioritize actions.

## Project mobile view

Tabs/sections:
- Overview
- Progress
- Storyboard Review
- Takes/Assets
- Approvals
- Publish
- Activity

Shows long-form hierarchy summary without attempting full track editing.

## Safe editable fields

Mobile v1 may edit:
- project title/description;
- selected safe project defaults;
- status/priority where product supports it;
- review comments;
- approval decisions;
- provider routing preference within allowed policy;
- budget threshold/approval choice within role;
- scheduled publication time/metadata where authorized;
- notification preferences.

Mobile v1 does **not** provide full complex editing for:
- multi-track timeline;
- frame-accurate trim graph;
- advanced audio mixer;
- large character/reference-pack authoring;
- deep admin/role matrix configuration.

## Approval center

Queue filters:
- Creative
- Continuity/QA
- Cost
- Rights
- Publishing
- Workspace/security where user has role.

Approval card shows:
- exact resource/version;
- preview;
- reason requested;
- cost/public impact;
- AI decision summary;
- comments;
- Approve/Reject/Request Changes.

Before final approval re-check current version so stale mobile notification cannot approve modified content.

## Media review

### Images
- pinch zoom;
- metadata/reference toggle;
- compare candidates;
- approve/reject;
- comment.

### Video
- adaptive/proxy playback;
- frame/timecode display;
- scrub;
- compare takes sequentially or side-by-side on tablet;
- continuity/QA findings;
- approve/reject.

### Audio
- playback;
- waveform if useful;
- transcript/lyrics;
- language/voice metadata;
- approval/comments.

Mobile downloads use proxies by default, originals only on explicit action/entitlement.

## Storyboard review

Mobile storyboard supports:
- vertical list/grid;
- shot number/frame;
- duration/action/camera summary;
- character chips;
- status;
- comments/approval;
- limited reordering only if product later validates touch UX; default v1 review-only for structural reordering.

## Job monitoring

Job page:
- workflow phase;
- completed/failed/pending counts;
- provider/fallback state;
- cost estimate/reserved/actual where allowed;
- ETA is not invented if unreliable;
- retry/cancel actions only when authorized;
- manual handoff details.

## Provider/cost alerts

Examples:
- provider disconnected;
- quota exhausted;
- paid fallback needs approval;
- budget threshold reached;
- storage/credit low;
- long job failed.

Quick actions route through canonical Command Center/business policies.

## Publishing

Mobile can:
- review platform variants;
- preview caption/thumbnail/metadata;
- approve/reject;
- schedule/reschedule;
- view per-platform processing/result;
- retry failed target;
- open published URL.

Connecting complex social OAuth can open secure system browser/deep-link flow.

## Authentication

Support same account identity model:
- email/password if enabled;
- Google/Apple;
- passkeys/platform credentials where Expo/native support and backend policy allow;
- MFA;
- recovery.

Use OS secure storage for session/refresh material. No provider API keys stored directly in app.

## Device/session security

- app lock using biometric/device credential can be optional/user setting;
- sensitive actions may require reauth/biometric step-up according to backend policy;
- screenshot/screen-capture prevention only for very sensitive screens if feasible and justified; do not promise universal prevention;
- device appears in account sessions list.

## Push notifications

Push categories:
- approval required;
- generation/render complete;
- terminal failure;
- provider reconnect;
- budget threshold;
- publishing success/failure;
- security/account alerts;
- invitation/mention.

Privacy mode controls lock-screen detail.

Push deep link always reauthenticates/re-authorizes resource; payload is not authorization.

## Deep links

Supported logical targets:
- project;
- approval;
- job;
- asset/take;
- publish target;
- security/account action;
- invite.

Links validate workspace access after app opens.

## Offline/degraded mode

Mobile may cache:
- recent project summaries;
- thumbnails/proxies explicitly cached;
- recent inbox/approval metadata.

Offline rules:
- read cached data clearly marked stale;
- comments/low-risk drafts may queue only if conflict-safe design implemented;
- approvals, publishing, billing, provider/security changes require online server confirmation;
- no offline generation command assumed successful.

## Upload/capture

Mobile can later support:
- photo/reference upload;
- camera capture;
- audio/reference upload;
- small video/reference upload.

Uses same resumable/signed asset upload pipeline. Camera/photo permission requested contextually, not at first launch without need.

## Mobile AI Command Center

Subset commands:
- next status/action;
- explain failure/decision;
- retry failed scope;
- approve/reject;
- compare takes;
- pause/cancel job;
- schedule/publish after review.

Complex free-form production authoring can exist but must not make mobile the only path for professional project setup.

## Notifications/inbox

Same canonical notification source as web; read/resolved state synchronized.

Mobile supports filters/quick actions and push preference settings.

## Settings

- profile;
- language/timezone;
- theme;
- notifications;
- security/sessions;
- provider/social connection status;
- billing/usage summary;
- workspace switcher;
- support/help.

Deep admin configuration redirects to web when mobile UI does not safely support it.

## Localization/accessibility

- dynamic font sizing;
- screen-reader labels;
- sufficient touch targets;
- motion reduction;
- captions/transcripts;
- RTL/localized dates/numbers;
- orientation responsive behavior where useful;
- color not sole status indicator.

## Performance

- list virtualization;
- image/video proxies;
- progressive loading;
- background downloads/uploads through supported platform mechanisms;
- avoid auto-playing many media assets;
- network-aware quality option.

## App lifecycle

On resume:
- refresh auth as needed;
- reconcile queued local actions;
- refresh active job/approval/publication state;
- do not repeat side effects because app was backgrounded.

## App-store/privacy readiness

Before public mobile release:
- privacy disclosures match actual SDK/data collection;
- permissions minimized;
- account deletion path accessible if store policy requires;
- social/provider OAuth redirects registered;
- push/camera/media permissions explained;
- no hidden tracking SDK not covered by consent/privacy inventory.

## Testing

Device matrix includes representative iOS/Android phones and tablets, low-memory/network-degraded conditions.

Required E2E:
- login/MFA;
- workspace switch;
- open project;
- review/approve current version;
- stale approval blocked;
- push deep link;
- provider failure alert;
- publication approval;
- offline cached view;
- session revoke;
- signed media access tenant isolation.

## Explicit non-goals for v1

- full desktop-equivalent multi-track timeline editing;
- advanced node/compositor UI;
- storing raw provider secrets locally;
- autonomous background public publishing from device independent of server;
- full support/admin console;
- offline AI generation orchestration.

## Acceptance criteria

Implementation does not require first-time planning for:
- target users/navigation;
- project/review/approval flows;
- safe editable vs desktop-only functionality;
- media/job/publishing UX;
- auth/security/push/deep links;
- offline/uploads/accessibility/performance;
- explicit v1 non-goals.
