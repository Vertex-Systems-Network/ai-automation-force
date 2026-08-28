# Rights, Consent & Provenance Specification

## Purpose

Define the evidence and publication rules for generated, imported and derived content/assets. Technical QA does not make an asset legally or commercially publishable by itself.

## Core principles

- Every material asset has lineage.
- Provider commercial-use terms and source identity consent are separate concerns.
- Imported assets are not assumed licensed because the user can upload them.
- Unresolved material rights state is fail-closed for public/commercial publication.
- Evidence should include source/date/version where terms can change.

## RightsRecord categories

Record where applicable:
- source ownership;
- provider/model/tier;
- provider commercial-use status;
- watermark restrictions;
- source license;
- public-domain basis;
- user-supplied permission assertion;
- real-person likeness consent;
- voice consent/cloning authorization;
- music/lyrics/recording rights;
- trademark/brand usage rights;
- archival/stock/media license;
- geographic/term restrictions;
- attribution requirements;
- platform restrictions;
- verification/evidence URLs/files;
- verification timestamp;
- reviewer/decision.

## Rights states

Suggested normalized states:
- UNKNOWN;
- EVIDENCE_REQUIRED;
- REVIEW_REQUIRED;
- CLEARED_INTERNAL_USE;
- CLEARED_NONCOMMERCIAL;
- CLEARED_COMMERCIAL;
- RESTRICTED;
- BLOCKED;
- EXPIRED_OR_STALE.

## Provider-generated assets

For each provider/model/tier capture:
- exact provider/model;
- access tier/account class;
- generation timestamp;
- current commercial-use evidence status;
- watermark status;
- relevant terms/source URL/date;
- provider generation ID;
- prompt/version/hash;
- source/reference asset IDs.

A free plan may have different commercial terms from a paid/API plan. Do not infer one from the other.

## Real people / likeness

If using an identifiable real person as visual identity/reference, store where relevant:
- person/reference ID;
- consent/authorization basis;
- permitted use scope;
- expiry/territory where applicable;
- restrictions;
- source evidence.

Do not silently transform a generic character into a recognizable real person.

## Voice / cloning

For a real identifiable person's voice or uploaded voice sample:
- consent/authorization is required where applicable;
- permitted usage scope is recorded;
- provider voice-clone policies remain independently applicable.

Default system behavior should use licensed/provider voices or original synthetic voice profiles rather than imitating celebrities/real people.

## Music

Separate rights layers:
- lyrics/text;
- composition/melody;
- arrangement;
- recording/master;
- generated output license;
- imported sample/loop licenses.

A public-domain composition does not automatically make a modern arrangement/recording public domain.

Generated song QA should flag suspicious imitation of a protected song/artist style where relevant.

## Characters and fictional IP

Original recurring characters should have:
- canonical creation source;
- creator/project ownership metadata;
- reference asset lineage;
- lock/version history.

Do not intentionally create close copies of protected branded characters/universes.

## Imported assets

Import flow should request/source:
- asset origin;
- ownership/license basis;
- permitted commercial use;
- attribution if any;
- real-person consent if relevant;
- modification rights;
- redistribution restrictions.

Missing declaration may allow private planning use but should block public/commercial use according to policy.

## Documentary/factual media

Distinguish:
- actual source footage/photo;
- licensed archival material;
- generated reenactment/illustration;
- synthetic visual approximation.

Do not represent generated visuals as authentic evidence when they are not.

## Provenance graph

Every derived asset links to parents.

Example:
`Imported Character Reference -> CharacterVersion -> Keyframe -> Video Take -> Approved Shot -> Final Master`

Rights restrictions must propagate downstream where applicable.

## Rights propagation

If parent asset is `BLOCKED` or has attribution/restriction, derived assets inherit the relevant constraint unless an explicit transformation/license review establishes otherwise.

Changing provider/tier/source may require re-verification of rights even if visual output appears identical.

## Terms freshness

Mutable provider/platform terms should carry:
- `verified_at`;
- evidence URL;
- optional freshness policy.

Before material commercial/publication use, stale or changed terms can trigger recheck.

Daily provider scout may report terms/licensing changes but must not automatically reinterpret complex legal rights or enable risky publication behavior without review.

## Publication gate

Before public/commercial publishing verify:
- final master RightsRecord resolved;
- all material upstream restrictions compatible;
- required attribution prepared;
- watermark restrictions satisfied;
- identity/voice consent resolved;
- platform-specific disclosure/review complete.

Unresolved state => `blocked-license` / review required.

## Deletion/revocation

If consent/license is revoked/expired where applicable:
- mark affected canonical source;
- traverse downstream asset graph;
- block new publication/use;
- create review/remediation task;
- preserve audit history according to retention/legal policy rather than silently rewriting history.

## Security/privacy

Rights evidence may contain sensitive/private documents. Do not place private consent documents or personal data in public Git. Store protected references/metadata in appropriate secure storage and expose only necessary status in project manifests.

## Acceptance criteria

Rights/provenance planning is development-ready when every publishable final asset can answer: where did it come from, which provider/source/assets contributed, what rights/consent apply, what evidence supports that status, and whether publication is currently allowed.