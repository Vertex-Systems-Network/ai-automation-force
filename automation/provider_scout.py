#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "provider-registry.yaml"
SOURCES_PATH = ROOT / "config" / "provider-sources.json"
POLICY_PATH = ROOT / "config" / "update-policy.yaml"
STATE_PATH = ROOT / "memory" / "provider-source-state.json"
REPORT_DIR = ROOT / "research" / "provider-updates"
AUTOMERGE_MARKER = ROOT / ".provider-scout-automerge-safe"

ALLOWED_PATCH_KEYS = {
    "capabilities",
    "access",
    "preferred_model",
    "free_api",
    "clip_seconds",
    "native_extension",
    "first_frame",
    "last_frame",
    "reference_images_max",
    "free_credits",
    "free_video_credits",
    "quota",
    "watermark",
    "commercial_use",
    "commercial_license",
    "api_credits_separate",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("Scout response must be a JSON object")
    return value


def call_gemini(prompt: str, model: str, api_key: str) -> tuple[dict[str, Any], dict[str, Any]]:
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}, {"url_context": {}}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "lullabies-provider-scout/1.0",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini HTTP {exc.code}: {body[:1200]}") from exc

    candidates = raw.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
    if not text.strip():
        raise RuntimeError("Gemini returned no textual scout result")
    return extract_json(text), raw


def build_prompt(registry: dict[str, Any], sources: dict[str, Any]) -> str:
    existing = json.dumps(registry, indent=2, sort_keys=True)
    source_json = json.dumps(sources, indent=2, sort_keys=True)
    return f"""
You are the daily provider capability auditor for a production AI media platform.

TASK
Research CURRENT official AI provider/API information and compare it with the existing provider registry below.
Use Google Search and URL Context. Prefer the registered official URLs. For any claim that would alter the registry, use an official provider/API/pricing/terms URL as evidence.
Also look for materially relevant NEW image/video/music/TTS APIs or newly released models from established providers.

DO NOT:
- use blogs/SEO articles as the evidence for a registry mutation;
- guess pricing/quota/licensing;
- enable a newly discovered provider for production;
- propose code/schema/security/budget/publishing changes as an automatic registry patch;
- treat a consumer free plan as a free API;
- output prose outside JSON.

EXISTING REGISTRY
{existing}

REGISTERED OFFICIAL SOURCES AND DISCOVERY QUERIES
{source_json}

OUTPUT EXACT JSON SHAPE
{{
  "summary": "short summary",
  "registry_updates": [
    {{
      "provider_key": "existing key from registry",
      "confidence": "low|medium|high",
      "evidence_urls": ["https://official.example/..."],
      "reason": "what changed and why",
      "patch": {{"allowed_existing_field": "new value"}}
    }}
  ],
  "new_provider_discoveries": [
    {{
      "provider_key": "suggested-slug",
      "provider_name": "Name",
      "confidence": "low|medium|high",
      "evidence_urls": ["https://official.example/..."],
      "capabilities": ["video"],
      "access": "api_free|api_paid|web_free_manual|web_paid_manual|unavailable|unknown",
      "reason": "why it may matter"
    }}
  ],
  "architecture_recommendations": [
    {{
      "title": "recommendation",
      "reason": "reason",
      "evidence_urls": ["https://official.example/..."]
    }}
  ],
  "no_material_change": false
}}

PATCH RULES
For existing providers, only propose factual provider fields such as model ID, documented capability, free/API status, clip limit, reference/keyframe support, quota/watermark/commercial-use facts.
If evidence conflicts or is unclear, set confidence to low/medium and do not guess.
If there is no material change, return empty arrays and no_material_change=true.
"""


def is_https_url(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("https://") and " " not in value


def sanitize_result(
    result: dict[str, Any], registry: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    providers = registry.setdefault("providers", {})
    if not isinstance(providers, dict):
        raise ValueError("provider-registry.yaml providers must be a mapping")

    applied: list[dict[str, Any]] = []
    safe = True
    cleaned_updates: list[dict[str, Any]] = []

    for item in result.get("registry_updates") or []:
        if not isinstance(item, dict):
            continue
        key = item.get("provider_key")
        confidence = item.get("confidence")
        evidence = [u for u in (item.get("evidence_urls") or []) if is_https_url(u)]
        patch = item.get("patch") if isinstance(item.get("patch"), dict) else {}
        patch = {k: v for k, v in patch.items() if k in ALLOWED_PATCH_KEYS}
        cleaned = {
            "provider_key": key,
            "confidence": confidence,
            "evidence_urls": evidence,
            "reason": str(item.get("reason") or ""),
            "patch": patch,
        }
        cleaned_updates.append(cleaned)

        if key not in providers or confidence != "high" or not evidence or not patch:
            safe = False
            continue

        old_values = {field: providers[key].get(field) for field in patch}
        if all(old_values[field] == value for field, value in patch.items()):
            continue
        providers[key].update(patch)
        providers[key]["verified_at"] = dt.date.today().isoformat()
        providers[key]["evidence_sources"] = evidence
        applied.append(
            {
                "provider_key": key,
                "old_values": old_values,
                "new_values": patch,
                "evidence_urls": evidence,
            }
        )

    new_discoveries = result.get("new_provider_discoveries") or []
    architecture = result.get("architecture_recommendations") or []
    if new_discoveries or architecture:
        safe = False

    result["registry_updates"] = cleaned_updates
    return registry, applied, safe


def render_markdown(
    result: dict[str, Any], applied: list[dict[str, Any]], model: str, safe: bool
) -> str:
    today = dt.date.today().isoformat()
    lines = [
        f"# Provider Scout — {today}",
        "",
        f"- Model: `{model}`",
        f"- Auto-merge classification: `{'SAFE_A_B' if safe else 'REVIEW_REQUIRED'}`",
        f"- Applied registry updates: {len(applied)}",
        "",
        "## Summary",
        "",
        str(result.get("summary") or "No summary."),
        "",
    ]
    if applied:
        lines += ["## Applied high-confidence registry changes", ""]
        for item in applied:
            lines += [
                f"### `{item['provider_key']}`",
                "",
                f"- Old: `{json.dumps(item['old_values'], sort_keys=True)}`",
                f"- New: `{json.dumps(item['new_values'], sort_keys=True)}`",
                "- Evidence:",
            ]
            lines += [f"  - {url}" for url in item["evidence_urls"]]
            lines.append("")

    discoveries = result.get("new_provider_discoveries") or []
    if discoveries:
        lines += ["## New provider/model discoveries — review required", ""]
        for item in discoveries:
            lines += [
                f"### {item.get('provider_name') or item.get('provider_key')}",
                "",
                f"- Confidence: `{item.get('confidence')}`",
                f"- Access: `{item.get('access')}`",
                f"- Capabilities: `{', '.join(item.get('capabilities') or [])}`",
                f"- Reason: {item.get('reason') or ''}",
                "- Evidence:",
            ]
            lines += [
                f"  - {u}"
                for u in item.get("evidence_urls") or []
                if is_https_url(u)
            ]
            lines.append("")

    recommendations = result.get("architecture_recommendations") or []
    if recommendations:
        lines += ["## Architecture recommendations — never auto-merged", ""]
        for item in recommendations:
            lines += [
                f"### {item.get('title') or 'Recommendation'}",
                "",
                str(item.get("reason") or ""),
                "",
            ]
            urls = [
                u for u in item.get("evidence_urls") or [] if is_https_url(u)
            ]
            if urls:
                lines.append("Evidence:")
                lines += [f"- {u}" for u in urls]
                lines.append("")

    lines += [
        "## Governance",
        "",
        "This report is generated under `config/update-policy.yaml`.",
        "New providers and architecture/code/schema/security changes are not enabled or auto-merged by discovery alone.",
        "",
    ]
    return "\n".join(lines)


def validate_registry(registry: dict[str, Any]) -> None:
    providers = registry.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise ValueError("provider registry must contain providers")
    for key, value in providers.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(value, dict):
            raise ValueError("invalid provider registry entry")
        access = value.get("access")
        if access is not None and access not in {
            "api_free",
            "api_paid",
            "web_free_manual",
            "web_paid_manual",
            "unavailable",
            "unknown",
        }:
            raise ValueError(f"provider {key} has invalid access class {access!r}")


def cmd_validate() -> int:
    registry = load_yaml(REGISTRY_PATH)
    load_yaml(POLICY_PATH)
    load_json(SOURCES_PATH)
    validate_registry(registry)
    print("provider scout configuration: valid")
    return 0


def cmd_run() -> int:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("PROVIDER_SCOUT_MODEL", "gemini-2.5-flash-lite").strip()
    if not api_key:
        print(
            "GEMINI_API_KEY is not configured; provider discovery cannot run.",
            file=sys.stderr,
        )
        return 2

    registry = load_yaml(REGISTRY_PATH)
    sources = load_json(SOURCES_PATH)
    validate_registry(registry)

    result, _raw = call_gemini(build_prompt(registry, sources), model, api_key)
    original_registry = json.loads(json.dumps(registry))
    registry, applied, safe = sanitize_result(result, registry)

    material = bool(
        applied
        or result.get("new_provider_discoveries")
        or result.get("architecture_recommendations")
        or not bool(result.get("no_material_change", False))
    )
    if not material:
        print("No material provider change found.")
        if AUTOMERGE_MARKER.exists():
            AUTOMERGE_MARKER.unlink()
        return 0

    today = dt.date.today().isoformat()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_json = REPORT_DIR / f"{today}.json"
    report_md = REPORT_DIR / f"{today}.md"

    report_payload = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": model,
        "result": result,
        "applied_registry_updates": applied,
        "automerge_safe": safe,
    }
    report_json.write_text(
        json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_md.write_text(render_markdown(result, applied, model, safe), encoding="utf-8")

    if applied and registry != original_registry:
        REGISTRY_PATH.write_text(
            yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "last_successful_scout_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "model": model,
                "report": str(report_json.relative_to(ROOT)),
                "automerge_safe": safe,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    if safe:
        AUTOMERGE_MARKER.write_text("safe\n", encoding="utf-8")
    elif AUTOMERGE_MARKER.exists():
        AUTOMERGE_MARKER.unlink()

    validate_registry(load_yaml(REGISTRY_PATH))
    print(f"Material provider research written to {report_md.relative_to(ROOT)}")
    print(f"Auto-merge safe: {safe}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    return cmd_validate() if args.validate else cmd_run()


if __name__ == "__main__":
    raise SystemExit(main())
