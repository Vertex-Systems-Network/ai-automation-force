from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from ai_automation_force_core import (
    AssetAccessClass,
    DeliveryAuthorizationError,
    DeliveryAuthorizationKind,
    DeliveryMode,
    DeliverySubject,
    PostgresShareLinkRepository,
    ShareLinkConstraint,
    ShareLinkPersistenceConflictError,
)

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def insert_project_and_asset(engine: object, project_id: str, asset_id: str) -> None:
    with engine.begin() as connection:  # type: ignore[attr-defined]
        connection.execute(
            text(
                """
                INSERT INTO core.projects (
                    id, external_id, title, status, audience, "cast", content_format,
                    language, target_duration_seconds, output, creative, provider_policy,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :project_id, :title, 'draft',
                    '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                    '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, now(), now()
                )
                """
            ),
            {"project_id": project_id, "title": f"Share-link fixture {project_id}"},
        )
        connection.execute(
            text(
                """
                INSERT INTO core.assets (
                    id, external_id, project_id, kind, uri, sha256, mime_type,
                    size_bytes, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :asset_id,
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    'image', :uri,
                    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                    'image/png', 12, now(), now()
                )
                """
            ),
            {
                "project_id": project_id,
                "asset_id": asset_id,
                "uri": f"s3://aaf-private/source/{project_id}/STO-006201",
            },
        )


def subject(project_id: str, asset_id: str) -> DeliverySubject:
    return DeliverySubject(
        project_id=project_id,
        asset_id=asset_id,
        storage_object_id="STO-006201",
        object_key=f"source/{project_id}/STO-006201",
        mime_type="image/png",
        access_class=AssetAccessClass.PRIVATE,
    )


def link(
    share_link_id: str,
    project_id: str,
    asset_id: str,
    token_sha256: str,
    *,
    started: datetime,
    max_uses: int | None = 2,
    allowed_modes: list[DeliveryMode] | None = None,
) -> ShareLinkConstraint:
    return ShareLinkConstraint(
        share_link_id=share_link_id,
        project_id=project_id,
        asset_id=asset_id,
        token_sha256=token_sha256,
        allowed_modes=allowed_modes or [DeliveryMode.STREAM],
        expires_at=started + timedelta(hours=1),
        max_uses=max_uses,
    )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_share_link_persistence_is_digest_only_idempotent_and_fail_closed() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)

    try:
        project_id = "PRJ-006201"
        asset_id = "AST-006201"
        started = datetime(2026, 9, 1, 20, 0, tzinfo=UTC)
        digest = "b" * 64
        insert_project_and_asset(engine, project_id, asset_id)
        repository = PostgresShareLinkRepository(engine)
        requested = link(
            "SHARE-006201",
            project_id,
            asset_id,
            digest,
            started=started,
        )

        created = repository.create(requested, created_at=started)
        assert created.action == "created"
        assert created.use_count == 0
        assert created.revision == 1

        replayed = repository.create(requested, created_at=started + timedelta(seconds=1))
        assert replayed.action == "reused"
        assert replayed.revision == 1
        assert repository.load_by_token_sha256(digest) == requested

        with engine.connect() as connection:
            columns = {
                row[0]
                for row in connection.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'core'
                          AND table_name = 'delivery_share_links'
                        """
                    )
                )
            }
            persisted_digest = connection.execute(
                text(
                    "SELECT token_sha256 FROM core.delivery_share_links WHERE external_id = :id"
                ),
                {"id": requested.share_link_id},
            ).scalar_one()
        assert persisted_digest == digest
        assert "token" not in columns
        assert "raw_token" not in columns

        authorization = repository.authorize_and_consume(
            subject(project_id, asset_id),
            DeliveryMode.STREAM,
            token_sha256=digest,
            now=started + timedelta(minutes=1),
        )
        assert authorization.authorization.kind is DeliveryAuthorizationKind.SHARE_LINK
        assert authorization.use_count == 1
        assert authorization.revision == 2

        with pytest.raises(DeliveryAuthorizationError, match="requested mode"):
            repository.authorize_and_consume(
                subject(project_id, asset_id),
                DeliveryMode.DOWNLOAD,
                token_sha256=digest,
                now=started + timedelta(minutes=2),
            )
        assert repository.load(requested.share_link_id).use_count == 1

        wrong_subject = subject(project_id, "AST-006999")
        with pytest.raises(DeliveryAuthorizationError, match="not bound"):
            repository.authorize_and_consume(
                wrong_subject,
                DeliveryMode.STREAM,
                token_sha256=digest,
                now=started + timedelta(minutes=2),
            )
        assert repository.load(requested.share_link_id).use_count == 1

        second = repository.authorize_and_consume(
            subject(project_id, asset_id),
            DeliveryMode.STREAM,
            token_sha256=digest,
            now=started + timedelta(minutes=3),
        )
        assert second.use_count == 2
        with pytest.raises(DeliveryAuthorizationError, match="use limit"):
            repository.authorize_and_consume(
                subject(project_id, asset_id),
                DeliveryMode.STREAM,
                token_sha256=digest,
                now=started + timedelta(minutes=4),
            )

        with pytest.raises(
            ShareLinkPersistenceConflictError,
            match="different creation semantics",
        ):
            repository.create(
                requested.model_copy(update={"max_uses": 3}),
                created_at=started,
            )
    finally:
        engine.dispose()
        command.downgrade(config, "base")


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_share_link_last_use_is_atomic_under_concurrent_requests_and_revoke_is_durable() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL, pool_size=4, max_overflow=0)

    try:
        project_id = "PRJ-006210"
        asset_id = "AST-006210"
        started = datetime(2026, 9, 1, 20, 10, tzinfo=UTC)
        digest = "c" * 64
        insert_project_and_asset(engine, project_id, asset_id)
        repository = PostgresShareLinkRepository(engine)
        requested = link(
            "SHARE-006210",
            project_id,
            asset_id,
            digest,
            started=started,
            max_uses=1,
        )
        assert repository.create(requested, created_at=started).action == "created"

        gate = Barrier(2)

        def consume_once() -> str:
            gate.wait(timeout=5)
            try:
                result = repository.authorize_and_consume(
                    subject(project_id, asset_id),
                    DeliveryMode.STREAM,
                    token_sha256=digest,
                    now=started + timedelta(minutes=1),
                )
            except DeliveryAuthorizationError:
                return "denied"
            return f"authorized:{result.use_count}"

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _: consume_once(), range(2)))

        assert sorted(outcomes) == ["authorized:1", "denied"]
        persisted = repository.load(requested.share_link_id)
        assert persisted.use_count == 1

        revoked_at = started + timedelta(minutes=2)
        revoked = repository.revoke(requested.share_link_id, revoked_at=revoked_at)
        assert revoked.action == "revoked"
        assert revoked.use_count == 1
        assert revoked.revision == 3
        assert revoked.revoked_at == revoked_at

        replayed = repository.revoke(requested.share_link_id, revoked_at=revoked_at)
        assert replayed.action == "reused"
        assert replayed.revision == 3

        with pytest.raises(DeliveryAuthorizationError, match="revoked"):
            repository.authorize_and_consume(
                subject(project_id, asset_id),
                DeliveryMode.STREAM,
                token_sha256=digest,
                now=started + timedelta(minutes=3),
            )
    finally:
        engine.dispose()
        command.downgrade(config, "base")
