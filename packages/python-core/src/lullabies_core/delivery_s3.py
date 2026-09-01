from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .delivery import (
    DeliveryAuthorization,
    DeliveryAuthorizationError,
    DeliveryMode,
    DeliverySubject,
    SignedDeliveryGrant,
)
from .storage import StorageBackend
from .storage_s3 import S3StorageAdapter


class DeliverySigningError(RuntimeError):
    """The storage backend could not issue a valid ephemeral delivery capability."""


@dataclass(frozen=True)
class S3DeliveryAdapter:
    """Issue exact-object, short-lived S3 GET capabilities after authorization."""

    storage: S3StorageAdapter
    max_expiry_seconds: int = 3600

    def __post_init__(self) -> None:
        if self.max_expiry_seconds < 1 or self.max_expiry_seconds > 3600:
            raise ValueError("max_expiry_seconds must be between 1 and 3600 seconds")

    def create_grant(
        self,
        subject: DeliverySubject,
        authorization: DeliveryAuthorization,
        *,
        mode: DeliveryMode,
        now: datetime,
        expires_in_seconds: int = 900,
    ) -> SignedDeliveryGrant:
        if authorization.project_id != subject.project_id:
            raise DeliveryAuthorizationError("authorization project does not match delivery subject")
        if authorization.asset_id != subject.asset_id:
            raise DeliveryAuthorizationError("authorization asset does not match delivery subject")
        if expires_in_seconds < 1 or expires_in_seconds > self.max_expiry_seconds:
            raise ValueError(
                f"signed delivery expiry must be between 1 and {self.max_expiry_seconds} seconds"
            )

        params: dict[str, Any] = {
            "Bucket": self.storage.settings.bucket,
            "Key": subject.object_key,
            "ResponseContentType": subject.mime_type,
            "ResponseContentDisposition": (
                "attachment" if mode is DeliveryMode.DOWNLOAD else "inline"
            ),
        }
        url = self.storage.client.generate_presigned_url(
            ClientMethod="get_object",
            Params=params,
            ExpiresIn=expires_in_seconds,
            HttpMethod="GET",
        )
        if not isinstance(url, str) or not url:
            raise DeliverySigningError("S3 did not return a signed delivery URL")

        return SignedDeliveryGrant(
            url=url,
            object_key=subject.object_key,
            mode=mode,
            authorization=authorization.kind,
            expires_at=now + timedelta(seconds=expires_in_seconds),
            # S3 GET accepts ordinary HTTP Range requests against the same signed
            # capability. Range is deliberately not embedded in the signature so one
            # short-lived stream grant can support seeking without widening object scope.
            supports_range=True,
        )

    @property
    def backend(self) -> StorageBackend:
        return self.storage.backend
