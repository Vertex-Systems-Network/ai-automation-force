# M03-WP4 — Fresh-Main Replay Checkpoint

Status: `REPLAYED / FRESH VERIFICATION REQUIRED / GOVERNANCE BLOCKED`

Repository: `Vertex-Systems-Network/ai-automation-force`  
Linear: `ABD-203`  
Fresh branch: `agent/20260830-ai-automation-force-abd-203-fresh-main`  
Current governed-main base: `b23ba008a142e8974978bb4c8075943142772d97`  
Fresh replay implementation commit: `62ddb97100922482532cd60c5c6c1ab8b79af8fc`  
Historical source carrier: PR #33 / final source head `4fea2fefc44c022a1073765e133e4910f755c29f`  
Historical final reviewed code head: `df214410f040033097b3d2e018e3a8db3d3deb22`

## Why this carrier exists

The original WP4 branch and current `main` diverged after repository-governance tooling was accepted on `main`. The historical WP4 green checks therefore cannot be treated as current-main promotion evidence.

A two-way Git comparison established that:

- the WP4 candidate changes only provenance migration/domain/persistence/export/test paths plus its historical checkpoint;
- the intervening `main` changes only repository-governance workflow/document/applicator/verifier paths;
- there is no changed-path overlap between the reviewed WP4 implementation payload and the intervening governance-main changes.

The fresh carrier was therefore created from current `main` and the final reviewed WP4 implementation/test/migration **blobs were replayed exactly**, without force-moving the historical branch and without copying its now-stale checkpoint metadata.

## Exact replayed implementation paths

1. `packages/python-core/migrations/sql/0011_asset_provenance_down.sql`
2. `packages/python-core/migrations/sql/0011_asset_provenance_up.sql`
3. `packages/python-core/migrations/versions/20260830_0011_asset_provenance.py`
4. `packages/python-core/src/ai_automation_force_core/__init__.py`
5. `packages/python-core/src/lullabies_core/persistence/__init__.py`
6. `packages/python-core/src/lullabies_core/persistence/asset_provenance.py`
7. `packages/python-core/src/lullabies_core/provenance.py`
8. `packages/python-core/tests/test_asset_provenance_graph_authority.py`
9. `packages/python-core/tests/test_asset_provenance_persistence.py`
10. `packages/python-core/tests/test_asset_usability.py`
11. `packages/python-core/tests/test_migrations.py`

The fresh checkpoint itself is coordination evidence, not implementation authority.

## Retained WP4 boundary

The replay preserves only M03/WP4:

- append-only asset provenance records;
- storage-object ↔ canonical Asset linkage;
- source/import/provider evidence;
- derived-from lineage integrity;
- canonical/storage hash consistency;
- rights/licensing linkage;
- fail-closed chronology and project-boundary validation;
- usability evaluation without duplicating canonical Asset/Rights authority;
- migration and PostgreSQL acceptance coverage.

Still excluded: WP5 deterministic derivative generation, WP6 signed delivery, WP7 retention/archive/delete orchestration, M04+, unrestricted AI authority, unrelated refactors, and repository-admin configuration inside the WP4 code diff.

## Evidence state

Historical source evidence remains diagnostic/history only after replay:

- historical Core Domain Contracts: PASS;
- historical Durable Control Plane: PASS;
- historical review classification: `SELF REVIEW`;
- independent approval: not claimed.

The fresh replay head must independently pass the **current** repository workflows, including Repository Governance plus the current Core Domain Contracts and Durable Control Plane workflows. Review must be repeated on the fresh exact head.

## Live repository-governance blocker

Current live branch read-back after the governance-tooling merge still reports `main protected=false` with status-check protection unenforced. Linear `ABD-265` / GitHub Issue #36 therefore remain open.

The retained repository applicator/verifier is present on current `main`, but the connected execution path cannot substitute for the required authenticated repository-admin application/read-back.

This checkpoint does not treat tooling presence, CI success, or user intent as proof that hosted protection is effective.

## Exact next actions

1. Open a fresh draft PR from this replay branch to current `main`.
2. Require current exact-head Repository Governance, Core Domain Contracts and Durable Control Plane checks.
3. Review the fresh exact diff against current `main`; preserve `SELF REVIEW` unless a genuine independent reviewer participates.
4. Keep WP4 promotion fail-closed while ABD-265 live protection acceptance remains unresolved, unless repository governance records an explicit accepted exception.
5. Do not start WP5 until WP4 is accepted and merged through the governed integration path.