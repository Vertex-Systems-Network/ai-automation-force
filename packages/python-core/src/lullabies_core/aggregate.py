from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from typing import Protocol, TypeVar

from pydantic import Field, model_validator

from .character import Character, CharacterVersion
from .common import LockScope, StrictModel
from .entities import Location, Prop, World
from .project import Project
from .timeline import Act, Scene, Sequence, Shot, Take, Timeline

T = TypeVar("T")


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
        self._validate_primary_edit()
        return self

    def _validate_project_timeline(self) -> None:
        if self.timeline.project_id != self.project.project_id:
            raise ValueError("timeline.project_id must equal project.project_id")
        if (
            self.project.active_timeline_id is not None
            and self.project.active_timeline_id != self.timeline.timeline_id
        ):
            raise ValueError("project.active_timeline_id must reference the loaded timeline")
        if abs(self.timeline.duration_seconds - self.project.target_duration_seconds) > 0.001:
            raise ValueError("timeline duration must equal project target duration")

        self._unique_by_id(self.timeline.tracks, "track_id", "TimelineTrack")
        self._assert_unique_refs(self.project.character_ids, "project.character_ids")
        self._assert_unique_refs(self.project.world_ids, "project.world_ids")
        self._assert_unique_refs(self.project.prop_ids, "project.prop_ids")

        for shot in self.shots:
            if shot.time_range.end_seconds > self.timeline.duration_seconds + 0.001:
                raise ValueError(f"shot {shot.shot_id} exceeds timeline duration")

    def _validate_hierarchy(self) -> None:
        acts = self._unique_by_id(self.acts, "act_id", "Act")
        sequences = self._unique_by_id(self.sequences, "sequence_id", "Sequence")
        scenes = self._unique_by_id(self.scenes, "scene_id", "Scene")
        shots = self._unique_by_id(self.shots, "shot_id", "Shot")

        self._assert_unique_refs(self.timeline.act_ids, "timeline.act_ids")
        if set(self.timeline.act_ids) != set(acts):
            raise ValueError("timeline.act_ids must exactly match loaded acts")
        self._assert_unique_orders(self.acts, "timeline", "Act")

        for act in self.acts:
            if act.project_id != self.project.project_id:
                raise ValueError(f"act {act.act_id} belongs to another project")
            self._assert_unique_refs(act.sequence_ids, f"act {act.act_id} sequence_ids")
            missing = [item for item in act.sequence_ids if item not in sequences]
            if missing:
                raise ValueError(f"act {act.act_id} references missing sequences: {missing}")
            owned_sequences = [
                sequence for sequence in self.sequences if sequence.act_id == act.act_id
            ]
            if set(act.sequence_ids) != {
                sequence.sequence_id for sequence in owned_sequences
            }:
                raise ValueError(f"act {act.act_id} sequence membership is inconsistent")
            self._assert_unique_orders(owned_sequences, act.act_id, "Sequence")

        for sequence in self.sequences:
            if sequence.act_id not in acts:
                raise ValueError(f"sequence {sequence.sequence_id} has missing parent act")
            self._assert_unique_refs(
                sequence.scene_ids,
                f"sequence {sequence.sequence_id} scene_ids",
            )
            missing = [item for item in sequence.scene_ids if item not in scenes]
            if missing:
                raise ValueError(
                    f"sequence {sequence.sequence_id} references missing scenes: {missing}"
                )
            owned_scenes = [
                scene for scene in self.scenes if scene.sequence_id == sequence.sequence_id
            ]
            if set(sequence.scene_ids) != {scene.scene_id for scene in owned_scenes}:
                raise ValueError(
                    f"sequence {sequence.sequence_id} scene membership is inconsistent"
                )
            self._assert_unique_orders(owned_scenes, sequence.sequence_id, "Scene")

        for shot in self.shots:
            if shot.scene_id not in scenes:
                raise ValueError(f"shot {shot.shot_id} has missing parent scene")

        for scene in self.scenes:
            if scene.sequence_id not in sequences:
                raise ValueError(f"scene {scene.scene_id} has missing parent sequence")
            self._assert_unique_refs(scene.shot_ids, f"scene {scene.scene_id} shot_ids")
            missing = [item for item in scene.shot_ids if item not in shots]
            if missing:
                raise ValueError(f"scene {scene.scene_id} references missing shots: {missing}")
            owned_shots = [shot for shot in self.shots if shot.scene_id == scene.scene_id]
            if set(scene.shot_ids) != {shot.shot_id for shot in owned_shots}:
                raise ValueError(f"scene {scene.scene_id} shot membership is inconsistent")
            self._assert_unique_orders(owned_shots, scene.scene_id, "Shot")
            ordered_shots = sorted(owned_shots, key=lambda shot: shot.order)
            starts = [shot.time_range.start_seconds for shot in ordered_shots]
            if starts != sorted(starts):
                raise ValueError(f"scene {scene.scene_id} shot time order moves backwards")

    def _validate_takes(self) -> None:
        takes = self._unique_by_id(self.takes, "take_id", "Take")
        shots = {shot.shot_id for shot in self.shots}
        for take in self.takes:
            if take.shot_id not in shots:
                raise ValueError(f"take {take.take_id} references missing shot {take.shot_id}")
        for shot in self.shots:
            self._assert_unique_refs(shot.take_ids, f"shot {shot.shot_id} take_ids")
            missing = [take_id for take_id in shot.take_ids if take_id not in takes]
            if missing:
                raise ValueError(f"shot {shot.shot_id} references missing takes: {missing}")
            owned_takes = [take for take in self.takes if take.shot_id == shot.shot_id]
            if set(shot.take_ids) != {take.take_id for take in owned_takes}:
                raise ValueError(f"shot {shot.shot_id} take membership is inconsistent")
            if shot.selected_take_id is not None and shot.selected_take_id not in takes:
                raise ValueError(f"shot {shot.shot_id} selected take is not loaded")

    def _validate_references(self) -> None:
        characters = self._unique_by_id(self.characters, "character_id", "Character")
        character_versions = self._unique_by_id(
            self.character_versions, "character_version_id", "CharacterVersion"
        )
        worlds = self._unique_by_id(self.worlds, "world_id", "World")
        locations = self._unique_by_id(self.locations, "location_id", "Location")
        props = self._unique_by_id(self.props, "prop_id", "Prop")

        self._validate_character_versions(characters, character_versions)
        self._validate_character_usage(characters)
        self._validate_world_and_location_usage(worlds, locations)
        self._validate_prop_usage(props)

    def _validate_character_versions(
        self,
        characters: dict[str, Character],
        character_versions: dict[str, CharacterVersion],
    ) -> None:
        versions_by_character: dict[str, set[int]] = defaultdict(set)
        seen_look_ids: set[str] = set()

        for version in self.character_versions:
            if version.character_id not in characters:
                raise ValueError(
                    f"character version {version.character_version_id} has missing character"
                )
            if version.version in versions_by_character[version.character_id]:
                raise ValueError(
                    f"character {version.character_id} has duplicate version number "
                    f"{version.version}"
                )
            versions_by_character[version.character_id].add(version.version)
            local_look_ids = [look.look_id for look in version.looks]
            self._assert_unique_refs(
                local_look_ids,
                f"character version {version.character_version_id} look_ids",
            )
            duplicate_global_looks = seen_look_ids.intersection(local_look_ids)
            if duplicate_global_looks:
                raise ValueError(
                    f"duplicate CharacterLook IDs: {sorted(duplicate_global_looks)}"
                )
            seen_look_ids.update(local_look_ids)

        scene_ids = {scene.scene_id for scene in self.scenes}
        scenes = {scene.scene_id: scene for scene in self.scenes}
        for character in self.characters:
            if character.active_version_id not in character_versions:
                raise ValueError(f"character {character.character_id} active version is not loaded")
            version = character_versions[character.active_version_id]
            if version.character_id != character.character_id:
                raise ValueError(
                    f"character version {version.character_version_id} belongs to another character"
                )

            lock = character.lock
            pinned = lock.pinned_character_version_id
            if pinned is not None:
                if pinned not in character_versions:
                    raise ValueError(f"character {character.character_id} lock version is missing")
                pinned_version = character_versions[pinned]
                if pinned_version.character_id != character.character_id:
                    raise ValueError(
                        f"character {character.character_id} lock pins another identity"
                    )
                if lock.pinned_look_id is not None:
                    look_ids = {look.look_id for look in pinned_version.looks}
                    if lock.pinned_look_id not in look_ids:
                        raise ValueError(
                            f"character {character.character_id} lock look is not in pinned version"
                        )

            if lock.scope == LockScope.PROJECT and lock.project_id != self.project.project_id:
                raise ValueError(
                    f"character {character.character_id} project lock targets another project"
                )
            if lock.scope == LockScope.SCENE:
                if lock.scene_id not in scene_ids:
                    raise ValueError(
                        f"character {character.character_id} scene lock references missing scene"
                    )
                if character.character_id not in scenes[lock.scene_id].character_ids:
                    raise ValueError(
                        f"character {character.character_id} scene lock targets a scene "
                        "where the character is not declared"
                    )

    def _validate_character_usage(self, characters: dict[str, Character]) -> None:
        declared = set(self.project.character_ids)
        missing_declared = declared - set(characters)
        if missing_declared:
            raise ValueError(
                f"project references missing characters: {sorted(missing_declared)}"
            )

        scenes = {scene.scene_id: scene for scene in self.scenes}
        used: set[str] = set()
        for scene in self.scenes:
            self._assert_unique_refs(
                scene.character_ids,
                f"scene {scene.scene_id} character_ids",
            )
            used.update(scene.character_ids)
        for shot in self.shots:
            self._assert_unique_refs(
                shot.character_ids,
                f"shot {shot.shot_id} character_ids",
            )
            used.update(shot.character_ids)
            undeclared_in_scene = set(shot.character_ids) - set(
                scenes[shot.scene_id].character_ids
            )
            if undeclared_in_scene:
                raise ValueError(
                    f"shot {shot.shot_id} uses characters not declared by scene: "
                    f"{sorted(undeclared_in_scene)}"
                )

        missing_characters = used - set(characters)
        if missing_characters:
            raise ValueError(
                f"project graph references missing characters: {sorted(missing_characters)}"
            )
        undeclared_in_project = used - declared
        if undeclared_in_project:
            raise ValueError(
                f"project graph uses undeclared characters: {sorted(undeclared_in_project)}"
            )

    def _validate_world_and_location_usage(
        self,
        worlds: dict[str, World],
        locations: dict[str, Location],
    ) -> None:
        declared_worlds = set(self.project.world_ids)
        missing_worlds = declared_worlds - set(worlds)
        if missing_worlds:
            raise ValueError(f"project references missing worlds: {sorted(missing_worlds)}")

        for location in self.locations:
            if location.world_id is not None and location.world_id not in worlds:
                raise ValueError(f"location {location.location_id} references missing world")

        scenes = {scene.scene_id: scene for scene in self.scenes}
        required_location_ids: set[str] = set()
        for scene in self.scenes:
            if scene.location_id is not None:
                required_location_ids.add(scene.location_id)
        for shot in self.shots:
            if shot.location_id is not None:
                required_location_ids.add(shot.location_id)
            scene = scenes[shot.scene_id]
            if (
                scene.location_id is not None
                and shot.location_id is not None
                and shot.location_id != scene.location_id
            ):
                raise ValueError(
                    f"shot {shot.shot_id} location differs from its continuous scene location"
                )

        missing_locations = required_location_ids - set(locations)
        if missing_locations:
            raise ValueError(
                f"project graph references missing locations: {sorted(missing_locations)}"
            )

        for location_id in required_location_ids:
            world_id = locations[location_id].world_id
            if world_id is not None and world_id not in declared_worlds:
                raise ValueError(
                    f"used location {location_id} belongs to undeclared world {world_id}"
                )

    def _validate_prop_usage(self, props: dict[str, Prop]) -> None:
        declared = set(self.project.prop_ids)
        missing_declared = declared - set(props)
        if missing_declared:
            raise ValueError(f"project references missing props: {sorted(missing_declared)}")

        used: set[str] = set()
        for shot in self.shots:
            self._assert_unique_refs(shot.prop_ids, f"shot {shot.shot_id} prop_ids")
            used.update(shot.prop_ids)
        missing_props = used - set(props)
        if missing_props:
            raise ValueError(f"project graph references missing props: {sorted(missing_props)}")
        undeclared = used - declared
        if undeclared:
            raise ValueError(f"project graph uses undeclared props: {sorted(undeclared)}")

    def _validate_primary_edit(self) -> None:
        if not self.shots:
            return

        acts = {act.act_id: act for act in self.acts}
        sequences = {sequence.sequence_id: sequence for sequence in self.sequences}
        scenes = {scene.scene_id: scene for scene in self.scenes}

        def hierarchy_key(shot: Shot) -> tuple[int, int, int, int]:
            scene = scenes[shot.scene_id]
            sequence = sequences[scene.sequence_id]
            act = acts[sequence.act_id]
            return (act.order, sequence.order, scene.order, shot.order)

        ordered = sorted(self.shots, key=hierarchy_key)
        starts = [shot.time_range.start_seconds for shot in ordered]
        if starts != sorted(starts):
            raise ValueError("primary edit shot timing moves backwards across hierarchy")

        previous = ordered[0]
        for current in ordered[1:]:
            if current.time_range.start_seconds < previous.time_range.end_seconds - 0.001:
                raise ValueError(
                    f"primary edit shots overlap: {previous.shot_id} and {current.shot_id}"
                )
            previous = current

    @staticmethod
    def _unique_by_id(items: Iterable[T], field: str, label: str) -> dict[str, T]:
        materialized = list(items)
        values = [str(getattr(item, field)) for item in materialized]
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            raise ValueError(f"duplicate {label} IDs: {sorted(duplicates)}")
        return {str(getattr(item, field)): item for item in materialized}

    @staticmethod
    def _assert_unique_orders(items: Iterable[Orderable], parent: str, label: str) -> None:
        values = [int(item.order) for item in items]
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            raise ValueError(f"duplicate {label} order under {parent}: {sorted(duplicates)}")

    @staticmethod
    def _assert_unique_refs(items: Iterable[str], label: str) -> None:
        values = list(items)
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            raise ValueError(f"duplicate references in {label}: {sorted(duplicates)}")
