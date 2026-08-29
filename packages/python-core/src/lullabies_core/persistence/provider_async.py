from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import MetaData, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..provider_async import (
    TERMINAL_PROVIDER_ASYNC_STATUSES,
    ProviderAsyncResult,
    ProviderAsyncStatus,
    ProviderAsyncSubmission,
    ProviderAsyncTransitionError,
    ProviderCallbackEvent,
    assert_provider_async_transition,
)
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError


class ProviderAsyncConflictError(PersistenceConflictError):
    """Async provider state conflicts with canonical attempt or persisted transport state."""


class ProviderAsyncVersionConflictError(ProviderAsyncConflictError):
    """Async provider state changed after the caller observed it."""


class ProviderCallbackConflictError(ProviderAsyncConflictError):
    """A callback event ID was reused for different callback semantics."""


class PostgresProviderAsyncRepository:
    """Durable fake-provider submit/poll/callback/timeout reconciliation boundary."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {
            "generation_attempts",
            "provider_async_states",
            "provider_callback_events",
        }
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                "provider-async persistence tables are not migrated: "
                + ", ".join(sorted(missing))
            )
        self.attempts = metadata.tables["core.generation_attempts"]
        self.states = metadata.tables["core.provider_async_states"]
        self.callbacks = metadata.tables["core.provider_callback_events"]

    def register_submission(self, submission: ProviderAsyncSubmission) -> ProviderAsyncResult:
        try:
            with self.engine.begin() as connection:
                attempt = self._require_attempt_for_update(connection, submission.attempt_id)
                if attempt["provider_id"] != submission.provider_id:
                    raise ProviderAsyncConflictError(
                        f"attempt {submission.attempt_id} belongs to another provider"
                    )
                existing = self._state_by_attempt(connection, attempt["id"], lock=True)
                if existing is not None:
                    if (
                        existing["provider_id"] == submission.provider_id
                        and existing["provider_generation_id"]
                        == submission.provider_generation_id
                        and existing["submitted_at"] == submission.submitted_at
                        and existing["deadline_at"] == submission.deadline_at
                        and existing["next_poll_at"] == submission.next_poll_at
                    ):
                        return self._result(existing, duplicate=True)
                    raise ProviderAsyncConflictError(
                        "attempt is already bound to different async submission semantics"
                    )
                existing_generation_id = attempt["provider_generation_id"]
                if existing_generation_id not in {None, submission.provider_generation_id}:
                    raise ProviderAsyncConflictError(
                        "canonical attempt already has a different provider generation ID"
                    )
                if str(attempt["status"]) not in {"pending", "running"}:
                    raise ProviderAsyncConflictError(
                        f"attempt {submission.attempt_id} is already terminal"
                    )

                connection.execute(
                    update(self.attempts)
                    .where(self.attempts.c.id == attempt["id"])
                    .values(
                        provider_generation_id=submission.provider_generation_id,
                        status="running",
                    )
                )
                connection.execute(
                    insert(self.states).values(
                        attempt_id=attempt["id"],
                        provider_id=submission.provider_id,
                        provider_generation_id=submission.provider_generation_id,
                        status=ProviderAsyncStatus.SUBMITTED.value,
                        provider_status="submitted",
                        submitted_at=submission.submitted_at,
                        next_poll_at=submission.next_poll_at,
                        deadline_at=submission.deadline_at,
                        poll_count=0,
                        last_polled_at=None,
                        last_callback_at=None,
                        last_provider_event_at=None,
                        last_reconciled_at=submission.submitted_at,
                        terminal_at=None,
                        revision=1,
                    )
                )
                return ProviderAsyncResult(
                    submission.attempt_id,
                    ProviderAsyncStatus.SUBMITTED,
                    1,
                )
        except (ProviderAsyncConflictError, PersistenceNotFoundError):
            raise
        except IntegrityError as exc:
            raise ProviderAsyncConflictError(
                f"database rejected provider submission: {exc.orig}"
            ) from exc

    def record_poll(
        self,
        attempt_id: str,
        *,
        provider_status: str,
        normalized_status: ProviderAsyncStatus,
        observed_at: datetime,
        next_poll_at: datetime | None,
        expected_revision: int,
    ) -> ProviderAsyncResult:
        provider_status = provider_status.strip()
        if not provider_status:
            raise ValueError("provider_status must not be blank")
        with self.engine.begin() as connection:
            attempt = self._require_attempt_for_update(connection, attempt_id)
            state = self._require_state_for_update(connection, attempt["id"])
            self._require_revision(state, expected_revision)
            current = ProviderAsyncStatus(str(state["status"]))
            if current in TERMINAL_PROVIDER_ASYNC_STATUSES:
                return self._result(state, stale=True)
            self._validate_observation_times(state, observed_at, next_poll_at)
            if normalized_status is not current:
                self._require_transition(current, normalized_status)

            new_revision = expected_revision + 1
            values = {
                "status": normalized_status.value,
                "provider_status": provider_status,
                "next_poll_at": (
                    None
                    if normalized_status in TERMINAL_PROVIDER_ASYNC_STATUSES
                    else next_poll_at
                ),
                "poll_count": int(state["poll_count"]) + 1,
                "last_polled_at": observed_at,
                "last_reconciled_at": observed_at,
                "terminal_at": (
                    observed_at
                    if normalized_status in TERMINAL_PROVIDER_ASYNC_STATUSES
                    else None
                ),
                "revision": new_revision,
            }
            self._update_state(connection, state, expected_revision, values)
            self._reconcile_attempt_terminal(
                connection,
                attempt,
                normalized_status,
                observed_at,
            )
            return ProviderAsyncResult(attempt_id, normalized_status, new_revision)

    def receive_callback(self, event: ProviderCallbackEvent) -> ProviderAsyncResult:
        try:
            with self.engine.begin() as connection:
                existing_event = self._callback_by_event_id(
                    connection,
                    event.provider_id,
                    event.event_id,
                )
                if existing_event is not None:
                    if existing_event["payload_sha256"] != event.payload_sha256:
                        raise ProviderCallbackConflictError(
                            "callback event ID is already bound to a different payload hash"
                        )
                    state = self._require_state_for_update(
                        connection,
                        existing_event["attempt_id"],
                    )
                    return self._result(
                        state,
                        duplicate=True,
                        event_id=event.event_id,
                    )

                state = self._require_state_by_generation_for_update(
                    connection,
                    event.provider_id,
                    event.provider_generation_id,
                )
                attempt = self._require_attempt_by_id_for_update(
                    connection,
                    state["attempt_id"],
                )
                current = ProviderAsyncStatus(str(state["status"]))
                previous_provider_event_at = state["last_provider_event_at"]
                stale = (
                    previous_provider_event_at is not None
                    and event.provider_event_at <= previous_provider_event_at
                ) or current in TERMINAL_PROVIDER_ASYNC_STATUSES

                if stale:
                    self._insert_callback(connection, state["attempt_id"], event, stale=True)
                    return self._result(state, stale=True, event_id=event.event_id)

                if event.normalized_status is not current:
                    self._require_transition(current, event.normalized_status)
                new_revision = int(state["revision"]) + 1
                values = {
                    "status": event.normalized_status.value,
                    "provider_status": event.provider_status,
                    "next_poll_at": (
                        None
                        if event.normalized_status in TERMINAL_PROVIDER_ASYNC_STATUSES
                        else state["next_poll_at"]
                    ),
                    "last_callback_at": event.received_at,
                    "last_provider_event_at": event.provider_event_at,
                    "last_reconciled_at": event.received_at,
                    "terminal_at": (
                        event.received_at
                        if event.normalized_status in TERMINAL_PROVIDER_ASYNC_STATUSES
                        else None
                    ),
                    "revision": new_revision,
                }
                self._update_state(
                    connection,
                    state,
                    int(state["revision"]),
                    values,
                )
                self._reconcile_attempt_terminal(
                    connection,
                    attempt,
                    event.normalized_status,
                    event.received_at,
                )
                self._insert_callback(connection, state["attempt_id"], event, stale=False)
                return ProviderAsyncResult(
                    str(attempt["external_id"]),
                    event.normalized_status,
                    new_revision,
                    event_id=event.event_id,
                )
        except (
            ProviderAsyncConflictError,
            PersistenceNotFoundError,
            PersistenceReferenceError,
        ):
            raise
        except IntegrityError as exc:
            raise ProviderAsyncConflictError(
                f"database rejected provider callback: {exc.orig}"
            ) from exc

    def mark_timeout(
        self,
        attempt_id: str,
        *,
        now: datetime,
        expected_revision: int,
    ) -> ProviderAsyncResult:
        with self.engine.begin() as connection:
            attempt = self._require_attempt_for_update(connection, attempt_id)
            state = self._require_state_for_update(connection, attempt["id"])
            self._require_revision(state, expected_revision)
            current = ProviderAsyncStatus(str(state["status"]))
            if current in TERMINAL_PROVIDER_ASYNC_STATUSES:
                return self._result(state, stale=True)
            if state["deadline_at"] > now:
                raise ProviderAsyncConflictError(
                    f"provider deadline for {attempt_id} has not elapsed"
                )
            self._require_transition(current, ProviderAsyncStatus.TIMED_OUT)
            new_revision = expected_revision + 1
            self._update_state(
                connection,
                state,
                expected_revision,
                {
                    "status": ProviderAsyncStatus.TIMED_OUT.value,
                    "provider_status": "timeout",
                    "next_poll_at": None,
                    "last_reconciled_at": now,
                    "terminal_at": now,
                    "revision": new_revision,
                },
            )
            self._reconcile_attempt_terminal(
                connection,
                attempt,
                ProviderAsyncStatus.TIMED_OUT,
                now,
            )
            return ProviderAsyncResult(
                attempt_id,
                ProviderAsyncStatus.TIMED_OUT,
                new_revision,
            )

    def load(self, attempt_id: str) -> RowMapping:
        with self.engine.connect() as connection:
            attempt = self._require_attempt(connection, attempt_id)
            state = self._state_by_attempt(connection, attempt["id"], lock=False)
        if state is None:
            raise PersistenceNotFoundError(
                f"async provider state for attempt {attempt_id} was not found"
            )
        return state

    def _callback_by_event_id(
        self,
        connection: Connection,
        provider_id: str,
        event_id: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.callbacks).where(
                self.callbacks.c.provider_id == provider_id,
                self.callbacks.c.event_id == event_id,
            )
        ).mappings().one_or_none()

    def _insert_callback(
        self,
        connection: Connection,
        attempt_id: UUID,
        event: ProviderCallbackEvent,
        *,
        stale: bool,
    ) -> None:
        connection.execute(
            insert(self.callbacks).values(
                id=uuid4(),
                attempt_id=attempt_id,
                provider_id=event.provider_id,
                event_id=event.event_id,
                provider_generation_id=event.provider_generation_id,
                payload_sha256=event.payload_sha256,
                signature_scheme="synthetic-hmac-sha256-v1",
                provider_status=event.provider_status,
                normalized_status=event.normalized_status.value,
                provider_event_at=event.provider_event_at,
                received_at=event.received_at,
                processed_at=event.received_at,
                stale=stale,
            )
        )

    @staticmethod
    def _validate_observation_times(
        state: RowMapping,
        observed_at: datetime,
        next_poll_at: datetime | None,
    ) -> None:
        if observed_at < state["submitted_at"]:
            raise ProviderAsyncConflictError("poll observation predates provider submission")
        if next_poll_at is not None and not (
            observed_at <= next_poll_at < state["deadline_at"]
        ):
            raise ProviderAsyncConflictError(
                "next poll must be no earlier than observation and before deadline"
            )

    @staticmethod
    def _require_transition(
        current: ProviderAsyncStatus,
        target: ProviderAsyncStatus,
    ) -> None:
        try:
            assert_provider_async_transition(current, target)
        except ProviderAsyncTransitionError as exc:
            raise ProviderAsyncConflictError(str(exc)) from exc

    @staticmethod
    def _require_revision(state: RowMapping, expected_revision: int) -> None:
        if int(state["revision"]) != expected_revision:
            raise ProviderAsyncVersionConflictError(
                f"stale provider async revision: expected {expected_revision}, "
                f"current {state['revision']}"
            )

    def _update_state(
        self,
        connection: Connection,
        state: RowMapping,
        expected_revision: int,
        values: Mapping[str, object],
    ) -> None:
        result = connection.execute(
            update(self.states)
            .where(
                self.states.c.attempt_id == state["attempt_id"],
                self.states.c.revision == expected_revision,
            )
            .values(**values)
        )
        if result.rowcount != 1:
            raise ProviderAsyncVersionConflictError(
                "provider async state changed during reconciliation"
            )

    def _reconcile_attempt_terminal(
        self,
        connection: Connection,
        attempt: RowMapping,
        status: ProviderAsyncStatus,
        observed_at: datetime,
    ) -> None:
        if status not in TERMINAL_PROVIDER_ASYNC_STATUSES:
            return
        values: dict[str, object] = {"finished_at": observed_at}
        if status is ProviderAsyncStatus.SUCCEEDED:
            values.update(status="succeeded", normalized_error_code=None, error_detail=None)
        elif status is ProviderAsyncStatus.CANCELLED:
            values.update(status="cancelled", normalized_error_code="provider_cancelled")
        elif status is ProviderAsyncStatus.TIMED_OUT:
            values.update(status="failed", normalized_error_code="provider_timeout")
        else:
            values.update(status="failed", normalized_error_code="provider_failed")
        connection.execute(
            update(self.attempts).where(self.attempts.c.id == attempt["id"]).values(**values)
        )

    def _require_attempt(self, connection: Connection, attempt_id: str) -> RowMapping:
        row = connection.execute(
            select(self.attempts).where(self.attempts.c.external_id == attempt_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"attempt {attempt_id} was not found")
        return row

    def _require_attempt_for_update(
        self,
        connection: Connection,
        attempt_id: str,
    ) -> RowMapping:
        row = connection.execute(
            select(self.attempts)
            .where(self.attempts.c.external_id == attempt_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(f"attempt {attempt_id} was not found")
        return row

    def _require_attempt_by_id_for_update(
        self,
        connection: Connection,
        attempt_id: UUID,
    ) -> RowMapping:
        row = connection.execute(
            select(self.attempts).where(self.attempts.c.id == attempt_id).with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(
                f"async provider state references missing attempt {attempt_id}"
            )
        return row

    def _state_by_attempt(
        self,
        connection: Connection,
        attempt_id: UUID,
        *,
        lock: bool,
    ) -> RowMapping | None:
        statement = select(self.states).where(self.states.c.attempt_id == attempt_id)
        if lock:
            statement = statement.with_for_update()
        return connection.execute(statement).mappings().one_or_none()

    def _require_state_for_update(
        self,
        connection: Connection,
        attempt_id: UUID,
    ) -> RowMapping:
        row = self._state_by_attempt(connection, attempt_id, lock=True)
        if row is None:
            raise PersistenceNotFoundError(
                f"async provider state for attempt {attempt_id} was not found"
            )
        return row

    def _require_state_by_generation_for_update(
        self,
        connection: Connection,
        provider_id: str,
        provider_generation_id: str,
    ) -> RowMapping:
        row = connection.execute(
            select(self.states)
            .where(
                self.states.c.provider_id == provider_id,
                self.states.c.provider_generation_id == provider_generation_id,
            )
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(
                "async provider state for callback generation ID was not found"
            )
        return row

    def _result(
        self,
        state: RowMapping,
        *,
        stale: bool = False,
        duplicate: bool = False,
        event_id: str | None = None,
    ) -> ProviderAsyncResult:
        with self.engine.connect() as connection:
            attempt = self._require_attempt_by_id(connection, state["attempt_id"])
        return ProviderAsyncResult(
            str(attempt["external_id"]),
            ProviderAsyncStatus(str(state["status"])),
            int(state["revision"]),
            stale=stale,
            duplicate=duplicate,
            event_id=event_id,
        )

    def _require_attempt_by_id(
        self,
        connection: Connection,
        attempt_id: UUID,
    ) -> RowMapping:
        row = connection.execute(
            select(self.attempts).where(self.attempts.c.id == attempt_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(
                f"async provider state references missing attempt {attempt_id}"
            )
        return row
