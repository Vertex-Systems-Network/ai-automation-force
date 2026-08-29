from __future__ import annotations

from collections.abc import Mapping
from os import environ
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

Environment = Literal["development", "test", "staging", "production"]


class SettingsError(RuntimeError):
    """Raised when control-plane configuration is invalid or unsafe."""


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    environment: Environment = "development"
    service_name: str = Field(default="ai-automation-force-api", min_length=3, max_length=80)
    api_version: str = Field(default="v1", pattern=r"^v[1-9][0-9]*$")
    build_revision: str = Field(default="dev", min_length=1, max_length=80)
    internal_dev_identity: str | None = Field(default=None, min_length=3, max_length=120)

    @field_validator("service_name", "build_revision", "internal_dev_identity")
    @classmethod
    def reject_control_characters(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("control characters are not allowed")
        return value

    @model_validator(mode="after")
    def prevent_insecure_identity_outside_dev(self) -> Settings:
        if self.environment in {"staging", "production"} and self.internal_dev_identity:
            raise ValueError("internal_dev_identity is allowed only in development/test")
        return self

    @property
    def api_prefix(self) -> str:
        return f"/api/{self.api_version}"


def load_settings(source: Mapping[str, str] | None = None) -> Settings:
    values = environ if source is None else source
    payload: dict[str, str] = {}
    env_map = {
        "AAF_ENVIRONMENT": "environment",
        "AAF_SERVICE_NAME": "service_name",
        "AAF_API_VERSION": "api_version",
        "AAF_BUILD_REVISION": "build_revision",
        "AAF_INTERNAL_DEV_IDENTITY": "internal_dev_identity",
    }
    for environment_key, model_key in env_map.items():
        value = values.get(environment_key)
        if value is not None:
            payload[model_key] = value
    try:
        return Settings.model_validate(payload)
    except ValidationError as exc:
        raise SettingsError(f"invalid API configuration: {exc}") from exc
