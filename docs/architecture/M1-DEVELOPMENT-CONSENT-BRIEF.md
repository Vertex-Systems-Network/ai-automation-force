# Milestone 1 — Development Consent Brief

Status: `PLANNING_READY_FOR_CONSENT`

This document defines the next executable development scope. No implementation in this scope should begin until the operator explicitly approves it.

## 1. Milestone / scope

Continue **Milestone 1 — Core domain model and repository migration boundary** only.

Proposed executable scope:

1. Commit/reconcile generated JSON Schema artifacts from current Pydantic contracts.
2. Add full lineage fixtures/tests covering:
   - Character -> CharacterVersion -> CharacterLock;
   - Asset -> RightsRecord;
   - Job -> GenerationAttempt -> QARecord -> CostRecord;
   - Shot -> Take -> selected canonical take;
   - publication-blocked rights default.
3. Define and implement the legacy importer boundary from existing `schemas/content-package.schema.json` packages into generalized `Content` / `ContentVersion` domain records without mutating legacy files.
4. Stabilize aggregate validation for the currently modeled hierarchy and references.
5. Design and implement the initial PostgreSQL persistence mapping for the stabilized Milestone 1 contracts only, including migration scaffolding and reversible initial migration(s).
6. Add migration/contract tests required to prove the persistence mapping.
7. Update architecture/checkpoint documentation with verified results.

## 2. Why now

Milestone 2 will introduce durable orchestration and runtime jobs. Starting Temporal/FastAPI/provider integrations before domain/persistence contracts stabilize would create avoidable migration and compatibility risk.

The current Pydantic contracts and aggregate validator already establish the domain vocabulary. The correct next step is to make those contracts persistable, migratable and backwards-compatible with the existing repository-first content history.

## 3. Expected files/components

Likely affected areas:

- `packages/python-core/`
- `packages/python-core/tests/`
- `schemas/generated/`
- new persistence package/module under the agreed monorepo boundary
- PostgreSQL model/migration files
- migration/legacy-import tests
- `docs/architecture/DOMAIN-MODEL.md`
- persistence/migration ADR or architecture document
- checkpoints
- CI configuration only if required to validate this approved Milestone 1 scope

Exact file names may be refined during implementation without expanding the approved product scope.

## 4. Behavioral changes

After the proposed scope:

- current domain contracts will have committed machine-readable JSON Schema artifacts;
- the system will be able to validate complete lineage fixtures, not only isolated entities;
- legacy kids content packages will have a defined/importable mapping into the generalized content domain;
- operational Milestone 1 records will have a PostgreSQL persistence model;
- migrations will be reproducible/reversible where practical;
- no AI provider generation, Temporal workflow, web UI or publishing behavior will be introduced yet.

## 5. Data / migration impact

Current repository-backed content/history must remain unchanged.

The persistence design must:

- treat legacy files as import sources, not rewrite targets;
- preserve stable external IDs such as `PRJ-*`, `CHR-*`, `CNT-*`, `SHT-*` where applicable;
- use internal database primary keys separately from external stable IDs;
- enforce uniqueness and referential integrity;
- provide deterministic/repeatable import behavior;
- avoid duplicate import on retry;
- document rollback and migration assumptions.

Recommended internal DB identifier strategy remains UUID/ULID-like internal keys plus stable human/audit external IDs, subject to implementation validation.

## 6. Security / rights / cost impact

Security/data:

- no API/provider credentials required for this scope;
- no paid AI calls required;
- no public publishing;
- rights/provenance records remain fail-closed for publication;
- migration/import code must treat repository content as untrusted input and validate before persistence;
- database credentials must be environment-managed and never committed.

Cost:

- no AI provider spend is authorized or required by this scope;
- infrastructure/runtime database cost is outside this code-development authorization unless separately configured by the operator.

## 7. Tests / verification

Proposed gates:

- Ruff/format/lint as configured;
- Pydantic/schema generation checks;
- unit tests for all new lineage invariants;
- legacy importer tests, including retry/idempotency and invalid input;
- database model/constraint tests;
- migration upgrade test;
- migration downgrade/rollback test where practical;
- uniqueness/referential-integrity tests;
- representative 2-minute song persistence round trip;
- representative 90-minute movie-plan persistence round trip;
- >3-hour rejection remains protected;
- existing domain tests must remain green.

No test will be reported as passed unless actually executed.

## 8. Rollback / recovery

Implementation should be additive.

Rollback strategy:

- existing repository content remains untouched;
- initial DB migration must be reversible where practical;
- importer must be repeatable/idempotent rather than destructive;
- generated schema artifacts can be regenerated from versioned domain models;
- no existing canonical asset/content deletion is part of this scope;
- if persistence design proves incorrect, it can be reverted before Milestone 2 without losing legacy repository history.

## 9. Explicitly out of scope

This consent would NOT authorize:

- Temporal workflows;
- FastAPI product endpoints beyond any minimal internal test scaffolding strictly required for M1 (default: none);
- Gemini/Lyria/Veo/Kling/Runway/Pika/Hailuo provider integration;
- actual AI content/audio/video generation;
- object storage/media uploads;
- FFmpeg render pipeline;
- Character UI;
- Next.js frontend;
- mobile app;
- YouTube publishing;
- analytics;
- authentication/RBAC;
- autonomous paid spend;
- public deployment;
- Milestone 2 or later development.

## 10. Consent request

Before implementing the scope above, the operator must explicitly approve Milestone 1 development.

Suggested approval phrase:

`Milestone 1 development approve — start.`

Any equally clear instruction approving this described implementation scope is valid.
