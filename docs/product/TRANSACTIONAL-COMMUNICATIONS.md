# Transactional Communications

## Status

`PREDEVELOPMENT_READY`

## Purpose

Define service email, mobile push and other transactional communication behavior before implementation. Marketing campaigns are outside this contract unless separately enabled.

## Communication categories

### Identity/account
- verify email;
- password reset;
- email change confirmation;
- new login/session/security alert;
- MFA/passkey/recovery change;
- account export/delete lifecycle.

### Workspace/collaboration
- invitation;
- ownership transfer;
- member/role change when policy requires;
- mention/comment/review;
- approval request/reminder/result.

### Production
- long-running generation/render completion;
- terminal generation/render failure;
- manual handoff required;
- provider reconnect required;
- quota/budget threshold;
- rights/consent blocker;
- export ready.

### Publishing/social
- scheduled publication reminder where configured;
- publish failure;
- manual handoff;
- account/token reauthorization;
- post rejected/restricted where surfaced.

### Billing
- trial ending;
- subscription change;
- invoice/receipt availability;
- payment failed/recovered;
- restriction/grace-period warning;
- credit expiry where configured.

### Security/incident
- important account/security changes;
- workspace security policy change;
- credential/API key creation/revocation where configured;
- incident/customer-action notice.

## Channel policy

Channels:
- `IN_APP`
- `EMAIL`
- `PUSH`
- `WEBHOOK` when developer webhooks are enabled.

Each communication template declares:
- category;
- severity;
- required/optional channels;
- whether user can opt out;
- recipient resolution;
- dedupe/grouping;
- urgency;
- localization key/version;
- data sensitivity.

## Mandatory vs optional

Essential transactional/security messages cannot be treated as marketing opt-in.

Examples generally mandatory while relevant:
- email verification/reset;
- password/security changes;
- critical payment/account restriction;
- account deletion/export security confirmations.

Optional service notifications can be disabled or digested according to preferences.

Marketing/promotional communications require separate consent/unsubscribe architecture if introduced.

## Email address states

Per user/contact:
- unverified;
- verified;
- bounced temporary;
- bounced permanent;
- complaint/suppressed;
- changed pending verification.

Security-critical recovery should not depend on a known-undeliverable address without alternate recovery policy.

## Template model

`CommunicationTemplate`
- stable template key;
- version;
- locale;
- subject key/content;
- HTML body;
- plain-text body;
- variables/schema;
- action-link type;
- expiry messaging;
- sender identity class;
- category/severity;
- legal/footer rules.

Templates are versioned; message records keep template version used.

## Rendering

Template rendering validates required variables before sending.

Rules:
- escape untrusted/user content;
- do not allow project titles/comments to inject HTML;
- no secrets in template variables;
- links use canonical application origins;
- action links encode opaque short-lived tokens or signed references, not raw user secrets;
- plain-text alternative required for email;
- responsive accessible markup.

## Identity/action links

Verification/reset/invite/export/delete links require:
- single-purpose token;
- expiry;
- single-use where appropriate;
- server-side hash/storage or equivalent secure design;
- bind to intended account/action;
- invalidate on state changes where appropriate;
- generic failure messages that avoid account enumeration.

## Sender identities

Separate logical sender classes:
- account/security;
- product operations;
- billing;
- support.

Domain/provider implementation may share infrastructure but templates and reply handling must be intentional.

## Reply behavior

Every email declares one of:
- no-reply with clear support route;
- monitored support reply;
- conversation/thread route when collaboration email replies are deliberately supported.

Do not imply replies are monitored when they are not.

## Deliverability

Prelaunch operational requirements:
- SPF;
- DKIM;
- DMARC policy staged appropriately;
- verified sending domain;
- bounce/complaint webhooks;
- suppression handling;
- rate/volume monitoring;
- separate marketing stream if introduced;
- provider reputation monitoring.

Exact email vendor remains replaceable.

## Idempotency and deduplication

Every send attempt links to source event and a communication idempotency key.

Examples:
- same password-reset request can intentionally create a new token/message, but retries of the same send job do not send duplicates;
- provider outage groups repeated failures;
- approval reminder cadence is controlled, not emitted on every workflow poll.

## Retry policy

Classify delivery errors:
- transient provider/network -> bounded retry/backoff;
- permanent invalid recipient -> suppress/fail final;
- provider rate limit -> delayed retry;
- template/schema error -> internal failure, no blind retry loop.

Communication failure does not roll back the underlying business transaction unless the business flow explicitly requires confirmed delivery.

Example: successful payment remains successful even if receipt email temporarily fails.

## User preferences

Preferences store category/channel choices.

Constraints:
- critical account/security/service messages cannot all be disabled;
- marketing preferences separate;
- workspace-wide notification policies can set defaults/required classes within product/legal bounds;
- individual user can reduce optional noise.

## Digest

Daily/weekly digest can aggregate optional events:
- generation completions;
- project activity;
- approvals pending;
- usage/cost summary;
- publication/analytics highlights.

Critical security/payment/publish failures remain immediate.

## Push notifications

When mobile is enabled:
- device tokens are per user/device/app environment;
- revoke invalid tokens;
- privacy mode controls sensitive preview text;
- deep links are authenticated and resource-authorized after app open;
- push payload does not contain secrets or large private content;
- no assumption that push delivery is guaranteed.

## Workspace contacts

Separate contact roles may exist:
- billing contact;
- security contact;
- workspace owner/admin;
- publication approvers.

Recipient resolution uses current canonical roles/contacts, not stale copied email lists.

## Localization

- locale preference per user;
- fallback locale;
- locale-aware date/time/timezone/currency;
- pluralization;
- RTL-compatible templates;
- action timestamps use explicit timezone/absolute date for security/scheduling.

## Message history

Store delivery metadata:
- communication ID;
- recipient reference/address as privacy policy permits;
- template/version;
- source event;
- channel;
- queued/sent/delivered/bounced/failed state where provider exposes it;
- timestamps;
- external provider message ID;
- retry count;
- suppression reason.

Do not store full sensitive rendered message indefinitely unless required; retention depends on class.

## Provider abstraction

Email/push vendor adapter contract supports:
- send;
- delivery/bounce/complaint webhook;
- provider message ID;
- normalized error;
- rate-limit metadata;
- template-independent payload where rendering is internal or explicitly delegated.

No product logic should depend on one email vendor’s template naming.

## Security

- provider credentials secret-managed;
- webhook verification;
- no open redirect in action links;
- no user-controlled From/Reply-To injection;
- CRLF/header injection blocked;
- HTML escaping;
- security emails avoid revealing too much account state to unverified recipients;
- support tooling masks sensitive content.

## Testing

Required:
- template schema tests for every locale;
- HTML/plain-text snapshot/accessibility checks;
- expired/used token flows;
- bounce/suppression;
- duplicate event dedupe;
- security notification preference override;
- timezone/localization;
- malicious user-supplied title/comment escaping;
- provider retry/final failure;
- push deep-link authorization.

## Acceptance criteria

Implementation can determine:
- transactional categories/templates;
- mandatory vs optional delivery;
- template/token/security model;
- preferences/digest;
- email deliverability/bounce/suppression;
- push behavior;
- vendor abstraction;
- history/retention/testing.
