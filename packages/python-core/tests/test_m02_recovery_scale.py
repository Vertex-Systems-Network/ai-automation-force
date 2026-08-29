from __future__ import annotations

from ai_automation_force_core import operation_fingerprint


def test_100_shot_operations_have_unique_order_independent_fingerprints() -> None:
    operations = [
        {
            "project_id": "PRJ-009800",
            "shot_id": f"SHT-{index + 1:06d}",
            "operation": "synthetic-recovery-shot",
            "shot_index": index,
        }
        for index in range(100)
    ]
    fingerprints = [operation_fingerprint(operation) for operation in operations]

    assert len(fingerprints) == 100
    assert len(set(fingerprints)) == 100

    for operation, fingerprint in zip(operations, fingerprints, strict=True):
        reordered = {
            "shot_index": operation["shot_index"],
            "operation": operation["operation"],
            "shot_id": operation["shot_id"],
            "project_id": operation["project_id"],
        }
        assert operation_fingerprint(reordered) == fingerprint
