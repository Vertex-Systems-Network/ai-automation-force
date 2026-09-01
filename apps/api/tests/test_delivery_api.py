from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from ai_automation_force_core import (
    AssetAccessClass,
    DeliveryAuthorization,
    DeliveryMode,
    PostgresDeliveryRepository,
    PostgresShareLinkRepository,
    ShareLinkConstraint,
    SignedDeliveryGrant,
    StorageObject,
)
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from ai_automation_force_api import Settings, create_app

DATABASE_URL = os.environ.get("DATABASE_URL")
ALEMBIC_INI = Path(__file__).parents[3] / "packages/python-core/alembic.ini"
NOW = datetime(2026, 9, 1, 21, 30, tzinfo=UTC)
DIGEST = "f" * 64
RAW_SHARE_TOKEN = "share-token-006501-secure"


def alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def seed_deliverable(engine: Any) -> tuple[str, str]:
    project_id = "PRJ-006501"
    asset_id = "AST-006501"
    storage_id = "STO-006501"
    rights_id = "RGT-006501"
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO core.projects (
                    id, external_id, title, status, audience, "cast", content_format,
                    language, target_duration_seconds, output, creative, provider_policy,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :project_id, 'API delivery fixture', 'draft',
                    '{}'::jsonb, '{}'::jsonb, 'song', 'en', 120,
                    '{}'::jsonb, '{}'::jsonb, '{}'::jsonb, :now, :now
                )
                """
            ),
            {"project_id": project_id, "now": NOW},
        )
        connection.execute(
            text(
                """
                INSERT INTO core.rights_records (
                    id, external_id, subject_type, subject_id, commercial_use,
                    publication_blocked, verified_at
                ) VALUES (
                    gen_random_uuid(), :rights_id, 'asset', :asset_id,
                    'allowed', false, :now
                )
                """
            ),
            {"rights_id": rights_id, "asset_id": asset_id, "now": NOW},
        )
        connection.execute(
            text(
                """
                INSERT INTO core.assets (
                    id, external_id, project_id, kind, uri, sha256, mime_type,
                    size_bytes, rights_record_id, canonical_status,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :asset_id,
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    'video', :uri, :digest, 'video/mp4', 128,
                    (SELECT id FROM core.rights_records WHERE external_id = :rights_id),
                    'approved', :now, :now
                )
                """
            ),
            {
                "asset_id": asset_id,
                "project_id": project_id,
                "uri": f"s3://canonical-media/source/{project_id}/{storage_id}",
                "digest": DIGEST,
                "rights_id": rights_id,
                "now": NOW,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO core.storage_objects (
                    id, external_id, project_id, backend, bucket, object_key,
                    sha256, mime_type, size_bytes, region, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :storage_id,
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    's3', 'canonical-media', :object_key, :digest,
                    'video/mp4', 128, 'eu-west-1', :now, :now
                )
                """
            ),
            {
                "storage_id": storage_id,
                "project_id": project_id,
                "object_key": f"source/{project_id}/{storage_id}",
                "digest": DIGEST,
                "now": NOW,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO core.asset_provenance_records (
                    id, external_id, asset_id, project_id, storage_object_id,
                    source_kind, content_sha256, rights_record_id, created_at
                ) VALUES (
                    gen_random_uuid(), 'PRV-006501',
                    (SELECT id FROM core.assets WHERE external_id = :asset_id),
                    (SELECT id FROM core.projects WHERE external_id = :project_id),
                    (SELECT id FROM core.storage_objects WHERE external_id = :storage_id),
                    'upload', :digest,
                    (SELECT id FROM core.rights_records WHERE external_id = :rights_id),
                    :created_at
                )
                """
            ),
            {
                "asset_id": asset_id,
                "project_id": project_id,
                "storage_id": storage_id,
                "digest": DIGEST,
                "rights_id": rights_id,
                "created_at": NOW + timedelta(seconds=1),
            },
        )
    return project_id, asset_id


class CapturingSigner:
    def __init__(self, storage: StorageObject, captures: list[StorageObject]) -> None:
        self.storage = storage
        self.captures = captures

    def create_grant(
        self,
        subject: Any,
        authorization: DeliveryAuthorization,
        *,
        mode: DeliveryMode,
        now: datetime,
        expires_in_seconds: int = 900,
    ) -> SignedDeliveryGrant:
        self.captures.append(self.storage)
        return SignedDeliveryGrant(
            url=(
                "https://signed.example/"
                f"{self.storage.bucket}/{subject.object_key}?signature=opaque"
            ),
            object_key=subject.object_key,
            mode=mode,
            authorization=authorization.kind,
            expires_at=now + timedelta(seconds=expires_in_seconds),
            supports_range=True,
        )


@pytest.mark.postgres
@pytest.mark.skipif(DATABASE_URL is None, reason="DATABASE_URL is not configured")
def test_signed_delivery_api_enforces_tenant_public_share_and_canonical_bucket_boundaries() -> None:
    assert DATABASE_URL is not None
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = create_engine(DATABASE_URL)
    try:
        project_id, asset_id = seed_deliverable(engine)
        share_links = PostgresShareLinkRepository(engine)
        share_links.create(
            ShareLinkConstraint(
                share_link_id="SHARE-006501",
                project_id=project_id,
                asset_id=asset_id,
                token_sha256=hashlib.sha256(RAW_SHARE_TOKEN.encode()).hexdigest(),
                allowed_modes=[DeliveryMode.STREAM],
                expires_at=NOW + timedelta(hours=2),
                max_uses=2,
            ),
            created_at=NOW + timedelta(minutes=1),
        )

        settings = Settings(
            environment="test",
            internal_dev_identity="wp6-api-test",
            database_url=DATABASE_URL,
            delivery_url_max_ttl_seconds=300,
            s3_region_name="us-east-1",
        )
        app = create_app(settings)
        captures: list[StorageObject] = []

        with TestClient(app) as client:
            service = app.state.delivery_service
            assert service is not None
            service.signer_factory = lambda storage, _: CapturingSigner(storage, captures)

            denied = client.post(
                f"/api/v1/assets/{asset_id}/delivery",
                headers={"X-Project-ID": "PRJ-006599"},
                json={"mode": "stream", "expires_in_seconds": 120},
            )
            assert denied.status_code == 403
            assert captures == []

            project_grant = client.post(
                f"/api/v1/assets/{asset_id}/delivery",
                headers={"X-Project-ID": project_id},
                json={"mode": "stream", "expires_in_seconds": 120},
            )
            assert project_grant.status_code == 200
            payload = project_grant.json()
            assert payload["authorization"] == "project"
            assert payload["supports_range"] is True
            assert payload["accept_ranges"] == "bytes"
            assert captures[-1].bucket == "canonical-media"
            assert captures[-1].region == "eu-west-1"
            assert "canonical-media" in payload["url"]

            public_repo = PostgresDeliveryRepository(service.engine)
            public_repo.set_access_class(
                asset_id,
                AssetAccessClass.PUBLIC,
                now=NOW + timedelta(minutes=2),
            )
            public_grant = client.post(
                f"/api/v1/assets/{asset_id}/delivery",
                json={"mode": "download"},
            )
            assert public_grant.status_code == 200
            assert public_grant.json()["authorization"] == "public"

            public_repo.set_access_class(
                asset_id,
                AssetAccessClass.PRIVATE,
                now=NOW + timedelta(minutes=3),
            )
            share_grant = client.post(
                f"/api/v1/assets/{asset_id}/delivery",
                headers={"Authorization": f"Bearer {RAW_SHARE_TOKEN}"},
                json={"mode": "stream", "expires_in_seconds": 60},
            )
            assert share_grant.status_code == 200
            assert share_grant.json()["authorization"] == "share-link"
            assert share_links.load("SHARE-006501").use_count == 1

            wrong_mode = client.post(
                f"/api/v1/assets/{asset_id}/delivery",
                headers={"Authorization": f"Bearer {RAW_SHARE_TOKEN}"},
                json={"mode": "download"},
            )
            assert wrong_mode.status_code == 403
            assert share_links.load("SHARE-006501").use_count == 1
    finally:
        engine.dispose()
        command.downgrade(config, "base")


def test_project_header_is_not_trusted_in_production_without_authenticated_context() -> None:
    settings = Settings(environment="production")
    app = create_app(settings)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/assets/AST-006501/delivery",
            headers={"X-Project-ID": "PRJ-006501"},
            json={"mode": "stream"},
        )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNTRUSTED_PROJECT_IDENTITY"
