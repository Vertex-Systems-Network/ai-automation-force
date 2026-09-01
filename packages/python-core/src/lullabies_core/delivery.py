from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from .common import AssetId, ProjectId, StorageObjectId, StrictModel
from .production import Asset
from .provenance import AssetProvenanceRecord
from .storage import StorageObject, validate_object_key


class AssetAccessClass(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"


class DeliveryMode(StrEnum):
    DOWNLOAD = "download"
    STREAM = "stream"


class DeliveryAuthorizationKind(StrEnum):
    PROJECT = "project"
    SHARE_LINK = "share-link"
    PUBLIC = "public"


class DeliveryAuthorizationError(RuntimeError):
    """A delivery request is not authorized by the canonical access boundary."""


class DeliveryBindingError(RuntimeError):
    """Canonical asset/provenance/storage records do not describe one object."""


class DeliverySubject(StrictModel):
    project_id: ProjectId
    asset_id: AssetId
    storage_object_id: StorageObjectId
    object_key: str = Field(min_length=1, max_length=1024)
    mime_type: str = Field(min_length=3, max_length=255)
    access_class: AssetAccessClass = AssetAccessClass.PRIVATE

    @model_validator(mode="after")
    def validate_key(self) -> DeliverySubject:
        validate_object_key(self.object_key)
        return self


class ShareLinkConstraint(StrictModel):
    """Resolved share-link authority; raw bearer tokens are intentionally excluded."""

    share_link_id: str = Field(min_length=8, max_length=160)
    project_id: ProjectId
    asset_id: AssetId
    token_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    allowed_modes: list[DeliveryMode] = Field(min_length=1, max_length=2)
    expires_at: AwareDatetime
    revoked_at: AwareDatetime | None = None
    max_uses: int | None = Field(default=None, ge=1, le=1_000_000)
    use_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_constraint(self) -> ShareLinkConstraint:
        if len(set(self.allowed_modes)) != len(self.allowed_modes):
            raise ValueError("allowed_modes must not contain duplicates")
        if self.revoked_at is not None and self.revoked_at > self.expires_at:
            raise ValueError("revoked_at must not follow expires_at")
        if self.max_uses is not None and self.use_count > self.max_uses:
            raise ValueError("use_count must not exceed max_uses")
        return self


class DeliveryAuthorization(StrictModel):
    kind: DeliveryAuthorizationKind
    project_id: ProjectId
    asset_id: AssetId
    share_link_id: str | None = Field(default=None, min_length=8, max_length=160)

    @model_validator(mode="after")
    def validate_share_link_reference(self) -> DeliveryAuthorization:
        if self.kind is DeliveryAuthorizationKind.SHARE_LINK and self.share_link_id is None:
            raise ValueError("share-link authorization requires share_link_id")
        if self.kind is not DeliveryAuthorizationKind.SHARE_LINK and self.share_link_id is not None:
            raise ValueError("only share-link authorization may carry share_link_id")
        return self


class SignedDeliveryGrant(StrictModel):
    """Ephemeral delivery capability; never canonical persistence or authorization."""

    method: Literal["GET"] = "GET"
    url: str = Field(min_length=1)
    object_key: str = Field(min_length=1, max_length=1024)
    mode: DeliveryMode
    authorization: DeliveryAuthorizationKind
    expires_at: AwareDatetime
    supports_range: bool = True

    @model_validator(mode="after")
    def validate_key(self) -> SignedDeliveryGrant:
        validate_object_key(self.object_key)
        return self


def bind_delivery_subject(
    asset: Asset,
    provenance: AssetProvenanceRecord,
    storage_object: StorageObject,
    *,
    access_class: AssetAccessClass = AssetAccessClass.PRIVATE,
) -> DeliverySubject:
    """Bind delivery only when canonical identity, project and bytes agree exactly."""

    if asset.project_id is None:
        raise DeliveryBindingError("delivery requires a project-scoped asset")
    if provenance.asset_id != asset.asset_id:
        raise DeliveryBindingError("provenance asset does not match delivery asset")
    if provenance.project_id != asset.project_id:
        raise DeliveryBindingError("provenance project does not match delivery asset")
    if provenance.storage_object_id != storage_object.storage_object_id:
        raise DeliveryBindingError("provenance storage object does not match delivery object")
    if storage_object.project_id != asset.project_id:
        raise DeliveryBindingError("storage object project does not match delivery asset")
    if provenance.content_sha256 != asset.sha256 or storage_object.sha256 != asset.sha256:
        raise DeliveryBindingError("delivery authority hashes do not agree")
    if storage_object.mime_type != asset.mime_type:
        raise DeliveryBindingError("storage object MIME type does not match delivery asset")

    return DeliverySubject(
        project_id=asset.project_id,
        asset_id=asset.asset_id,
        storage_object_id=storage_object.storage_object_id,
        object_key=storage_object.object_key,
        mime_type=storage_object.mime_type,
        access_class=access_class,
    )


def authorize_delivery(
    subject: DeliverySubject,
    mode: DeliveryMode,
    *,
    now: datetime,
    requester_project_id: str | None = None,
    share_link: ShareLinkConstraint | None = None,
) -> DeliveryAuthorization:
    """Resolve one fail-closed access path without treating a signed URL as authorization."""

    if requester_project_id is not None and requester_project_id == subject.project_id:
        return DeliveryAuthorization(
            kind=DeliveryAuthorizationKind.PROJECT,
            project_id=subject.project_id,
            asset_id=subject.asset_id,
        )

    if share_link is not None:
        if share_link.project_id != subject.project_id or share_link.asset_id != subject.asset_id:
            raise DeliveryAuthorizationError("share link is not bound to the requested asset")
        if share_link.revoked_at is not None:
            raise DeliveryAuthorizationError("share link is revoked")
        if now >= share_link.expires_at:
            raise DeliveryAuthorizationError("share link is expired")
        if mode not in share_link.allowed_modes:
            raise DeliveryAuthorizationError("share link does not authorize the requested mode")
        if share_link.max_uses is not None and share_link.use_count >= share_link.max_uses:
            raise DeliveryAuthorizationError("share link use limit is exhausted")
        return DeliveryAuthorization(
            kind=DeliveryAuthorizationKind.SHARE_LINK,
            project_id=subject.project_id,
            asset_id=subject.asset_id,
            share_link_id=share_link.share_link_id,
        )

    if subject.access_class is AssetAccessClass.PUBLIC:
        return DeliveryAuthorization(
            kind=DeliveryAuthorizationKind.PUBLIC,
            project_id=subject.project_id,
            asset_id=subject.asset_id,
        )

    raise DeliveryAuthorizationError("private asset delivery requires project or share-link authority")
