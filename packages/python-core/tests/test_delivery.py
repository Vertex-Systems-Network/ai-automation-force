from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ai_automation_force_core import (
    Asset,
    AssetKind,
    AssetProvenanceRecord,
    AssetProvenanceSource,
    AuditFields,
    StorageBackend,
    StorageObject,
    build_object_key,
)
from ai_automation_force_core.delivery import (
    AssetAccessClass,
    DeliveryAuthorizationError,
    DeliveryAuthorizationKind,
    DeliveryBindingError,
    DeliveryMode,
    ShareLinkConstraint,
    authorize_delivery,
    bind_delivery_subject,
)


NOW = datetime(2026, 9, 1, 19, 0, tzinfo=UTC)
DIGEST = "a" * 64


def canonical_records() -> tuple[Asset, AssetProvenanceRecord, StorageObject]:
    asset = Asset(
        asset_id="AST-006001",
        project_id="PRJ-006001",
        kind=AssetKind.IMAGE,
        uri="s3://aaf-private/source/PRJ-006001/STO-006001",
        sha256=DIGEST,
        mime_type="image/png",
        size_bytes=12,
        audit=AuditFields(created_at=NOW, updated_at=NOW, created_by="wp6-test"),
    )
    provenance = AssetProvenanceRecord(
        provenance_record_id="PRV-006001",
        asset_id=asset.asset_id,
        project_id=asset.project_id,
        storage_object_id="STO-006001",
        source_kind=AssetProvenanceSource.UPLOAD,
        content_sha256=DIGEST,
        created_at=NOW,
    )
    storage = StorageObject(
        storage_object_id="STO-006001",
        project_id=asset.project_id,
        backend=StorageBackend.S3,
        bucket="aaf-private",
        object_key=build_object_key(
            "source",
            "STO-006001",
            project_id="PRJ-006001",
        ),
        sha256=DIGEST,
        mime_type="image/png",
        size_bytes=12,
        region="us-east-1",
        audit=AuditFields(created_at=NOW, updated_at=NOW, created_by="wp6-test"),
    )
    return asset, provenance, storage


def test_delivery_binding_requires_exact_project_storage_hash_and_mime_authority() -> None:
    asset, provenance, storage = canonical_records()

    subject = bind_delivery_subject(asset, provenance, storage)

    assert subject.project_id == "PRJ-006001"
    assert subject.asset_id == "AST-006001"
    assert subject.storage_object_id == "STO-006001"
    assert subject.access_class is AssetAccessClass.PRIVATE

    with pytest.raises(DeliveryBindingError, match="storage object project"):
        bind_delivery_subject(
            asset,
            provenance,
            storage.model_copy(update={"project_id": "PRJ-006002"}),
        )

    with pytest.raises(DeliveryBindingError, match="hashes do not agree"):
        bind_delivery_subject(
            asset,
            provenance,
            storage.model_copy(update={"sha256": "b" * 64}),
        )

    with pytest.raises(DeliveryBindingError, match="MIME type"):
        bind_delivery_subject(
            asset,
            provenance,
            storage.model_copy(update={"mime_type": "image/jpeg"}),
        )


def test_private_delivery_fails_closed_across_projects() -> None:
    asset, provenance, storage = canonical_records()
    subject = bind_delivery_subject(asset, provenance, storage)

    authorized = authorize_delivery(
        subject,
        DeliveryMode.DOWNLOAD,
        now=NOW,
        requester_project_id="PRJ-006001",
    )
    assert authorized.kind is DeliveryAuthorizationKind.PROJECT

    with pytest.raises(DeliveryAuthorizationError, match="private asset"):
        authorize_delivery(
            subject,
            DeliveryMode.DOWNLOAD,
            now=NOW,
            requester_project_id="PRJ-006999",
        )


def test_public_access_is_explicit_and_does_not_change_object_scope() -> None:
    asset, provenance, storage = canonical_records()
    subject = bind_delivery_subject(
        asset,
        provenance,
        storage,
        access_class=AssetAccessClass.PUBLIC,
    )

    authorized = authorize_delivery(subject, DeliveryMode.STREAM, now=NOW)

    assert authorized.kind is DeliveryAuthorizationKind.PUBLIC
    assert authorized.asset_id == asset.asset_id
    assert authorized.project_id == asset.project_id


def test_share_link_is_exact_asset_mode_expiry_revocation_and_use_bound() -> None:
    asset, provenance, storage = canonical_records()
    subject = bind_delivery_subject(asset, provenance, storage)
    link = ShareLinkConstraint(
        share_link_id="SHARE-006001",
        project_id="PRJ-006001",
        asset_id="AST-006001",
        token_sha256="c" * 64,
        allowed_modes=[DeliveryMode.STREAM],
        expires_at=NOW + timedelta(minutes=10),
        max_uses=2,
        use_count=1,
    )

    authorized = authorize_delivery(
        subject,
        DeliveryMode.STREAM,
        now=NOW,
        requester_project_id="PRJ-006999",
        share_link=link,
    )
    assert authorized.kind is DeliveryAuthorizationKind.SHARE_LINK
    assert authorized.share_link_id == "SHARE-006001"

    with pytest.raises(DeliveryAuthorizationError, match="requested mode"):
        authorize_delivery(subject, DeliveryMode.DOWNLOAD, now=NOW, share_link=link)

    with pytest.raises(DeliveryAuthorizationError, match="expired"):
        authorize_delivery(
            subject,
            DeliveryMode.STREAM,
            now=link.expires_at,
            share_link=link,
        )

    with pytest.raises(DeliveryAuthorizationError, match="revoked"):
        authorize_delivery(
            subject,
            DeliveryMode.STREAM,
            now=NOW,
            share_link=link.model_copy(update={"revoked_at": NOW}),
        )

    with pytest.raises(DeliveryAuthorizationError, match="use limit"):
        authorize_delivery(
            subject,
            DeliveryMode.STREAM,
            now=NOW,
            share_link=link.model_copy(update={"use_count": 2}),
        )

    with pytest.raises(DeliveryAuthorizationError, match="not bound"):
        authorize_delivery(
            subject,
            DeliveryMode.STREAM,
            now=NOW,
            share_link=link.model_copy(update={"asset_id": "AST-006002"}),
        )
