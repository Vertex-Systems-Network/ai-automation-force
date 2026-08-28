# Workspace, RBAC and Collaboration

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define multi-user/agency architecture before implementation so a single-user launch does not create a data model that later requires destructive redesign.

## Workspace model

A user may belong to zero or more workspaces.

Workspace fields include:
- stable workspace ID;
- name/slug;
- owner membership;
- plan/entitlements;
- default locale/timezone/currency;
- security policy;
- provider/social connections;
- project defaults/presets;
- retention policy;
- billing profile reference;
- status (`ACTIVE | RESTRICTED | SUSPENDED | DELETION_PENDING | DELETED`).

Personal onboarding creates an initial workspace even when only one user exists.

## Membership lifecycle

`INVITED -> ACTIVE -> SUSPENDED | REMOVED`

Membership records:
- user;
- workspace;
- role(s);
- invite source;
- joined timestamp;
- last role change;
- status;
- delegated scopes if supported;
- audit metadata.

Removing membership does not delete the user’s account.

## Baseline roles

### Owner
Full workspace governance, ownership transfer, billing/admin/security controls subject to step-up authentication.

### Admin
Manage most workspace settings, members and resources, but cannot silently transfer ownership or exceed specifically reserved owner-only actions.

### Producer
Create/manage projects, generation workflows, assets, provider usage within policy/budget; no billing/security administration by default.

### Editor
Edit project creative/editorial state, storyboard/timeline/audio/assets according to project permissions; may generate within allowed policy.

### Reviewer
Review, comment, compare, approve/reject if approval policy grants it; limited editing.

### Viewer
Read-only access to allowed workspace/projects/assets.

### Publisher
Manage publishing packages/schedules/accounts according to granted scopes; public-publish rights can be distinct from general editing.

### Billing
View/manage billing/subscription/usage according to commercial policy without granting creative/admin access.

A user can hold multiple composable roles if product chooses, but effective permission resolution must be deterministic.

## Permission domains

Canonical permissions are capability keys, not role-name conditionals.

Examples:
- `workspace.read`
- `workspace.settings.manage`
- `workspace.members.invite`
- `workspace.members.remove`
- `workspace.roles.manage`
- `workspace.ownership.transfer`
- `project.create`
- `project.read`
- `project.edit`
- `project.delete`
- `project.generate`
- `project.approve`
- `asset.read/download/delete`
- `character.manage/lock`
- `provider.connect/use/manage`
- `social.connect/publish/manage`
- `billing.read/manage/adjust`
- `api.manage`
- `security.manage`
- `audit.read`
- `support_access.approve` where applicable.

Roles map to permission sets versioned in canonical policy.

## Resource scoping

Permissions evaluate:
- workspace;
- project;
- asset/entity;
- provider/social connection;
- publication campaign;
- billing/security scope.

Initial v1 can use workspace-wide roles plus project membership overrides. Architecture must permit future project-specific roles without changing resource ownership model.

## Project access

Project visibility modes:
- `WORKSPACE_DEFAULT`
- `RESTRICTED_MEMBERS`
- `REVIEW_LINK_ONLY` for narrowly scoped external review artifacts, not full membership.

Restricted project membership cannot grant permissions above the user’s workspace/security/entitlement ceilings.

## Invitations

Invite fields:
- workspace;
- recipient email/identity hint;
- intended roles;
- inviter;
- expiry;
- token hash/reference;
- status;
- accepted user;
- created/accepted/revoked timestamps.

Rules:
- invite token single-use/expiring;
- acceptance requires matching/verified identity policy;
- inviter cannot grant permissions they are not allowed to grant;
- role changes after invitation require fresh permission check;
- invitations can be revoked;
- duplicate invitations deduplicated.

## Ownership transfer

Transfer requires:
- current owner authorization;
- eligible active destination member;
- step-up authentication;
- confirmation;
- billing/security implications surfaced;
- audit event.

Workspace always has one canonical owner unless enterprise policy explicitly permits another ownership structure.

Owner leaving requires transfer or workspace deletion workflow.

## Custom roles

Product stance:
- architecture supports permission-bundle custom roles;
- initial launch may disable custom-role creation;
- `TEAM/ENTERPRISE` entitlement can enable later;
- custom roles cannot grant reserved platform/system permissions;
- role definition changes are versioned/audited.

This decision prevents future data-model redesign while keeping v1 UI simpler.

## Collaboration objects

### Comment
- author;
- workspace/project/resource;
- body;
- mentions;
- created/edited/deleted;
- resolved state when attached to review issue;
- visibility.

### Annotation
Attach to:
- timeline time range;
- shot/take;
- frame coordinate/region where supported;
- image region;
- audio time range;
- text/script location.

### Review thread
Groups comments/annotations around a reviewable version.

### Mention
Notifies only users who can already access the referenced resource.

## Share/review links

External review link is a scoped capability, not full account impersonation.

Fields:
- target version/resource;
- permissions (`VIEW | COMMENT | APPROVE` as explicitly enabled);
- expiry;
- optional password/verified email;
- max uses/session policy if desired;
- revocation;
- watermark/download policy;
- audit.

Default:
- no provider/billing/settings access;
- no hidden project data beyond target;
- no generated API credentials;
- download disabled unless explicitly allowed.

## Approval delegation

Approval policy can define:
- required permission/role;
- one-of or N-of-M approvers;
- separate creative, cost, rights, publishing approvals;
- escalation/expiry;
- delegation allowed or prohibited;
- self-approval restrictions where appropriate.

Delegation record binds scope and expiry; it does not permanently grant role permissions.

## Concurrency and version conflicts

Versioned mutable resources use optimistic concurrency/version numbers or equivalent.

On stale edit:
- preserve user draft;
- refuse silent overwrite;
- show changed version/actor;
- merge only for resource types with safe deterministic merge;
- otherwise require reload/compare/manual resolution.

For timeline/storyboard, operation-level collaboration may later use more advanced synchronization, but v1 must still preserve version conflict safety.

## Locks

Differentiate:
- creative/entity lock (character/look canon);
- edit lease/soft lock for concurrent editing;
- approval lock/frozen version;
- system workflow lock.

One lock type must not be reused ambiguously for another.

## Audit log

Tenant audit events include:
- invite/member/role changes;
- ownership transfer;
- project delete/restore;
- provider/social connect/revoke;
- billing/admin/security changes;
- approval decisions/delegation;
- share-link creation/revoke/use where appropriate;
- support/admin access;
- API key/webhook changes.

Audit record:
- actor/effective actor;
- workspace;
- action;
- target;
- before/after summary where safe;
- IP/session/request context where privacy permits;
- timestamp;
- reason/case for privileged admin actions.

Audit records must not contain secrets.

## Workspace suspension/restriction

States may be triggered by:
- owner/admin action;
- billing state;
- security/abuse action;
- deletion flow.

Restriction policy explicitly controls:
- sign-in;
- read access;
- new generation;
- publishing;
- API access;
- provider/social token use;
- exports/deletion/support access.

Billing failure should not immediately make data inaccessible without the commercial grace policy.

## Enterprise identity

Architecture reserves future support for:
- SAML/OIDC enterprise SSO;
- domain verification;
- SCIM provisioning;
- enforced MFA;
- session duration policy;
- audit export.

Launch stance: `NOT_REQUIRED_FOR_INITIAL_V1`, but identity/member schema must not prevent it later.

## Tenant isolation tests

Mandatory tests:
- user in Workspace A cannot enumerate/read/mutate Workspace B resources;
- shared asset IDs do not bypass tenant checks;
- vector memory is tenant-scoped;
- signed URLs cannot access another tenant’s object;
- reviewer link only exposes target;
- removed member loses access promptly;
- role downgrade invalidates prohibited actions;
- background jobs re-check relevant authorization/policy where long-lived actions require it.

## Collaboration notifications

Events:
- invitation;
- mention;
- comment/reply;
- approval request/result;
- role change;
- ownership transfer;
- share-link activity where configured.

Notification delivery follows Pack E rules.

## UI areas

Workspace settings:
- Members
- Roles
- Invitations
- Security
- Audit Log
- Billing
- Providers
- Social Accounts

Project UI:
- members/access;
- comments/annotations;
- review status;
- version/activity.

## Acceptance criteria

Implementation can determine without new planning:
- workspace/membership lifecycle;
- baseline roles + permission-key model;
- project/resource scoping;
- invitations/ownership/custom-role stance;
- comments/annotations/review links;
- approval delegation;
- concurrency/conflict/lock semantics;
- tenant audit requirements;
- enterprise identity future boundary.
