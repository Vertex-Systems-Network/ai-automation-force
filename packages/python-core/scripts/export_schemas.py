from __future__ import annotations

import json
from pathlib import Path

from lullabies_core import (
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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = repo_root / "schemas" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, model in MODELS.items():
        path = output_dir / f"{name}.schema.json"
        schema = model.model_json_schema(mode="validation")
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = f"https://schemas.lullabies.local/v1/{name}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(path.relative_to(repo_root))


if __name__ == "__main__":
    main()
