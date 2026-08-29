from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


def test_capture_exact_schema_generator_output() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "export_schemas.py"
    spec = importlib.util.spec_from_file_location("aaf_export_schemas_capture", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    artifacts = module.expected_artifacts()
    quarantine = artifacts["quarantine-inspection.schema.json"]
    manifest = artifacts["manifest.json"]
    print("WP3_QUARANTINE_EXPECTED_SHA256=" + hashlib.sha256(quarantine.encode()).hexdigest())
    print("WP3_MANIFEST_EXPECTED_SHA256=" + hashlib.sha256(manifest.encode()).hexdigest())
    print("WP3_QUARANTINE_BEGIN")
    print(quarantine, end="")
    print("WP3_QUARANTINE_END")
    print("WP3_MANIFEST_BEGIN")
    print(manifest, end="")
    print("WP3_MANIFEST_END")
    raise AssertionError("intentional temporary exact-generator capture")
