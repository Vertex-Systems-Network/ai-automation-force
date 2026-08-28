# PostgreSQL Migration Operating Procedure

Status: M01/WP6

## Scope

This runbook covers the M01 application schema managed by Alembic under:

`packages/python-core/migrations/`

The application schema is `core`. Alembic's version table remains outside `core` so the empty/test downgrade may remove the entire application schema without deleting the migration-control table mid-revision.

## Configuration

Database configuration is environment-only.

Required variable:

`DATABASE_URL`

Example shape only — do not copy credentials into the repository:

`postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE`

The migration environment intentionally fails when `DATABASE_URL` is absent. There is no committed development password, localhost fallback, or production default.

## Tooling baseline verified for WP6

The WP6 CI path uses stable release lines selected on 2026-08-29:

- SQLAlchemy 2.0.x;
- Alembic 1.19.x;
- Psycopg 3.3.x;
- PostgreSQL 18 service in CI.

Dependency ranges are declared in `packages/python-core/pyproject.toml`.

## Upgrade

From repository root:

```bash
alembic -c packages/python-core/alembic.ini upgrade head
```

Expected first revision:

`20260829_0001`

The initial revision creates the `core` schema, M01 tables, relationship tables, constraints and indexes. It does **not** import repository content or call providers.

Running `upgrade head` again when already at head is expected to be a no-op.

## Current revision

```bash
alembic -c packages/python-core/alembic.ini current --check-heads
```

This should fail non-zero if the configured database is not at all migration heads.

## Test/empty database downgrade

```bash
alembic -c packages/python-core/alembic.ini downgrade base
```

The initial downgrade drops the `core` schema with `CASCADE`. This behavior exists to make the initial migration fully reversible on empty/test databases and is exercised by CI.

## Production rollback safety

`downgrade base` is **destructive once operational data exists**. It is not the normal production rollback mechanism after launch.

For a populated environment:

1. stop or drain writers;
2. capture/verify backup according to the future production backup runbook;
3. determine whether the application release can roll back while keeping the forward-compatible schema;
4. prefer a corrective forward migration when data-preserving rollback requires schema change;
5. use a destructive downgrade only with an explicit data-loss-approved recovery plan.

WP6's successful downgrade test proves schema reversibility on disposable databases. It does not authorize production data deletion.

## Immutable migration artifacts

Files tied to revision `20260829_0001` are versioned migration evidence:

- `migrations/versions/20260829_0001_core_schema.py`
- `migrations/sql/0001_core_schema_up.sql`
- `migrations/sql/0001_core_schema_down.sql`

Once merged and used outside disposable test environments, do not rewrite this revision to alter deployed databases. Add a new Alembic revision instead.

## Secrets and data

Migrations must never:

- contain database passwords/tokens;
- embed provider credentials;
- auto-import Git repository legacy content;
- call external AI/media providers;
- publish content;
- delete repository history.

## CI acceptance

The permanent `Core Domain Contracts` workflow starts PostgreSQL 18 and verifies:

1. clean `upgrade head`;
2. exact expected `core` table set;
3. Alembic head revision;
4. stable external-ID uniqueness;
5. Rights fail-closed publication constraint;
6. mandatory `Content.active_version_id` persistence constraint;
7. repeated `upgrade head` no-op;
8. `downgrade base` removes `core`;
9. clean re-upgrade succeeds;
10. existing Ruff/mypy/unit/schema-sync/compile gates remain green.
