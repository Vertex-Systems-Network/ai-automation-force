from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, Field, model_validator

from .common import AssetId, ProjectId, StorageObjectId, StrictModel, external_id_pattern
from .storage import StorageBackend, validate_object_key


class AssetLifecycleState(StrEnum):
    ACTIVE = "active"
    ARCHIVE_REQUESTED = "archive-requested"
    ARCHIVING = "archiving"
    ARCHIVED = "archived"
    ARCHIVE_FAILED = "archive-failed"
    RESTORE_REQUESTED = "restore-requested"
    RESTORING = "restoring"
    RESTORE_FAILED = "restore-failed"
    DELETION_PENDING = "deletion-pending"
    HARD_DELETE_SCHEDULED = "hard-delete-scheduled"
    DELETED = "deleted"


STABLE_DELETION_SOURCES = {
    AssetLifecycleState.ACTIVE,
    AssetLifecycleState.ARCHIVED,
    AssetLifecycleState.ARCHIVE_FAILED,
    AssetLifecycleState.RESTORE_FAILED,
}

DELIVERABLE_LIFECYCLE_STATES = frozenset(
    {
        AssetLifecycleState.ACTIVE,
        AssetLifecycleState.ARCHIVE_REQUESTED,
    }
)

ASSET_LIFECYCLE_TRANSITIONS: dict[AssetLifecycleState, set[AssetLifecycleState]] = {
    AssetLifecycleState.ACTIVE: {
        AssetLifecycleState.ARCHIVE_REQUESTED,
        AssetLifecycleState.DELETION_PENDING,
    },
    AssetLifecycleState.ARCHIVE_REQUESTED: {
        AssetLifecycleState.ARCHIVING,
        AssetLifecycleState.ACTIVE,
    },
    AssetLifecycleState.ARCHIVING: {
        AssetLifecycleState.ARCHIVED,
        AssetLifecycleState.ARCHIVE_FAILED,
    },
    AssetLifecycleState.ARCHIVED: {
        AssetLifecycleState.RESTORE_REQUESTED,
        AssetLifecycleState.DELETION_PENDING,
    },
    AssetLifecycleState.ARCHIVE_FAILED: {
        AssetLifecycleState.ARCHIVE_REQUESTED,
        AssetLifecycleState.ACTIVE,
        AssetLifecycleState.DELETION_PENDING,
    },
    AssetLifecycleState.RESTORE_REQUESTED: {
        AssetLifecycleState.RESTORING,
        AssetLifecycleState.ARCHIVED,
    },
    AssetLifecycleState.RESTORING: {
        AssetLifecycleState.ACTIVE,
        AssetLifecycleState.RESTORE_FAILED,
    },
    AssetLifecycleState.RESTORE_FAILED: {
        AssetLifecycleState.RESTORE_REQUESTED,
        AssetLifecycleState.ARCHIVED,
        AssetLifecycleState.DELETION_PENDING,
    },
    AssetLifecycleState.DELETION_PENDING: {
        AssetLifecycleState.HARD_DELETE_SCHEDULED,
        AssetLifecycleState.ACTIVE,
        AssetLifecycleState.ARCHIVED,
        AssetLifecycleState.ARCHIVE_FAILED,
        AssetLifecycleState.RESTORE_FAILED,
    },
    AssetLifecycleState.HARD_DELETE_SCHEDULED: {AssetLifecycleState.DELETED},
    AssetLifecycleState.DELETED: set(),
}


class InvalidAssetLifecycleTransitionError(RuntimeError):
    """Requested asset lifecycle transition violates the canonical state machine."""


class AssetLifecycleDeliveryError(RuntimeError):
    """Asset lifecycle state does not permit routing the asset to a consumer."""


class InvalidDeletionPropagationError(RuntimeError):
    """Deletion propagation was planned against lifecycle evidence that forbids it."""


class AssetLifecycleSnapshot(StrictModel):
    asset_id: AssetId
    project_id: ProjectId
    state: AssetLifecycleState = AssetLifecycleState.ACTIVE
    recovery_state: AssetLifecycleState | None = None
    recovery_until: AwareDatetime | None = None
    updated_at: AwareDatetime
    revision: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_recovery_window(self) -> AssetLifecycleSnapshot:
        if self.state is AssetLifecycleState.DELETION_PENDING:
            if self.recovery_state not in STABLE_DELETION_SOURCES:
                raise ValueError("deletion-pending state requires a stable recovery_state")
            if self.recovery_until is None:
                raise ValueError("deletion-pending state requires recovery_until")
            if self.recovery_until <= self.updated_at:
                raise ValueError("recovery_until must follow the deletion request time")
        elif self.recovery_state is not None or self.recovery_until is not None:
            raise ValueError("recovery metadata is only valid while deletion is pending")
        return self


class AssetLifecycleEvent(StrictModel):
    asset_id: AssetId
    project_id: ProjectId
    from_state: AssetLifecycleState
    to_state: AssetLifecycleState
    operation_key: str = Field(min_length=8, max_length=200)
    actor: str = Field(min_length=1, max_length=200)
    reason: str | None = Field(default=None, min_length=1, max_length=2000)
    recovery_state: AssetLifecycleState | None = None
    recovery_until: AwareDatetime | None = None
    occurred_at: AwareDatetime
    revision: int = Field(ge=2)

    @model_validator(mode="after")
    def validate_transition_evidence(self) -> AssetLifecycleEvent:
        if self.from_state is self.to_state:
            raise ValueError("lifecycle event must change state")
        if self.to_state is AssetLifecycleState.DELETION_PENDING:
            if self.recovery_state not in STABLE_DELETION_SOURCES:
                raise ValueError("deletion event requires a stable recovery_state")
            if self.recovery_until is None or self.recovery_until <= self.occurred_at:
                raise ValueError("deletion event requires a future recovery_until")
        elif self.recovery_state is not None or self.recovery_until is not None:
            raise ValueError("recovery metadata is only valid on deletion-pending events")
        return self


class PlannedAssetLifecycleTransition(StrictModel):
    from_state: AssetLifecycleState
    to_state: AssetLifecycleState
    recovery_state: AssetLifecycleState | None = None
    recovery_until: AwareDatetime | None = None


def plan_asset_lifecycle_transition(
    current: AssetLifecycleSnapshot,
    target: AssetLifecycleState,
    *,
    occurred_at: AwareDatetime,
    recovery_until: AwareDatetime | None = None,
) -> PlannedAssetLifecycleTransition:
    """Validate one lifecycle transition without causing persistence or storage effects."""

    if occurred_at < current.updated_at:
        raise InvalidAssetLifecycleTransitionError(
            "lifecycle transition cannot predate the current state"
        )
    if target not in ASSET_LIFECYCLE_TRANSITIONS[current.state]:
        raise InvalidAssetLifecycleTransitionError(
            f"asset lifecycle cannot transition from {current.state.value} to {target.value}"
        )

    if target is AssetLifecycleState.DELETION_PENDING:
        if current.state not in STABLE_DELETION_SOURCES:
            raise InvalidAssetLifecycleTransitionError(
                "soft deletion may begin only from a stable lifecycle state"
            )
        if recovery_until is None or recovery_until <= occurred_at:
            raise InvalidAssetLifecycleTransitionError(
                "soft deletion requires a recovery window ending after the request time"
            )
        return PlannedAssetLifecycleTransition(
            from_state=current.state,
            to_state=target,
            recovery_state=current.state,
            recovery_until=recovery_until,
        )

    if current.state is AssetLifecycleState.DELETION_PENDING:
        if current.recovery_state is None or current.recovery_until is None:
            raise InvalidAssetLifecycleTransitionError(
                "deletion-pending state is missing recovery evidence"
            )
        if target is AssetLifecycleState.HARD_DELETE_SCHEDULED:
            if occurred_at < current.recovery_until:
                raise InvalidAssetLifecycleTransitionError(
                    "hard deletion cannot be scheduled before the recovery window closes"
                )
        else:
            if target is not current.recovery_state:
                raise InvalidAssetLifecycleTransitionError(
                    "soft deletion may recover only to the recorded prior lifecycle state"
                )
            if occurred_at > current.recovery_until:
                raise InvalidAssetLifecycleTransitionError(
                    "soft deletion recovery window has already closed"
                )

    if recovery_until is not None:
        raise InvalidAssetLifecycleTransitionError(
            "recovery_until is accepted only when entering deletion-pending state"
        )

    return PlannedAssetLifecycleTransition(
        from_state=current.state,
        to_state=target,
    )


def require_deliverable_lifecycle(snapshot: AssetLifecycleSnapshot) -> None:
    """Fail closed unless the asset lifecycle state still permits delivery."""

    if snapshot.state not in DELIVERABLE_LIFECYCLE_STATES:
        raise AssetLifecycleDeliveryError(
            f"asset {snapshot.asset_id} is not deliverable in lifecycle state "
            f"{snapshot.state.value}"
        )


DerivativeRecordRef = Annotated[str, Field(pattern=external_id_pattern("DRV"))]
ShareLinkRef = Annotated[str, Field(min_length=8, max_length=160)]


class DeletionPropagationTargetKind(StrEnum):
    SOURCE_STORAGE_OBJECT = "source-storage-object"
    DERIVATIVE_STORAGE_OBJECT = "derivative-storage-object"


class StorageObjectPurgeTarget(StrictModel):
    """One physical object that hard deletion must purge, with its canonical identity."""

    kind: DeletionPropagationTargetKind
    storage_object_id: StorageObjectId
    backend: StorageBackend
    bucket: str | None = Field(default=None, min_length=1, max_length=255)
    object_key: str = Field(min_length=1, max_length=1024)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    derivative_record_id: DerivativeRecordRef | None = None

    @model_validator(mode="after")
    def validate_target(self) -> StorageObjectPurgeTarget:
        validate_object_key(self.object_key)
        if self.backend is StorageBackend.S3 and self.bucket is None:
            raise ValueError("S3 purge targets require a bucket")
        if self.backend is StorageBackend.FILESYSTEM and self.bucket is not None:
            raise ValueError("filesystem purge targets must not carry a bucket")
        if self.kind is DeletionPropagationTargetKind.DERIVATIVE_STORAGE_OBJECT:
            if self.derivative_record_id is None:
                raise ValueError("derivative purge targets require derivative_record_id")
        elif self.derivative_record_id is not None:
            raise ValueError("source purge targets must not reference a derivative record")
        return self


class RetainedSharedStorageObject(StrictModel):
    """A physical object excluded from purge because other canonical rows still need it."""

    storage_object_id: StorageObjectId
    retained_for_asset_ids: list[AssetId] = Field(min_length=1)


class AssetDeletionPropagationPlan(StrictModel):
    """Deterministic, auditable propagation set for one hard-delete-scheduled asset."""

    asset_id: AssetId
    project_id: ProjectId
    lifecycle_revision: int = Field(ge=2)
    planned_at: AwareDatetime
    storage_targets: list[StorageObjectPurgeTarget] = Field(default_factory=list)
    retained_shared_storage: list[RetainedSharedStorageObject] = Field(default_factory=list)
    share_link_ids: list[ShareLinkRef] = Field(default_factory=list)
    open_derivative_record_ids: list[DerivativeRecordRef] = Field(default_factory=list)
    derived_asset_ids: list[AssetId] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_disjoint_and_ordered(self) -> AssetDeletionPropagationPlan:
        target_ids = [target.storage_object_id for target in self.storage_targets]
        retained_ids = [item.storage_object_id for item in self.retained_shared_storage]
        if len(set(target_ids)) != len(target_ids):
            raise ValueError("purge targets must not repeat a storage object")
        if len(set(retained_ids)) != len(retained_ids):
            raise ValueError("retained storage objects must not repeat")
        if set(target_ids) & set(retained_ids):
            raise ValueError("a storage object cannot be both purged and retained")
        if target_ids != sorted(target_ids):
            raise ValueError("purge targets must be ordered by storage object identity")
        if retained_ids != sorted(retained_ids):
            raise ValueError("retained storage objects must be ordered by identity")
        if self.share_link_ids != sorted(set(self.share_link_ids)):
            raise ValueError("share link identities must be unique and ordered")
        if self.open_derivative_record_ids != sorted(set(self.open_derivative_record_ids)):
            raise ValueError("derivative record identities must be unique and ordered")
        if self.derived_asset_ids != sorted(set(self.derived_asset_ids)):
            raise ValueError("derived asset identities must be unique and ordered")
        if self.asset_id in self.derived_asset_ids:
            raise ValueError("an asset cannot be derived from itself")
        return self

    def fingerprint(self) -> str:
        """Stable digest of the propagation set, independent of when it was planned."""

        payload = self.model_dump(mode="json", exclude={"planned_at"})
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_deletion_propagation_plan(
    snapshot: AssetLifecycleSnapshot,
    *,
    planned_at: AwareDatetime,
    storage_targets: list[StorageObjectPurgeTarget],
    retained_shared_storage: list[RetainedSharedStorageObject],
    share_link_ids: list[str],
    open_derivative_record_ids: list[str],
    derived_asset_ids: list[str],
) -> AssetDeletionPropagationPlan:
    """Bind enumerated propagation effects to lifecycle evidence that authorizes them."""

    if snapshot.state is not AssetLifecycleState.HARD_DELETE_SCHEDULED:
        raise InvalidDeletionPropagationError(
            "deletion propagation may be planned only for hard-delete-scheduled assets, "
            f"not {snapshot.state.value}"
        )
    if planned_at < snapshot.updated_at:
        raise InvalidDeletionPropagationError(
            "deletion propagation cannot be planned before hard deletion was scheduled"
        )
    return AssetDeletionPropagationPlan(
        asset_id=snapshot.asset_id,
        project_id=snapshot.project_id,
        lifecycle_revision=snapshot.revision,
        planned_at=planned_at,
        storage_targets=sorted(storage_targets, key=lambda item: item.storage_object_id),
        retained_shared_storage=sorted(
            (
                item.model_copy(
                    update={"retained_for_asset_ids": sorted(set(item.retained_for_asset_ids))}
                )
                for item in retained_shared_storage
            ),
            key=lambda item: item.storage_object_id,
        ),
        share_link_ids=sorted(set(share_link_ids)),
        open_derivative_record_ids=sorted(set(open_derivative_record_ids)),
        derived_asset_ids=sorted(set(derived_asset_ids)),
    )
