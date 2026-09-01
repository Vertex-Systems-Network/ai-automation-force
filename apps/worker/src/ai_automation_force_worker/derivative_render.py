from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ai_automation_force_core import (
    DerivativeKind,
    DerivativeSpec,
    FilesystemStorageAdapter,
    StorageConflictError,
    StorageIntegrityError,
    validate_object_key,
)
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from temporalio import activity
from temporalio.exceptions import ApplicationError

DerivativeRenderStatus = Literal["succeeded", "failed", "timed-out", "unavailable"]
type DerivativeRenderScalar = str | int | None
type DerivativeRenderPayload = dict[str, DerivativeRenderScalar]

_IMAGE_MIME_TYPES = frozenset({"image/jpeg", "image/png"})
_ALLOWED_VIDEO_PRESETS = frozenset(
    {"ultrafast", "superfast", "veryfast", "faster", "fast", "medium"}
)
_MAX_DIMENSION = 8192
_MAX_PIXEL_COUNT = 33_554_432


class DerivativeRenderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    derivative_record_id: str = Field(min_length=5, max_length=80)
    source_object_key: str = Field(min_length=1, max_length=1024)
    output_object_key: str = Field(min_length=1, max_length=1024)
    spec: DerivativeSpec

    @field_validator("source_object_key", "output_object_key")
    @classmethod
    def validate_storage_key(cls, value: str) -> str:
        return validate_object_key(value)


@dataclass(frozen=True)
class DerivativeRenderSettings:
    storage_root: Path
    scratch_root: Path
    executable: str = "ffmpeg"
    timeout_seconds: int = 120
    max_input_bytes: int = 4_000_000_000
    max_output_bytes: int = 134_217_728
    max_error_output_bytes: int = 262_144
    max_alloc_bytes: int = 134_217_728
    threads: int = 2
    default_audio_preview_seconds: int = 30

    def __post_init__(self) -> None:
        storage_root = self.storage_root.expanduser().resolve()
        scratch_root = self.scratch_root.expanduser().resolve()
        storage_root.mkdir(parents=True, exist_ok=True)
        scratch_root.mkdir(parents=True, exist_ok=True)
        if storage_root == scratch_root:
            raise ValueError("derivative scratch root must differ from canonical storage root")
        if self.timeout_seconds < 1 or self.timeout_seconds > 600:
            raise ValueError("derivative timeout must be between 1 and 600 seconds")
        if self.max_input_bytes < 1:
            raise ValueError("derivative input byte limit must be positive")
        if self.max_output_bytes < 1 or self.max_output_bytes > 536_870_912:
            raise ValueError("derivative output limit must be between 1 byte and 512 MiB")
        if self.max_error_output_bytes < 1 or self.max_error_output_bytes > 4_194_304:
            raise ValueError("derivative stderr limit must be between 1 byte and 4 MiB")
        if self.max_alloc_bytes < 1_048_576 or self.max_alloc_bytes > 1_073_741_824:
            raise ValueError("ffmpeg allocation cap must be between 1 MiB and 1 GiB")
        if self.threads < 1 or self.threads > 16:
            raise ValueError("ffmpeg thread count must be between 1 and 16")
        if self.default_audio_preview_seconds < 1 or self.default_audio_preview_seconds > 600:
            raise ValueError("audio preview duration must be between 1 and 600 seconds")
        if not self.executable or self.executable != self.executable.strip():
            raise ValueError("ffmpeg executable must be non-empty without edge whitespace")
        object.__setattr__(self, "storage_root", storage_root)
        object.__setattr__(self, "scratch_root", scratch_root)


def load_derivative_render_settings() -> DerivativeRenderSettings:
    temp_root = Path(tempfile.gettempdir())
    return DerivativeRenderSettings(
        storage_root=Path(
            os.environ.get("AAF_MEDIA_STORAGE_ROOT", str(temp_root / "aaf-storage"))
        ),
        scratch_root=Path(
            os.environ.get(
                "AAF_DERIVATIVE_SCRATCH_ROOT",
                str(temp_root / "aaf-derivative-scratch"),
            )
        ),
        executable=os.environ.get("AAF_FFMPEG_EXECUTABLE", "ffmpeg"),
        timeout_seconds=int(os.environ.get("AAF_DERIVATIVE_TIMEOUT_SECONDS", "120")),
        max_input_bytes=int(
            os.environ.get("AAF_DERIVATIVE_MAX_INPUT_BYTES", "4000000000")
        ),
        max_output_bytes=int(
            os.environ.get("AAF_DERIVATIVE_MAX_OUTPUT_BYTES", "134217728")
        ),
        max_error_output_bytes=int(
            os.environ.get("AAF_DERIVATIVE_MAX_ERROR_OUTPUT_BYTES", "262144")
        ),
        max_alloc_bytes=int(
            os.environ.get("AAF_DERIVATIVE_MAX_ALLOC_BYTES", "134217728")
        ),
        threads=int(os.environ.get("AAF_DERIVATIVE_THREADS", "2")),
        default_audio_preview_seconds=int(
            os.environ.get("AAF_AUDIO_PREVIEW_SECONDS", "30")
        ),
    )


def resolve_storage_path(object_key: str, settings: DerivativeRenderSettings) -> Path:
    key = validate_object_key(object_key)
    candidate = (settings.storage_root / Path(*key.split("/"))).resolve(strict=False)
    if not candidate.is_relative_to(settings.storage_root):
        raise StorageIntegrityError("storage object key escaped the configured root")
    return candidate


def _failure(status: DerivativeRenderStatus, error_code: str) -> DerivativeRenderPayload:
    return {
        "status": status,
        "output_object_key": None,
        "sha256": None,
        "size_bytes": None,
        "mime_type": None,
        "error_code": error_code,
    }


def _validated_dimensions(
    width: int | None,
    height: int | None,
    *,
    required: bool,
) -> tuple[int, int] | None:
    if width is None or height is None:
        if required or width is not None or height is not None:
            raise ValueError("derivative width and height must be supplied together")
        return None
    if width > _MAX_DIMENSION or height > _MAX_DIMENSION:
        raise ValueError("derivative dimensions exceed the 8192-pixel edge limit")
    if width * height > _MAX_PIXEL_COUNT:
        raise ValueError("derivative dimensions exceed the pixel-count limit")
    return width, height


def _option_int(
    spec: DerivativeSpec,
    name: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    raw = spec.options.get(name, default)
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError(f"derivative option {name} must be an integer")
    if raw < minimum or raw > maximum:
        raise ValueError(
            f"derivative option {name} must be between {minimum} and {maximum}"
        )
    return raw


def _option_float(
    spec: DerivativeSpec,
    name: str,
    *,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    raw = spec.options.get(name, default)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ValueError(f"derivative option {name} must be numeric")
    value = float(raw)
    if value < minimum or value > maximum:
        raise ValueError(
            f"derivative option {name} must be between {minimum} and {maximum}"
        )
    return value


def _option_str(
    spec: DerivativeSpec,
    name: str,
    *,
    default: str,
    allowed: frozenset[str],
) -> str:
    raw = spec.options.get(name, default)
    if not isinstance(raw, str) or raw not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"derivative option {name} must be one of: {allowed_values}")
    return raw


def _reject_unknown_options(spec: DerivativeSpec, allowed: frozenset[str]) -> None:
    unknown = set(spec.options) - allowed
    if unknown:
        raise ValueError(f"unsupported derivative options: {sorted(unknown)}")


def _scale_filter(width: int, height: int, fit: str) -> str:
    if fit == "stretch":
        return f"scale={width}:{height}"
    if fit == "contain":
        return (
            f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        )
    if fit == "cover":
        return (
            f"scale=w={width}:h={height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height}"
        )
    raise ValueError(f"unsupported fit mode: {fit}")


def _image_encoder_args(spec: DerivativeSpec) -> tuple[list[str], str]:
    if spec.mime_type not in _IMAGE_MIME_TYPES:
        raise ValueError("image derivative MIME type must be image/jpeg or image/png")
    dimensions = _validated_dimensions(spec.width, spec.height, required=True)
    assert dimensions is not None
    width, height = dimensions
    allowed = {"fit", "quality"}
    if spec.kind is DerivativeKind.VIDEO_POSTER:
        allowed.add("time_seconds")
    _reject_unknown_options(spec, frozenset(allowed))
    fit = _option_str(
        spec,
        "fit",
        default="contain",
        allowed=frozenset({"contain", "cover", "stretch"}),
    )
    args = ["-vf", _scale_filter(width, height, fit), "-frames:v", "1"]
    if spec.mime_type == "image/jpeg":
        quality = _option_int(spec, "quality", default=82, minimum=1, maximum=100)
        qscale = max(2, min(31, round(31 - (quality / 100) * 29)))
        args.extend(["-c:v", "mjpeg", "-q:v", str(qscale)])
        return args, ".jpg"
    if "quality" in spec.options:
        raise ValueError("quality option is only supported for JPEG derivatives")
    args.extend(["-c:v", "png"])
    return args, ".png"


def _duration_args(seconds: float | None, *, maximum: float) -> list[str]:
    if seconds is None:
        return []
    if seconds > maximum:
        raise ValueError(f"derivative duration exceeds the {maximum:g}-second limit")
    return ["-t", f"{seconds:.3f}"]


def _video_proxy_args(spec: DerivativeSpec) -> tuple[list[str], str]:
    if spec.mime_type != "video/mp4":
        raise ValueError("video proxy MIME type must be video/mp4")
    _reject_unknown_options(
        spec,
        frozenset({"fit", "video_crf", "video_preset", "audio_bitrate_kbps"}),
    )
    dimensions = _validated_dimensions(spec.width, spec.height, required=False)
    if dimensions is None and "fit" in spec.options:
        raise ValueError("video proxy fit option requires width and height")

    args = ["-map", "0:v:0", "-map", "0:a:0?"]
    if dimensions is not None:
        width, height = dimensions
        fit = _option_str(
            spec,
            "fit",
            default="contain",
            allowed=frozenset({"contain", "cover", "stretch"}),
        )
        args.extend(["-vf", _scale_filter(width, height, fit)])

    preset = _option_str(
        spec,
        "video_preset",
        default="veryfast",
        allowed=_ALLOWED_VIDEO_PRESETS,
    )
    crf = _option_int(spec, "video_crf", default=28, minimum=18, maximum=40)
    audio_bitrate = _option_int(
        spec,
        "audio_bitrate_kbps",
        default=128,
        minimum=32,
        maximum=320,
    )
    args.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            f"{audio_bitrate}k",
            "-movflags",
            "+faststart",
        ]
    )
    args.extend(_duration_args(spec.max_duration_seconds, maximum=3600.0))
    return args, ".mp4"


def _audio_preview_args(
    spec: DerivativeSpec,
    settings: DerivativeRenderSettings,
) -> tuple[list[str], str]:
    if spec.mime_type != "audio/mp4":
        raise ValueError("audio preview MIME type must be audio/mp4")
    _reject_unknown_options(spec, frozenset({"audio_bitrate_kbps"}))
    audio_bitrate = _option_int(
        spec,
        "audio_bitrate_kbps",
        default=128,
        minimum=32,
        maximum=320,
    )
    duration = spec.max_duration_seconds or float(settings.default_audio_preview_seconds)
    if duration > 600:
        raise ValueError("audio preview duration exceeds the 600-second limit")
    args = [
        "-map",
        "0:a:0",
        "-vn",
        "-c:a",
        "aac",
        "-b:a",
        f"{audio_bitrate}k",
        "-movflags",
        "+faststart",
        "-t",
        f"{duration:.3f}",
    ]
    return args, ".m4a"


def _waveform_args(spec: DerivativeSpec) -> tuple[list[str], str]:
    if spec.mime_type != "image/png":
        raise ValueError("audio waveform MIME type must be image/png")
    _reject_unknown_options(spec, frozenset())
    if spec.width is None and spec.height is None:
        width, height = 1200, 240
    else:
        dimensions = _validated_dimensions(spec.width, spec.height, required=True)
        assert dimensions is not None
        width, height = dimensions
    filter_value = (
        "aformat=channel_layouts=mono,"
        f"showwavespic=s={width}x{height}:colors=white"
    )
    return [
        "-filter_complex",
        filter_value,
        "-frames:v",
        "1",
        "-c:v",
        "png",
    ], ".png"


def build_derivative_command(
    request: DerivativeRenderRequest,
    settings: DerivativeRenderSettings,
    source_path: Path,
    output_path: Path,
) -> list[str]:
    spec = request.spec
    pre_input: list[str] = []
    if spec.kind is DerivativeKind.VIDEO_POSTER:
        time_seconds = _option_float(
            spec,
            "time_seconds",
            default=0.0,
            minimum=0.0,
            maximum=86_400.0,
        )
        if time_seconds:
            pre_input = ["-ss", f"{time_seconds:.3f}"]

    if spec.kind in {
        DerivativeKind.THUMBNAIL,
        DerivativeKind.IMAGE_PREVIEW,
        DerivativeKind.VIDEO_POSTER,
    }:
        output_args, _ = _image_encoder_args(spec)
        output_args = ["-map", "0:v:0", *output_args]
    elif spec.kind is DerivativeKind.VIDEO_PROXY:
        output_args, _ = _video_proxy_args(spec)
    elif spec.kind is DerivativeKind.AUDIO_PREVIEW:
        output_args, _ = _audio_preview_args(spec, settings)
    elif spec.kind is DerivativeKind.AUDIO_WAVEFORM:
        output_args, _ = _waveform_args(spec)
    else:
        raise ValueError(f"unsupported derivative kind: {spec.kind.value}")

    return [
        settings.executable,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-max_alloc",
        str(settings.max_alloc_bytes),
        "-filter_threads",
        "1",
        "-filter_complex_threads",
        "1",
        "-threads",
        str(settings.threads),
        *pre_input,
        "-i",
        str(source_path),
        "-map_metadata",
        "-1",
        "-map_chapters",
        "-1",
        *output_args,
        "-threads",
        str(settings.threads),
        "-fs",
        str(settings.max_output_bytes),
        "-y",
        str(output_path),
    ]


def _output_suffix(
    spec: DerivativeSpec,
    settings: DerivativeRenderSettings,
) -> str:
    if spec.kind in {
        DerivativeKind.THUMBNAIL,
        DerivativeKind.IMAGE_PREVIEW,
        DerivativeKind.VIDEO_POSTER,
    }:
        _, suffix = _image_encoder_args(spec)
        return suffix
    if spec.kind is DerivativeKind.VIDEO_PROXY:
        _, suffix = _video_proxy_args(spec)
        return suffix
    if spec.kind is DerivativeKind.AUDIO_PREVIEW:
        _, suffix = _audio_preview_args(spec, settings)
        return suffix
    if spec.kind is DerivativeKind.AUDIO_WAVEFORM:
        _, suffix = _waveform_args(spec)
        return suffix
    raise ValueError(f"unsupported derivative kind: {spec.kind.value}")


def run_derivative(
    request: DerivativeRenderRequest,
    settings: DerivativeRenderSettings,
) -> DerivativeRenderPayload:
    if request.source_object_key == request.output_object_key:
        return _failure("failed", "derivative-source-output-key-collision")

    source_path = resolve_storage_path(request.source_object_key, settings)
    try:
        input_size = source_path.stat().st_size
    except FileNotFoundError:
        return _failure("failed", "derivative-input-missing")
    if not source_path.is_file():
        return _failure("failed", "derivative-input-not-file")
    if input_size > settings.max_input_bytes:
        return _failure("failed", "derivative-input-too-large")

    try:
        suffix = _output_suffix(request.spec, settings)
    except ValueError:
        return _failure("failed", "derivative-invalid-spec")

    descriptor, temp_name = tempfile.mkstemp(
        prefix=".aaf-derivative-",
        suffix=suffix,
        dir=settings.scratch_root,
    )
    os.close(descriptor)
    temp_path = Path(temp_name)
    temp_path.unlink(missing_ok=True)

    try:
        command = build_derivative_command(request, settings, source_path, temp_path)
        with tempfile.TemporaryFile() as stderr_file:
            try:
                completed = subprocess.run(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=stderr_file,
                    timeout=settings.timeout_seconds,
                    check=False,
                    shell=False,
                )
            except FileNotFoundError:
                return _failure("unavailable", "ffmpeg-not-found")
            except subprocess.TimeoutExpired:
                return _failure("timed-out", "derivative-timeout")

            if stderr_file.tell() > settings.max_error_output_bytes:
                return _failure("failed", "derivative-error-output-too-large")
            if completed.returncode != 0:
                return _failure("failed", f"ffmpeg-exit-{completed.returncode}")

        try:
            output_size = temp_path.stat().st_size
        except FileNotFoundError:
            return _failure("failed", "derivative-output-missing")
        if output_size < 1:
            return _failure("failed", "derivative-output-empty")
        if output_size > settings.max_output_bytes:
            return _failure("failed", "derivative-output-too-large")

        data = temp_path.read_bytes()
        if len(data) != output_size or len(data) > settings.max_output_bytes:
            return _failure("failed", "derivative-output-size-race")

        adapter = FilesystemStorageAdapter(settings.storage_root)
        try:
            result = adapter.put_bytes(
                request.output_object_key,
                data,
                mime_type=request.spec.mime_type,
            )
        except StorageConflictError:
            return _failure("failed", "derivative-output-conflict")

        return {
            "status": "succeeded",
            "output_object_key": result.object_key,
            "sha256": result.sha256,
            "size_bytes": result.size_bytes,
            "mime_type": result.mime_type,
            "error_code": None,
        }
    finally:
        temp_path.unlink(missing_ok=True)


@activity.defn(name="render_media_derivative")
async def render_media_derivative(payload: dict[str, object]) -> DerivativeRenderPayload:
    """Render one bounded derivative outside Temporal deterministic workflow code."""

    try:
        request = DerivativeRenderRequest.model_validate(payload)
    except ValidationError as exc:
        raise ApplicationError(
            "invalid derivative render request",
            type="DerivativeInput",
            non_retryable=True,
        ) from exc
    settings = load_derivative_render_settings()
    return await asyncio.to_thread(run_derivative, request, settings)
