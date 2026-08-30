# M03-WP4 — Review Checkpoint

Status: `REVIEWED / GOVERNANCE BLOCKED`

Repository: `Vertex-Systems-Network/ai-automation-force`
Linear: `ABD-203`
Pull request: `#33`
Branch: `agent/20260830-ai-automation-force-abd-203`
Accepted base: `a92388a287051ddffe123b5cf90d74fa17553b41`
Final reviewed implementation code head: `df214410f040033097b3d2e018e3a8db3d3deb22`

## Scope completed in the implementation candidate

- append-only `AssetProvenanceRecord` contracts for upload/import/provider/derived origins;
- additive/reversible migration `0011_asset_provenance`;
- restrictive foreign-key linkage to canonical assets, projects, storage objects and rights records;
- immutable create/noop/conflict persistence;
- fail-closed project-boundary, canonical/storage hash, rights and parent-derived provenance checks;
- fail-closed chronology: provenance evidence cannot predate the canonical asset it describes;
- asset usability evaluation without duplicating `Asset.canonical_status` or `RightsRecord` authority;
- canonical package exports and PostgreSQL acceptance coverage.

## Data / migration impact

- adds `core.asset_provenance_records` only;
- source assets remain immutable and are not overwritten by derivatives;
- downgrade removes only the WP4 provenance table/indexes;
- no destructive backfill is performed;
- no external provider credentials, spend or production media routing is introduced.

Recovery class: `ROLLBACK WITH COMPATIBILITY` while no later schema depends on migration 0011. After downstream migrations depend on it, prefer forward fix unless the dependency chain is explicitly rolled back in reverse order.

## Security / rights / integrity review

The candidate is fail-closed for:

- cross-project references;
- mismatched storage/canonical hashes;
- mismatched rights links;
- derived records without a valid parent path;
- provenance timestamps earlier than canonical asset creation.

Rights/publication authority remains with the existing rights model; provenance evidence does not self-authorize publication. No secrets, provider credentials or unrestricted AI authority are added.

The chronology defect was found during SELF REVIEW and corrected in-scope with a focused PostgreSQL regression rather than broad refactoring.

## Verification evidence

Exact reviewed implementation code head `df214410f040033097b3d2e018e3a8db3d3deb22`:

- `Core Domain Contracts` run `33304722513` — PASS;
- `Durable Control Plane` run `33304722516` — PASS.

The SELF REVIEW is recorded on PR #33 against this exact code head. These checks establish implementation validity but do not override repository-governance requirements.

## Review state

- PR remains draft;
- submitted independent approving reviews: `0`;
- current review classification: `SELF REVIEW`;
- no independent-review claim is made.

## Repository-governance blocker

Live `main` protection/ruleset enforcement is absent and is tracked as Linear `ABD-265`.

The available connected GitHub capability can read branch protection/rulesets but cannot mutate hosted protection settings. Therefore this checkpoint does not fake or document an unenforced protection as complete.

Before WP4 promotion under the adopted Universal Master Prompt governance baseline, require live repository read-back showing the intended protected-main controls are actually effective, or an explicit approved repository exception that records the residual risk and review model.

Do not mix this hosted-admin remediation into the WP4 implementation diff and do not weaken tests/checks to bypass it.

## Known limitations / locked scope

- no WP5 derivative generation;
- no WP6 signed delivery;
- no WP7 retention/archive/delete orchestration;
- no M04+ work;
- no claim that green CI alone makes WP4 released or production-verified;
- no WP5 implementation while WP4 promotion remains blocked.

## Exact next safe action

1. resolve `ABD-265` with live GitHub protection/ruleset read-back evidence (or an explicit approved exception if protection genuinely cannot be enabled);
2. re-read `main`, PR base/head, review state and exact current checks after that hosted-admin change;
3. if branch freshness or check identity changed, reconcile and run fresh exact-head Core + Durable gates;
4. promote WP4 only through the accepted repository integration path;
5. after accepted merge, record exact merge/evidence and activate only the next documented WP5 boundary.
