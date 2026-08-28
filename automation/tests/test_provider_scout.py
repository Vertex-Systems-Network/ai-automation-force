from __future__ import annotations

import unittest

from automation.provider_scout import extract_json, sanitize_result, validate_registry


class ProviderScoutTests(unittest.TestCase):
    def base_registry(self):
        return {
            "schema_version": 1,
            "providers": {
                "veo": {
                    "capabilities": ["video"],
                    "access": "api_paid",
                    "preferred_model": "old-model",
                    "free_api": False,
                }
            },
        }

    def test_high_confidence_existing_provider_patch_is_applied_and_safe(self):
        result = {
            "registry_updates": [
                {
                    "provider_key": "veo",
                    "confidence": "high",
                    "evidence_urls": ["https://ai.google.dev/gemini-api/docs/video"],
                    "reason": "official model changed",
                    "patch": {"preferred_model": "new-model"},
                }
            ],
            "new_provider_discoveries": [],
            "architecture_recommendations": [],
            "no_material_change": False,
        }

        registry, applied, safe = sanitize_result(result, self.base_registry())

        self.assertTrue(safe)
        self.assertEqual(registry["providers"]["veo"]["preferred_model"], "new-model")
        self.assertEqual(len(applied), 1)

    def test_low_confidence_patch_is_not_applied(self):
        result = {
            "registry_updates": [
                {
                    "provider_key": "veo",
                    "confidence": "medium",
                    "evidence_urls": ["https://ai.google.dev/gemini-api/docs/video"],
                    "reason": "uncertain",
                    "patch": {"preferred_model": "uncertain-model"},
                }
            ],
            "new_provider_discoveries": [],
            "architecture_recommendations": [],
        }

        registry, applied, safe = sanitize_result(result, self.base_registry())

        self.assertFalse(safe)
        self.assertEqual(registry["providers"]["veo"]["preferred_model"], "old-model")
        self.assertEqual(applied, [])

    def test_new_provider_forces_review_and_is_not_enabled(self):
        result = {
            "registry_updates": [],
            "new_provider_discoveries": [
                {
                    "provider_key": "new-ai",
                    "provider_name": "New AI",
                    "confidence": "high",
                    "evidence_urls": ["https://example.com/official"],
                    "capabilities": ["video"],
                    "access": "api_free",
                    "reason": "new provider",
                }
            ],
            "architecture_recommendations": [],
        }

        registry, applied, safe = sanitize_result(result, self.base_registry())

        self.assertFalse(safe)
        self.assertNotIn("new-ai", registry["providers"])
        self.assertEqual(applied, [])

    def test_unapproved_patch_field_is_dropped(self):
        result = {
            "registry_updates": [
                {
                    "provider_key": "veo",
                    "confidence": "high",
                    "evidence_urls": ["https://ai.google.dev/gemini-api/docs/video"],
                    "reason": "attempt unsafe field",
                    "patch": {
                        "preferred_model": "new-model",
                        "arbitrary_command": "rm -rf /",
                    },
                }
            ],
            "new_provider_discoveries": [],
            "architecture_recommendations": [],
        }

        registry, applied, safe = sanitize_result(result, self.base_registry())

        self.assertTrue(safe)
        self.assertNotIn("arbitrary_command", registry["providers"]["veo"])
        self.assertEqual(applied[0]["new_values"], {"preferred_model": "new-model"})

    def test_invalid_access_class_fails_registry_validation(self):
        registry = self.base_registry()
        registry["providers"]["veo"]["access"] = "anything"

        with self.assertRaises(ValueError):
            validate_registry(registry)

    def test_extract_json_accepts_fenced_json(self):
        value = extract_json('```json\n{"no_material_change": true}\n```')
        self.assertTrue(value["no_material_change"])


if __name__ == "__main__":
    unittest.main()
