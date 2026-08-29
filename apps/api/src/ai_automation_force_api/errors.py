from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .request_context import current_request_id


class ErrorDetail(BaseModel):
    code: str = Field(min_length=3, max_length=80)
    message: str = Field(min_length=1, max_length=500)
    request_id: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class APIError(RuntimeError):
    def __init__(self, code: str, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", None) or current_request_id() or "unavailable")


def _response(
    request: Request,
    *,
    code: str,
    message: str,
    status_code: int,
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    payload = ErrorEnvelope(
        error=ErrorDetail(
            code=code,
            message=message,
            request_id=_request_id(request),
            details=details or [],
        )
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


def _normalized_api_error(exc: APIError) -> APIError:
    """Preserve an already-normalized API error wrapped by a route translation boundary."""

    cause = exc.__cause__
    if isinstance(cause, APIError):
        return cause
    return exc


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        normalized = _normalized_api_error(exc)
        return _response(
            request,
            code=normalized.code,
            message=normalized.message,
            status_code=normalized.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _response(
            request,
            code="REQUEST_VALIDATION_FAILED",
            message="request validation failed",
            status_code=422,
            details=jsonable_encoder(exc.errors()),
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _response(
            request,
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        _ = exc
        return _response(
            request,
            code="INTERNAL_ERROR",
            message="an unexpected internal error occurred",
            status_code=500,
        )
