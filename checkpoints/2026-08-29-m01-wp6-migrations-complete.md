# M01 / WP6 — Reversible PostgreSQL Migration Scaffold Complete

Date: 2026-08-29

Status: `M01_DEVELOPMENT_IN_PROGRESS`

Work package: `WP6 — Reversible initial database migrations`

## Result

WP6 is implementation-complete and verified against a real PostgreSQL 18 service in GitHub Actions.

The repository now contains an environment-configured Alembic migration scaffold, a versioned initial `core` PostgreSQL schema snapshot, reversible empty/test-database downgrade, permanent PostgreSQL-backed CI verification, and an operating runbook.

## Verified executable head

Executable revision verified by CI:

`43a11c5a2ef386298685341aacaab044fd9af0ba`

GitHub Actions workflow:

`Core Domain Contracts`

Run:

`33219768541`

Job:

`99011168309`

The CI service ran PostgreSQL 18 and its container logs reported PostgreSQL `18.6`.

## Successful gates

The verified run passed:

- PostgreSQL service initialization and health check;
- Python 3.12 dependency installation;
- Ruff;
- strict mypy including migration code;
- unit tests;
- real PostgreSQL migration integration tests;
- deterministic generated-schema synchronization;
- Python compile/import checks for package and migrations;
- service/container cleanup.

## Migration proof

Against the disposable PostgreSQL database the test verified:

1. clean `alembic upgrade head` succeeds;
2. the `core` schema is created;
3. the exact expected M01 table set exists;
4. Alembic revision is `20260829_0001`;
5. duplicate stable Project external IDs are rejected by PostgreSQL;
6. Rights cannot be publication-unblocked while commercial use is unresolved;
7. `Content.active_version_id` is mandatory at persistence level;
8. running `upgrade head` again is a no-op;
9. `downgrade base` removes the disposable `core` schema;
10. a clean re-upgrade succeeds after downgrade.

This is actual database execution evidence, not static SQL inspection.

## Migration/runtime contracts added

- `packages/python-core/alembic.ini`
- `packages/python-core/migrations/env.py`
- `packages/python-core/migrations/versions/20260829_0001_core_schema.py`
- `packages/python-core/migrations/sql/0001_core_schema_up.sql`
- `packages/python-core/migrations/sql/0001_core_schema_down.sql`
- `packages/python-core/migrations/script.py.mako`
- `packages/python-core/tests/test_migrations.py`
- PostgreSQL-backed `Core Domain Contracts` workflow
- stable SQLAlchemy/Alembic/Psycopg dependency ranges in `pyproject.toml`

Migration configuration requires `DATABASE_URL`; no production DB credential or secret fallback is committed.

## Documentation after green executable head

After executable head `43a11c5a...` was green, the following documentation-only operating guide was added:

`docs/operations/DATABASE-MIGRATIONS.md`

That documentation does not alter migration/runtime behavior. Any checkpoint/PR-description commits after the green executable head are likewise evidence-only.

## Production safety boundary

The successful `downgrade base` test proves reversibility on disposable/empty test databases.

It does **not** authorize destructive downgrade on a populated production database. Once operational data exists, production rollback should prefer backup-verified, data-preserving code/schema rollback or corrective forward migration. The runbook states this explicitly.

No real production database was migrated by WP6.

## Repository/data boundary preserved

WP6 did not:

- import any repository legacy `CNT-*` content;
- rewrite or delete Git-backed historical content;
- connect to a production database;
- commit provider or database secrets;
- implement persistence repository/service CRUD;
- execute AI/media providers;
- implement Temporal, auth/UI, publishing, analytics, or M02+ behavior.

## Next authorized work

Within the already-approved M01 scope:

`WP7 — Persistence repositories and round-trip verification`

WP7 must use the verified PostgreSQL schema to prove exact canonical write/read behavior for representative short and long projects, preserve selected/locked lineage, integrate WP4 legacy reconciliation transactionally, and prove transaction failure leaves no partial aggregate.
