# Notifications and Inbox UX

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define user-facing notification behavior independently of the underlying event-transport implementation. This covers in-app inbox, toasts/banners, email/push preferences and action-oriented alerts.

The canonical event architecture is specified separately in Pack E; this document defines product UX and preference behavior.

## Notification surfaces

- transient toast;
- persistent in-app inbox;
- contextual banner/panel;
- email;
- mobile push when mobile exists;
- optional webhook/customer API event when Pack F enables it.

Not every event should use every surface.

## Notification classes

### Action required
Examples:
- approval requested;
- budget approval required;
- provider reauthentication required;
- rights/consent missing;
- publish failure requires intervention;
- workspace invitation;
- payment failure/account restriction.

Persistent until resolved/dismissed according to policy.

### Success/completion
- generation complete;
- render complete;
- publish verified;
- export ready;
- import completed.

Usually inbox + optional toast/push/email based on duration/importance/preferences.

### Warning
- credits/storage near limit;
- provider quota low/exhausted;
- scheduled token expiry;
- continuity quality degraded;
- partial job failure;
- trial ending.

### Failure
- generation/workflow final failure;
- upload failed;
- publication failed;
- billing reconciliation problem;
- provider disconnected;
- security action blocked.

### Security
- new login/session/device;
- password/MFA/passkey change;
- email change;
- provider/social account connected/revoked;
- suspicious/blocked high-risk action;
- role/ownership change;
- account export/delete initiated/completed.

Security notifications have stricter dismissal/email rules and cannot all be disabled.

### Informational
- product announcement;
- provider capability update;
- new feature;
- research/scout informational change.

Marketing announcements are separate from transactional/service notifications and respect applicable consent/unsubscribe rules.

## Canonical notification record

Fields:
- `notification_id`
- workspace/user recipient
- type/category
- severity
- title/message key
- structured variables
- source event ID
- resource references
- action links/intents
- created timestamp
- read timestamp
- resolved timestamp
- dismissed timestamp
- deduplication key
- delivery-state per channel
- retention/expiry

Use localization keys + structured variables rather than persisting fully rendered English as the only representation when practical.

## Inbox UX

Global inbox supports:
- unread count;
- filters: Action Required, Failures, Approvals, Security, Publishing, Billing, System;
- workspace/project filter;
- unread/read;
- resolved/unresolved;
- mark read;
- bulk mark read for low-risk informational items;
- open related project/job/resource;
- execute allowed quick action;
- search/recent history.

Action-required notifications visually distinguish unresolved from merely unread.

## Quick actions

Allowed examples:
- Review approval
- Retry failed scope
- Reconnect provider
- View billing issue
- Open failed publication
- View security activity

A notification itself never bypasses permission/approval checks. Quick actions resolve through the same typed command/business logic as normal UI.

## Preferences

User preferences by category/channel:
- in-app inbox: generally always enabled for core operational events;
- email: instant/digest/off where legally/policy permitted;
- push: instant/off;
- webhook: workspace-level if enabled separately.

Preference dimensions:
- generation completion;
- failures;
- approvals;
- budget/usage;
- provider health;
- publishing;
- analytics summaries;
- workspace/team;
- billing;
- security;
- product updates.

Critical security/account notifications may ignore opt-out where required for account safety/service operation.

## Digest behavior

Supported digest modes:
- none;
- daily;
- weekly.

Digest may summarize:
- completed projects/jobs;
- failures needing attention;
- usage/cost;
- upcoming scheduled publications;
- analytics highlights;
- provider/quota changes.

Do not bury urgent approval/security/payment failures only in digest.

## Deduplication and grouping

Avoid notification storms.

Rules:
- group repeated provider outage events;
- one parent notification can show N affected jobs;
- retries updating same incident modify/group rather than create endless duplicates;
- resolved incident may create one resolution notification;
- independent projects/users remain separately actionable when needed.

Deduplication never hides a new severity escalation.

## Toast vs inbox

Toast is for immediate feedback in active session, e.g.:
- saved;
- job queued;
- copy/export started;
- low-risk error.

Inbox is for events users may need after navigation/session:
- completion;
- failure;
- approval;
- provider/billing/security/publish state.

A toast can link to persistent inbox/job state.

## Project notification panel

Project view can show scoped activity:
- job completion/failure;
- approvals;
- continuity issues;
- asset/import events;
- publish state;
- collaboration events later.

This is filtered view over canonical event/notification data, not duplicate independent history.

## Approval notifications

Must show:
- what needs approval;
- exact scope/count;
- requester/system source;
- estimated cost/public impact;
- expiration if any;
- Approve/Reject/View details.

Approval quick action still rechecks state/version before finalizing; stale approval requests become `STALE` rather than approving changed work.

## Cost/quota notifications

Examples:
- 50/80/100% usage threshold;
- platform credit low;
- provider free quota exhausted;
- reserved usage unusually high;
- autonomous spend paused;
- storage/egress near limit.

Thresholds can be workspace defaults + user preferences within allowed bounds.

## Provider notifications

- account connected;
- token expiring/expired where known;
- authorization revoked;
- provider incident/degraded;
- capability change affecting projects;
- quota reset when actionable.

Do not promise quota reset times unless provider evidence supports them.

## Publishing notifications

- schedule accepted;
- time changed;
- publish started;
- platform processing;
- published/verified;
- partial cross-platform failure;
- rejected by platform;
- manual handoff required;
- post removed/restricted where analytics/API exposes it.

Cross-platform campaigns group results while retaining per-target status.

## Email templates UX contract

Transactional emails require templates for:
- verify email;
- password reset;
- login/security alert;
- invite;
- approval request;
- provider reconnect;
- billing/payment failure;
- scheduled/publish failure;
- export ready;
- account deletion confirmation;
- trial/plan lifecycle where enabled.

Template requirements:
- localized subject/body;
- plain-text fallback;
- clear sender identity;
- no secrets/raw tokens except purpose-built short-lived links;
- expiry explanation;
- support/security contact;
- responsive accessible markup.

## Notification privacy

Lock-screen/push/email content can expose project details. Preference/security policy may allow `privacy_mode`:
- full title/context;
- generic “Action required in AI Automation Force” for sensitive workspaces.

Never include provider API keys, raw secrets or sensitive hidden metadata.

## Read/resolve semantics

`READ` means user viewed it.
`RESOLVED` means underlying issue no longer needs action.

Reading an approval/failure notification must not mark the issue resolved.

## Retention

Notification history retention varies by class:
- low-value informational: shorter;
- security/billing/audit-linked: longer according to data/legal policy;
- notification deletion does not delete canonical job/security/audit records.

## Accessibility and localization

- inbox keyboard navigable;
- icons paired with text;
- screen-reader-friendly severity/action labels;
- time shown in user timezone with explicit absolute time for schedules/security;
- locale-aware pluralization;
- RTL supported.

## Acceptance criteria

Implementation can determine:
- notification categories/severity;
- persistent vs transient behavior;
- inbox filters/actions;
- channel preferences/digests;
- dedupe/grouping;
- approval/cost/provider/publishing/security UX;
- transactional email template inventory;
- read vs resolved semantics;
- privacy/retention/accessibility requirements.
