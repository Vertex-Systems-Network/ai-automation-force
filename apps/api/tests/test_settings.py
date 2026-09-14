from __future__ import annotations

import pytest

from ai_automation_force_api import SettingsError, load_settings


def test_settings_defaults_are_safe_for_local_development() -> None:
    settings = load_settings({})
    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"
    assert settings.internal_dev_identity is None
    assert settings.control_api_key is None


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


def test_settings_require_control_key_for_production_control_surface() -> None:
    with pytest.raises(SettingsError, match="control_api_key"):
        load_settings(
            {
                "AAF_ENVIRONMENT": "production",
                "DATABASE_URL": "postgresql+psycopg://example.invalid/aaf",
            }
        )


def test_settings_reject_weak_control_key() -> None:
    with pytest.raises(SettingsError, match="control_api_key"):
        load_settings(
            {
                "AAF_ENVIRONMENT": "production",
                "DATABASE_URL": "postgresql+psycopg://example.invalid/aaf",
                "AAF_CONTROL_API_KEY": "too-short",
            }
        )


def test_settings_accept_strong_control_key_for_production_control_surface() -> None:
    settings = load_settings(
        {
            "AAF_ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql+psycopg://example.invalid/aaf",
            "AAF_CONTROL_API_KEY": "production-control-key-0123456789abcdef",
        }
    )
    assert settings.control_api_key is not None
