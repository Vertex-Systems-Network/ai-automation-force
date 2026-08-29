from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import MetaData, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping

from ..retry_control import (
    CircuitBreakerPolicy,
    CircuitPermission,
    CircuitRecordResult,
    CircuitState,
    FailureClass,
    retry_decision,
)
from ._db import PersistenceConflictError, PersistenceReferenceError


class CircuitBreakerConflictError(PersistenceConflictError):
    """Circuit probe ownership or state changed before the requested mutation."""


class PostgresCircuitBreakerRepository:
    """Durable provider-neutral circuit state with one half-open probe lease."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        key = "core.circuit_breakers"
        if key not in metadata.tables:
            raise PersistenceReferenceError("circuit breaker persistence is not migrated")
        self.table = metadata.tables[key]

    def acquire_permission(
        self,
        circuit_key: str,
        *,
        owner: str,
        now: datetime,
        policy: CircuitBreakerPolicy,
    ) -> CircuitPermission:
        circuit_key = self._normalized_key(circuit_key)
        owner = self._normalized_owner(owner)
        with self.engine.begin() as connection:
            row = self._row_for_update(connection, circuit_key)
            if row is None:
                connection.execute(
                    insert(self.table).values(
                        id=uuid4(),
                        circuit_key=circuit_key,
                        state=CircuitState.CLOSED.value,
                        consecutive_failures=0,
                        failure_threshold=policy.failure_threshold,
                        updated_at=now,
                        revision=1,
                    )
                )
                return CircuitPermission(True, CircuitState.CLOSED, 1)

            state = CircuitState(str(row["state"]))
            revision = int(row["revision"])
            if state is CircuitState.CLOSED:
                return CircuitPermission(True, state, revision)

            if state is CircuitState.OPEN:
                retry_at = row["next_probe_at"]
                if retry_at is None:
                    raise CircuitBreakerConflictError("open circuit is missing next_probe_at")
                if retry_at > now:
                    return CircuitPermission(False, state, revision, retry_at=retry_at)
                new_revision = revision + 1
                probe_expiry = now + timedelta(seconds=policy.probe_lease_seconds)
                self._update(
                    connection,
                    row,
                    revision,
                    {
                        "state": CircuitState.HALF_OPEN.value,
                        "failure_threshold": policy.failure_threshold,
                        "probe_owner": owner,
                        "probe_lease_expires_at": probe_expiry,
                        "updated_at": now,
                        "revision": new_revision,
                    },
                )
                return CircuitPermission(
                    True,
                    CircuitState.HALF_OPEN,
                    new_revision,
                    probe_owner=owner,
                )

            probe_expiry = row["probe_lease_expires_at"]
            probe_owner = row["probe_owner"]
            if probe_owner == owner and probe_expiry is not None and probe_expiry > now:
                return CircuitPermission(
                    True,
                    CircuitState.HALF_OPEN,
                    revision,
                    probe_owner=owner,
                )
            if probe_expiry is not None and probe_expiry > now:
                return CircuitPermission(
                    False,
                    CircuitState.HALF_OPEN,
                    revision,
                    retry_at=probe_expiry,
                    probe_owner=str(probe_owner) if probe_owner is not None else None,
                )

            new_revision = revision + 1
            replacement_expiry = now + timedelta(seconds=policy.probe_lease_seconds)
            self._update(
                connection,
                row,
                revision,
                {
                    "probe_owner": owner,
                    "probe_lease_expires_at": replacement_expiry,
                    "updated_at": now,
                    "revision": new_revision,
                },
            )
            return CircuitPermission(
                True,
                CircuitState.HALF_OPEN,
                new_revision,
                probe_owner=owner,
            )

    def record_failure(
        self,
        circuit_key: str,
        *,
        owner: str,
        failure_class: FailureClass,
        now: datetime,
        policy: CircuitBreakerPolicy,
    ) -> CircuitRecordResult:
        decision = retry_decision(failure_class)
        if not decision.counts_toward_circuit:
            raise ValueError(f"{failure_class.value} does not count toward circuit health")
        circuit_key = self._normalized_key(circuit_key)
        owner = self._normalized_owner(owner)

        with self.engine.begin() as connection:
            row = self._row_for_update(connection, circuit_key)
            if row is None:
                failures = 1
                state = (
                    CircuitState.OPEN
                    if failures >= policy.failure_threshold
                    else CircuitState.CLOSED
                )
                next_probe_at = (
                    now + timedelta(seconds=policy.open_seconds)
                    if state is CircuitState.OPEN
                    else None
                )
                connection.execute(
                    insert(self.table).values(
                        id=uuid4(),
                        circuit_key=circuit_key,
                        state=state.value,
                        consecutive_failures=failures,
                        failure_threshold=policy.failure_threshold,
                        opened_at=now if state is CircuitState.OPEN else None,
                        next_probe_at=next_probe_at,
                        last_failure_class=failure_class.value,
                        updated_at=now,
                        revision=1,
                    )
                )
                return CircuitRecordResult(state, failures, 1, next_probe_at)

            state = CircuitState(str(row["state"]))
            revision = int(row["revision"])
            if state is CircuitState.HALF_OPEN and row["probe_owner"] != owner:
                raise CircuitBreakerConflictError("half-open probe is owned by another worker")

            failures = int(row["consecutive_failures"]) + 1
            should_open = state is CircuitState.HALF_OPEN or failures >= policy.failure_threshold
            target = CircuitState.OPEN if should_open else CircuitState.CLOSED
            next_probe_at = (
                now + timedelta(seconds=policy.open_seconds)
                if target is CircuitState.OPEN
                else None
            )
            new_revision = revision + 1
            self._update(
                connection,
                row,
                revision,
                {
                    "state": target.value,
                    "consecutive_failures": failures,
                    "failure_threshold": policy.failure_threshold,
                    "opened_at": now if target is CircuitState.OPEN else None,
                    "next_probe_at": next_probe_at,
                    "probe_owner": None,
                    "probe_lease_expires_at": None,
                    "last_failure_class": failure_class.value,
                    "updated_at": now,
                    "revision": new_revision,
                },
            )
            return CircuitRecordResult(target, failures, new_revision, next_probe_at)

    def record_success(
        self,
        circuit_key: str,
        *,
        owner: str,
        now: datetime,
    ) -> CircuitRecordResult:
        circuit_key = self._normalized_key(circuit_key)
        owner = self._normalized_owner(owner)
        with self.engine.begin() as connection:
            row = self._row_for_update(connection, circuit_key)
            if row is None:
                connection.execute(
                    insert(self.table).values(
                        id=uuid4(),
                        circuit_key=circuit_key,
                        state=CircuitState.CLOSED.value,
                        consecutive_failures=0,
                        failure_threshold=1,
                        updated_at=now,
                        revision=1,
                    )
                )
                return CircuitRecordResult(CircuitState.CLOSED, 0, 1)

            state = CircuitState(str(row["state"]))
            revision = int(row["revision"])
            if state is CircuitState.HALF_OPEN and row["probe_owner"] != owner:
                raise CircuitBreakerConflictError("half-open probe is owned by another worker")
            if state is CircuitState.CLOSED and int(row["consecutive_failures"]) == 0:
                return CircuitRecordResult(CircuitState.CLOSED, 0, revision)

            new_revision = revision + 1
            self._update(
                connection,
                row,
                revision,
                {
                    "state": CircuitState.CLOSED.value,
                    "consecutive_failures": 0,
                    "opened_at": None,
                    "next_probe_at": None,
                    "probe_owner": None,
                    "probe_lease_expires_at": None,
                    "last_failure_class": None,
                    "updated_at": now,
                    "revision": new_revision,
                },
            )
            return CircuitRecordResult(CircuitState.CLOSED, 0, new_revision)

    def _row_for_update(self, connection: Connection, circuit_key: str) -> RowMapping | None:
        return connection.execute(
            select(self.table)
            .where(self.table.c.circuit_key == circuit_key)
            .with_for_update()
        ).mappings().one_or_none()

    def _update(
        self,
        connection: Connection,
        row: RowMapping,
        expected_revision: int,
        values: dict[str, object],
    ) -> None:
        result = connection.execute(
            update(self.table)
            .where(self.table.c.id == row["id"], self.table.c.revision == expected_revision)
            .values(**values)
        )
        if result.rowcount != 1:
            raise CircuitBreakerConflictError("circuit revision changed during mutation")

    @staticmethod
    def _normalized_key(value: str) -> str:
        value = value.strip()
        if len(value) < 3 or len(value) > 240:
            raise ValueError("circuit_key length must be between 3 and 240")
        return value

    @staticmethod
    def _normalized_owner(value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("circuit owner must not be blank")
        return value
