# Core Domain Model — Milestone 1

## Status

Implementation started. The canonical Python contracts live in `packages/python-core/src/lullabies_core/` and are designed to export JSON Schema for API/storage interoperability.

The existing repository-first kids content package is preserved. `schemas/content-package.schema.json` remains a legacy/importable contract until a migration adapter is implemented; it is not silently rewritten by Milestone 1.

## Domain hierarchy

The editorial/production hierarchy is:

`Project -> Act -> Sequence -> Scene -> Shot -> Take`

Reusable entities exist outside that hierarchy and are referenced by stable IDs:

- Character / CharacterVersion / CharacterLook
- World / Location
- Prop
- StyleProfile
- VoiceProfile
- Content / ContentVersion
- Asset
- ProviderModelRef
- GenerationAttempt
- Job
- QARecord
- CostRecord
- RightsRecord
- Approval

## Stable ID namespaces

Initial namespaces:

- `PRJ-######` Project
- `CNT-######` Content
- `CTV-######` ContentVersion
- `CHR-######` Character
- `CHV-######` CharacterVersion
- `LOOK-######` CharacterLook
- `WRL-######` World
- `LOC-######` Location
- `PRP-######` Prop
- `STY-######` StyleProfile
- `VOC-######` VoiceProfile
- `ACT-######` Act
- `SEQ-######` Sequence
- `SCN-######` Scene
- `SHT-######` Shot
- `TAK-######` Take
- `TML-######` Timeline
- `TRK-######` TimelineTrack
- `AST-######` Asset
- `JOB-######` Job
- `ATT-######` GenerationAttempt
- `QAR-######` QARecord
- `CST-######` CostRecord
- `RGT-######` RightsRecord
- `APR-######` Approval

Numeric suffixes are repository/test-friendly initial identifiers. Runtime database implementation may use UUID/ULID primary keys internally while preserving these stable external/public IDs.

## Project contract

A Project owns product-level intent, not provider-specific settings.

Required concepts:
- audience profile;
- cast profile;
- content format;
- language;
- target duration;
- output format;
- creative treatment;
- provider/cost policy reference;
- reusable characters/worlds/props;
- active content/timeline references.

Project duration is currently constrained to `60..10800` seconds (1 minute through 3 hours).

### Audience and cast are separate

Do not store `kids|adult|man|woman|both` as one overloaded field.

Use:
- AudienceProfile: who the media is for;
- CastProfile.ages: apparent cast age categories;
- CastProfile.genders: cast gender presentation categories.

This avoids ambiguity such as an adult-targeted project starring children, or a family-targeted project with adult and non-human characters.

## Character invariants

Character identity is versioned.

`Character` points to an active `CharacterVersion`.

A `CharacterVersion` contains canonical identity data and one or more `CharacterLook` records.

Locks are explicit:
- global;
- project;
- look;
- scene;
- unlocked.

A locked scope must pin a CharacterVersion. Project and scene locks must also identify their scope target.

Provider-specific references are derived data and must never replace the canonical CharacterVersion.

## World/location/prop/style/voice

These are first-class reusable entities because continuity failures are not limited to faces.

A World establishes global setting rules.
A Location is a reusable place, optionally inside a World.
A Prop carries stable visual identity/constraints.
A StyleProfile defines treatment/palette/lighting/camera/negative rules.
A VoiceProfile stores provider-neutral voice intent plus optional provider voice references.

## Content contracts

`Content` is stable identity/lineage.
`ContentVersion` contains versioned canonical script/lyrics and production intent.

Existing `CNT-*` repository packages will later be imported by an explicit adapter.

No Milestone 1 change deletes or mutates existing approved packages.

## Timeline contracts

Timeline duration is independent of provider clip duration.

A Shot contains:
- exact edit time range;
- purpose/action;
- characters/location/props;
- camera intent;
- incoming continuity state;
- outgoing continuity state;
- optional first/end frames;
- references;
- generated Takes;
- selected Take;
- transitions;
- render handles.

Provider calls create Takes; they do not redefine the canonical Shot.

A failed Take therefore does not invalidate the Shot plan.

## Continuity state

Continuity is explicit and provider-independent.

Initial fields:
- character states;
- prop states;
- environment state;
- camera state;
- lighting state;
- motion state;
- notes.

Later milestones may normalize frequently queried subfields into typed nested models after real production fixtures prove the required granularity.

## Production and generation

### Job

Represents a durable unit of requested work and owns:
- idempotency key;
- dependencies;
- state;
- retry budget;
- attempts;
- lease/claim data;
- blocked reason.

### GenerationAttempt

Represents one provider/model attempt for a Job.

It records:
- provider/model/access class;
- canonical GenerationRequest;
- provider generation ID;
- timestamps;
- output assets;
- normalized error;
- free credits / paid cost;
- QA record IDs.

Failed attempts remain history.

### Asset

Every media/document asset has:
- stable ID;
- URI;
- SHA-256;
- MIME;
- size;
- optional duration/resolution;
- parent assets;
- provider/attempt lineage;
- rights record;
- canonical status;
- retention class.

Raw binaries do not belong in normal Git history.

## QA, cost, rights and approval

These are separate entities rather than fields hidden inside provider responses.

- QARecord can hard-fail safety/identity/license-sensitive gates.
- CostRecord makes free credits and paid spend auditable.
- RightsRecord blocks publication by default until commercial-use state is resolved.
- Approval represents explicit human/system policy decisions.

## Repository-first to PostgreSQL migration boundary

### Current phase

Git remains canonical for:
- engineering policy;
- schemas/contracts;
- prompts;
- research;
- provider source definitions;
- current legacy content/memory records;
- generated/exported manifests.

### Runtime application phase

PostgreSQL becomes canonical operational state for:
- projects;
- content versions;
- reusable entities;
- timelines;
- jobs/attempts;
- assets metadata;
- QA/cost/rights/approvals;
- publishing/analytics.

Object storage becomes canonical for large media bytes.

### Migration rule

Do not switch source-of-truth silently.

Implement an explicit importer/reconciler that:
1. reads existing Git-backed content/memory;
2. validates legacy schemas;
3. maps to current domain contracts;
4. writes idempotently to PostgreSQL;
5. records import lineage;
6. emits a reconciliation report;
7. leaves original Git history untouched.

## Contract source of truth

Python/Pydantic models are the executable domain contract during Milestone 1.

`packages/python-core/scripts/export_schemas.py` exports provider/API-neutral JSON Schemas under `schemas/generated/`.

Later FastAPI OpenAPI contracts should reuse these domain types rather than redefine them independently.

## Compatibility principles

- additive changes first;
- schema version fields on persisted entities;
- no silent enum/semantic changes;
- breaking changes require migration + rollback documentation;
- stable IDs survive provider changes;
- provider IDs never become domain primary keys;
- accepted Takes/assets are versioned, not destructively overwritten.

## Milestone 1 exit criteria

Before Milestone 1 is DONE:
- domain tests must pass;
- Ruff/static checks must pass;
- schema export must execute;
- committed/generated schemas must be reconciled;
- representative 2-minute song project must validate;
- representative 90-minute movie project must validate;
- character lock invalid cases must fail validation;
- legacy content import boundary must be documented;
- checkpoint must identify remaining persistence decisions.
