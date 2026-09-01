from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from ai_automation_force_core.delivery import (
    AssetAccessClass,
    DeliveryAuthorization,
    DeliveryAuthorizationError,
    DeliveryAuthorizationKind,
    DeliveryMode,
    DeliverySubject,
)
from ai_automation_force_core.delivery_s3 import S3DeliveryAdapter
from ai_automation_force_core.storage_s3 import S3StorageAdapter, S3StorageSettings


NOW = datetime(2026, 9, 1, 19, 30, tzinfo=UTC)


class FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.signed_url: object = "https://storage.example/private-object?signature=opaque"

    def generate_presigned_url(self, **kwargs: Any) -> object:
        self.calls.append(("generate_presigned_url", kwargs))
        return self.signed_url


def subject() -> DeliverySubject:
    return DeliverySubject(
        project_id="PRJ-006101",
        asset_id="AST-006101",
        storage_object_id="STO-006101",
        object_key="source/PRJ-006101/STO-006101",
        mime_type="video/mp4",
        access_class=AssetAccessClass.PRIVATE,
    )


def authorization() -> DeliveryAuthorization:
    return DeliveryAuthorization(
        kind=DeliveryAuthorizationKind.PROJECT,
        project_id="PRJ-006101",
        asset_id="AST-006101",
    )


def adapter(client: FakeS3Client) -> S3DeliveryAdapter:
    storage = S3StorageAdapter(
        S3StorageSettings(bucket="aaf-private", region_name="us-east-1"),
        client=client,
    )
    return S3DeliveryAdapter(storage)


def test_stream_grant_signs_exact_get_object_and_leaves_range_requestable() -> None:
    client = FakeS3Client()
    delivery = adapter(client)

    grant = delivery.create_grant(
        subject(),
        authorization(),
        mode=DeliveryMode.STREAM,
        now=NOW,
        expires_in_seconds=300,
    )

    assert grant.method == "GET"
    assert grant.mode is DeliveryMode.STREAM
    assert grant.supports_range is True
    assert grant.expires_at == NOW + timedelta(seconds=300)
    assert grant.authorization is DeliveryAuthorizationKind.PROJECT

    name, kwargs = client.calls[-1]
    assert name == "generate_presigned_url"
    assert kwargs["ClientMethod"] == "get_object"
    assert kwargs["HttpMethod"] == "GET"
    assert kwargs["ExpiresIn"] == 300
    assert kwargs["Params"] == {
        "Bucket": "aaf-private",
        "Key": "source/PRJ-006101/STO-006101",
        "ResponseContentType": "video/mp4",
        "ResponseContentDisposition": "inline",
    }
    assert "Range" not in kwargs["Params"]


def test_download_grant_uses_attachment_and_is_short_lived() -> None:
    client = FakeS3Client()
    delivery = adapter(client)

    grant = delivery.create_grant(
        subject(),
        authorization(),
        mode=DeliveryMode.DOWNLOAD,
        now=NOW,
        expires_in_seconds=60,
    )

    assert grant.expires_at == NOW + timedelta(seconds=60)
    assert client.calls[-1][1]["Params"]["ResponseContentDisposition"] == "attachment"

    with pytest.raises(ValueError, match="between 1 and 3600"):
        delivery.create_grant(
            subject(),
            authorization(),
            mode=DeliveryMode.DOWNLOAD,
            now=NOW,
            expires_in_seconds=3601,
        )


def test_signing_refuses_authority_for_another_asset_or_project() -> None:
    client = FakeS3Client()
    delivery = adapter(client)

    with pytest.raises(DeliveryAuthorizationError, match="project"):
        delivery.create_grant(
            subject(),
            authorization().model_copy(update={"project_id": "PRJ-006999"}),
            mode=DeliveryMode.STREAM,
            now=NOW,
        )

    with pytest.raises(DeliveryAuthorizationError, match="asset"):
        delivery.create_grant(
            subject(),
            authorization().model_copy(update={"asset_id": "AST-006999"}),
            mode=DeliveryMode.STREAM,
            now=NOW,
        )

    assert client.calls == []


def test_invalid_signed_url_fails_closed() -> None:
    client = FakeS3Client()
    client.signed_url = ""
    delivery = adapter(client)

    with pytest.raises(RuntimeError, match="did not return"):
        delivery.create_grant(
            subject(),
            authorization(),
            mode=DeliveryMode.STREAM,
            now=NOW,
        )
