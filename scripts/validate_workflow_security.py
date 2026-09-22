#!/usr/bin/env python3
"""Fail closed on GitHub Actions trust-boundary regressions.

This validator intentionally uses only the Python standard library so repository
governance can run before installing project dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORKFLOW_ROOT = Path(".github/workflows")
PROVIDER_SCOUT_REQUIREMENTS = Path("automation/requirements-scout.txt")
PROVIDER_SCOUT_INSTALL = (
    "python -m pip install --disable-pip-version-check --require-hashes "
    "--only-binary=:all: -r automation/requirements-scout.txt"
)
PROVIDER_SCOUT_PIN = (
    "PyYAML==6.0.3 \\\n"
    "    --hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc"
)
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
USES = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
CHECKOUT = re.compile(r"^actions/checkout@([0-9a-fA-F]{40})$")


def workflow_files() -> list[Path]:
    return sorted(
        p
        for p in WORKFLOW_ROOT.iterdir()
        if p.is_file() and p.suffix.lower() in {".yml", ".yaml"}
    )


def external_action_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = USES.match(line)
        if not match:
            continue
        target = match.group(1)
        if target.startswith("./"):
            continue
        if target.startswith("docker://"):
            if "@sha256:" not in target:
                errors.append(
                    f"{path}:{number}: external container action must use an immutable sha256 digest: {target}"
                )
            continue
        if "@" not in target:
            errors.append(
                f"{path}:{number}: external action is missing an immutable ref: {target}"
            )
            continue
        _, ref = target.rsplit("@", 1)
        if not SHA40.fullmatch(ref):
            errors.append(
                f"{path}:{number}: external action must be pinned to a 40-character commit SHA: {target}"
            )
    return errors


def checkout_credential_errors(path: Path, text: str) -> list[str]:
    """Require every checkout step to remove credentials after source fetch."""

    errors: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = USES.match(line)
        if not match or not CHECKOUT.fullmatch(match.group(1)):
            continue

        uses_indent = len(line) - len(line.lstrip())
        persist_false = False
        explicit_token = False
        for later in lines[index + 1 :]:
            if not later.strip():
                continue
            indent = len(later) - len(later.lstrip())
            if indent <= uses_indent and later.lstrip().startswith("-"):
                break
            stripped = later.strip()
            if stripped == "persist-credentials: false":
                persist_false = True
            if stripped.startswith("token:"):
                explicit_token = True

        line_number = index + 1
        if not persist_false:
            errors.append(
                f"{path}:{line_number}: actions/checkout must set persist-credentials: false"
            )
        if explicit_token:
            errors.append(
                f"{path}:{line_number}: actions/checkout must not receive an explicit token; introduce write credentials only in the narrow mutation step"
            )
    return errors


def provider_scout_errors(path: Path, text: str) -> list[str]:
    if path.name != "provider-scout.yml":
        return []

    errors: list[str] = []
    forbidden = {
        "gh pr merge": "AI/external-content-derived provider changes must never auto-merge",
        "vars.PROVIDER_SCOUT_RUNNER": "secret-bearing provider scout must not use a repository-variable-selected runner",
    }
    for needle, reason in forbidden.items():
        if needle in text:
            errors.append(f"{path}: forbidden provider-scout pattern {needle!r}: {reason}")
    if "runs-on: ubuntu-24.04" not in text:
        errors.append(
            f"{path}: provider scout must stay on the reviewed GitHub-hosted ubuntu-24.04 runner"
        )
    if PROVIDER_SCOUT_INSTALL not in text:
        errors.append(
            f"{path}: provider scout dependencies must use --require-hashes and binary-only installation"
        )
    if not PROVIDER_SCOUT_REQUIREMENTS.is_file():
        errors.append(
            f"{PROVIDER_SCOUT_REQUIREMENTS}: provider scout requirements file is missing"
        )
    else:
        requirement_text = PROVIDER_SCOUT_REQUIREMENTS.read_text(encoding="utf-8").strip()
        if requirement_text != PROVIDER_SCOUT_PIN:
            errors.append(
                f"{PROVIDER_SCOUT_REQUIREMENTS}: secret-bearing provider scout dependency must match the reviewed exact version and SHA-256 hash"
            )
    return errors


def validate() -> list[str]:
    if not WORKFLOW_ROOT.is_dir():
        return [f"workflow directory missing: {WORKFLOW_ROOT}"]

    errors: list[str] = []
    files = workflow_files()
    if not files:
        return [f"no workflow files found under {WORKFLOW_ROOT}"]

    for path in files:
        text = path.read_text(encoding="utf-8")
        errors.extend(external_action_errors(path, text))
        errors.extend(checkout_credential_errors(path, text))
        errors.extend(provider_scout_errors(path, text))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Workflow security governance FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Workflow security governance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
