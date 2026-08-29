from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_automation_force_api import Settings, create_app

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "packages" / "contracts" / "openapi" / "control-plane-v1.json"


def rendered_schema() -> str:
    app = create_app(Settings(environment="test", build_revision="schema-export"))
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = rendered_schema()
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"OpenAPI artifact is out of sync: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
