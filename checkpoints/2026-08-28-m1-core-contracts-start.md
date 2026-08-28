# Checkpoint — Milestone 1 Core Contracts Started

Date: 2026-08-28
Status: PARTIALLY COMPLETE

## Objective

Start Milestone 1 from `docs/architecture/DEVELOPMENT-PLAN.md`: establish provider-neutral typed domain contracts before database, orchestration, provider integration, or UI work.

## Completed

### Python core package

Created `packages/python-core/` using Python 3.12+ and Pydantic v2.

Implemented contracts for:
- Project
- AudienceProfile
- CastProfile
- output/creative/provider-policy profiles
- Character
- CharacterVersion
- CharacterLook
- CharacterLock
- World
- Location
- Prop
- StyleProfile
- VoiceProfile
- Content
- ContentVersion
- Act
- Sequence
- Scene
- Shot
- Take
- Timeline
- Asset
- ProviderModelRef
- GenerationRequest
- GenerationAttempt
- Job
- QARecord
- CostRecord
- RightsRecord
- Approval

### Domain invariants implemented

- Project duration: minimum 60 seconds, maximum 10,800 seconds (3 hours).
- Audience and cast dimensions are separate.
- Custom content format requires an explicit custom value.
- Locked character scopes require a pinned CharacterVersion.
- Project character lock requires Project ID.
- Scene character lock requires Scene ID.
- Look character lock requires Look ID.
- Shot selected Take must belong to Shot take list.
- Job selected GenerationAttempt must belong to Job attempt list.
- Asset SHA-256 and stable ID formats validate.
- Rights records default to publication-blocked until resolved.

### Schema export

Added `packages/python-core/scripts/export_schemas.py` to export Pydantic validation contracts as JSON Schema Draft 2020-12 documents under `schemas/generated/`.

### Tests

Added `packages/python-core/tests/test_domain.py` covering:
- two-minute song project;
- 90-minute movie project;
- >3-hour project rejection;
- locked character version requirement;
- look-lock look-pin requirement.

### CI

Added `.github/workflows/core-contracts.yml` for:
- Ruff;
- pytest;
- schema export;
- compileall.

### Architecture documentation

Added `docs/architecture/DOMAIN-MODEL.md` covering relationships, stable ID namespaces, provider-independent Take/Shot separation, character locking, continuity, asset/provenance records, and the Git-backed -> PostgreSQL migration boundary.

Existing `schemas/content-package.schema.json` remains untouched and importable. Milestone 1 is additive; legacy content/history is not rewritten.

## Verification

### Verified locally in isolated Python environment

- Pydantic import/model construction works.
- 23 primary domain models successfully produce validation JSON Schema.
- representative tests: 5/5 passed.
- two-minute project validated.
- 90-minute project validated.
- 10,801-second project rejected.
- invalid project/look character locks rejected.

Local verification runtime used Python 3.13 + Pydantic 2.13, which is compatible with but not identical to the target Python 3.12 environment.

### GitHub Actions — NOT VERIFIED

Workflow run `33183484774` concluded failure before any workflow step executed.

Observed:
- `runner_id: 0`
- empty runner name
- zero job steps
- approximately two-second job lifetime

This indicates GitHub Actions runner/infrastructure/organization configuration failure rather than a recorded Ruff/pytest/code failure. No claim is made that GitHub-hosted CI passed.

## Known gaps before Milestone 1 can be DONE

1. Run CI on an available GitHub-hosted or configured self-hosted runner.
2. Commit/reconcile exported `schemas/generated/*.schema.json` outputs or formally decide build-generated-only policy.
3. Add cross-entity aggregate validators/services for:
   - unique ordering inside hierarchy;
   - timeline/project duration agreement;
   - scene/shot duration boundaries;
   - reference existence;
   - version pin existence;
   - no overlapping canonical primary video edits where disallowed.
4. Add test fixtures for full Character/Asset/Job/Attempt/QA/Rights lineage.
5. Add explicit legacy `content-package.schema.json` -> `Content/ContentVersion` importer design/implementation.
6. Decide runtime internal primary-key strategy (recommended DB UUID/ULID + stable external IDs) during PostgreSQL schema work.
7. Add PostgreSQL table/migration design only after core contracts stabilize.

## Security/data notes

- No secrets added.
- Provider IDs remain references, not domain primary keys.
- Rights default is fail-closed for publication.
- Large media remains URI/hash based and out of ordinary Git history.
- Existing canonical content/history was not mutated.

## Recommended next action

Continue Milestone 1 with aggregate validation + committed schema artifacts + lineage fixtures. Then design PostgreSQL persistence mapping without beginning Temporal/provider integrations yet.
