from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from lullabies_core.deletion_execution import DeletionPropagationExecutionResult
from lullabies_core.index_cleanup import (
    AssetIndexCleanupPlan,
    IndexCleanupHook,
    IndexCleanupPlanningError,
    IndexCleanupReceipt,
    IndexCleanupReceiptError,
    IndexCleanupReceiptStatus,
    IndexCleanupTarget,
    IndexCleanupTargetKind,
    build_index_cleanup_plan,
    validate_index_cleanup_receipts,
)


def deletion_result(
    *,
    fingerprint: str = "a" * 64,
    final_revision: int = 5,
) -> DeletionPropagationExecutionResult:
    return DeletionPropagationExecutionResult(
        asset_id="AST-001701",
        project_id="PRJ-001701",
        plan_fingerprint=fingerprint,
        deleted_storage_object_ids=("STO-001701",),
        already_absent_storage_object_ids=(),
        revoked_share_link_ids=(),
        already_inactive_share_link_ids=(),
        cancelled_derivative_record_ids=(),
        already_terminal_derivative_record_ids=(),
        final_revision=final_revision,
    )


def vector_target() -> IndexCleanupTarget:
    return IndexCleanupTarget(
        kind=IndexCleanupTargetKind.VECTOR_RECORD,
        namespace="asset-embeddings-v1",
        record_key="AST-001701:embedding",
    )


def search_target() -> IndexCleanupTarget:
    return IndexCleanupTarget(
        kind=IndexCleanupTargetKind.SEARCH_DOCUMENT,
        namespace="asset-search-v1",
        record_key="AST-001701",
    )


def test_build_index_cleanup_plan_is_ordered_stable_and_provider_neutral() -> None:
    planned_at = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)
    deletion = deletion_result()

    plan = build_index_cleanup_plan(
        deletion,
        targets=[vector_target(), search_target()],
        planned_at=planned_at,
    )

    assert plan.asset_id == deletion.asset_id
    assert plan.project_id == deletion.project_id
    assert plan.deletion_plan_fingerprint == deletion.plan_fingerprint
    assert plan.deletion_final_revision == deletion.final_revision
    assert [hook.target.identity() for hook in plan.hooks] == sorted(
        [vector_target().identity(), search_target().identity()]
    )
    assert all(hook.idempotency_key.startswith("index-cleanup:") for hook in plan.hooks)

    later = build_index_cleanup_plan(
        deletion,
        targets=[search_target(), vector_target()],
        planned_at=planned_at + timedelta(minutes=10),
    )
    assert [hook.idempotency_key for hook in later.hooks] == [
        hook.idempotency_key for hook in plan.hooks
    ]
    assert later.fingerprint() == plan.fingerprint()


def test_deletion_binding_changes_cleanup_idempotency_keys() -> None:
    planned_at = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)
    first = build_index_cleanup_plan(
        deletion_result(fingerprint="a" * 64, final_revision=5),
        targets=[vector_target()],
        planned_at=planned_at,
    )
    changed_fingerprint = build_index_cleanup_plan(
        deletion_result(fingerprint="b" * 64, final_revision=5),
        targets=[vector_target()],
        planned_at=planned_at,
    )
    changed_revision = build_index_cleanup_plan(
        deletion_result(fingerprint="a" * 64, final_revision=6),
        targets=[vector_target()],
        planned_at=planned_at,
    )

    assert first.hooks[0].idempotency_key != changed_fingerprint.hooks[0].idempotency_key
    assert first.hooks[0].idempotency_key != changed_revision.hooks[0].idempotency_key


def test_duplicate_cleanup_targets_fail_closed() -> None:
    with pytest.raises(IndexCleanupPlanningError, match="duplicate"):
        build_index_cleanup_plan(
            deletion_result(),
            targets=[vector_target(), vector_target()],
            planned_at=datetime(2026, 9, 5, 12, 0, tzinfo=UTC),
        )


def test_target_identity_rejects_ambiguous_whitespace_and_controls() -> None:
    with pytest.raises(ValidationError, match="surrounding whitespace"):
        IndexCleanupTarget(
            kind=IndexCleanupTargetKind.VECTOR_RECORD,
            namespace=" asset-embeddings-v1",
            record_key="AST-001701",
        )
    with pytest.raises(ValidationError, match="control characters"):
        IndexCleanupTarget(
            kind=IndexCleanupTargetKind.SEARCH_DOCUMENT,
            namespace="asset-search-v1",
            record_key="AST-001701\nother",
        )


def test_plan_rejects_tampered_idempotency_key() -> None:
    plan = build_index_cleanup_plan(
        deletion_result(),
        targets=[vector_target()],
        planned_at=datetime(2026, 9, 5, 12, 0, tzinfo=UTC),
    )
    tampered = IndexCleanupHook(
        target=plan.hooks[0].target,
        idempotency_key=f"index-cleanup:{'f' * 64}",
    )

    with pytest.raises(ValidationError, match="does not match plan binding"):
        AssetIndexCleanupPlan(
            asset_id=plan.asset_id,
            project_id=plan.project_id,
            deletion_plan_fingerprint=plan.deletion_plan_fingerprint,
            deletion_final_revision=plan.deletion_final_revision,
            planned_at=plan.planned_at,
            hooks=[tampered],
        )


def test_receipts_must_prove_exact_terminal_hook_set() -> None:
    plan = build_index_cleanup_plan(
        deletion_result(),
        targets=[vector_target(), search_target()],
        planned_at=datetime(2026, 9, 5, 12, 0, tzinfo=UTC),
    )
    receipts = [
        IndexCleanupReceipt(
            idempotency_key=plan.hooks[1].idempotency_key,
            status=IndexCleanupReceiptStatus.ALREADY_ABSENT,
        ),
        IndexCleanupReceipt(
            idempotency_key=plan.hooks[0].idempotency_key,
            status=IndexCleanupReceiptStatus.DELETED,
        ),
    ]

    completion = validate_index_cleanup_receipts(plan, receipts)
    assert completion.plan_fingerprint == plan.fingerprint()
    assert [receipt.idempotency_key for receipt in completion.receipts] == sorted(
        hook.idempotency_key for hook in plan.hooks
    )

    with pytest.raises(IndexCleanupReceiptError, match="mismatch"):
        validate_index_cleanup_receipts(plan, receipts[:1])

    with pytest.raises(IndexCleanupReceiptError, match="repeat"):
        validate_index_cleanup_receipts(plan, [receipts[0], receipts[0]])

    unexpected = IndexCleanupReceipt(
        idempotency_key=f"index-cleanup:{'0' * 64}",
        status=IndexCleanupReceiptStatus.DELETED,
    )
    with pytest.raises(IndexCleanupReceiptError, match="unexpected"):
        validate_index_cleanup_receipts(plan, [receipts[0], unexpected])


def test_planned_at_must_be_timezone_aware() -> None:
    with pytest.raises(ValidationError):
        build_index_cleanup_plan(
            deletion_result(),
            targets=[vector_target()],
            planned_at=datetime(2026, 9, 5, 12, 0),
        )
