from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Protocol

from pydantic import Field, model_validator

from .character import Character, CharacterVersion
from .common import StrictModel
from .entities import Location, Prop, World
from .project import Project
from .timeline import Act, Scene, Sequence, Shot, Take, Timeline


class Orderable(Protocol):
    order: int


class ProjectBundle(StrictModel):
    """Provider-neutral aggregate used to validate a complete project graph.

    This is intentionally an in-memory/domain validation boundary, not the future
    database storage shape. Runtime repositories may load these records from
    PostgreSQL and validate the assembled graph before high-impact operations.
    """

    project: Project
    timeline: Timeline
    acts: list[Act] = Field(default_factory=list)
    sequences: list[Sequence] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)
    shots: list[Shot] = Field(default_factory=list)
    takes: list[Take] = Field(default_factory=list)
    characters: list[Character] = Field(default_factory=list)
    character_versions: list[CharacterVersion] = Field(default_factory=list)
    worlds: list[World] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    props: list[Prop] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_graph(self) -> ProjectBundle:
        self._validate_project_timeline()
        self._validate_hierarchy()
        self._validate_takes()
        self._validate_references()
        return self

    def _validate_project_timeline(self) -> None:
        if self.timeline.project_id != self.project.project_id:
            raise ValueError("timeline.project_id must equal project.project_id")
        if abs(self.timeline.duration_seconds - self.project.target_duration_seconds) > 0.001:
            raise ValueError("timeline duration must equal project target duration")
        for shot in self.shots:
            if shot.time_range.end_seconds > self.timeline.duration_seconds + 0.001:
                raise ValueError(f"shot {shot.shot_id} exceeds timeline duration")

    def _validate_hierarchy(self) -> None:
        acts = self._unique_by_id(self.acts, "act_id", "Act")
        sequences = self._unique_by_id(self.sequences, "sequence_id", "Sequence")
        scenes = self._unique_by_id(self.scenes, "scene_id", "Scene")
        shots = self._unique_by_id(self.shots, "shot_id", "Shot")

        if set(self.timeline.act_ids) != set(acts):
            raise ValueError("timeline.act_ids must exactly match loaded acts")
        self._assert_unique_orders(self.acts, "timeline", "Act")

        for act in self.acts:
            if act.project_id != self.project.project_id:
                raise ValueError(f"act {act.act_id} belongs to another project")
            missing = [item for item in act.sequence_ids if item not in sequences]
            if missing:
                raise ValueError(f"act {act.act_id} references missing sequences: {missing}")
            owned = [sequence for sequence in self.sequences if sequence.act_id == act.act_id]
            if set(act.sequence_ids) != {sequence.sequence_id for sequence in owned}:
                raise ValueError(f"act {act.act_id} sequence membership is inconsistent")
            self._assert_unique_orders(owned, act.act_id, "Sequence")

        for sequence in self.sequences:
            if sequence.act_id not in acts:
                raise ValueError(f"sequence {sequence.sequence_id} has missing parent act")
            missing = [item for item in sequence.scene_ids if item not in scenes]
            if missing:
                raise ValueError(
                    f"sequence {sequence.sequence_id} references missing scenes: {missing}"
                )
            owned = [scene for scene in self.scenes if scene.sequence_id == sequence.sequence_id]
            if set(sequence.scene_ids) != {scene.scene_id for scene in owned}:
                raise ValueError(
                    f"sequence {sequence.sequence_id} scene membership is inconsistent"
                )
            self._assert_unique_orders(owned, sequence.sequence_id, "Scene")

        for scene in self.scenes:
            if scene.sequence_id not in sequences:
                raise ValueError(f"scene {scene.scene_id} has missing parent sequence")
            missing = [item for item in scene.shot_ids if item not in shots]
            if missing:
                raise ValueError(f"scene {scene.scene_id} references missing shots: {missing}")
            owned = [shot for shot in self.shots if shot.scene_id == scene.scene_id]
            if set(scene.shot_ids) != {shot.shot_id for shot in owned}:
                raise ValueError(f"scene {scene.scene_id} shot membership is inconsistent")
            self._assert_unique_orders(owned, scene.scene_id, "Shot")
            ordered = sorted(owned, key=lambda shot: shot.order)
            starts = [shot.time_range.start_seconds for shot in ordered]
            if starts != sorted(starts):
                raise ValueError(f"scene {scene.scene_id} shot time order moves backwards")

    def _validate_takes(self) -> None:
        takes = self._unique_by_id(self.takes, "take_id", "Take")
        shots = {shot.shot_id for shot in self.shots}
        for take in self.takes:
            if take.shot_id not in shots:
                raise ValueError(f"take {take.take_id} references missing shot {take.shot_id}")
        for shot in self.shots:
            missing = [take_id for take_id in shot.take_ids if take_id not in takes]
            if missing:
                raise ValueError(f"shot {shot.shot_id} references missing takes: {missing}")
            owned = [take for take in self.takes if take.shot_id == shot.shot_id]
            if set(shot.take_ids) != {take.take_id for take in owned}:
                raise ValueError(f"shot {shot.shot_id} take membership is inconsistent")

    def _validate_references(self) -> None:
        characters = self._unique_by_id(self.characters, "character_id", "Character")
        character_versions = self._unique_by_id(
            self.character_versions, "character_version_id", "CharacterVersion"
        )
        worlds = self._unique_by_id(self.worlds, "world_id", "World")
        locations = self._unique_by_id(self.locations, "location_id", "Location")
        props = self._unique_by_id(self.props, "prop_id", "Prop")

        for character in self.characters:
            if character.active_version_id not in character_versions:
                raise ValueError(f"character {character.character_id} active version is not loaded")
            version = character_versions[character.active_version_id]
            if version.character_id != character.character_id:
                raise ValueError(
                    f"character version {version.character_version_id} belongs to another character"
                )
            pinned = character.lock.pinned_character_version_id
            if pinned is not None:
                if pinned not in character_versions:
                    raise ValueError(f"character {character.character_id} lock version is missing")
                if character_versions[pinned].character_id != character.character_id:
                    raise ValueError(
                        f"character {character.character_id} lock pins another identity"
                    )

        required_character_ids = set(self.project.character_ids)
        for scene in self.scenes:
            required_character_ids.update(scene.character_ids)
        for shot in self.shots:
            required_character_ids.update(shot.character_ids)
        missing_characters = required_character_ids - set(characters)
        if missing_characters:
            raise ValueError(
                f"project graph references missing characters: {sorted(missing_characters)}"
            )

        scene_locations = (scene.location_id for scene in self.scenes)
        shot_locations = (shot.location_id for shot in self.shots)
        required_location_ids = {
            location_id
            for location_id in [*scene_locations, *shot_locations]
            if location_id is not None
        }
        missing_locations = required_location_ids - set(locations)
        if missing_locations:
            raise ValueError(
                f"project graph references missing locations: {sorted(missing_locations)}"
            )

        required_prop_ids = set(self.project.prop_ids)
        for shot in self.shots:
            required_prop_ids.update(shot.prop_ids)
        missing_props = required_prop_ids - set(props)
        if missing_props:
            raise ValueError(f"project graph references missing props: {sorted(missing_props)}")

        missing_worlds = set(self.project.world_ids) - set(worlds)
        if missing_worlds:
            raise ValueError(f"project references missing worlds: {sorted(missing_worlds)}")
        for location in self.locations:
            if location.world_id is not None and location.world_id not in worlds:
                raise ValueError(f"location {location.location_id} references missing world")

    @staticmethod
    def _unique_by_id(items: list[object], field: str, label: str) -> dict[str, object]:
        values = [str(getattr(item, field)) for item in items]
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            raise ValueError(f"duplicate {label} IDs: {sorted(duplicates)}")
        return {str(getattr(item, field)): item for item in items}

    @staticmethod
    def _assert_unique_orders(items: Iterable[Orderable], parent: str, label: str) -> None:
        values = [int(item.order) for item in items]
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            raise ValueError(f"duplicate {label} order under {parent}: {sorted(duplicates)}")
