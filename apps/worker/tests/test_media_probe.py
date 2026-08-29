from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, BinaryIO

import pytest

from ai_automation_force_worker.media_probe import (
    MediaProbeSettings,
    resolve_quarantine_path,
    run_ffprobe,
)


def settings(root: Path) -> MediaProbeSettings:
    return MediaProbeSettings(
        quarantine_root=root,
        executable="ffprobe-test",
        timeout_seconds=3,
        max_input_bytes=1024,
        max_output_bytes=4096,
        probe_size_bytes=2048,
        analyze_duration_us=1_000_000,
        max_alloc_bytes=8_388_608,
    )


def test_probe_invocation_is_argument_list_non_shell_and_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "quarantine"
    media = root / "QIN-003501" / "payload.mp4"
    media.parent.mkdir(parents=True)
    media.write_bytes(b"fixture")

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert command[0] == "ffprobe-test"
        assert command[-2:] == ["-i", str(media.resolve())]
        assert command[command.index("-max_alloc") + 1] == "8388608"
        assert command[command.index("-probesize") + 1] == "2048"
        assert command[command.index("-analyzeduration") + 1] == "1000000"
        assert kwargs["shell"] is False
        assert kwargs["timeout"] == 3
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert "capture_output" not in kwargs
        stdout = kwargs["stdout"]
        assert hasattr(stdout, "write")
        payload = {
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "4.25"},
            "streams": [{"index": 0}, {"index": 1}],
        }
        stdout.write(json.dumps(payload).encode("utf-8"))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_ffprobe("QIN-003501/payload.mp4", settings(root))

    assert result == {
        "status": "succeeded",
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "duration_seconds": 4.25,
        "stream_count": 2,
        "error_code": None,
    }


def test_probe_path_cannot_escape_quarantine_root(tmp_path: Path) -> None:
    config = settings(tmp_path / "quarantine")

    with pytest.raises(ValueError, match="safe relative path"):
        resolve_quarantine_path("../outside.mp4", config)
    with pytest.raises(ValueError, match="safe relative path"):
        resolve_quarantine_path(str((tmp_path / "outside.mp4").resolve()), config)


def test_probe_timeout_and_missing_executable_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "quarantine"
    media = root / "QIN-003502" / "payload.mp4"
    media.parent.mkdir(parents=True)
    media.write_bytes(b"fixture")
    config = settings(root)

    def timeout_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timeout_run)
    assert run_ffprobe("QIN-003502/payload.mp4", config)["status"] == "timed-out"

    def missing_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise FileNotFoundError(command[0])

    monkeypatch.setattr(subprocess, "run", missing_run)
    result = run_ffprobe("QIN-003502/payload.mp4", config)
    assert result["status"] == "unavailable"
    assert result["error_code"] == "ffprobe-not-found"


def test_probe_input_and_output_limits_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "quarantine"
    media = root / "QIN-003503" / "payload.mp4"
    media.parent.mkdir(parents=True)
    media.write_bytes(b"12345")

    tiny_input = MediaProbeSettings(
        quarantine_root=root,
        max_input_bytes=4,
        max_output_bytes=4096,
    )
    assert run_ffprobe("QIN-003503/payload.mp4", tiny_input)["error_code"] == (
        "probe-input-too-large"
    )

    def large_output_run(
        command: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        stdout: BinaryIO = kwargs["stdout"]
        stdout.write(b"x" * 10)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", large_output_run)
    tiny_output = MediaProbeSettings(
        quarantine_root=root,
        max_input_bytes=1024,
        max_output_bytes=4,
    )
    assert run_ffprobe("QIN-003503/payload.mp4", tiny_output)["error_code"] == (
        "probe-output-too-large"
    )
