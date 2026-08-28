#!/usr/bin/env python3
"""Compatibility entry point for the daily grounded provider scout.

The core provider_scout module owns parsing, patch allowlists, reports and state.
This runner owns the Gemini transport so the default Gemini 2.5 Flash-Lite path
can combine Google Search + URL Context without requesting the newer
structured-output-with-tools feature.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from automation import provider_scout as scout


def call_gemini_compatible(prompt: str, model: str, api_key: str):
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}, {"url_context": {}}],
        "generationConfig": {"temperature": 0.1},
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "lullabies-provider-scout/1.1",
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
    text = "".join(
        str(part.get("text", "")) for part in parts if isinstance(part, dict)
    )
    if not text.strip():
        raise RuntimeError("Gemini returned no textual scout result")
    return scout.extract_json(text), raw


def main() -> int:
    scout.call_gemini = call_gemini_compatible
    return scout.main()


if __name__ == "__main__":
    raise SystemExit(main())
