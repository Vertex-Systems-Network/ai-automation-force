from __future__ import annotations

import re

from fastapi import APIRouter
from fastapi.testclient import TestClient

from ai_automation_force_api import Settings, create_app
from ai_automation_force_api.errors import APIError

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def test_health_endpoints_and_request_id() -> None:
    app = create_app(Settings(environment="test", build_revision="test-sha"))
    with TestClient(app) as client:
        live = client.get("/api/v1/health/live", headers={"X-Request-ID": "req-test-001"})
        ready = client.get("/api/v1/health/ready")

    assert live.status_code == 200
    assert live.headers["X-Request-ID"] == "req-test-001"
    assert live.json() == {
        "status": "ok",
        "service": "ai-automation-force-api",
        "api_version": "v1",
        "build_revision": "test-sha",
    }
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert UUID_PATTERN.fullmatch(ready.headers["X-Request-ID"])


def test_invalid_request_id_is_not_reflected() -> None:
    app = create_app(Settings(environment="test"))
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live", headers={"X-Request-ID": "bad id value"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "bad id value"
    assert UUID_PATTERN.fullmatch(response.headers["X-Request-ID"])


def test_structured_api_error_contains_request_id() -> None:
    app = create_app(Settings(environment="test"))
    router = APIRouter()

    @router.get("/boom")
    async def boom() -> None:
        raise APIError("TEST_FAILURE", "synthetic failure", status_code=409)

    app.include_router(router, prefix="/api/v1")
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/v1/boom", headers={"X-Request-ID": "req-error-001"})

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "TEST_FAILURE",
            "message": "synthetic failure",
            "request_id": "req-error-001",
            "details": [],
        }
    }


def test_control_surface_fails_closed_when_database_is_not_configured() -> None:
    app = create_app(Settings(environment="test"))
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/jobs/JOB-000001",
            headers={"X-Request-ID": "req-control-001"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "CONTROL_SURFACE_UNAVAILABLE",
            "message": "job control surface is not configured",
            "request_id": "req-control-001",
            "details": [],
        }
    }


def test_openapi_schema_is_deterministic_and_versioned() -> None:
    first = create_app(Settings(environment="test", build_revision="schema-export")).openapi()
    second = create_app(Settings(environment="test", build_revision="schema-export")).openapi()

    assert first == second
    assert first["openapi"] == "3.1.0"
    expected_paths = {
        "/api/v1/health/live",
        "/api/v1/health/ready",
        "/api/v1/jobs",
        "/api/v1/jobs/{job_id}",
        "/api/v1/jobs/{job_id}/start",
        "/api/v1/jobs/{job_id}/cancel",
        "/api/v1/jobs/{job_id}/retry",
        "/api/v1/jobs/{job_id}/history",
        "/api/v1/jobs/{job_id}/events",
        "/api/v1/projects/{project_id}/jobs",
        "/api/v1/projects/{project_id}/status",
        "/api/v1/workflows/{workflow_execution_id}",
    }
    assert expected_paths.issubset(first["paths"])
