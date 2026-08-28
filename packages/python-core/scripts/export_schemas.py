from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ai_automation_force_core import (
    SCHEMA_VERSION,
    Act,
    Approval,
    Asset,
    Character,
    CharacterVersion,
    Content,
    ContentVersion,
    CostRecord,
    GenerationAttempt,
    Job,
    Location,
    Project,
    ProjectBundle,
    Prop,
    QARecord,
    RightsRecord,
    Scene,
    Sequence,
    Shot,
    StyleProfile,
    Take,
    Timeline,
    VoiceProfile,
    World,
)

SCHEMA_BASE_ID = f"urn:ai-automation-force:schema:v{SCHEMA_VERSION}"

MODELS = {
    "project": Project,
    "project-bundle": ProjectBundle,
    "character": Character,
    "character-version": CharacterVersion,
    "world": World,
    "location": Location,
    "prop": Prop,
    "style-profile": StyleProfile,
    "voice-profile": VoiceProfile,
    "content": Content,
    "content-version": ContentVersion,
    "act": Act,
    "sequence": Sequence,
    "scene": Scene,
    "shot": Shot,
    "take": Take,
    "timeline": Timeline,
    "asset": Asset,
    "generation-attempt": GenerationAttempt,
    "job": Job,
    "qa-record": QARecord,
    "cost-record": CostRecord,
    "rights-record": RightsRecord,
    "approval": Approval,
}


def render_schema(name: str, model: type) -> str:
    schema = model.model_json_schema(mode="validation")
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"{SCHEMA_BASE_ID}:{name}"
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def expected_artifacts() -> dict[str, str]:
    artifacts = {
        f"{name}.schema.json": render_schema(name, model) for name, model in MODELS.items()
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "schema_base_id": SCHEMA_BASE_ID,
        "artifacts": {
            filename: hashlib.sha256(content.encode("utf-8")).hexdigest()
            for filename, content in sorted(artifacts.items())
        },
    }
    artifacts["manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return artifacts


def check_artifacts(output_dir: Path, expected: dict[str, str]) -> int:
    failures: list[str] = []
    for filename, content in expected.items():
        path = output_dir / filename
        if not path.exists():
            failures.append(f"missing: {path}")
        elif path.read_text(encoding="utf-8") != content:
            failures.append(f"drifted: {path}")

    expected_names = set(expected)
    if output_dir.exists():
        actual_managed = {
            path.name
            for path in output_dir.iterdir()
            if path.is_file()
            and (path.name.endswith(".schema.json") or path.name == "manifest.json")
        }
        for filename in sorted(actual_managed - expected_names):
            failures.append(f"stale: {output_dir / filename}")

    if failures:
        print("Generated schema check failed:")
        for failure in failures:
            print(f"- {failure}")
        print("Run: python packages/python-core/scripts/export_schemas.py")
        return 1

    print(f"Verified {len(expected)} generated schema artifacts")
    return 0


def write_artifacts(output_dir: Path, expected: dict[str, str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_names = set(expected)
    for path in output_dir.iterdir():
        if (
            path.is_file()
            and (path.name.endswith(".schema.json") or path.name == "manifest.json")
            and path.name not in expected_names
        ):
            path.unlink()

    for filename, content in expected.items():
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        print(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic core JSON Schemas")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if committed generated artifacts are missing, stale, or drifted",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "schemas" / "generated"
    expected = expected_artifacts()

    if args.check:
        return check_artifacts(output_dir, expected)

    write_artifacts(output_dir, expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
