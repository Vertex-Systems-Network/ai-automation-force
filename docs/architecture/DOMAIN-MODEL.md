# Core Domain Model — Milestone 1

## Status

M01/WP1 contract freeze implemented and verified on Python 3.12 CI.

Canonical public Python import surface:
`packages/python-core/src/ai_automation_force_core/`

The historical `lullabies_core` namespace remains temporarily available only as a compatibility surface for pre-M01 repository code.

The existing repository-first content packages are preserved. `schemas/content-package.schema.json` remains a legacy/importable contract until the explicit M01 importer is implemented; it is not silently rewritten.

## Domain hierarchy

`Project -> Act -> Sequence -> Scene -> Shot -> Take`

Reusable/versioned entities include:
- Character / CharacterVersion / CharacterLook
- World / Location / Prop
- StyleProfile / VoiceProfile
- Content / ContentVersion
- Asset
- ProviderModelRef
- GenerationAttempt / Job
- QARecord / CostRecord / RightsRecord / Approval

## Schema versioning

Persisted M01 entities carry `schema_version` as an executable literal contract. Version 1 models reject incompatible version values rather than accepting an arbitrary integer.

Breaking semantic changes require an explicit version/migration path; they must not be hidden behind the same schema version.

## Stable external IDs

Canonical external/public IDs retain their existing prefixes and six-digit fixtures, but the numeric suffix can scale from 6 through 20 digits. Examples:
- `PRJ-000001` Project
- `CNT-000001` Content
- `CTV-000001` ContentVersion
- `CHR-000001` Character
- `CHV-000001` CharacterVersion
- `LOOK-000001` CharacterLook
- `WRL-000001` World
- `LOC-000001` Location
- `PRP-000001` Prop
- `STY-000001` StyleProfile
- `VOC-000001` VoiceProfile
- `ACT-000001` Act
- `SEQ-000001` Sequence
- `SCN-000001` Scene
- `SHT-000001` Shot
- `TAK-000001` Take
- `TML-000001` Timeline
- `TRK-000001` TimelineTrack
- `AST-000001` Asset
- `JOB-000001` Job
- `ATT-000001` GenerationAttempt
- `QAR-000001` QARecord
- `CST-000001` CostRecord
- `RGT-000001` RightsRecord
- `APR-000001` Approval

These IDs are durable business/audit identifiers, not a commitment to use text IDs as PostgreSQL primary keys. Persistence may use native UUIDs internally while preserving stable external IDs.

## Registry-owned taxonomy boundary

Audience, cast and content-format taxonomies are registry-owned product data. Core contracts therefore validate these fields structurally as non-empty bounded strings instead of making the Pydantic package the only accepted-value registry.

Built-in enums remain convenience constants for known values, including `custom`, cast `none/custom`, and `trailer-teaser` compatibility.

Rules:
- registry validation is applied at the product/config boundary;
- core schemas remain forward-compatible with approved registry additions;
- `content_format=custom` requires `custom_content_format`;
- a non-custom format rejects an unrelated custom-format payload.

This prevents a configuration-valid project from becoming backend-invalid merely because a taxonomy entry was added without a core-package release.

## Project contract

A Project owns provider-neutral product intent:
- audience profile;
- cast profile;
- content format;
- language;
- duration;
- output profile;
- creative treatment;
- provider/cost policy reference;
- reusable characters/worlds/props;
- active content/timeline references.

Project/content duration is constrained to `60..10800` seconds (1 minute through 3 hours).

Audience and cast remain separate concepts; `kids|adult|man|woman|both` is not stored as one overloaded field.

## Character/entity invariants

Character identity is versioned. A lock pins the required CharacterVersion and, when applicable, project/look/scene scope.

World, Location, Prop, StyleProfile and VoiceProfile are first-class reusable entities because continuity is broader than face identity.

All canonical entity references use typed ID aliases so malformed cross-domain IDs fail before persistence or provider execution.

## Content contracts

`Content` is stable identity/lineage. `ContentVersion` contains versioned canonical script/lyrics and production intent.

Existing `CNT-*` repository packages are imported later by an explicit idempotent adapter; no M01 migration silently mutates the source packages.

## Timeline contracts

Timeline duration is independent of provider clip duration.

A Shot contains exact edit time range, creative purpose/action, entity references, camera intent, incoming/outgoing continuity state, optional first/end frames, references, Takes, selected Take, transitions and render handles.

Provider calls create Takes; they do not redefine the canonical Shot. A failed Take therefore does not invalidate the Shot plan.

## Production/generation contracts

### Job
Owns durable requested-work state, idempotency key, dependencies, retries, attempts, lease/claim information and blockers.

### GenerationAttempt
Represents one provider/model attempt and records typed status, request, provider route, timestamps, outputs, normalized errors, cost/credits and QA references. Failed attempts remain history.

Attempt timestamps are timezone-aware and cannot finish before they start.

### ProviderModelRef
Provider provenance separates:
- `provider_id` — API transport/billing provider;
- `model_provider_id` — underlying model vendor;
- `model_id` — concrete model identifier.

For direct APIs, `model_provider_id` normalizes to `provider_id`. For gateways/aggregators they may differ. This distinction is mandatory for cost, rights, provenance and incident analysis.

### Asset
Every asset records stable ID, URI, SHA-256, MIME/size, optional media dimensions/duration, parent lineage, provider/model/attempt provenance, rights, canonical status and retention class.

Provider output URLs are not assumed to be durable canonical storage.

## QA, cost, rights and approval

These remain explicit entities rather than unstructured provider-response fields.

- QARecord carries normalized gate outcomes.
- CostRecord rejects negative credit/spend values and keeps provider/model provenance.
- RightsRecord defaults to publication-blocked until commercial-use evidence is resolved.
- Approval uses typed decisions.

## Audit timestamps

Canonical audit timestamps are timezone-aware. `updated_at` cannot precede `created_at`. Equivalent chronology checks apply to generation attempts where both endpoints exist.

## Repository-first to PostgreSQL boundary

Git remains canonical for engineering policy, schemas/contracts, prompts, research, provider source definitions and legacy repository records.

PostgreSQL becomes canonical runtime operational state for projects, versions, reusable entities, timelines, jobs/attempts, asset metadata, QA/cost/rights/approvals and later product state. Object storage becomes canonical for large media bytes.

Source-of-truth migration is explicit and idempotent:
1. read legacy Git-backed records;
2. validate legacy schemas;
3. map to current contracts;
4. write transactionally/idempotently;
5. preserve source lineage;
6. produce reconciliation evidence;
7. leave original Git history untouched.

## Generated contract artifacts

`packages/python-core/scripts/export_schemas.py` deterministically exports Draft 2020-12 JSON Schemas under `schemas/generated/`.

Schema IDs use:
`urn:ai-automation-force:schema:v1:<artifact>`

`schemas/generated/manifest.json` stores the schema version, base ID and SHA-256 digest for each generated artifact.

CI executes exporter `--check` and fails if a generated file is missing, stale or drifted.

## Static/compatibility gates

M01 core CI on Python 3.12 runs:
- Ruff;
- strict mypy;
- pytest;
- generated-schema drift verification;
- Python compile/import validation.

The canonical package distribution is `ai-automation-force-core`. New code imports `ai_automation_force_core`; the historical namespace is transitional compatibility only.

## M01 boundaries

M01 does not implement provider APIs, Temporal workflows, product FastAPI endpoints, object storage, FFmpeg production rendering, web/mobile UI, auth, billing, social publishing or deployment.

Provider/model/API versions remain mutable facts and are revalidated in their later implementation milestones.

## M01 exit criteria

Before M01 is complete:
- WP1 contract freeze is accepted;
- full lineage fixtures/invariants are covered;
- aggregate validation is hardened;
- legacy content import is implemented idempotently;
- PostgreSQL mapping/migrations/repositories are verified;
- 2-minute, 90-minute and 180-minute representative round trips pass;
- over-3-hour input is rejected;
- rollback/recovery evidence exists;
- final M01 checkpoint is recorded.
