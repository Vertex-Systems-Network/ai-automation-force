from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Final

from fastapi import APIRouter, FastAPI, Request, status
from pydantic import BaseModel, ConfigDict

from .errors import APIError, ErrorEnvelope, install_error_handlers
from .request_context import RequestContextMiddleware
from .settings import Settings, load_settings

OPENAPI_VERSION: Final[str] = "3.1.0"


class RuntimeState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    started_at: datetime
    ready: bool = False


class HealthResponse(BaseModel):
    status: str
    service: str
    api_version: str
    build_revision: str


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        runtime = RuntimeState(started_at=datetime.now(UTC), ready=True)
        app.state.runtime = runtime
        try:
            yield
        finally:
            runtime.ready = False

    app = FastAPI(
        title="AI Automation Force Control API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.openapi_version = OPENAPI_VERSION
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)

    router = APIRouter(tags=["system"])

    @router.get("/health/live", response_model=HealthResponse)
    async def liveness() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=resolved.service_name,
            api_version=resolved.api_version,
            build_revision=resolved.build_revision,
        )

    @router.get(
        "/health/ready",
        response_model=HealthResponse,
        responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorEnvelope}},
    )
    async def readiness(request: Request) -> HealthResponse:
        runtime = getattr(request.app.state, "runtime", None)
        if runtime is None or not runtime.ready:
            raise APIError(
                "SERVICE_NOT_READY",
                "service readiness dependencies are not available",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return HealthResponse(
            status="ready",
            service=resolved.service_name,
            api_version=resolved.api_version,
            build_revision=resolved.build_revision,
        )

    app.include_router(router, prefix=resolved.api_prefix)
    return app
