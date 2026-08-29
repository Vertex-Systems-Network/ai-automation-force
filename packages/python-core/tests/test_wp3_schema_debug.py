from __future__ import annotations

import hashlib
import json

from ai_automation_force_core import SCHEMA_VERSION, QuarantineInspection


def test_emit_runner_exact_quarantine_schema() -> None:
    schema = QuarantineInspection.model_json_schema(mode="validation")
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"urn:ai-automation-force:schema:v{SCHEMA_VERSION}:quarantine-inspection"
    content = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    print("WP3_SCHEMA_BEGIN")
    print(content, end="")
    print("WP3_SCHEMA_SHA256=" + hashlib.sha256(content.encode("utf-8")).hexdigest())
    print("WP3_SCHEMA_END")
    raise AssertionError("intentional temporary schema diagnostic")
