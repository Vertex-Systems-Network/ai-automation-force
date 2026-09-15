from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Header, Request

from .errors import APIError
from .settings import Settings


def _bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise APIError(
            "CONTROL_AUTH_REQUIRED",
            "control-plane authentication is required",
            status_code=401,
        )
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token:
        raise APIError(
            "CONTROL_AUTH_REQUIRED",
            "control-plane authentication is required",
            status_code=401,
        )
    if token != token.strip() or len(token) > 4096:
        raise APIError(
            "CONTROL_AUTH_INVALID",
            "control-plane credentials are invalid",
            status_code=401,
        )
    return token


async def require_control_auth(
    request: Request,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise APIError(
            "CONTROL_AUTH_UNAVAILABLE",
            "control-plane authentication is unavailable",
            status_code=503,
        )

    configured = settings.control_api_key
    if configured is None:
        # Keep test fixtures lightweight, but never fail open in a runnable
        # development/staging/production service. A forgotten environment or API
        # key must not silently expose the control plane.
        if settings.environment == "test":
            return
        raise APIError(
            "CONTROL_AUTH_UNAVAILABLE",
            "control-plane authentication is not configured",
            status_code=503,
        )

    provided = _bearer_token(authorization)
    expected = configured.get_secret_value()
    if not secrets.compare_digest(provided, expected):
        raise APIError(
            "CONTROL_AUTH_INVALID",
            "control-plane credentials are invalid",
            status_code=401,
        )
