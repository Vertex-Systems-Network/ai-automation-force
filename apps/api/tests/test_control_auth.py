from __future__ import annotations

from typing import Final

from fastapi.testclient import TestClient

from ai_automation_force_api import Settings, create_app

CONTROL_KEY: Final = "control-plane-test-key-0123456789abcdef"


def test_control_routes_require_bearer_auth_when_key_is_configured() -> None:
    app = create_app(Settings(environment="production", control_api_key=CONTROL_KEY))

    with TestClient(app) as client:
        health = client.get("/api/v1/health/live")
        assert health.status_code == 200

        missing = client.get("/api/v1/jobs/JOB-999999")
        assert missing.status_code == 401
        assert missing.json()["error"]["code"] == "CONTROL_AUTH_REQUIRED"

        malformed = client.get(
            "/api/v1/jobs/JOB-999999",
            headers={"Authorization": "Basic not-a-bearer-token"},
        )
        assert malformed.status_code == 401
        assert malformed.json()["error"]["code"] == "CONTROL_AUTH_REQUIRED"

        wrong = client.get(
            "/api/v1/jobs/JOB-999999",
            headers={"Authorization": "Bearer wrong-control-plane-key-0123456789abcdef"},
        )
        assert wrong.status_code == 401
        assert wrong.json()["error"]["code"] == "CONTROL_AUTH_INVALID"

        authorized = client.get(
            "/api/v1/jobs/JOB-999999",
            headers={"Authorization": f"Bearer {CONTROL_KEY}"},
        )
        assert authorized.status_code == 503
        assert authorized.json()["error"]["code"] == "CONTROL_SURFACE_UNAVAILABLE"


def test_local_control_routes_remain_available_without_key_for_dev_compatibility() -> None:
    app = create_app(Settings(environment="test"))

    with TestClient(app) as client:
        response = client.get("/api/v1/jobs/JOB-999999")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "CONTROL_SURFACE_UNAVAILABLE"
