# Support, Admin and Moderation Operations

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define internal operational tooling and authority before implementation so support/admin work is not performed through ad hoc database edits, secret sharing or unrestricted impersonation.

## Principles

- support/admin actions use product APIs/services, not direct DB edits as normal workflow;
- least privilege;
- sensitive access requires reason/case reference;
- every privileged action audited;
- no raw secret visibility;
- customer data access minimized;
- reversible actions preferred;
- billing/security/moderation authority separated where practical.

## Internal roles

### Support Agent
- search user/workspace by safe identifiers;
- view account/workspace state;
- inspect jobs/errors/non-secret provider status;
- resend selected transactional communications;
- guide user recovery;
- create/escalate cases.

Cannot silently alter billing balances, roles, secrets or security policy.

### Senior Support / Operations
- controlled job retry/replay;
- limited service credits according to policy;
- workspace restriction diagnostics;
- provider/social reconnect support;
- data export/delete case handling;
- escalation.

### Billing Admin
- subscription/invoice/credit adjustment operations;
- refund/credit actions within approval thresholds;
- no broad project-content access by default.

### Trust & Safety / Moderator
- abuse reports;
- content/account restriction;
- rights/privacy complaints;
- moderation evidence;
- escalation/appeal.

### Security Admin
- security cases;
- session/credential revocation;
- security policy actions;
- incident containment.

### Platform Admin
Rare high-privilege role for global configuration/operations; requires strong authentication and maximum audit.

## Support console

Main modules:
- Search
- User Account
- Workspace
- Membership/RBAC
- Projects/Jobs
- Providers/Social Connections
- Usage/Billing
- Publishing
- Security/Audit
- Data Requests
- Abuse/Moderation Cases
- Communications
- System/Incident context

## Search

Allowed search keys:
- user ID;
- verified email;
- workspace ID/name;
- project/job ID;
- invoice/customer reference;
- provider/social connection ID;
- publication ID;
- support case ID.

Avoid broad full-text search across private customer prompts/media unless a higher-authority investigation specifically permits it.

## Customer data visibility

Default support views show metadata first:
- IDs;
- status;
- timestamps;
- normalized errors;
- entitlement/usage;
- provider connection health;
- job timeline.

Private project media/prompts/content require explicit “view customer content” permission and case reason when access is needed.

## Impersonation stance

Default: **no silent full-session impersonation**.

Preferred support patterns:
- metadata diagnostics;
- user-visible screen/state recreation using synthetic/admin views;
- scoped support access grants.

If impersonation is later implemented:
- explicit privileged permission;
- step-up authentication;
- case/reason;
- prominent impersonation banner;
- no access to secrets/payment details;
- start/end audit;
- time limit;
- optionally customer-visible history according to policy.

## Job diagnostics

Support can inspect:
- workflow/job state;
- task/attempt history;
- provider normalized errors;
- retries/fallback;
- QA failures;
- cost reservations/settlements;
- asset references;
- logs/traces linked by IDs with privacy redaction.

## Controlled retry/replay

Support action must choose:
- retry same failed activity;
- retry failed scope;
- switch provider if policy/user allows;
- reconcile external status;
- cancel;
- mark manual action required.

Before retry:
- current state revalidated;
- idempotency checked;
- cost implication shown;
- duplicate external side effect risk assessed.

Support cannot use replay to bypass user budget/rights/approval policy.

## Provider/social support

Can:
- view connection status/scopes/expiry metadata;
- trigger reconnect flow;
- revoke/disconnect where authorized;
- inspect capability evidence;
- diagnose provider incident.

Cannot reveal stored API/OAuth secrets.

## Billing support

Actions:
- view plan/subscription/invoices;
- explain usage/ledger;
- apply permitted service credit;
- initiate supported refund/credit note;
- correct billing profile via user/admin process;
- reconcile failed webhook/state.

Every financial adjustment records:
- amount/units;
- reason;
- actor;
- case;
- approval if over threshold;
- external provider transaction reference.

No destructive balance editing.

## Workspace suspension/restoration

Restriction reasons:
- user-requested;
- billing;
- abuse/AUP;
- security incident;
- legal/rights;
- administrative error/recovery.

State change includes:
- reason code;
- scope (generation/publishing/API/login/full);
- actor;
- start/expiry/review;
- user communication;
- appeal path where appropriate.

Restore revalidates unresolved risk and records decision.

## Moderation/abuse case model

Case types:
- illegal/harmful content;
- child safety;
- non-consensual/identity/likeness abuse;
- fraud/deception/spam;
- harassment/hate/violence;
- copyright/IP;
- privacy/data request;
- provider/platform ToS issue;
- security abuse;
- billing/payment abuse.

Case fields:
- case ID;
- reporter/source;
- subject user/workspace/project/asset/publication;
- category/severity;
- evidence references;
- data sensitivity;
- assigned queue/owner;
- actions/decisions;
- appeal/review;
- retention/legal hold;
- status.

## Moderation states

`OPEN -> TRIAGED -> INVESTIGATING -> ACTION_REQUIRED | NO_ACTION -> ACTIONED -> APPEALED/REVIEW -> CLOSED`

Urgent safety/security cases can enter containment immediately while preserving evidence.

## Moderation actions

Potential scoped actions:
- block specific asset from publication;
- disable public publishing;
- disable generation feature/capability;
- remove/restrict share link;
- suspend workspace/account;
- revoke provider/social/API credentials;
- preserve legal/security hold;
- require rights/consent remediation;
- report/escalate to external platform when appropriate.

Avoid deleting evidence before case/legal policy permits.

## Appeals/review

For user-impacting moderation actions, architecture supports:
- reason/category notification as legally/safely appropriate;
- appeal request;
- different reviewer for material appeal when staffing permits;
- decision/audit trail.

## Copyright/rights complaints

Support system links complaint to:
- asset/content/publication;
- provenance/rights record;
- uploader/workspace;
- external publication URL;
- takedown/restriction action;
- counter/appeal process if legally applicable.

Exact statutory process depends on business jurisdiction and counsel.

## Data export/delete support

Support can:
- verify status of user-initiated request;
- troubleshoot failed export/delete jobs;
- initiate on behalf of user only under strict identity/authority verification;
- place/resolve documented hold where authorized;
- see propagation state.

Cannot simply “delete database rows” manually.

## Communications

Support console can send approved templates or case replies.

Rules:
- sender identity clear;
- templates localized where applicable;
- no copying secrets;
- case timeline records outbound/inbound support messages;
- marketing cannot be sent through transactional/support tooling.

## Help center/support channels

Preplan:
- in-app help/contact;
- email/ticket support;
- status page;
- security reporting contact;
- billing contact/process;
- developer support if API launched.

Live chat is optional and not required for initial launch unless business chooses it; support architecture remains channel-neutral.

## Escalation matrix

- product/how-to -> Support
- reproducible defect -> Engineering issue
- service outage -> Operations/Incident
- billing/refund -> Billing Admin
- account takeover/security -> Security
- abuse/rights/privacy -> Trust & Safety/Legal escalation
- data-loss/recovery -> Operations + Security/Engineering

## Admin global controls

High-risk global settings:
- provider/model enable/disable;
- global publishing kill switch;
- signup restriction;
- maintenance/degraded mode;
- feature flags;
- emergency budget/spend stop.

Changes require privileged role, audit and incident/change reference when emergency.

## Admin audit

Record:
- admin identity;
- original/effective user if impersonation;
- case/reason;
- action/target;
- before/after summary;
- approval;
- timestamp/request/session;
- result.

Audit export/search restricted; no secrets.

## Privacy/access reviews

Periodic review:
- who has support/admin roles;
- dormant privileged accounts;
- access usage;
- suspicious customer-content views;
- impersonation/support access;
- billing adjustments;
- moderation consistency.

## Testing

- support user cannot view raw secrets;
- role separation enforced;
- support retry does not double publish/charge;
- impersonation disabled by default;
- customer content access audited;
- financial adjustment threshold approval;
- suspend/restore behavior deterministic;
- moderation evidence retained;
- cross-tenant support lookup restricted by privilege;
- export/delete support cannot bypass identity checks.

## Acceptance criteria

Implementation can determine:
- internal roles/console modules;
- customer-data/impersonation stance;
- job/provider/billing support actions;
- suspension/moderation case lifecycle;
- rights/privacy/data-request operations;
- escalation/help channels;
- global admin controls/audit/testing.
