# M01 / WP2 — Full Production Lineage Complete

Date: 2026-08-29

Status: `M01_DEVELOPMENT_IN_PROGRESS`

Work package: `WP2 — Full lineage model fixture`

## Result

WP2 is implementation-complete and verified on Python 3.12.

The core now has an additive `ProductionLineageBundle` that validates the provider-neutral production lineage around the existing editorial `ProjectBundle` without introducing provider execution, persistence, Temporal, UI, publishing, or M02+ behavior.

The representative lineage connects:

`Project -> Content -> ContentVersion -> Character -> CharacterVersion -> CharacterLock -> Timeline -> Act -> Sequence -> Scene -> Shot -> Take -> Job -> GenerationAttempt -> Asset -> QARecord -> CostRecord -> RightsRecord`

## Proven invariants

- stable external IDs survive full model dump/validation round trips;
- project content and active timeline references resolve to the loaded canonical identities;
- content versions cannot silently reference unloaded characters/worlds/props;
- project/scene/look character locks must resolve inside the loaded project graph;
- a project lock may remain pinned to an approved historical CharacterVersion while the Character active version advances;
- jobs, attempts, request project/shot/content references, and attempt membership remain consistent;
- generated assets retain exact attempt/provider/model lineage;
- input/output/parent asset references must resolve and asset-parent cycles are rejected;
- Takes resolve to the intended Shot, Attempt, generated Asset, and QA subject;
- actual CostRecords require and match the concrete generation attempt/provider/model;
- Asset rights references resolve to the actual asset subject;
- rights remain fail-closed: publication cannot be unblocked unless commercial use is explicitly `ALLOWED`.

## Generated contract

Additive Draft 2020-12 artifact:

`schemas/generated/production-lineage-bundle.schema.json`

The normal generated-schema synchronization gate verifies the artifact against source contracts.

## Verification evidence

GitHub Actions workflow: `Core Domain Contracts`

Run: `33217247563`

Job: `99003521049`

Verified successful gates:

- Ruff;
- strict mypy;
- unit tests, including full lineage positive/negative fixtures;
- generated-schema synchronization;
- Python compile/import check.

## Scope boundary preserved

WP2 did **not** implement:

- provider API calls or generation;
- Temporal workflows;
- PostgreSQL models/migrations/repositories;
- FastAPI/UI/auth;
- object storage/FFmpeg runtime;
- publishing/analytics;
- M02+ behavior.

## Next authorized work

Within the already-approved M01 scope, the next work package is:

`WP3 — Aggregate validation hardening`

WP3 should extend only invariants supported by the current domain model and must not invent unresolved editorial semantics.
