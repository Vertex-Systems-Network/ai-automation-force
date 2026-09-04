from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from lullabies_core.deletion_execution import (
    DeletionPropagationExecutionError,
    execute_deletion_propagation,
)
from lullabies_core.delivery import DeliveryMode, ShareLinkConstraint
from lullabies_core.derivatives import (
    DerivativeKind,
    DerivativeRecord,
    DerivativeSpec,
    DerivativeStatus,
    derivative_operation_fingerprint,
)
from lullabies_core.lifecycle import (
    AssetDeletionPropagationPlan,
    AssetLifecycleSnapshot,
    AssetLifecycleState,
    DeletionPropagationTargetKind,
    StorageObjectPurgeTarget,
)
from lullabies_core.storage import (
    StorageBackend,
    StorageBlobStat,
    StorageIntegrityError,
    StorageNotFoundError,
    StorageWriteResult,
    sha256_bytes,
)


class FakeLifecycle:
    def __init__(
        self,
        snapshot: AssetLifecycleSnapshot,
        live_plan: AssetDeletionPropagationPlan,
    ) -> None:
        self.snapshot = snapshot
        self.live_plan = live_plan
        self.transitions: list[AssetLifecycleState] = []

    def load(self, asset_id: str) -> AssetLifecycleSnapshot:
        assert asset_id == self.snapshot.asset_id
        return self.snapshot

    def plan_deletion_propagation(
        self,
        asset_id: str,
        *,
        planned_at: datetime,
    ) -> AssetDeletionPropagationPlan:
        assert asset_id == self.snapshot.asset_id
        assert planned_at >= self.live_plan.planned_at
        return self.live_plan.model_copy(update={"planned_at": planned_at})

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
    ) -> object:
        assert asset_id == self.snapshot.asset_id
        assert operation_key
        assert actor
        assert occurred_at >= self.snapshot.updated_at
        assert expected_revision == self.snapshot.revision
        assert reason is not None and reason.startswith("deletion-propagation:")
        assert recovery_until is None
        self.transitions.append(target)
        self.snapshot = self.snapshot.model_copy(
            update={
                "state": target,
                "updated_at": occurred_at,
                "revision": self.snapshot.revision + 1,
            }
        )
        return object()


class FakeShareLinks:
    def __init__(self, links: dict[str, ShareLinkConstraint]) -> None:
        self.links = links
        self.revoked: list[str] = []

    def load(self, share_link_id: str) -> ShareLinkConstraint:
        return self.links[share_link_id]

    def revoke(self, share_link_id: str, *, revoked_at: datetime) -> object:
        current = self.links[share_link_id]
        self.links[share_link_id] = current.model_copy(update={"revoked_at": revoked_at})
        self.revoked.append(share_link_id)
        return object()


class FakeDerivatives:
    def __init__(self, records: dict[str, DerivativeRecord]) -> None:
        self.records = records
        self.cancelled: list[str] = []

    def load(self, derivative_record_id: str) -> DerivativeRecord:
        return self.records[derivative_record_id]

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
    ) -> object:
        current = self.records[derivative_record_id]
        assert expected_revision == current.revision
        assert target_status is DerivativeStatus.CANCELLED
        assert output_asset_id is None
        assert output_storage_object_id is None
        assert completed_at is None
        assert error_code is None
        self.records[derivative_record_id] = current.model_copy(
            update={
                "status": target_status,
                "updated_at": updated_at,
                "revision": current.revision + 1,
            }
        )
        self.cancelled.append(derivative_record_id)
        return object()


class FakeStorage:
    backend = StorageBackend.FILESYSTEM

    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = objects
        self.deleted: list[str] = []
        self.stat_sha_override: str | None = None

    def put_bytes(self, object_key: str, data: bytes, *, mime_type: str) -> StorageWriteResult:
        self.objects[object_key] = data
        return StorageWriteResult(
            backend=self.backend,
            object_key=object_key,
            sha256=sha256_bytes(data),
            mime_type=mime_type,
            size_bytes=len(data),
        )

    def get_bytes(self, object_key: str) -> bytes:
        try:
            return self.objects[object_key]
        except KeyError as exc:
            raise StorageNotFoundError(object_key) from exc

    def stat(self, object_key: str) -> StorageBlobStat:
        try:
            data = self.objects[object_key]
        except KeyError as exc:
            raise StorageNotFoundError(object_key) from exc
        return StorageBlobStat(
            backend=self.backend,
            object_key=object_key,
            size_bytes=len(data),
            sha256=self.stat_sha_override or sha256_bytes(data),
        )

    def delete(self, object_key: str) -> None:
        self.objects.pop(object_key, None)
        self.deleted.append(object_key)


def fixtures() -> tuple[
    datetime,
    AssetLifecycleSnapshot,
    AssetDeletionPropagationPlan,
    FakeShareLinks,
    FakeDerivatives,
    FakeStorage,
]:
    planned_at = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)
    asset_id = "AST-003040"
    project_id = "PRJ-003040"
    payload = b"delete-me"
    object_key = "canonical/PRJ-003040/STO-003040"
    target = StorageObjectPurgeTarget(
        kind=DeletionPropagationTargetKind.SOURCE_STORAGE_OBJECT,
        storage_object_id="STO-003040",
        backend=StorageBackend.FILESYSTEM,
        object_key=object_key,
        sha256=sha256_bytes(payload),
    )
    snapshot = AssetLifecycleSnapshot(
        asset_id=asset_id,
        project_id=project_id,
        state=AssetLifecycleState.HARD_DELETE_SCHEDULED,
        updated_at=planned_at,
        revision=4,
    )
    plan = AssetDeletionPropagationPlan(
        asset_id=asset_id,
        project_id=project_id,
        lifecycle_revision=4,
        planned_at=planned_at,
        storage_targets=[target],
        share_link_ids=["SHL-003040-active"],
        open_derivative_record_ids=["DRV-003040"],
    )
    links = FakeShareLinks(
        {
            "SHL-003040-active": ShareLinkConstraint(
                share_link_id="SHL-003040-active",
                project_id=project_id,
                asset_id=asset_id,
                token_sha256="a" * 64,
                allowed_modes=[DeliveryMode.STREAM],
                expires_at=planned_at + timedelta(days=1),
            )
        }
    )
    spec = DerivativeSpec(
        kind=DerivativeKind.VIDEO_POSTER,
        width=1280,
        height=720,
        mime_type="image/png",
    )
    derivative = DerivativeRecord(
        derivative_record_id="DRV-003040",
        project_id=project_id,
        source_asset_id=asset_id,
        job_id="JOB-003040",
        spec=spec,
        operation_fingerprint=derivative_operation_fingerprint(
            project_id=project_id,
            source_asset_id=asset_id,
            spec=spec,
        ),
        created_at=planned_at - timedelta(minutes=10),
        updated_at=planned_at - timedelta(minutes=5),
    )
    derivatives = FakeDerivatives({derivative.derivative_record_id: derivative})
    storage = FakeStorage({object_key: payload})
    return planned_at, snapshot, plan, links, derivatives, storage


def test_execute_deletion_propagation_completes_only_after_all_effects() -> None:
    planned_at, snapshot, plan, links, derivatives, storage = fixtures()
    lifecycle = FakeLifecycle(snapshot, plan)

    result = execute_deletion_propagation(
        plan,
        lifecycle=lifecycle,
        share_links=links,
        derivatives=derivatives,
        resolve_storage_adapter=lambda target: storage,
        executed_at=planned_at + timedelta(minutes=1),
        actor="wp7-worker",
        operation_key="delete-exec-003040",
    )

    assert result.deleted_storage_object_ids == ("STO-003040",)
    assert result.revoked_share_link_ids == ("SHL-003040-active",)
    assert result.cancelled_derivative_record_ids == ("DRV-003040",)
    assert result.final_revision == 5
    assert lifecycle.snapshot.state is AssetLifecycleState.DELETED
    assert lifecycle.transitions == [AssetLifecycleState.DELETED]
    assert storage.objects == {}
    assert links.revoked == ["SHL-003040-active"]
    assert derivatives.cancelled == ["DRV-003040"]


def test_execute_rejects_live_plan_expansion_before_any_side_effect() -> None:
    planned_at, snapshot, plan, links, derivatives, storage = fixtures()
    expanded = plan.model_copy(
        update={"share_link_ids": ["SHL-003040-active", "SHL-003040-new"]}
    )
    lifecycle = FakeLifecycle(snapshot, expanded)

    with pytest.raises(
        DeletionPropagationExecutionError,
        match="introduced a new share-link effect",
    ):
        execute_deletion_propagation(
            plan,
            lifecycle=lifecycle,
            share_links=links,
            derivatives=derivatives,
            resolve_storage_adapter=lambda target: storage,
            executed_at=planned_at + timedelta(minutes=1),
            actor="wp7-worker",
            operation_key="delete-exec-003040",
        )

    assert storage.deleted == []
    assert links.revoked == []
    assert derivatives.cancelled == []
    assert lifecycle.transitions == []


def test_execute_fails_closed_on_storage_hash_mismatch() -> None:
    planned_at, snapshot, plan, links, derivatives, storage = fixtures()
    lifecycle = FakeLifecycle(snapshot, plan)
    storage.stat_sha_override = "f" * 64

    with pytest.raises(StorageIntegrityError, match="storage hash mismatch"):
        execute_deletion_propagation(
            plan,
            lifecycle=lifecycle,
            share_links=links,
            derivatives=derivatives,
            resolve_storage_adapter=lambda target: storage,
            executed_at=planned_at + timedelta(minutes=1),
            actor="wp7-worker",
            operation_key="delete-exec-003040",
        )

    assert storage.deleted == []
    assert links.revoked == []
    assert derivatives.cancelled == []
    assert lifecycle.transitions == []


def test_execute_can_resume_when_prior_effects_are_already_terminal() -> None:
    planned_at, snapshot, plan, links, derivatives, storage = fixtures()
    executed_at = planned_at + timedelta(minutes=1)
    storage.objects.clear()
    links.links["SHL-003040-active"] = links.links["SHL-003040-active"].model_copy(
        update={"revoked_at": executed_at}
    )
    current_derivative = derivatives.records["DRV-003040"]
    derivatives.records["DRV-003040"] = current_derivative.model_copy(
        update={
            "status": DerivativeStatus.CANCELLED,
            "updated_at": executed_at,
            "revision": current_derivative.revision + 1,
        }
    )
    reduced_live = plan.model_copy(
        update={"share_link_ids": [], "open_derivative_record_ids": []}
    )
    lifecycle = FakeLifecycle(snapshot, reduced_live)

    result = execute_deletion_propagation(
        plan,
        lifecycle=lifecycle,
        share_links=links,
        derivatives=derivatives,
        resolve_storage_adapter=lambda target: storage,
        executed_at=executed_at,
        actor="wp7-worker",
        operation_key="delete-exec-003040",
    )

    assert result.already_absent_storage_object_ids == ("STO-003040",)
    assert result.already_inactive_share_link_ids == ("SHL-003040-active",)
    assert result.already_terminal_derivative_record_ids == ("DRV-003040",)
    assert result.deleted_storage_object_ids == ()
    assert result.revoked_share_link_ids == ()
    assert result.cancelled_derivative_record_ids == ()
    assert lifecycle.snapshot.state is AssetLifecycleState.DELETED
