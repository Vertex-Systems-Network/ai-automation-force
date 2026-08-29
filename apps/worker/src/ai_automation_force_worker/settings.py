from __future__ import annotations

from collections.abc import Mapping
from os import environ

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class WorkerSettingsError(RuntimeError):
    """Raised when Temporal worker configuration is invalid."""


class WorkerSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    temporal_target: str = Field(default="127.0.0.1:7233", min_length=3, max_length=255)
    temporal_namespace: str = Field(default="default", min_length=1, max_length=160)
    task_queue: str = Field(default="aaf-control-v1", min_length=1, max_length=160)

    @field_validator("temporal_target", "temporal_namespace", "task_queue")
    @classmethod
    def reject_whitespace_and_controls(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("leading/trailing whitespace is not allowed")
        if any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("control characters are not allowed")
        return value


def load_worker_settings(source: Mapping[str, str] | None = None) -> WorkerSettings:
    values = environ if source is None else source
    env_map = {
        "AAF_TEMPORAL_TARGET": "temporal_target",
        "AAF_TEMPORAL_NAMESPACE": "temporal_namespace",
        "AAF_TEMPORAL_TASK_QUEUE": "task_queue",
    }
    payload: dict[str, str] = {}
    for environment_key, model_key in env_map.items():
        value = values.get(environment_key)
        if value is not None:
            payload[model_key] = value
    try:
        return WorkerSettings.model_validate(payload)
    except ValidationError as exc:
        raise WorkerSettingsError(f"invalid worker configuration: {exc}") from exc
