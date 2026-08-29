from __future__ import annotations

import pytest

from ai_automation_force_worker import WorkerSettingsError, load_worker_settings


def test_worker_settings_have_safe_local_defaults() -> None:
    settings = load_worker_settings({})
    assert settings.temporal_target == "127.0.0.1:7233"
    assert settings.temporal_namespace == "default"
    assert settings.task_queue == "aaf-control-v1"


def test_worker_settings_reject_surrounding_whitespace() -> None:
    with pytest.raises(WorkerSettingsError, match="whitespace"):
        load_worker_settings({"AAF_TEMPORAL_TASK_QUEUE": " bad-queue "})
