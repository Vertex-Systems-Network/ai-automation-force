from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping

from ..lifecycle import (
    AssetLifecycleEvent,
    AssetLifecycleSnapshot,
    AssetLifecycleState,
    plan_asset_lifecycle_transition,
)
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
            "assets",
            "projects",
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
