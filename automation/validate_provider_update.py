#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "config" / "provider-sources.json"
REPORT_DIR = ROOT / "research" / "provider-updates"
MARKER = ROOT / ".provider-scout-automerge-safe"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def hostname(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return ""
    return (parsed.hostname or "").lower()


def main() -> int:
    if MARKER.exists():
        MARKER.unlink()

    sources = load_json(SOURCES_PATH)
    trusted_hosts = {
        hostname(item["url"])
        for item in sources.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("url"), str)
    }
    trusted_hosts.discard("")
    if not trusted_hosts:
        print("No trusted official provider source hosts configured.", file=sys.stderr)
        return 2

    today = dt.date.today().isoformat()
    report_path = REPORT_DIR / f"{today}.json"
    if not report_path.exists():
        print("No material provider report for today; no auto-merge authorization.")
        return 0

    report = load_json(report_path)
    result = report.get("result") if isinstance(report.get("result"), dict) else {}
    applied = report.get("applied_registry_updates") or []

    for item in applied:
        if not isinstance(item, dict):
            print("Malformed applied registry update.", file=sys.stderr)
            return 3
        evidence = item.get("evidence_urls") or []
        if not evidence:
            print("Applied registry update has no evidence.", file=sys.stderr)
            return 4
        for url in evidence:
            host = hostname(url) if isinstance(url, str) else ""
            if host not in trusted_hosts:
                print(
                    f"Untrusted evidence host {host!r} for provider "
                    f"{item.get('provider_key')!r}; refusing update.",
                    file=sys.stderr,
                )
                return 5

    discoveries = result.get("new_provider_discoveries") or []
    recommendations = result.get("architecture_recommendations") or []

    # The independent validator, not the LLM, is authoritative for merge safety.
    # Existing high-confidence registry patches are already allow-listed in
    # provider_scout.py. New providers and architecture recommendations require review.
    safe = not discoveries and not recommendations

    if safe:
        MARKER.write_text("independently-validated-safe\n", encoding="utf-8")
        print("Independent evidence gate: Class A/B auto-merge eligible.")
    else:
        print("Independent evidence gate: review required; no auto-merge marker created.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
