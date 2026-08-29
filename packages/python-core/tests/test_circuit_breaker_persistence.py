from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

from ai_automation_force_core import (
    CircuitBreakerConflictError,
    CircuitBreakerPolicy,
    CircuitState,
    FailureClass,
    PostgresCircuitBreakerRepository,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_circuit_opens_cools_down_allows_one_probe_and_recovers() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    repository = PostgresCircuitBreakerRepository(engine)
    policy = CircuitBreakerPolicy(
        failure_threshold=3,
        open_seconds=20,
        probe_lease_seconds=10,
    )
    now = datetime.now(UTC)
    key = "provider:synthetic-video"

    try:
        initial = repository.acquire_permission(key, owner="worker-a", now=now, policy=policy)
        assert initial.allowed
        assert initial.state is CircuitState.CLOSED

        first = repository.record_failure(
            key,
            owner="worker-a",
            failure_class=FailureClass.TRANSIENT,
            now=now + timedelta(seconds=1),
            policy=policy,
        )
        second = repository.record_failure(
            key,
            owner="worker-a",
            failure_class=FailureClass.TIMEOUT,
            now=now + timedelta(seconds=2),
            policy=policy,
        )
        opened = repository.record_failure(
            key,
            owner="worker-a",
            failure_class=FailureClass.PROVIDER_UNAVAILABLE,
            now=now + timedelta(seconds=3),
            policy=policy,
        )
        assert first.state is CircuitState.CLOSED
        assert second.state is CircuitState.CLOSED
        assert opened.state is CircuitState.OPEN
        assert opened.consecutive_failures == 3
        assert opened.next_probe_at == now + timedelta(seconds=23)

        denied = repository.acquire_permission(
            key,
            owner="worker-b",
            now=now + timedelta(seconds=10),
            policy=policy,
        )
        assert not denied.allowed
        assert denied.state is CircuitState.OPEN
        assert denied.retry_at == opened.next_probe_at

        probe = repository.acquire_permission(
            key,
            owner="worker-b",
            now=now + timedelta(seconds=24),
            policy=policy,
        )
        assert probe.allowed
        assert probe.state is CircuitState.HALF_OPEN
        assert probe.probe_owner == "worker-b"

        competing_probe = repository.acquire_permission(
            key,
            owner="worker-c",
            now=now + timedelta(seconds=25),
            policy=policy,
        )
        assert not competing_probe.allowed
        assert competing_probe.state is CircuitState.HALF_OPEN

        with pytest.raises(CircuitBreakerConflictError, match="another worker"):
            repository.record_success(
                key,
                owner="worker-c",
                now=now + timedelta(seconds=26),
            )

        closed = repository.record_success(
            key,
            owner="worker-b",
            now=now + timedelta(seconds=27),
        )
        assert closed.state is CircuitState.CLOSED
        assert closed.consecutive_failures == 0

        permitted = repository.acquire_permission(
            key,
            owner="worker-c",
            now=now + timedelta(seconds=28),
            policy=policy,
        )
        assert permitted.allowed
        assert permitted.state is CircuitState.CLOSED
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_failed_half_open_probe_reopens_and_expired_probe_can_be_reassigned() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    repository = PostgresCircuitBreakerRepository(engine)
    policy = CircuitBreakerPolicy(
        failure_threshold=1,
        open_seconds=5,
        probe_lease_seconds=3,
    )
    now = datetime.now(UTC)
    key = "provider:synthetic-audio"

    try:
        repository.record_failure(
            key,
            owner="worker-a",
            failure_class=FailureClass.RATE_LIMIT,
            now=now,
            policy=policy,
        )
        first_probe = repository.acquire_permission(
            key,
            owner="worker-b",
            now=now + timedelta(seconds=6),
            policy=policy,
        )
        assert first_probe.state is CircuitState.HALF_OPEN

        replacement = repository.acquire_permission(
            key,
            owner="worker-c",
            now=now + timedelta(seconds=10),
            policy=policy,
        )
        assert replacement.allowed
        assert replacement.probe_owner == "worker-c"

        reopened = repository.record_failure(
            key,
            owner="worker-c",
            failure_class=FailureClass.TRANSIENT,
            now=now + timedelta(seconds=11),
            policy=policy,
        )
        assert reopened.state is CircuitState.OPEN
        assert reopened.next_probe_at == now + timedelta(seconds=16)
    finally:
        engine.dispose()
        command.downgrade(config, "base")
