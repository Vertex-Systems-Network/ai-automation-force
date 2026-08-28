# M01 / WP4 — Legacy Content Import Boundary Complete

Date: 2026-08-29

Status: `M01_DEVELOPMENT_IN_PROGRESS`

Work package: `WP4 — Legacy CNT content importer boundary`

## Result

WP4 is implementation-complete and verified on Python 3.12.

The core now has a deterministic, provider-neutral compatibility boundary for legacy `schemas/content-package.schema.json` v1 packages. The mapper accepts parsed legacy metadata plus explicitly resolved exact content text, validates compatibility with current canonical contracts, and returns generalized `Content`, `ContentVersion`, and an import report without filesystem reads or persistence side effects.

## Proven behavior

- legacy source payload is never mutated;
- stable `CNT-*` identity is preserved;
- first canonical version identity is deterministic (`CNT-000321` -> `CTV-000321`, version 1);
- exact content/performance text is preserved without rewriting;
- source status, timestamps, provenance path, objective, premise/hook, tags/topics and originality fingerprint are mapped deterministically;
- documented lullaby modes refine safely to `spoken-lullaby` or `sung-lullaby`;
- free-text legacy character names/settings never fabricate canonical Character/World/Location IDs;
- missing duration, incompatible duration, malformed metadata, empty exact content and invalid timestamp chronology fail explicitly;
- deterministic SHA-256 source fingerprint/import key is generated;
- reconciliation is pure and returns `create`, `noop`, or fail-closed `conflict`;
- exact repeat import is idempotency-ready and becomes a `noop` once the same canonical records are persisted;
- changed source material under the same stable legacy identity is a conflict rather than an overwrite;
- partial or drifted persisted state is a conflict requiring recovery.

## Mapping contract

Canonical documentation:

`docs/architecture/LEGACY-CONTENT-IMPORT-BOUNDARY.md`

Mapping version:

`legacy-content-v1-to-core-v1`

## Repository evidence limitation

At implementation time `memory/content-index.json` contains no legacy catalogue items. WP4 therefore does not claim that a real production catalogue migration has already run.

Acceptance uses a schema-faithful representative legacy fixture. Actual legacy packages, when available, must pass through the same deterministic mapper/reconciliation boundary and be recorded as migration evidence.

## Verification evidence

GitHub Actions workflow: `Core Domain Contracts`

Run: `33218758449`

Job: `99008142155`

Verified successful gates:

- Ruff;
- strict mypy;
- unit tests, including positive, negative, deterministic and reconciliation cases;
- generated-schema synchronization;
- Python compile/import check.

## Scope boundary preserved

WP4 did **not** implement:

- PostgreSQL writes, tables, migrations or repositories;
- filesystem traversal/mutation of legacy packages;
- AI/media provider execution;
- Temporal workflows;
- FastAPI/UI/auth;
- publishing/analytics;
- M02+ behavior.

## Next authorized work

Within the already-approved M01 scope, the next work package is:

`WP5 — PostgreSQL persistence architecture`

WP5 should define the relational persistence mapping, constraints, transaction boundaries and repository contracts for the stabilized canonical domain without yet applying irreversible production migrations.
