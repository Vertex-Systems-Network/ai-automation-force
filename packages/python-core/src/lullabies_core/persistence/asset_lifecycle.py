from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping

from ..derivatives import TERMINAL_DERIVATIVE_STATUSES, DerivativeStatus
from ..lifecycle import (
    AssetDeletionPropagationPlan,
    AssetLifecycleEvent,
    AssetLifecycleSnapshot,
    AssetLifecycleState,
    DeletionPropagationTargetKind,
    RetainedSharedStorageObject,
    StorageObjectPurgeTarget,
    build_deletion_propagation_plan,
    plan_asset_lifecycle_transition,
)
from ..storage import StorageBackend
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

AssetLifecycleAction = Literal["transitioned", "reused"]


class AssetLifecyclePersistenceConflictError(PersistenceConflictError):
    """Persisted lifecycle evidence conflicts with the requested operation."""


class AssetLifecycleVersionConflictError(AssetLifecyclePersistenceConflictError):
    """Lifecycle mutation was based on a stale state revision."""


@dataclass(frozen=True)
class AssetLifecycleTransitionResult:
    action: AssetLifecycleAction
    snapshot: AssetLifecycleSnapshot
    event: AssetLifecycleEvent


class PostgresAssetLifecycleRepository:
    """Durable lifecycle authority for archive/restore and deletion scheduling."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "asset_lifecycle_events",
            "asset_lifecycle_states",
            "asset_provenance_records",
            "assets",
            "delivery_share_links",
            "derivative_records",
            "projects",
            "storage_objects",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"asset lifecycle tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.events = metadata.tables["core.asset_lifecycle_events"]
        self.states = metadata.tables["core.asset_lifecycle_states"]
        self.assets = metadata.tables["core.assets"]
        self.projects = metadata.tables["core.projects"]
        self.provenance = metadata.tables["core.asset_provenance_records"]
        self.storage = metadata.tables["core.storage_objects"]
        self.derivatives = metadata.tables["core.derivative_records"]
        self.share_links = metadata.tables["core.delivery_share_links"]

    def load(self, asset_id: str) -> AssetLifecycleSnapshot:
        with self.engine.connect() as connection:
            asset = self._require_asset(connection, asset_id)
            project_id = self._project_external(connection, asset)
            row = self._state_row(connection, cast(UUID, asset["id"]), for_update=False)
            return self._snapshot(asset_id, project_id, asset, row)

    def history(self, asset_id: str) -> list[AssetLifecycleEvent]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(self.events)
                .where(self.events.c.asset_external_id == asset_id)
                .order_by(self.events.c.occurred_at, self.events.c.id)
            ).mappings()
            return [self._event_from_row(row) for row in rows]

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
    ) -> AssetLifecycleTransitionResult:
        if expected_revision < 1:
            raise ValueError("expected_revision must be at least 1")
        if not 8 <= len(operation_key) <= 200:
            raise ValueError("operation_key must contain between 8 and 200 characters")
        if not 1 <= len(actor) <= 200:
            raise ValueError("actor must contain between 1 and 200 characters")
        if reason is not None and not 1 <= len(reason) <= 2000:
            raise ValueError("reason must contain between 1 and 2000 characters")

        with self.engine.begin() as connection:
            asset = self._require_asset_for_update(connection, asset_id)
            project_id = self._project_external(connection, asset)

            existing_event = connection.execute(
                select(self.events)
                .where(self.events.c.asset_external_id == asset_id)
                .where(self.events.c.operation_key == operation_key)
            ).mappings().one_or_none()
            if existing_event is not None:
                event = self._event_from_row(existing_event)
                self._assert_idempotent_replay(
                    event,
                    target=target,
                    actor=actor,
                    reason=reason,
                    recovery_until=recovery_until,
                )
                return AssetLifecycleTransitionResult(
                    action="reused",
                    snapshot=self._snapshot_from_event(event),
                    event=event,
                )

            asset_internal_id = cast(UUID, asset["id"])
            state_row = self._state_row(
                connection,
                asset_internal_id,
                for_update=True,
            )
            current = self._snapshot(asset_id, project_id, asset, state_row)
            if current.revision != expected_revision:
                raise AssetLifecycleVersionConflictError(
                    f"asset lifecycle revision is {current.revision}; "
                    f"expected {expected_revision}"
                )

            planned = plan_asset_lifecycle_transition(
                current,
                target,
                occurred_at=occurred_at,
                recovery_until=recovery_until,
            )
            revision = current.revision + 1
            next_snapshot = AssetLifecycleSnapshot(
                asset_id=asset_id,
                project_id=project_id,
                state=planned.to_state,
                recovery_state=planned.recovery_state,
                recovery_until=planned.recovery_until,
                updated_at=occurred_at,
                revision=revision,
            )

            if state_row is None:
                connection.execute(
                    insert(self.states).values(
                        id=uuid4(),
                        asset_id=asset_internal_id,
                        project_id=asset["project_id"],
                        state=next_snapshot.state.value,
                        recovery_state=(
                            next_snapshot.recovery_state.value
                            if next_snapshot.recovery_state is not None
                            else None
                        ),
                        recovery_until=next_snapshot.recovery_until,
                        updated_at=next_snapshot.updated_at,
                        revision=next_snapshot.revision,
                    )
                )
            else:
                connection.execute(
                    update(self.states)
                    .where(self.states.c.id == state_row["id"])
                    .values(
                        state=next_snapshot.state.value,
                        recovery_state=(
                            next_snapshot.recovery_state.value
                            if next_snapshot.recovery_state is not None
                            else None
                        ),
                        recovery_until=next_snapshot.recovery_until,
                        updated_at=next_snapshot.updated_at,
                        revision=next_snapshot.revision,
                    )
                )

            event = AssetLifecycleEvent(
                asset_id=asset_id,
                project_id=project_id,
                from_state=planned.from_state,
                to_state=planned.to_state,
                operation_key=operation_key,
                actor=actor,
                reason=reason,
                recovery_state=planned.recovery_state,
                recovery_until=planned.recovery_until,
                occurred_at=occurred_at,
                revision=revision,
            )
            connection.execute(
                insert(self.events).values(
                    id=uuid4(),
                    asset_external_id=event.asset_id,
                    project_external_id=event.project_id,
                    from_state=event.from_state.value,
                    to_state=event.to_state.value,
                    operation_key=event.operation_key,
                    actor=event.actor,
                    reason=event.reason,
                    recovery_state=(
                        event.recovery_state.value
                        if event.recovery_state is not None
                        else None
                    ),
                    recovery_until=event.recovery_until,
                    occurred_at=event.occurred_at,
                    revision=event.revision,
                )
            )
            return AssetLifecycleTransitionResult(
                action="transitioned",
                snapshot=next_snapshot,
                event=event,
            )

    def plan_deletion_propagation(
        self,
        asset_id: str,
        *,
        planned_at: datetime,
    ) -> AssetDeletionPropagationPlan:
        """Enumerate what hard deletion must purge, revoke, or cancel, without executing it.

        Physical objects still referenced by another asset's provenance or derivative
        output are reported as retained rather than purged, so shared content is never
        destroyed through one asset's deletion. Derived assets keep their own lifecycle
        and are listed for auditability rather than cascaded.
        """

        with self.engine.connect() as connection:
            asset = self._require_asset(connection, asset_id)
            project_id = self._project_external(connection, asset)
            asset_internal_id = cast(UUID, asset["id"])
            snapshot = self._snapshot(
                asset_id,
                project_id,
                asset,
                self._state_row(connection, asset_internal_id, for_update=False),
            )

            candidates: dict[UUID, tuple[DeletionPropagationTargetKind, str | None]] = {}
            provenance_rows = connection.execute(
                select(self.provenance.c.storage_object_id)
                .where(self.provenance.c.asset_id == asset_internal_id)
                .where(self.provenance.c.storage_object_id.is_not(None))
            ).mappings()
            for row in provenance_rows:
                candidates.setdefault(
                    cast(UUID, row["storage_object_id"]),
                    (DeletionPropagationTargetKind.SOURCE_STORAGE_OBJECT, None),
                )

            output_rows = connection.execute(
                select(
                    self.derivatives.c.external_id,
                    self.derivatives.c.output_storage_object_id,
                )
                .where(self.derivatives.c.output_asset_id == asset_internal_id)
                .where(self.derivatives.c.output_storage_object_id.is_not(None))
                .order_by(self.derivatives.c.external_id)
            ).mappings()
            for row in output_rows:
                candidates.setdefault(
                    cast(UUID, row["output_storage_object_id"]),
                    (
                        DeletionPropagationTargetKind.DERIVATIVE_STORAGE_OBJECT,
                        str(row["external_id"]),
                    ),
                )

            open_derivatives: list[str] = []
            derived_assets: set[UUID] = set()
            sourced_rows = connection.execute(
                select(
                    self.derivatives.c.external_id,
                    self.derivatives.c.status,
                    self.derivatives.c.output_asset_id,
                ).where(self.derivatives.c.source_asset_id == asset_internal_id)
            ).mappings()
            for row in sourced_rows:
                if DerivativeStatus(str(row["status"])) not in TERMINAL_DERIVATIVE_STATUSES:
                    open_derivatives.append(str(row["external_id"]))
                output_asset_id = cast(UUID | None, row["output_asset_id"])
                if output_asset_id is not None:
                    derived_assets.add(output_asset_id)

            targets: list[StorageObjectPurgeTarget] = []
            retained: list[RetainedSharedStorageObject] = []
            for storage_internal_id, (kind, derivative_ref) in candidates.items():
                storage_row = connection.execute(
                    select(self.storage).where(self.storage.c.id == storage_internal_id)
                ).mappings().one_or_none()
                if storage_row is None:
                    raise PersistenceReferenceError(
                        f"missing storage object internal row {storage_internal_id}"
                    )
                other_owners = self._other_storage_owners(
                    connection,
                    storage_internal_id,
                    asset_internal_id,
                )
                storage_external_id = str(storage_row["external_id"])
                if other_owners:
                    retained.append(
                        RetainedSharedStorageObject(
                            storage_object_id=storage_external_id,
                            retained_for_asset_ids=other_owners,
                        )
                    )
                    continue
                targets.append(
                    StorageObjectPurgeTarget(
                        kind=kind,
                        storage_object_id=storage_external_id,
                        backend=StorageBackend(str(storage_row["backend"])),
                        bucket=(
                            str(storage_row["bucket"])
                            if storage_row["bucket"] is not None
                            else None
                        ),
                        object_key=str(storage_row["object_key"]),
                        sha256=str(storage_row["sha256"]),
                        derivative_record_id=derivative_ref,
                    )
                )

            share_links = connection.execute(
                select(self.share_links.c.external_id)
                .where(self.share_links.c.asset_id == asset_internal_id)
                .where(self.share_links.c.revoked_at.is_(None))
            ).scalars()

            return build_deletion_propagation_plan(
                snapshot,
                planned_at=planned_at,
                storage_targets=targets,
                retained_shared_storage=retained,
                share_link_ids=[str(value) for value in share_links],
                open_derivative_record_ids=open_derivatives,
                derived_asset_ids=self._asset_externals(connection, derived_assets),
            )

    def _asset_externals(self, connection: Connection, internal_ids: set[UUID]) -> list[str]:
        if not internal_ids:
            return []
        external_ids = connection.execute(
            select(self.assets.c.external_id).where(self.assets.c.id.in_(sorted(internal_ids)))
        ).scalars()
        resolved = sorted(str(value) for value in external_ids)
        if len(resolved) != len(internal_ids):
            raise PersistenceReferenceError("asset references resolve to unknown asset rows")
        return resolved

    def _other_storage_owners(
        self,
        connection: Connection,
        storage_internal_id: UUID,
        asset_internal_id: UUID,
    ) -> list[str]:
        owners: set[UUID] = set()
        provenance_owners = connection.execute(
            select(self.provenance.c.asset_id)
            .where(self.provenance.c.storage_object_id == storage_internal_id)
            .where(self.provenance.c.asset_id != asset_internal_id)
        ).scalars()
        owners.update(cast(UUID, value) for value in provenance_owners)
        derivative_outputs = connection.execute(
            select(self.derivatives.c.output_asset_id)
            .where(self.derivatives.c.output_storage_object_id == storage_internal_id)
            .where(self.derivatives.c.output_asset_id.is_not(None))
            .where(self.derivatives.c.output_asset_id != asset_internal_id)
        ).scalars()
        owners.update(cast(UUID, value) for value in derivative_outputs)
        return self._asset_externals(connection, owners)

    def _snapshot(
        self,
        asset_id: str,
        project_id: str,
        asset: RowMapping,
        row: RowMapping | None,
    ) -> AssetLifecycleSnapshot:
        if row is None:
            return AssetLifecycleSnapshot(
                asset_id=asset_id,
                project_id=project_id,
                state=AssetLifecycleState.ACTIVE,
                updated_at=asset["created_at"],
                revision=1,
            )
        if row["project_id"] != asset["project_id"]:
            raise PersistenceReferenceError(
                f"asset lifecycle project does not match asset {asset_id}"
            )
        return AssetLifecycleSnapshot(
            asset_id=asset_id,
            project_id=project_id,
            state=AssetLifecycleState(str(row["state"])),
            recovery_state=(
                AssetLifecycleState(str(row["recovery_state"]))
                if row["recovery_state"] is not None
                else None
            ),
            recovery_until=row["recovery_until"],
            updated_at=row["updated_at"],
            revision=int(row["revision"]),
        )

    @staticmethod
    def _snapshot_from_event(event: AssetLifecycleEvent) -> AssetLifecycleSnapshot:
        return AssetLifecycleSnapshot(
            asset_id=event.asset_id,
            project_id=event.project_id,
            state=event.to_state,
            recovery_state=event.recovery_state,
            recovery_until=event.recovery_until,
            updated_at=event.occurred_at,
            revision=event.revision,
        )

    @staticmethod
    def _assert_idempotent_replay(
        event: AssetLifecycleEvent,
        *,
        target: AssetLifecycleState,
        actor: str,
        reason: str | None,
        recovery_until: datetime | None,
    ) -> None:
        if (
            event.to_state is not target
            or event.actor != actor
            or event.reason != reason
            or event.recovery_until != recovery_until
        ):
            raise AssetLifecyclePersistenceConflictError(
                "lifecycle operation key is already bound to different mutation semantics"
            )

    def _project_external(self, connection: Connection, asset: RowMapping) -> str:
        internal_id = cast(UUID | None, asset["project_id"])
        if internal_id is None:
            raise PersistenceReferenceError("asset lifecycle requires a project-scoped asset")
        value = connection.execute(
            select(self.projects.c.external_id).where(self.projects.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(
                f"missing project external identity for lifecycle asset {asset['external_id']}"
            )
        return str(value)

    def _require_asset(self, connection: Connection, asset_id: str) -> RowMapping:
        row = connection.execute(
            select(self.assets).where(self.assets.c.external_id == asset_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"asset {asset_id} was not found")
        return row

    def _require_asset_for_update(
        self,
        connection: Connection,
        asset_id: str,
    ) -> RowMapping:
        row = connection.execute(
            select(self.assets)
            .where(self.assets.c.external_id == asset_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"asset {asset_id} was not found")
        return row

    def _state_row(
        self,
        connection: Connection,
        asset_internal_id: UUID,
        *,
        for_update: bool,
    ) -> RowMapping | None:
        statement = select(self.states).where(self.states.c.asset_id == asset_internal_id)
        if for_update:
            statement = statement.with_for_update()
        return connection.execute(statement).mappings().one_or_none()

    @staticmethod
    def _event_from_row(row: RowMapping) -> AssetLifecycleEvent:
        return AssetLifecycleEvent(
            asset_id=str(row["asset_external_id"]),
            project_id=str(row["project_external_id"]),
            from_state=AssetLifecycleState(str(row["from_state"])),
            to_state=AssetLifecycleState(str(row["to_state"])),
            operation_key=str(row["operation_key"]),
            actor=str(row["actor"]),
            reason=(str(row["reason"]) if row["reason"] is not None else None),
            recovery_state=(
                AssetLifecycleState(str(row["recovery_state"]))
                if row["recovery_state"] is not None
                else None
            ),
            recovery_until=row["recovery_until"],
            occurred_at=row["occurred_at"],
            revision=int(row["revision"]),
        )
