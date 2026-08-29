from __future__ import annotations

import asyncio
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from temporalio import activity

type ProbeScalar = str | int | float | None
type ProbePayload = dict[str, ProbeScalar]


@dataclass(frozen=True)
class MediaProbeSettings:
    quarantine_root: Path
    executable: str = "ffprobe"
    timeout_seconds: int = 5
    max_input_bytes: int = 2_000_000_000
    max_output_bytes: int = 262_144
    probe_size_bytes: int = 5_000_000
    analyze_duration_us: int = 5_000_000
    max_alloc_bytes: int = 64_000_000

    def __post_init__(self) -> None:
        root = self.quarantine_root.expanduser().resolve()
        if self.timeout_seconds < 1 or self.timeout_seconds > 60:
            raise ValueError("media probe timeout must be between 1 and 60 seconds")
        if self.max_input_bytes < 1:
            raise ValueError("media probe input limit must be positive")
        if self.max_output_bytes < 1 or self.max_output_bytes > 4_194_304:
            raise ValueError("media probe output limit must be between 1 byte and 4 MiB")
        if self.probe_size_bytes < 32 or self.probe_size_bytes > 100_000_000:
            raise ValueError("ffprobe probe-size limit must be between 32 bytes and 100 MB")
        if self.analyze_duration_us < 0 or self.analyze_duration_us > 60_000_000:
            raise ValueError("ffprobe analyze duration must be between 0 and 60 seconds")
        if self.max_alloc_bytes < 1_048_576 or self.max_alloc_bytes > 1_073_741_824:
            raise ValueError("ffprobe allocation cap must be between 1 MiB and 1 GiB")
        if not self.executable or self.executable != self.executable.strip():
            raise ValueError("media probe executable must be non-empty without edge whitespace")
        object.__setattr__(self, "quarantine_root", root)


def load_media_probe_settings() -> MediaProbeSettings:
    root = Path(
        os.environ.get(
            "AAF_MEDIA_QUARANTINE_ROOT",
            str(Path(tempfile.gettempdir()) / "aaf-quarantine"),
        )
    )
    executable = os.environ.get("AAF_FFPROBE_EXECUTABLE", "ffprobe")
    timeout_seconds = int(os.environ.get("AAF_MEDIA_PROBE_TIMEOUT_SECONDS", "5"))
    max_input_bytes = int(os.environ.get("AAF_MEDIA_PROBE_MAX_INPUT_BYTES", "2000000000"))
    max_output_bytes = int(os.environ.get("AAF_MEDIA_PROBE_MAX_OUTPUT_BYTES", "262144"))
    probe_size_bytes = int(os.environ.get("AAF_MEDIA_PROBE_SIZE_BYTES", "5000000"))
    analyze_duration_us = int(os.environ.get("AAF_MEDIA_ANALYZE_DURATION_US", "5000000"))
    max_alloc_bytes = int(os.environ.get("AAF_MEDIA_PROBE_MAX_ALLOC_BYTES", "64000000"))
    return MediaProbeSettings(
        quarantine_root=root,
        executable=executable,
        timeout_seconds=timeout_seconds,
        max_input_bytes=max_input_bytes,
        max_output_bytes=max_output_bytes,
        probe_size_bytes=probe_size_bytes,
        analyze_duration_us=analyze_duration_us,
        max_alloc_bytes=max_alloc_bytes,
    )


def resolve_quarantine_path(relative_path: str, settings: MediaProbeSettings) -> Path:
    if relative_path != relative_path.strip() or not relative_path:
        raise ValueError("quarantine relative path must be non-empty without edge whitespace")
    if "\\" in relative_path or any(ord(char) < 32 or ord(char) == 127 for char in relative_path):
        raise ValueError("quarantine relative path contains unsafe characters")
    candidate_input = Path(relative_path)
    invalid_component = any(part in {"", ".", ".."} for part in candidate_input.parts)
    if candidate_input.is_absolute() or invalid_component:
        raise ValueError("quarantine probe path must be a safe relative path")
    candidate = (settings.quarantine_root / candidate_input).resolve(strict=False)
    if not candidate.is_relative_to(settings.quarantine_root):
        raise ValueError("quarantine probe path escaped the configured root")
    return candidate


def _failure(status: str, error_code: str) -> ProbePayload:
    return {
        "status": status,
        "format_name": None,
        "duration_seconds": None,
        "stream_count": None,
        "error_code": error_code,
    }


def run_ffprobe(relative_path: str, settings: MediaProbeSettings) -> ProbePayload:
    path = resolve_quarantine_path(relative_path, settings)
    try:
        size_bytes = path.stat().st_size
    except FileNotFoundError:
        return _failure("failed", "probe-input-missing")
    if not path.is_file():
        return _failure("failed", "probe-input-not-file")
    if size_bytes > settings.max_input_bytes:
        return _failure("failed", "probe-input-too-large")

    command = [
        settings.executable,
        "-v",
        "error",
        "-max_alloc",
        str(settings.max_alloc_bytes),
        "-probesize",
        str(settings.probe_size_bytes),
        "-analyzeduration",
        str(settings.analyze_duration_us),
        "-show_entries",
        "format=format_name,duration:stream=index,codec_type",
        "-of",
        "json",
        "-i",
        str(path),
    ]
    try:
        with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=settings.timeout_seconds,
                check=False,
                shell=False,
            )
            stdout_size = stdout_file.tell()
            stderr_size = stderr_file.tell()
            if stdout_size > settings.max_output_bytes:
                return _failure("failed", "probe-output-too-large")
            if stderr_size > settings.max_output_bytes:
                return _failure("failed", "probe-error-output-too-large")
            if completed.returncode != 0:
                return _failure("failed", f"ffprobe-exit-{completed.returncode}")
            stdout_file.seek(0)
            raw_output = stdout_file.read(settings.max_output_bytes + 1)
    except FileNotFoundError:
        return _failure("unavailable", "ffprobe-not-found")
    except subprocess.TimeoutExpired:
        return _failure("timed-out", "probe-timeout")

    if len(raw_output) > settings.max_output_bytes:
        return _failure("failed", "probe-output-too-large")
    try:
        payload = json.loads(raw_output.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _failure("failed", "probe-invalid-json")
    if not isinstance(payload, dict):
        return _failure("failed", "probe-invalid-shape")

    format_payload = payload.get("format")
    streams_payload = payload.get("streams")
    if not isinstance(format_payload, dict) or not isinstance(streams_payload, list):
        return _failure("failed", "probe-missing-format-or-streams")
    format_name = format_payload.get("format_name")
    if not isinstance(format_name, str) or not format_name:
        return _failure("failed", "probe-missing-format-name")

    duration: float | None = None
    raw_duration = format_payload.get("duration")
    if raw_duration is not None:
        try:
            duration = float(raw_duration)
        except (TypeError, ValueError):
            return _failure("failed", "probe-invalid-duration")
        if duration < 0:
            return _failure("failed", "probe-invalid-duration")

    return {
        "status": "succeeded",
        "format_name": format_name[:160],
        "duration_seconds": duration,
        "stream_count": len(streams_payload),
        "error_code": None,
    }


@activity.defn(name="media_probe_quarantine")
async def media_probe_quarantine(relative_path: str) -> ProbePayload:
    """Run resource-bounded ffprobe outside Temporal deterministic workflow code."""

    settings = load_media_probe_settings()
    return await asyncio.to_thread(run_ffprobe, relative_path, settings)
