from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from ai_automation_force_core import DerivativeKind, DerivativeSpec
from ai_automation_force_worker.derivative_render import (
    DerivativeRenderRequest,
    DerivativeRenderSettings,
    build_derivative_command,
    resolve_storage_path,
    run_derivative,
)


def settings(
    root: Path,
    *,
    max_input_bytes: int = 1024,
    max_output_bytes: int = 4096,
) -> DerivativeRenderSettings:
    return DerivativeRenderSettings(
        storage_root=root / "storage",
        scratch_root=root / "scratch",
        executable="ffmpeg-test",
        timeout_seconds=3,
        max_input_bytes=max_input_bytes,
        max_output_bytes=max_output_bytes,
        max_error_output_bytes=4096,
        max_alloc_bytes=8_388_608,
        threads=1,
        default_audio_preview_seconds=15,
    )


def request_for(spec: DerivativeSpec) -> DerivativeRenderRequest:
    return DerivativeRenderRequest(
        derivative_record_id="DRV-009001",
        source_object_key="source/PRJ-000500/STO-009001",
        output_object_key="derivatives/PRJ-000500/STO-009002",
        spec=spec,
    )


def video_proxy_spec() -> DerivativeSpec:
    return DerivativeSpec(
        kind=DerivativeKind.VIDEO_PROXY,
        width=960,
        height=540,
        max_duration_seconds=20,
        mime_type="video/mp4",
        options={
            "fit": "contain",
            "video_crf": 28,
            "video_preset": "veryfast",
            "audio_bitrate_kbps": 128,
        },
    )


def write_source(request: DerivativeRenderRequest, config: DerivativeRenderSettings) -> Path:
    source = resolve_storage_path(request.source_object_key, config)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"source-media")
    return source


def test_video_proxy_invocation_is_non_shell_bounded_and_atomically_published(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = settings(tmp_path)
    request = request_for(video_proxy_spec())
    source = write_source(request, config)

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert command[0] == "ffmpeg-test"
        assert command[command.index("-i") + 1] == str(source.resolve())
        assert command[command.index("-fs") + 1] == str(config.max_output_bytes)
        assert command[command.index("-max_alloc") + 1] == str(config.max_alloc_bytes)
        assert "libx264" in command
        assert "+faststart" in command
        assert kwargs["shell"] is False
        assert kwargs["timeout"] == 3
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["stdout"] == subprocess.DEVNULL
        output = Path(command[-1])
        assert output.parent == config.scratch_root
        output.write_bytes(b"proxy-bytes")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_derivative(request, config)

    assert result["status"] == "succeeded"
    assert result["output_object_key"] == request.output_object_key
    assert result["size_bytes"] == len(b"proxy-bytes")
    output = resolve_storage_path(request.output_object_key, config)
    assert output.read_bytes() == b"proxy-bytes"
    assert source.read_bytes() == b"source-media"
    assert list(config.scratch_root.iterdir()) == []


@pytest.mark.parametrize(
    ("spec", "marker"),
    [
        (
            DerivativeSpec(
                kind=DerivativeKind.THUMBNAIL,
                width=320,
                height=180,
                mime_type="image/jpeg",
                options={"fit": "cover", "quality": 80},
            ),
            "mjpeg",
        ),
        (
            DerivativeSpec(
                kind=DerivativeKind.IMAGE_PREVIEW,
                width=1280,
                height=720,
                mime_type="image/png",
                options={"fit": "contain"},
            ),
            "png",
        ),
        (
            DerivativeSpec(
                kind=DerivativeKind.VIDEO_POSTER,
                width=1280,
                height=720,
                mime_type="image/jpeg",
                options={"time_seconds": 2.5},
            ),
            "-ss",
        ),
        (
            DerivativeSpec(
                kind=DerivativeKind.AUDIO_WAVEFORM,
                width=1200,
                height=240,
                mime_type="image/png",
            ),
            "showwavespic",
        ),
        (
            DerivativeSpec(
                kind=DerivativeKind.AUDIO_PREVIEW,
                max_duration_seconds=12,
                mime_type="audio/mp4",
            ),
            "aac",
        ),
        (video_proxy_spec(), "libx264"),
    ],
)
def test_command_builder_supports_every_wp5_derivative_kind(
    tmp_path: Path,
    spec: DerivativeSpec,
    marker: str,
) -> None:
    config = settings(tmp_path)
    request = request_for(spec)
    command = build_derivative_command(
        request,
        config,
        config.storage_root / "source.bin",
        config.scratch_root / "output.bin",
    )

    assert command[0] == "ffmpeg-test"
    assert "-nostdin" in command
    assert "-map_metadata" in command
    assert "-map_chapters" in command
    assert any(marker in part for part in command)


def test_storage_key_traversal_is_rejected_before_ffmpeg(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="unsafe path segment"):
        DerivativeRenderRequest(
            derivative_record_id="DRV-009002",
            source_object_key="../outside.mp4",
            output_object_key="derivatives/PRJ-000500/STO-009002",
            spec=video_proxy_spec(),
        )


def test_timeout_and_missing_ffmpeg_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = settings(tmp_path)
    request = request_for(video_proxy_spec())
    write_source(request, config)

    def timeout_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise subprocess.TimeoutExpired(command, timeout=kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timeout_run)
    timed_out = run_derivative(request, config)
    assert timed_out["status"] == "timed-out"
    assert timed_out["error_code"] == "derivative-timeout"

    def missing_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise FileNotFoundError(command[0])

    monkeypatch.setattr(subprocess, "run", missing_run)
    unavailable = run_derivative(request, config)
    assert unavailable["status"] == "unavailable"
    assert unavailable["error_code"] == "ffmpeg-not-found"


def test_input_and_output_byte_limits_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = request_for(video_proxy_spec())
    tiny_input = settings(tmp_path / "input", max_input_bytes=4)
    write_source(request, tiny_input)
    assert run_derivative(request, tiny_input)["error_code"] == "derivative-input-too-large"

    tiny_output = settings(tmp_path / "output", max_output_bytes=4)
    write_source(request, tiny_output)

    def large_output_run(
        command: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        Path(command[-1]).write_bytes(b"1234567890")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", large_output_run)
    result = run_derivative(request, tiny_output)
    assert result["error_code"] == "derivative-output-too-large"


def test_existing_different_output_is_never_overwritten(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = settings(tmp_path)
    request = request_for(video_proxy_spec())
    source = write_source(request, config)
    output = resolve_storage_path(request.output_object_key, config)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"existing-canonical-bytes")

    def conflicting_run(
        command: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        Path(command[-1]).write_bytes(b"different-render")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", conflicting_run)
    result = run_derivative(request, config)

    assert result["error_code"] == "derivative-output-conflict"
    assert output.read_bytes() == b"existing-canonical-bytes"
    assert source.read_bytes() == b"source-media"


def test_invalid_resource_shape_fails_before_process_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = settings(tmp_path)
    spec = DerivativeSpec(
        kind=DerivativeKind.VIDEO_PROXY,
        width=9000,
        height=9000,
        mime_type="video/mp4",
    )
    request = request_for(spec)
    write_source(request, config)

    def unexpected_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise AssertionError("ffmpeg must not run for an invalid derivative spec")

    monkeypatch.setattr(subprocess, "run", unexpected_run)
    result = run_derivative(request, config)
    assert result["error_code"] == "derivative-invalid-spec"
