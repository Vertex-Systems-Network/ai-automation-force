from __future__ import annotations

from enum import StrEnum

from pydantic import AwareDatetime, Field, model_validator

from .common import AssetId, ProjectId, StrictModel


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
