from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol

from .delivery import ShareLinkConstraint
from .derivatives import DerivativeRecord, DerivativeStatus, TERMINAL_DERIVATIVE_STATUSES
from .lifecycle import (
    AssetDeletionPropagationPlan,
    AssetLifecycleSnapshot,
    AssetLifecycleState,
    StorageObjectPurgeTarget,
)
from .storage import StorageAdapter, StorageIntegrityError, StorageNotFoundError


class DeletionPropagationExecutionError(RuntimeError):
    """Approved hard-delete propagation cannot be executed safely."""


class LifecycleExecutionRepository(Protocol):
    def load(self, asset_id: str) -> AssetLifecycleSnapshot: ...

    def plan_deletion_propagation(
        self,
        asset_id: str,
        *,
        planned_at: datetime,
    ) -> AssetDeletionPropagationPlan: ...

    def transition(
        self,
        asset_id: str,
        target: AssetLifecycleState,
        *,
        operation_key: str,
        actor: str,
        occurred_at: datetime,
        expected_revision: int,
        reason: str | None = None,
        recovery_until: datetime | None = None,
    ) -> object: ...


class ShareLinkExecutionRepository(Protocol):
    def load(self, share_link_id: str) -> ShareLinkConstraint: ...

    def revoke(
        self,
        share_link_id: str,
        *,
        revoked_at: datetime,
    ) -> object: ...


class DerivativeExecutionRepository(Protocol):
    def load(self, derivative_record_id: str) -> DerivativeRecord: ...

    def transition(
        self,
        derivative_record_id: str,
        *,
        expected_revision: int,
        target_status: DerivativeStatus,
        updated_at: datetime,
        output_asset_id: str | None = None,
        output_storage_object_id: str | None = None,
        completed_at: datetime | None = None,
        error_code: str | None = None,
    ) -> object: ...


StorageAdapterResolver = Callable[[StorageObjectPurgeTarget], StorageAdapter]


@dataclass(frozen=True)
class DeletionPropagationExecutionResult:
    asset_id: str
    project_id: str
    plan_fingerprint: str
    deleted_storage_object_ids: tuple[str, ...]
    already_absent_storage_object_ids: tuple[str, ...]
    revoked_share_link_ids: tuple[str, ...]
    already_inactive_share_link_ids: tuple[str, ...]
    cancelled_derivative_record_ids: tuple[str, ...]
    already_terminal_derivative_record_ids: tuple[str, ...]
    final_revision: int


def execute_deletion_propagation(
    approved_plan: AssetDeletionPropagationPlan,
    *,
    lifecycle: LifecycleExecutionRepository,
    share_links: ShareLinkExecutionRepository,
    derivatives: DerivativeExecutionRepository,
    resolve_storage_adapter: StorageAdapterResolver,
    executed_at: datetime,
    actor: str,
    operation_key: str,
) -> DeletionPropagationExecutionResult:
    """Execute one approved hard-delete plan with stale-plan and partial-retry guards.

    The approved plan is treated as an upper bound. A live re-plan may contain fewer
    still-active share links or open derivatives after a partial retry, but it may not
    introduce new effects or change storage/retention/derived-asset ownership.
    Physical storage is integrity-checked before deletion. The lifecycle reaches
    ``deleted`` only after every approved propagation effect has completed or is already
    in a terminal/idempotent state.
    """

    _validate_execution_request(approved_plan, executed_at, actor, operation_key)

    current = lifecycle.load(approved_plan.asset_id)
    _require_matching_lifecycle(current, approved_plan)

    live_plan = lifecycle.plan_deletion_propagation(
        approved_plan.asset_id,
        planned_at=executed_at,
    )
    _require_compatible_live_plan(approved_plan, live_plan)

    storage_work: list[tuple[StorageObjectPurgeTarget, StorageAdapter]] = []
    already_absent_storage: list[str] = []
    for target in approved_plan.storage_targets:
        adapter = resolve_storage_adapter(target)
        if adapter.backend is not target.backend:
            raise DeletionPropagationExecutionError(
                f"storage adapter backend mismatch for {target.storage_object_id}"
            )
        try:
            stat = adapter.stat(target.object_key)
        except StorageNotFoundError:
            already_absent_storage.append(target.storage_object_id)
            continue
        if stat.backend is not target.backend or stat.bucket != target.bucket:
            raise DeletionPropagationExecutionError(
                f"storage location mismatch for {target.storage_object_id}"
            )
        if stat.object_key != target.object_key:
            raise DeletionPropagationExecutionError(
                f"storage object key mismatch for {target.storage_object_id}"
            )
        if stat.sha256 is None or stat.sha256 != target.sha256:
            raise StorageIntegrityError(
                f"storage hash mismatch for deletion target {target.storage_object_id}"
            )
        storage_work.append((target, adapter))

    loaded_links: dict[str, ShareLinkConstraint] = {}
    for share_link_id in approved_plan.share_link_ids:
        link = share_links.load(share_link_id)
        if link.project_id != approved_plan.project_id or link.asset_id != approved_plan.asset_id:
            raise DeletionPropagationExecutionError(
                f"share link {share_link_id} escaped the approved asset/project boundary"
            )
        loaded_links[share_link_id] = link

    loaded_derivatives: dict[str, DerivativeRecord] = {}
    for derivative_record_id in approved_plan.open_derivative_record_ids:
        record = derivatives.load(derivative_record_id)
        if (
            record.project_id != approved_plan.project_id
            or record.source_asset_id != approved_plan.asset_id
        ):
            raise DeletionPropagationExecutionError(
                f"derivative {derivative_record_id} escaped the approved asset/project boundary"
            )
        if record.status not in TERMINAL_DERIVATIVE_STATUSES and executed_at < record.updated_at:
            raise DeletionPropagationExecutionError(
                f"execution time predates derivative {derivative_record_id} state"
            )
        loaded_derivatives[derivative_record_id] = record

    deleted_storage: list[str] = []
    for target, adapter in storage_work:
        adapter.delete(target.object_key)
        deleted_storage.append(target.storage_object_id)

    revoked_links: list[str] = []
    already_inactive_links: list[str] = []
    for share_link_id in approved_plan.share_link_ids:
        link = loaded_links[share_link_id]
        if link.revoked_at is not None:
            already_inactive_links.append(share_link_id)
            continue
        revoked_at = min(executed_at, link.expires_at)
        share_links.revoke(share_link_id, revoked_at=revoked_at)
        revoked_links.append(share_link_id)

    cancelled_derivatives: list[str] = []
    already_terminal_derivatives: list[str] = []
    for derivative_record_id in approved_plan.open_derivative_record_ids:
        record = loaded_derivatives[derivative_record_id]
        if record.status in TERMINAL_DERIVATIVE_STATUSES:
            already_terminal_derivatives.append(derivative_record_id)
            continue
        derivatives.transition(
            derivative_record_id,
            expected_revision=record.revision,
            target_status=DerivativeStatus.CANCELLED,
            updated_at=executed_at,
        )
        cancelled_derivatives.append(derivative_record_id)

    lifecycle.transition(
        approved_plan.asset_id,
        AssetLifecycleState.DELETED,
        operation_key=operation_key,
        actor=actor,
        occurred_at=executed_at,
        expected_revision=approved_plan.lifecycle_revision,
        reason=f"deletion-propagation:{approved_plan.fingerprint()}",
    )
    final = lifecycle.load(approved_plan.asset_id)
    if final.state is not AssetLifecycleState.DELETED:
        raise DeletionPropagationExecutionError(
            f"asset {approved_plan.asset_id} did not reach deleted lifecycle state"
        )

    return DeletionPropagationExecutionResult(
        asset_id=approved_plan.asset_id,
        project_id=approved_plan.project_id,
        plan_fingerprint=approved_plan.fingerprint(),
        deleted_storage_object_ids=tuple(deleted_storage),
        already_absent_storage_object_ids=tuple(already_absent_storage),
        revoked_share_link_ids=tuple(revoked_links),
        already_inactive_share_link_ids=tuple(already_inactive_links),
        cancelled_derivative_record_ids=tuple(cancelled_derivatives),
        already_terminal_derivative_record_ids=tuple(already_terminal_derivatives),
        final_revision=final.revision,
    )


def _validate_execution_request(
    plan: AssetDeletionPropagationPlan,
    executed_at: datetime,
    actor: str,
    operation_key: str,
) -> None:
    if executed_at.utcoffset() is None:
        raise ValueError("executed_at must be timezone-aware")
    if executed_at < plan.planned_at:
        raise DeletionPropagationExecutionError("execution cannot predate the approved plan")
    if not 1 <= len(actor) <= 200:
        raise ValueError("actor must contain between 1 and 200 characters")
    if not 8 <= len(operation_key) <= 200:
        raise ValueError("operation_key must contain between 8 and 200 characters")


def _require_matching_lifecycle(
    current: AssetLifecycleSnapshot,
    approved: AssetDeletionPropagationPlan,
) -> None:
    if current.project_id != approved.project_id:
        raise DeletionPropagationExecutionError("approved deletion plan project no longer matches")
    if current.state is not AssetLifecycleState.HARD_DELETE_SCHEDULED:
        raise DeletionPropagationExecutionError(
            f"asset must remain hard-delete-scheduled, not {current.state.value}"
        )
    if current.revision != approved.lifecycle_revision:
        raise DeletionPropagationExecutionError(
            f"lifecycle revision moved from approved {approved.lifecycle_revision} "
            f"to {current.revision}"
        )


def _require_compatible_live_plan(
    approved: AssetDeletionPropagationPlan,
    live: AssetDeletionPropagationPlan,
) -> None:
    if live.asset_id != approved.asset_id or live.project_id != approved.project_id:
        raise DeletionPropagationExecutionError("live deletion plan identity changed")
    if live.lifecycle_revision != approved.lifecycle_revision:
        raise DeletionPropagationExecutionError("live deletion plan lifecycle revision changed")
    if live.storage_targets != approved.storage_targets:
        raise DeletionPropagationExecutionError("live storage purge targets changed after approval")
    if live.retained_shared_storage != approved.retained_shared_storage:
        raise DeletionPropagationExecutionError("live shared-storage retention set changed after approval")
    if live.derived_asset_ids != approved.derived_asset_ids:
        raise DeletionPropagationExecutionError("live derived-asset audit set changed after approval")
    if not set(live.share_link_ids).issubset(approved.share_link_ids):
        raise DeletionPropagationExecutionError("live deletion plan introduced a new share-link effect")
    if not set(live.open_derivative_record_ids).issubset(
        approved.open_derivative_record_ids
    ):
        raise DeletionPropagationExecutionError("live deletion plan introduced a new derivative effect")
