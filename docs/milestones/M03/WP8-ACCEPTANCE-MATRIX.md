# M03-WP8 Acceptance Matrix

## Scope and baseline

- Issue: #66 — M03-WP8 end-to-end source acceptance
- Acceptance branch: `agent/m03-wp8-acceptance-v2`
- Synchronized baseline: `main@fb685306a5fefc84488e78b27630727ddc30e54a`
- Source scope: evidence mapping and genuinely missing acceptance coverage only
- Product/API/schema/provider expansion: not authorized
- Active migration reservation: none
- Latest landed migration: `20260901_0016`

This matrix evaluates the six acceptance bullets defined by `docs/milestones/M03/PLAN.md` against current repository-native focused tests. Existing focused evidence is reused instead of duplicating behavior merely to create a new WP8 test file.

## Acceptance criteria

| Criterion | Current focused evidence | Source decision |
| --- | --- | --- |
| Multipart interruption / resume | `packages/python-core/tests/test_upload_persistence.py::test_multipart_upload_resumes_across_reload_and_terminal_complete_is_idempotent`; `packages/python-core/tests/test_upload_s3.py::test_multipart_begin_recovers_exact_key_upload_after_bind_crash`; `packages/python-core/tests/test_upload_s3.py::test_complete_reconciles_lost_ack_and_verifies_final_size` | Covered. Durable process restart, backend UploadId recovery, idempotent part replay/completion and lost acknowledgement reconciliation are explicitly tested. |
| Cross-tenant / cross-project signed URL denial | `packages/python-core/tests/test_delivery.py::test_private_delivery_fails_closed_across_projects`; `packages/python-core/tests/test_delivery_s3.py::test_signing_refuses_authority_for_another_asset_or_project` | Covered. Foreign project authorization fails closed and the S3 signing adapter performs no presign call for mismatched project/asset authority. |
| Malicious / malformed fixtures | `packages/python-core/tests/test_media_security.py` including content-based magic detection, MIME spoof/size mismatch/threat detection, probe timeout and scanner error fail-closed cases; persisted quarantine coverage in `test_quarantine_persistence.py` | Covered. Validation is content/evidence driven and terminal acceptance cannot be asserted from inconsistent evidence. |
| Lineage / hash integrity | `packages/python-core/tests/test_lineage.py::test_full_lineage_validates_and_preserves_stable_ids`; invalid parent/cross-project/attempt cases in the same file; `packages/python-core/tests/test_asset_provenance_persistence.py::test_asset_provenance_round_trip_is_append_only_and_integrity_safe` | Covered. Stable lineage IDs round-trip, cross-project/missing-parent references fail closed, provenance is append-only, and content-hash mismatches are rejected. |
| Deletion / temporary cleanup | `packages/python-core/tests/test_deletion_execution.py`; `packages/python-core/tests/test_temporary_cleanup.py`; deletion planning/state coverage in `packages/python-core/tests/test_asset_lifecycle.py` | Covered. Destructive execution, retry/idempotency/shared-storage safety, abandoned temporary upload cleanup and lifecycle deletion authority are exercised by focused suites. |
| Archive / restore smoke | `packages/python-core/tests/test_asset_lifecycle.py::test_lifecycle_repository_archive_restore_is_versioned_and_idempotent`; delivery-state smoke in `packages/python-core/tests/test_delivery_resolution.py` | Covered. Archive/restore is revisioned and idempotent; non-deliverable archive states fail closed and delivery returns only after restore completes. |

## WP7 exit-primitives carried into WP8

WP8 also verifies that the final WP7 primitives remain part of the exact-head source suite:

- private export staging: `packages/python-core/tests/test_export_staging.py`
- deterministic vector/search cleanup hooks: `packages/python-core/tests/test_index_cleanup.py`
- hard-delete execution: `packages/python-core/tests/test_deletion_execution.py`
- temporary cleanup: `packages/python-core/tests/test_temporary_cleanup.py`
- lifecycle migration chain: `20260901_0015 -> 20260901_0016`, with no active reservation

These are not extra M03 PLAN acceptance bullets, but they are required regression evidence because WP8 follows the complete WP7 closeout.

## Gap decision

The current evidence audit finds **no genuine missing product/API/schema/provider acceptance gap**. Therefore WP8 does not add duplicate implementation or a synthetic umbrella test merely to change source code. The acceptance artifact itself is the bounded deliverable, while the pull request exact-head CI provides the final integrated certification.

If exact-head CI exposes a real behavioral gap, this decision becomes invalid and the minimum targeted test/remediation must be added before promotion.

## Exact-head certification gate

Source acceptance is valid only when the WP8 pull request head is unchanged and all repository-required source lanes complete successfully:

1. Repository Governance
2. Core Domain Contracts
3. Durable Control Plane

The Core and Durable lanes provide the full unit/PostgreSQL integration coverage; Durable additionally exercises Temporal integration, deterministic OpenAPI generation and package/migration compilation. A stale prior run does not certify a moved WP8 head.

## External governance boundary

Issue #36 remains independent and unresolved until live GitHub `main` protection/ruleset read-back proves the required repository configuration. A green and merged WP8 source-acceptance PR may establish **M03 source acceptance**, but must not claim protected-main governance completion or final production promotion while Issue #36 is open.

## Acceptance statement

**READY FOR EXACT-HEAD CERTIFICATION.**

All six M03-WP8 source criteria map to explicit current focused tests. No unsupported production provider, credential, bucket, paid service, or cost-bearing action is required for this source acceptance.
