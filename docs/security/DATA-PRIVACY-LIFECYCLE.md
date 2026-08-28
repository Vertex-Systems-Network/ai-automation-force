# Data Privacy and Lifecycle

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define how personal, workspace, project, media, provider, analytics, billing and security data is classified, retained, exported, deleted and propagated through operational systems.

This is a product/data architecture contract, not legal advice. Jurisdiction-specific legal requirements must be revalidated before launch.

## Data classes

### Public
Content intentionally published or publicly exposed by the user/workspace.

### Internal product metadata
Non-public operational metadata such as job state, internal IDs, feature usage and non-sensitive diagnostics.

### Workspace confidential
Projects, scripts, prompts, media, characters, unpublished outputs, comments, provider configuration metadata.

### Personal data
Profile, email, membership, session/device data, support/billing contact details and user-linked product activity.

### Sensitive credentials/secrets
Provider API keys, OAuth refresh/access tokens, webhook secrets, signing/encryption material. Highest restricted class.

### Billing/tax records
Invoices, subscription/customer references, tax identifiers and payment-provider references. Card details should remain with payment provider where possible.

### Security/audit records
Authentication, permission, support/admin, deletion, credential and security incident records.

### Child-directed content metadata
Where projects target children, project/content safety classification may be sensitive operational metadata even when it is not child personal data. The platform should avoid collecting personal data from children unless a future product scope explicitly requires it and legal architecture is separately approved.

## Data inventory requirement

Every persistent domain declares:
- owner/controller context;
- purpose;
- classification;
- system(s) of record;
- tenant scope;
- retention class;
- export eligibility;
- delete/anonymize behavior;
- backup behavior;
- subprocessors/providers receiving it;
- regional restrictions if applicable.

## Canonical storage domains

### PostgreSQL
Operational state for users/workspaces/projects/jobs/metadata/permissions/billing mappings/analytics.

### Object storage
Media assets, references, renders, exports, large attachments.

### Vector/semantic index
Derived embeddings and retrieval metadata. Embeddings are treated as derived user/project data and follow source deletion/tenant isolation.

### Temporal/workflow history
Operational workflow history may contain structured references and selected inputs. Avoid placing unnecessary secrets/full sensitive content in workflow history because retention differs from ordinary DB rows.

### Logs/traces
Minimize payloads; redact secrets/personal data; define shorter operational retention than canonical business records unless security/audit need justifies longer.

### Git/repository
Engineering docs/prompts/schemas/research only. Live private customer data must not become ordinary Git history.

### Third-party providers
Generation, social, billing, email, analytics or identity providers receive only the data needed for their authorized purpose.

## Purpose limitation

Data collected for one purpose is not automatically reusable for another.

Examples:
- private generation media is not training/evaluation data by default;
- support access does not authorize product analytics reuse;
- billing records do not become creative personalization memory;
- social analytics do not authorize importing private social content beyond granted scopes.

## Training/evaluation policy

Default product rule:
- customer private content is not used to train foundation models controlled by AI Automation Force unless an explicit future opt-in program is defined;
- evaluation/debugging may use synthetic fixtures by default;
- production examples may only enter controlled evaluation datasets if privacy/rights/consent policy permits and records the source/retention;
- provider-side data-use terms are a provider-selection fact and must be surfaced in provider capability/rights metadata.

## Retention classes

Suggested canonical classes:
- `TRANSIENT` — temporary uploads/intermediates, hours/days;
- `ACTIVE_PROJECT` — retained while project/workspace active;
- `USER_CONFIGURED` — workspace selects allowed retention window;
- `AUDIT_SECURITY` — defined longer retention for security/audit needs;
- `BILLING_LEGAL` — legally/commercially required billing record retention;
- `ARCHIVE` — explicit user archive;
- `DELETION_PENDING` — excluded from active use while async deletion propagates.

Exact periods are configuration/legal decisions before launch; architecture must not hard-code one universal retention period.

## Temporary/intermediate media

Examples:
- failed takes;
- provider temporary inputs;
- proxies;
- extraction/transcode intermediates;
- upload quarantine;
- rejected candidates.

Policy defines whether they are:
- retained for debugging/learning;
- user-visible;
- automatically purged after N days;
- preserved only when attached to an audit/rights case.

Rejected content must not be retained forever by accident.

## User/workspace export

Export request flow:
`Request -> Reauthenticate if required -> Authorize -> Snapshot scope -> Generate export -> Notify -> Signed time-limited download -> Expire -> Audit`

Export package may include according to scope:
- profile/workspace metadata;
- project manifests;
- scripts/prompts/user settings;
- characters/entities;
- approved assets and optionally source assets;
- comments/approvals;
- publication records;
- usage/billing records where appropriate;
- AI memory/decision summaries;
- provider/social connection metadata excluding secrets;
- machine-readable JSON/CSV plus media files.

Very large exports may be segmented.

## Project deletion

Default architecture:
`Active -> Soft-deleted/Recovery Window -> Hard-delete Scheduled -> Delete operational rows/assets/indexes -> Propagate provider cleanup where supported/required -> Backup aging -> Tombstone/audit completion`

Rules:
- recovery window configurable;
- immediate hard-delete may be offered for specific scopes after warning/reauth where policy permits;
- deletion cancels future scheduled publication/jobs as applicable;
- shared/referenced assets require dependency-aware handling;
- derived embeddings/thumbnails/proxies are included;
- external published social posts are not automatically deleted unless user explicitly requests and platform API/policy supports it.

## Account/workspace deletion

Must resolve:
- ownership transfer or workspace deletion;
- active subscriptions/invoices;
- shared team assets;
- pending publications;
- provider/social credentials;
- API keys/webhooks;
- legal/security holds;
- exports before deletion;
- support case history.

Account deletion cannot silently delete a workspace owned by a team if ownership can/should be transferred according to workspace policy.

## Right to correct

Editable personal/profile data updates canonical state and dependent caches/indexes. Historical audit records may retain former values when necessary but access/retention is restricted.

AI memory correction has its own versioned controls and must not leave superseded wrong data active in retrieval.

## Provider/social credential deletion

Disconnect flow:
- revoke at provider when API supports it;
- delete/disable local token immediately;
- remove from routing;
- record revocation status/time;
- cancel provider-specific jobs that cannot continue;
- preserve non-secret audit/provenance required to explain historical outputs.

## External provider data propagation

For each third-party provider maintain:
- data categories sent;
- purpose;
- region/storage facts if known;
- retention/deletion API/support;
- training/data-use terms;
- subprocessor/contract reference;
- last verification date.

If provider cannot delete already processed input on demand, disclose/handle according to policy rather than pretending deletion was immediate.

## Backups

Deleted data may persist temporarily in immutable/point-in-time backups.

Architecture requirements:
- deleted data is excluded from restored active service through deletion replay/tombstone strategy where required;
- backups expire on documented schedules;
- direct surgical deletion from every immutable backup is not assumed;
- backup access is highly restricted;
- legal/privacy documentation clearly describes backup deletion semantics.

## Legal/security holds

A hold can pause hard deletion for narrowly defined records when required for legal/security reasons.

Hold record includes:
- authority/reason;
- scope;
- actor;
- start/end/review;
- access controls.

Hold should not preserve unrelated user data unnecessarily.

## Product analytics privacy

First-party analytics separates:
- anonymous/aggregate product metrics;
- user/workspace-linked operational analytics;
- social/content performance.

Define consent/cookie rules for marketing analytics separately from necessary product/security telemetry.

Avoid sending sensitive project titles/prompts/media content to general analytics tools by default.

## Logs and observability

Default redaction rules:
- no passwords;
- no provider/social/billing secrets;
- no full authorization headers;
- avoid full prompts/private content unless controlled debug mode with explicit retention/access;
- hash/tokenize identifiers where useful;
- production debug access audited.

## Data residency

Architecture supports a future residency policy but does not promise multiple regions until implemented.

Before selling residency commitments define:
- DB region;
- object storage region;
- workflow/log region;
- provider processing locations;
- backup locations;
- support access;
- subprocessors.

A workspace cannot be labeled “EU-only” if an enabled provider processes required data elsewhere.

## Subprocessor register

Maintain current register for third parties receiving customer/personal data, categorized by purpose:
- cloud hosting/storage;
- AI providers;
- authentication;
- billing;
- email/communications;
- monitoring/error tracking;
- analytics;
- social platforms.

## Consent and cookies

Separate:
- essential authentication/security storage;
- user settings/preferences;
- product analytics;
- marketing/advertising trackers.

Public-site cookie consent behavior depends on jurisdictions/tools and must be revalidated before launch.

## Data breach/incident linkage

Security incident process must be able to identify:
- affected tenants/users;
- data categories;
- providers/systems;
- exposure window;
- credentials requiring rotation;
- relevant audit/export/deletion state.

## Data lifecycle tests

Required scenarios:
- delete project removes DB/assets/vector entries after recovery window;
- disconnect provider removes token and routing eligibility;
- export excludes secrets and includes documented data classes;
- tenant A cannot export/delete tenant B;
- restored backup does not resurrect logically deleted active data improperly;
- analytics deletion/retention follows classification;
- account deletion handles owned/shared workspace correctly;
- pending publish/job cancellation is deterministic.

## Acceptance criteria

Implementation can determine:
- data classifications/systems of record;
- retention-class architecture;
- export/correct/delete flows;
- derived data and embedding deletion;
- provider/subprocessor propagation;
- backup deletion semantics;
- logs/analytics privacy;
- residency/subprocessor commitments boundary;
- test scenarios.
