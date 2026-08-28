# Authentication & Onboarding Edge-Case Specification

## Purpose

Define the non-happy-path behavior for signup, login, verification, password reset, onboarding and provider connection before authentication development begins.

This document covers product behavior and security expectations only. It does not authorize implementation.

---

## 1. Account lifecycle

Suggested states:
- `PENDING_VERIFICATION`
- `ACTIVE`
- `LOCKED_TEMPORARILY`
- `DISABLED`
- `DELETION_REQUESTED`
- `DELETED/ANONYMIZED` according to retention/legal policy

Onboarding state is separate:
- `NOT_STARTED`
- `IN_PROGRESS`
- `SKIPPED_OPTIONAL_STEPS`
- `COMPLETE`

A verified account may still have incomplete onboarding.

---

## 2. Signup cases

### New email/password signup
- validate email format;
- enforce password policy;
- accept required legal terms;
- create pending account;
- send verification;
- do not expose password in logs/events.

### Email already registered with password
Return safe `account already exists / sign in` UX without leaking unnecessary account details.

### Email already registered through OAuth/social
Offer safe sign-in/account-linking path rather than silently creating a duplicate identity.

### Signup interrupted after account creation
User can resume verification/onboarding later.

### Verification email delivery failure
Account remains pending; user can resend within rate limits.

### Multiple signup submissions
Use idempotent handling where practical; do not create duplicate User/Workspace records.

---

## 3. Email verification cases

Token requirements:
- random/unpredictable;
- single-purpose;
- expiring;
- single-use;
- securely stored/hashed where appropriate.

Cases:
- valid token -> verify;
- expired token -> offer resend;
- used token -> safe already-verified response;
- malformed token -> generic failure;
- account already verified -> route to login/onboarding;
- account disabled -> do not reactivate by verification token.

Resend requests must be rate-limited.

---

## 4. Login cases

Support:
- correct credentials;
- incorrect credentials;
- unverified account;
- temporarily rate-limited/locked;
- disabled account;
- social identity/provider failure;
- expired callback/state;
- session expired;
- intended-route redirect after login.

Do not produce errors that enable easy account enumeration.

---

## 5. OAuth/social login cases

For each configured provider:
- validate state/nonce/PKCE according to implementation choice;
- handle user cancel;
- handle provider outage;
- handle denied consent;
- handle missing/hidden email;
- handle provider email not verified;
- handle email collision with existing password identity;
- handle previously linked identity;
- handle revoked identity later.

Account linking must require a trustworthy proof path, not email-string equality alone when the identity provider does not establish verified ownership.

---

## 6. Password reset cases

Request page returns a generic acknowledgement whether or not the email exists.

Reset token:
- expiring;
- single-use;
- invalidated after successful reset;
- bound to intended account/action.

After reset:
- record security event;
- invalidate old reset tokens;
- evaluate whether to revoke other sessions according to policy;
- notify account owner when appropriate.

Cases:
- expired token;
- reused token;
- malformed token;
- disabled account;
- social-only account without local password;
- repeated requests/rate limiting.

---

## 7. Session behavior

Plan for:
- secure HttpOnly cookies where browser session architecture uses cookies;
- Secure flag in production;
- appropriate SameSite policy;
- CSRF protection where required;
- session rotation on login/privilege-sensitive change;
- explicit logout;
- session expiry;
- revoke-all-sessions capability later;
- device/session listing later if justified.

Avoid long-lived bearer secrets in local storage when safer session architecture is available.

---

## 8. Onboarding resumability

Every onboarding step should persist independently.

If user closes browser after Step 2:
- resume at Step 3;
- do not ask completed questions again unless defaults changed;
- do not lose provider connection state.

User may skip optional steps and finish onboarding.

Required steps should be minimal.

---

## 9. Provider connection during onboarding

Cases:
- provider connected successfully;
- invalid credential;
- credential accepted but required capability unavailable;
- provider API temporarily unavailable;
- credential lacks required permissions;
- free tier/no API route;
- connection skipped;
- provider already connected;
- replacing/revoking existing connection.

Connecting a provider must not:
- trigger generation automatically;
- authorize paid spend by itself;
- expose credential after storage;
- create multiple same-provider connections merely to rotate quotas.

Provider connection record should show safe metadata such as:
- provider;
- status;
- account label if appropriate;
- capabilities;
- last validation time;
- masked credential identifier if useful;
- revoke/replace action.

---

## 10. Workspace bootstrap

Recommended first-user flow:
- signup creates User;
- create default Workspace (`My Workspace` or generated name);
- assign owner membership;
- onboarding/defaults belong to Workspace;
- provider connections belong to Workspace;
- projects/assets belong to Workspace.

This enables later team features without moving project ownership from User to Workspace.

Detailed RBAC remains a separate pre-development specification for multi-user scope.

---

## 11. First project handoff

On onboarding completion, user may:
- create blank project;
- choose preset;
- open read-only demo;
- return to dashboard.

First Project CTA should open the same canonical New Project Wizard used inside the app.

Do not create a billable provider job as an implicit onboarding side effect.

---

## 12. Empty states

After signup with no providers/projects:
- explain that providers can be connected later;
- allow exploration of demo/read-only screens where product permits;
- show `Create Project` and `Connect Provider` as separate actions;
- do not imply the account is broken.

---

## 13. Abuse/rate-limit planning

Apply risk-based protections to:
- signup;
- login;
- verification resend;
- password reset;
- OAuth callbacks where appropriate;
- provider connection validation.

Potential controls:
- per-IP/per-account throttling;
- progressive cooldown;
- bot protection when abuse justifies it;
- security logging;
- alerting for abnormal failure patterns.

Do not make CAPTCHA mandatory everywhere by default if rate limiting/risk controls are sufficient.

---

## 14. Audit/security events

Record relevant events without secrets:
- signup created;
- email verified;
- login success/failure category;
- password changed/reset;
- provider identity linked/unlinked;
- provider credential connected/revoked;
- session revoked;
- account disabled/deletion action;
- onboarding completed.

Security logs must never include passwords, raw tokens or provider secrets.

---

## 15. Account deletion planning

Before implementation define:
- user-initiated deletion flow;
- grace period if any;
- project/media deletion vs retention;
- billing/legal retention obligations;
- provider credential revocation/removal;
- analytics anonymization;
- audit-log retention;
- restore policy if any.

Do not add destructive account deletion until this retention/deletion policy is approved.

---

## 16. Authentication acceptance criteria

Authentication/onboarding planning is implementation-ready when:
- signup/login/verification/reset states are defined;
- duplicate/social identity behavior is explicit;
- session/security boundaries are explicit;
- onboarding is resumable;
- provider connection errors have defined states;
- no provider spend occurs implicitly;
- workspace bootstrap is future-safe;
- rate-limit/security-event requirements are known;
- destructive account deletion is separately gated.
