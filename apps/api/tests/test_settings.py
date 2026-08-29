from __future__ import annotations

import pytest

from ai_automation_force_api import SettingsError, load_settings


def test_settings_defaults_are_safe_for_local_development() -> None:
    settings = load_settings({})
    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"
    assert settings.internal_dev_identity is None


def test_settings_reject_internal_dev_identity_in_production() -> None:
    with pytest.raises(SettingsError, match="internal_dev_identity"):
        load_settings(
            {
                "AAF_ENVIRONMENT": "production",
                "AAF_INTERNAL_DEV_IDENTITY": "unsafe-prod-actor",
            }
        )


def test_settings_reject_invalid_api_version() -> None:
    with pytest.raises(SettingsError, match="api_version"):
        load_settings({"AAF_API_VERSION": "latest"})
