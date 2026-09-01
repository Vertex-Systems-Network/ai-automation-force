from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from ai_automation_force_core import (
    DeliveryAuthorizationError,
    DeliveryMode,
    DeliveryResolutionError,
    DeliverySigningError,
    PersistenceNotFoundError,
    PostgresDeliveryRepository,
    PostgresShareLinkRepository,
    S3DeliveryAdapter,
    S3StorageAdapter,
    S3StorageSettings,
    SignedDeliveryGrant,
    StorageBackend,
    StorageObject,
    authorize_delivery,
)
from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .errors import APIError
from .settings import Settings

AssetIdValue = Annotated[str, Field(pattern=r"^AST-[0-9]{6,20}$")]
ProjectIdValue = Annotated[str, Field(pattern=r"^PRJ-[0-9]{6,20}$")]


class StrictDeliveryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DeliveryGrantRequest(StrictDeliveryModel):
    mode: DeliveryMode
    expires_in_seconds: int | None = Field(default=None, ge=1, le=3600)


class DeliveryGrantResponse(StrictDeliveryModel):
    asset_id: str
    project_id: str
    mode: DeliveryMode
    authorization: str
    url: str
    expires_at: datetime
    supports_range: bool
    accept_ranges: str | None = None


class DeliveryDependencyError(RuntimeError):
    """A delivery dependency is unavailable or incompatible with canonical storage."""


DeliverySignerFactory = Callable[[StorageObject, Settings], S3DeliveryAdapter]


def _secret(value: object) -> str | None:
    if value is None:
        return None
    getter = getattr(value, "get_secret_value", None)
    return str(getter()) if callable(getter) else str(value)


def _default_signer(storage: StorageObject, settings: Settings) -> S3DeliveryAdapter:
    if storage.backend is not StorageBackend.S3 or storage.bucket is None:
        raise DeliveryDependencyError("signed delivery requires canonical S3 storage")
    adapter = S3StorageAdapter(
        S3StorageSettings(
            bucket=storage.bucket,
            region_name=storage.region or settings.s3_region_name,
            endpoint_url=settings.s3_endpoint_url,
            addressing_style=settings.s3_addressing_style,
            verify_ssl=settings.s3_verify_ssl,
            access_key_id=_secret(settings.s3_access_key_id),
            secret_access_key=_secret(settings.s3_secret_access_key),
            session_token=_secret(settings.s3_session_token),
        )
    )
    if adapter.settings.bucket != storage.bucket:
        raise DeliveryDependencyError("delivery signer bucket does not match canonical storage")
    return S3DeliveryAdapter(
        adapter,
        max_expiry_seconds=settings.delivery_url_max_ttl_seconds,
    )


class DeliveryService:
    def __init__(
        self,
        settings: Settings,
        *,
        signer_factory: DeliverySignerFactory | None = None,
    ) -> None:
        if settings.database_url is None:
            raise ValueError("DATABASE_URL is required for signed delivery")
        self.settings = settings
        self.engine: Engine = create_engine(
            settings.database_url.get_secret_value(),
            pool_pre_ping=True,
        )
        self.delivery = PostgresDeliveryRepository(self.engine)
        self.share_links = PostgresShareLinkRepository(self.engine)
        self.signer_factory = signer_factory or _default_signer

    def close(self) -> None:
        self.engine.dispose()

    def create_grant(
        self,
        asset_id: str,
        request: DeliveryGrantRequest,
        *,
        requester_project_id: str | None,
        share_token: str | None,
        now: datetime | None = None,
    ) -> DeliveryGrantResponse:
        at = now or datetime.now(UTC)
        resolved = self.delivery.resolve(asset_id)
        subject = resolved.subject

        if share_token is not None:
            digest = hashlib.sha256(share_token.encode("utf-8")).hexdigest()
            consumed = self.share_links.authorize_and_consume(
                subject,
                request.mode,
                token_sha256=digest,
                now=at,
            )
            authorization = consumed.authorization
        else:
            authorization = authorize_delivery(
                subject,
                request.mode,
                now=at,
                requester_project_id=requester_project_id,
            )

        storage = resolved.storage_object
        if storage.backend is not StorageBackend.S3 or storage.bucket is None:
            raise DeliveryDependencyError("signed delivery requires canonical S3 storage")

        ttl = request.expires_in_seconds or self.settings.delivery_url_max_ttl_seconds
        if ttl > self.settings.delivery_url_max_ttl_seconds:
            raise ValueError(
                "requested delivery expiry exceeds the configured maximum"
            )
        signer = self.signer_factory(storage, self.settings)
        grant: SignedDeliveryGrant = signer.create_grant(
            subject,
            authorization,
            mode=request.mode,
            now=at,
            expires_in_seconds=ttl,
        )
        return DeliveryGrantResponse(
            asset_id=subject.asset_id,
            project_id=subject.project_id,
            mode=request.mode,
            authorization=authorization.kind.value,
            url=grant.url,
            expires_at=grant.expires_at,
            supports_range=grant.supports_range,
            accept_ranges="bytes" if grant.supports_range else None,
        )


def _service(request: Request) -> DeliveryService:
    service = getattr(request.app.state, "delivery_service", None)
    if not isinstance(service, DeliveryService):
        raise APIError(
            "DELIVERY_NOT_READY",
            "signed delivery dependencies are not available",
            status_code=503,
        )
    return service


def _share_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token:
        raise APIError(
            "INVALID_DELIVERY_AUTHORIZATION",
            "Authorization must use a Bearer token",
            status_code=401,
        )
    if token != token.strip() or len(token) < 16 or len(token) > 4096:
        raise APIError(
            "INVALID_DELIVERY_AUTHORIZATION",
            "share token is malformed",
            status_code=401,
        )
    return token


def _project_identity(request: Request, project_header: str | None) -> str | None:
    trusted = getattr(request.state, "authenticated_project_id", None)
    if trusted is not None:
        trusted_id = str(trusted)
        if project_header is not None and project_header != trusted_id:
            raise APIError(
                "PROJECT_IDENTITY_MISMATCH",
                "project header conflicts with authenticated request context",
                status_code=403,
            )
        return trusted_id

    settings = request.app.state.settings
    if project_header is None:
        return None
    if (
        settings.environment in {"development", "test"}
        and settings.internal_dev_identity is not None
    ):
        return project_header
    raise APIError(
        "UNTRUSTED_PROJECT_IDENTITY",
        "project identity must be supplied by trusted authentication context",
        status_code=401,
    )


def _translate_error(exc: Exception) -> APIError:
    if isinstance(exc, APIError):
        return exc
    if isinstance(exc, PersistenceNotFoundError):
        return APIError(
            "DELIVERY_NOT_FOUND",
            "asset delivery target was not found",
            status_code=404,
        )
    if isinstance(exc, (DeliveryAuthorizationError, DeliveryResolutionError)):
        return APIError("DELIVERY_FORBIDDEN", str(exc), status_code=403)
    if isinstance(exc, DeliverySigningError):
        return APIError(
            "DELIVERY_SIGNING_FAILED",
            "delivery capability could not be issued",
            status_code=503,
        )
    if isinstance(exc, DeliveryDependencyError):
        return APIError("DELIVERY_DEPENDENCY_UNAVAILABLE", str(exc), status_code=503)
    if isinstance(exc, ValueError):
        return APIError("INVALID_DELIVERY_REQUEST", str(exc), status_code=400)
    return APIError("DELIVERY_FAILURE", "signed delivery operation failed", status_code=500)


def delivery_router() -> APIRouter:
    router = APIRouter(tags=["assets"])

    @router.post("/assets/{asset_id}/delivery", response_model=DeliveryGrantResponse)
    async def create_delivery_grant(
        request: Request,
        asset_id: AssetIdValue,
        body: DeliveryGrantRequest,
        authorization: Annotated[str | None, Header(alias="Authorization")] = None,
        project_id: Annotated[ProjectIdValue | None, Header(alias="X-Project-ID")] = None,
    ) -> DeliveryGrantResponse:
        try:
            requester_project_id = _project_identity(request, project_id)
            share_token = _share_token(authorization)
            return _service(request).create_grant(
                asset_id,
                body,
                requester_project_id=requester_project_id,
                share_token=share_token,
            )
        except Exception as exc:
            raise _translate_error(exc) from exc

    return router
