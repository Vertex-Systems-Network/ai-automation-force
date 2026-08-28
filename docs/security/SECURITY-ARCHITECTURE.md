# Security Architecture

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define the application, identity, tenant, secrets, upload, webhook, provider, build and runtime security contract before implementation.

This document complements the AI-specific threat model. Current reference inputs include OWASP ASVS 5.x, NIST digital-identity guidance and WebAuthn/passkey standards; implementation must revalidate exact current versions.

## Security principles

- deny by default;
- least privilege;
- tenant isolation is enforced server-side;
- no security decision relies only on frontend state or model output;
- secrets are referenced, not exposed;
- external inputs/files/webhooks are untrusted;
- privileged/destructive actions require stronger authentication/authorization;
- all high-impact actions are auditable;
- reversible/contained failure is preferred;
- production and non-production trust boundaries remain separate.

## Identity model

Canonical account supports:
- email/password where enabled;
- federated sign-in (Google, Apple and future providers);
- passkeys/WebAuthn;
- MFA authenticators;
- recovery mechanisms;
- session/device records;
- verified email state;
- account security events.

The exact set enabled at launch is configurable.

## Password policy

If passwords are supported:
- allow long passwords/passphrases;
- do not impose arbitrary composition rules that reduce usability;
- block known compromised/common passwords using a privacy-preserving method where practical;
- normalize/validate length safely;
- hash using a modern memory-hard password hashing algorithm with versioned parameters;
- password reset invalidates or re-evaluates sensitive sessions according to policy;
- never log plaintext passwords or reset secrets.

Exact password length/algorithm parameters are implementation-time security configuration and must follow current guidance.

## Passkeys and MFA

Passkeys/WebAuthn are first-class strong-authentication candidates.

MFA methods may include:
- passkey/WebAuthn;
- TOTP;
- recovery codes;
- other standards-based methods when explicitly approved.

SMS is not a preferred primary MFA factor; if ever supported, it requires explicit risk analysis.

Sensitive operations can require step-up authentication even during a valid session.

## Step-up authentication

Require recent strong authentication for configured high-risk actions such as:
- changing password/email/MFA;
- generating/revoking recovery codes;
- connecting/revoking provider/social accounts;
- viewing/copying sensitive credential metadata;
- changing workspace ownership/admin roles;
- billing/payment changes;
- creating API credentials;
- account/workspace deletion;
- security policy changes.

## Session architecture

Session record includes:
- stable session ID;
- user;
- authentication methods/assurance;
- issued/last-used/expiry timestamps;
- device/user-agent/IP-derived risk metadata where privacy policy permits;
- revoked timestamp/reason;
- refresh/rotation state.

Rules:
- secure, HttpOnly, SameSite cookies for browser sessions where architecture uses cookies;
- CSRF protections for state-changing requests as appropriate;
- refresh/session token rotation;
- logout current/all sessions;
- revoke sessions on critical account events;
- absolute + idle expiration policy;
- session enumeration in account security UI;
- do not rely on client-stored role/entitlement claims without server validation.

## OAuth/OIDC account linking

Rules:
- use standards-compliant authorization code + PKCE where applicable;
- validate issuer, audience, nonce/state and redirect URI;
- never automatically merge accounts from unverified/untrusted email coincidence;
- linking an additional login method requires authenticated/verified user intent;
- detect provider-subject identity collisions;
- recovery flow avoids account takeover through OAuth linking.

## Signup and abuse controls

Layered controls:
- email verification;
- IP/device/rate heuristics where lawful;
- bot challenge/risk service where needed;
- progressive throttling;
- disposable/abusive signup heuristics as advisory signals;
- trial/credit abuse protections;
- breached credential checks where appropriate;
- no single heuristic becomes irreversible identity truth.

Rate-limit:
- signup;
- login;
- reset;
- verification resend;
- MFA attempts;
- provider/social OAuth callbacks;
- API key creation;
- expensive generation endpoints.

## Authorization

Authorization is evaluated using:
- authenticated principal;
- workspace membership/role;
- resource tenant ownership;
- resource-level permission;
- entitlement;
- approval/lock state;
- security policy.

Every resource query/mutation is tenant-scoped server-side.

Do not infer authorization from URL IDs, frontend visibility, AI instructions or provider responses.

## Service-to-service identity

API, worker, Temporal, media processors and internal services use scoped service identities.

Rules:
- least-privilege credentials;
- environment-specific identities;
- rotation;
- no shared global admin secret across all services;
- auditable access;
- short-lived credentials/identity federation where infrastructure supports it.

## Secrets management

Secrets include:
- provider API keys;
- social OAuth tokens;
- billing webhook secrets;
- JWT/session signing material if applicable;
- encryption keys;
- database/object-storage credentials;
- email/webhook credentials.

Requirements:
- central secret manager/KMS abstraction in production;
- envelope encryption for sensitive stored tokens where needed;
- no secrets in Git, client bundles, logs, analytics, prompts or support screenshots;
- version/rotation metadata;
- revoke/rotate workflow;
- scope by workspace/provider/account;
- access only in workers/services requiring the secret;
- redacted administrative display.

## Encryption

- TLS for network transport;
- storage encryption at rest through platform/object-store/DB capabilities;
- application-level encryption for especially sensitive secrets/tokens where justified;
- key hierarchy/versioning;
- rotation strategy;
- backups follow same sensitivity controls.

## Webhook security

Incoming webhooks:
- verify provider signature using raw body as required;
- validate timestamp/replay window where supported;
- event ID/idempotency record;
- payload size/schema limits;
- map external IDs to tenant/account safely;
- unknown events fail closed/recorded;
- async processing after verification;
- do not trust webhook URLs/accounts from payload when canonical mapping exists.

Outgoing webhooks are Pack F scope but require signing, retries and secret rotation.

## SSRF-safe URL retrieval

Any server-side fetch of user/provider URLs must:
- allow only `http/https` where appropriate;
- resolve and block loopback/link-local/private/internal ranges unless explicitly internal;
- protect against DNS rebinding/redirect chains;
- cap redirects/size/time;
- validate MIME/content;
- use dedicated egress controls where production supports them;
- never forward internal credentials to arbitrary destinations.

## File/media upload security

Uploads are untrusted.

Pipeline:
`Upload -> Size/Type Gate -> Quarantine -> Hash -> MIME/Magic Validation -> Malware/Threat Check as applicable -> Media Probe in Sandbox -> Metadata Policy -> Accept/Reject -> Canonical Asset`

Controls:
- direct signed uploads use constrained object key/size/type/expiry;
- filename never becomes trusted filesystem path;
- decompression/archive bombs blocked if archive support exists;
- image/video/audio parsers run resource-limited;
- SVG/HTML/scriptable files treated carefully or disallowed where not needed;
- metadata may be stripped for derivatives where appropriate;
- rejected/quarantined objects have retention/cleanup policy.

## FFmpeg/media processing isolation

- dedicated worker class;
- no shell command construction from raw user strings;
- parameterized/allowlisted operations;
- CPU/memory/time/disk/process ceilings;
- network access disabled unless explicitly required;
- temp directory isolation;
- input/output paths scoped to job;
- cleanup after termination;
- vulnerable media library updates tracked.

## API security

- request size limits;
- strict schemas;
- structured errors without sensitive stack details;
- idempotency for side effects;
- rate limits by principal/workspace/action;
- pagination/cursor limits;
- signed URLs for large objects;
- CORS explicit allowlist;
- CSRF strategy if cookies;
- security headers;
- no mass assignment of privileged fields;
- ownership checked after lookup and before action.

## Tenant isolation

Required at:
- DB queries/repositories;
- object storage keys/access;
- vector-memory queries;
- cache keys;
- job/workflow IDs;
- logs/analytics/support tools;
- provider/social account mappings;
- signed asset URLs.

Cross-tenant fixture tests are mandatory.

## Admin/support access

Admin access is not equivalent to unrestricted silent impersonation.

Rules:
- separate privileged roles;
- step-up auth;
- reason/case reference for sensitive support access;
- audit trail;
- customer-visible support access history where product policy chooses;
- impersonation default stance defined in Support/Admin spec;
- secrets remain masked.

## Security logging

Security events include:
- login success/failure/risk block;
- password/MFA/passkey changes;
- recovery use;
- session revoke;
- role/ownership changes;
- provider/social/API credential connect/revoke;
- billing/security setting changes;
- blocked authorization;
- webhook signature/replay failure;
- suspicious upload;
- AI privilege escalation blocks;
- admin/support access.

Logs are tamper-resistant enough for audit goals and exclude raw secrets.

## Secure SDLC

Before release, pipeline should include appropriate:
- dependency vulnerability scanning;
- secret scanning;
- SAST;
- container/image scanning;
- IaC scanning;
- SBOM generation;
- license policy checking;
- lockfile integrity;
- code review;
- security tests mapped to current baseline (e.g. OWASP ASVS where applicable).

Critical findings block release according to master QA matrix.

## Dependency/provider supply chain

- pin/lock dependencies;
- automated update review;
- provenance/signature verification where ecosystem supports it;
- minimal third-party SDK permissions;
- provider SDK is not trusted to bypass HTTP/business validation;
- deprecations/advisories tracked by provider scout/security process.

## Security headers/browser

Preplan use of:
- CSP;
- HSTS;
- frame-ancestors/clickjacking control;
- Referrer-Policy;
- Permissions-Policy;
- secure cookies;
- content-type protections.

Exact policy tuned to Next.js/product integrations; do not weaken CSP merely for convenience without review.

## Incident containment

Security architecture must support:
- revoke user/session/provider/social/API credentials;
- suspend workspace/account;
- disable provider/publishing adapter;
- disable feature via controlled flag;
- stop workers/jobs;
- rotate secrets;
- preserve evidence;
- notify affected users according to incident/legal policy.

## Reference posture

As of August 2026:
- OWASP ASVS lists 5.0.0 as current stable;
- NIST SP 800-63B-4 is current digital-authentication guidance;
- WebAuthn Level 3 is advancing through W3C Recommendation process.

These are implementation reference baselines, not hard-coded product-version dependencies.

## Acceptance criteria

Implementation can determine without new architecture planning:
- identity/session/MFA/passkey model;
- step-up actions;
- OAuth linking rules;
- tenant authorization;
- secrets/encryption lifecycle;
- webhook/SSRF/upload/media controls;
- service identities;
- secure SDLC/supply-chain expectations;
- security telemetry/containment.
