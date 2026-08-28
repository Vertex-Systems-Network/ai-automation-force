# Public Launch Legal Requirements

## Status

`PREDEVELOPMENT_READY_AS_PRODUCT_REQUIREMENTS`

This is a product/legal dependency checklist, not jurisdiction-specific legal advice. Final legal text and applicability must be reviewed against launch countries, business model, data flows and provider terms before public launch.

## Purpose

Ensure product architecture already knows which legal/compliance surfaces, records and user choices it must support before implementation begins.

## Required public legal surfaces

At minimum preplan routes/documents for:
- Terms of Service;
- Privacy Policy;
- Acceptable Use Policy;
- Cookie/Tracking Notice and consent where required;
- AI/Synthetic Media disclosures/policy;
- Copyright/IP complaint process;
- account/data deletion instructions;
- billing/refund/cancellation terms when paid plans launch;
- subprocessor list where applicable;
- security contact/vulnerability reporting;
- contact/legal entity details required by applicable commerce laws.

## Terms of Service product dependencies

Terms must align with actual product behavior for:
- account eligibility;
- workspace/team authority;
- acceptable content;
- user-owned/imported content rights;
- generated output ownership/licensing position;
- provider-dependent commercial rights limitations;
- prohibited impersonation/deceptive content;
- automation limits;
- social publishing responsibility;
- API/BYOK credential responsibility;
- suspension/termination;
- beta/experimental features;
- service availability;
- fees/credits/refunds;
- dispute/law/jurisdiction clauses as advised legally.

Product UI must not promise rights or availability broader than terms/provider facts.

## Privacy Policy dependencies

Privacy documentation must accurately describe:
- account/profile data;
- authentication/session/security data;
- project/prompts/media/assets;
- provider/social credentials and metadata;
- billing/tax data;
- product analytics;
- social publishing/analytics data;
- support communications;
- AI provider data sharing;
- retention/deletion/export;
- cookies/tracking;
- subprocessors;
- international transfers/residency where relevant;
- user rights/contact channels.

The privacy policy must map to `DATA-PRIVACY-LIFECYCLE.md`, not describe fictional deletion or residency guarantees.

## Acceptable Use Policy

Must address at least:
- unlawful content/use;
- sexual exploitation/CSAM;
- non-consensual intimate content;
- impersonation/deception/fraud;
- harassment/hate/violent abuse as legally/product-policy relevant;
- malware/phishing/credential theft;
- rights infringement;
- evasion of platform/provider quotas/ToS;
- unauthorized surveillance/privacy abuse;
- harmful automated social behavior/spam;
- provider credential misuse;
- attempts to bypass security/entitlement controls.

Enforcement paths must exist in support/admin/moderation architecture.

## Copyright and rights

Product must support records for:
- user assertion of rights to uploads;
- provider/model commercial-use restrictions;
- music/voice/character/likeness consent;
- public-domain/source provenance;
- generated asset lineage;
- takedown/copyright complaints;
- project/publication blocking where rights are unresolved.

Do not claim AI output is universally copyrightable or exclusively owned; legal position varies and must be reviewed.

## Voice, likeness and identity

Before enabling cloned/custom voices, real-person likeness or imported identity references, product policy must define:
- consent/authorization requirement;
- proof/attestation record;
- prohibited uses;
- revocation handling;
- publication blocking;
- provider-specific restrictions;
- abuse escalation.

## Child-directed content

The platform may generate child-directed media, but should not become a child-directed user service by default.

Public launch requirements:
- clearly define intended account holder/user age;
- avoid knowingly collecting child personal data unless a separately approved compliance model exists;
- maintain kids/audience metadata and publishing requirements;
- revalidate applicable platform and jurisdiction requirements for child-directed content.

## Synthetic/AI media disclosure

Product must support per-project/per-publish disclosure state where platform/law requires or user chooses.

Record:
- whether content is AI-generated/altered;
- disclosure requirement source;
- disclosure text/metadata supplied;
- platform-specific synthetic-media flags;
- who approved disclosure state.

Do not hard-code one universal label; platform/law rules vary.

## Social publishing

Before public automation, legal/product policy must cover:
- authorized account ownership/permission;
- platform ToS/developer policies;
- app-review/scopes;
- prohibited spam/manipulation;
- scheduled/automated posting disclosures where applicable;
- platform-specific audience/synthetic-media requirements;
- deletion/edit responsibility;
- user responsibility for final published content.

No unofficial/private endpoint automation when official authorization is absent.

## Billing/consumer commerce

Paid launch must predefine:
- displayed price/currency/tax treatment;
- billing interval;
- trial terms;
- automatic renewal notice/consent where applicable;
- cancellation mechanism;
- downgrade effect;
- refund/credit policy;
- invoice/receipt fields;
- payment failure/dunning;
- local consumer cancellation/refund rights where applicable.

Commercial terms must match actual entitlement/billing behavior.

## Cookies and tracking

Public site/app inventories trackers into:
- essential;
- preferences;
- product analytics;
- marketing/advertising.

Architecture supports blocking non-essential trackers until consent where required and stores consent/version state if implemented.

## Data processing and subprocessors

Maintain contractual/inventory readiness for:
- hosting/cloud;
- AI generation providers;
- authentication providers;
- email;
- billing/tax;
- monitoring/error tracking;
- analytics;
- social platforms.

Enterprise customers may require DPA/subprocessor change processes; do not promise them until operationally supported.

## Data rights operations

Product/support must be capable of handling applicable:
- access/export;
- correction;
- deletion;
- objection/restriction where relevant;
- consent withdrawal;
- marketing unsubscribe.

Identity verification and audit apply to sensitive requests.

## Security and breach readiness

Before public launch:
- security contact/process exists;
- incident response and evidence preservation exists;
- affected data/tenants can be identified;
- notification decision/escalation can be made according to applicable law/contract;
- credential revocation/containment is operational.

## Moderation and complaints

Need documented intake/escalation for:
- abuse;
- rights/copyright;
- privacy/identity;
- security;
- billing;
- platform takedown/restriction.

Cases connect to admin audit and relevant project/account records.

## Public claims governance

Marketing cannot claim:
- “100% identical cross-provider output”;
- guaranteed copyright/ownership;
- “fully compliant everywhere”;
- unlimited/free usage when provider limits exist;
- security certifications not obtained;
- specific data residency not actually enforced;
- platform integrations/capabilities not currently verified.

Feature/landing claims should come from a versioned claim inventory linked to real product capability.

## Launch legal gate

Public production launch is blocked until:
- final legal entity/countries/business model are known;
- counsel/qualified review determines applicable documents/requirements;
- Terms/Privacy/AUP/Cookie texts are approved;
- billing/refund terms match product if paid;
- subprocessors/data flows are inventoried;
- deletion/export/privacy operations are testable;
- social/provider ToS/API facts are current;
- child-directed/synthetic-media behavior is reviewed;
- support/moderation/security contacts and workflows exist.

## Acceptance criteria

Architecture/planning is complete when implementation knows which legal states/records/UI flows must exist, while final jurisdiction-specific legal wording remains an external launch approval rather than first-time product planning during coding.
