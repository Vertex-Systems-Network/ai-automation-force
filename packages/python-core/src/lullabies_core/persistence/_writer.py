from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.engine import Connection

from ..character import Character, CharacterLook, CharacterVersion
from ..common import AuditFields
from ..content import ContentVersion
from ..entities import Location, Prop, World
from ..lineage import ProductionLineageBundle
from ..production import Asset, CostRecord, GenerationAttempt, Job, QARecord, RightsRecord
from ..project import Project
from ..timeline import Act, Scene, Sequence, Shot, Take, Timeline
from ._db import DatabaseMap, IdMap, PersistenceShapeError


class BundleWriter:
    def __init__(self, database: DatabaseMap) -> None:
        self.db = database

    def write(self, connection: Connection, bundle: ProductionLineageBundle) -> None:
        self._validate_derived_order(bundle)
        ids = self._allocate_ids(bundle)
        pb = bundle.project_bundle

        for record in bundle.rights_records:
            self.db.insert(connection, "rights_records", self._rights_values(record, ids))

        self.db.insert(connection, "projects", self._project_values(pb.project, ids))
        self.db.insert(
            connection,
            "contents",
            {
                "id": ids.require("contents", bundle.content.content_id),
                "external_id": bundle.content.content_id,
                "schema_version": bundle.content.schema_version,
                "active_version_id": ids.require(
                    "content_versions", bundle.content.active_version_id
                ),
                "project_id": ids.optional("projects", bundle.content.project_id),
                "status": bundle.content.status,
                "source_legacy_package_path": bundle.content.source_legacy_package_path,
                **self._audit(bundle.content.audit),
            },
        )
        self.db.insert(
            connection,
            "content_versions",
            self._content_version_values(bundle.content_version, ids),
        )

        for character in pb.characters:
            self.db.insert(
                connection,
                "characters",
                self._character_values(character, ids),
            )
        for version in pb.character_versions:
            self.db.insert(
                connection,
                "character_versions",
                self._character_version_values(connection, version, ids),
            )
            for position, look in enumerate(version.looks):
                self.db.insert(
                    connection,
                    "character_looks",
                    self._look_values(look, version, position, ids),
                )

        for world in pb.worlds:
            self.db.insert(connection, "worlds", self._world_values(connection, world, ids))
        for location in pb.locations:
            self.db.insert(connection, "locations", self._location_values(location, ids))
        for prop in pb.props:
            self.db.insert(connection, "props", self._prop_values(prop, ids))

        self.db.insert(connection, "timelines", self._timeline_values(pb.timeline, ids))
        for position, track in enumerate(pb.timeline.tracks):
            self.db.insert(
                connection,
                "timeline_tracks",
                {
                    "id": ids.require("timeline_tracks", track.track_id),
                    "external_id": track.track_id,
                    "timeline_id": ids.require("timelines", pb.timeline.timeline_id),
                    "position": position,
                    "kind": track.kind,
                    "name": track.name,
                    "muted": track.muted,
                    "locked": track.locked,
                },
            )

        for act in pb.acts:
            self.db.insert(
                connection,
                "acts",
                self._act_values(act, pb.timeline, ids),
            )
        for sequence in pb.sequences:
            self.db.insert(connection, "sequences", self._sequence_values(sequence, ids))
        for scene in pb.scenes:
            self.db.insert(connection, "scenes", self._scene_values(scene, ids))
        for shot in pb.shots:
            self.db.insert(connection, "shots", self._shot_values(shot, ids))

        for job in bundle.jobs:
            self.db.insert(connection, "jobs", self._job_values(job, ids))
        for attempt in bundle.attempts:
            self.db.insert(
                connection,
                "generation_attempts",
                self._attempt_values(attempt, ids),
            )

        output_positions = self._attempt_output_positions(bundle.attempts)
        for asset in bundle.assets:
            self.db.insert(
                connection,
                "assets",
                self._asset_values(asset, ids, output_positions),
            )

        take_positions = self._take_positions(pb.shots)
        for take in pb.takes:
            self.db.insert(
                connection,
                "takes",
                self._take_values(take, ids, take_positions),
            )

        for record in bundle.qa_records:
            self.db.insert(connection, "qa_records", self._qa_values(record, ids))
        for record in bundle.cost_records:
            self.db.insert(connection, "cost_records", self._cost_values(record, ids))
        for character in pb.characters:
            self.db.insert(
                connection,
                "character_locks",
                self._lock_values(character, ids),
            )

        self._write_relationships(connection, bundle, ids)
        self._apply_immediate_pointer_updates(connection, bundle, ids)

    def _write_relationships(
        self,
        connection: Connection,
        bundle: ProductionLineageBundle,
        ids: IdMap,
    ) -> None:
        pb = bundle.project_bundle
        project = pb.project
        version = bundle.content_version

        self._ordered_external(
            connection,
            ids,
            "project_characters",
            "project_id",
            "projects",
            project.project_id,
            "character_id",
            "characters",
            project.character_ids,
        )
        self._ordered_external(
            connection,
            ids,
            "project_worlds",
            "project_id",
            "projects",
            project.project_id,
            "world_id",
            "worlds",
            project.world_ids,
        )
        self._ordered_external(
            connection,
            ids,
            "project_props",
            "project_id",
            "projects",
            project.project_id,
            "prop_id",
            "props",
            project.prop_ids,
        )
        self._ordered_external(
            connection,
            ids,
            "content_version_characters",
            "content_version_id",
            "content_versions",
            version.content_version_id,
            "character_id",
            "characters",
            version.character_ids,
        )
        self._ordered_external(
            connection,
            ids,
            "content_version_worlds",
            "content_version_id",
            "content_versions",
            version.content_version_id,
            "world_id",
            "worlds",
            version.world_ids,
        )
        self._ordered_external(
            connection,
            ids,
            "content_version_props",
            "content_version_id",
            "content_versions",
            version.content_version_id,
            "prop_id",
            "props",
            version.prop_ids,
        )

        for scene in pb.scenes:
            self._ordered_external(
                connection,
                ids,
                "scene_characters",
                "scene_id",
                "scenes",
                scene.scene_id,
                "character_id",
                "characters",
                scene.character_ids,
            )
        for shot in pb.shots:
            self._ordered_external(
                connection,
                ids,
                "shot_characters",
                "shot_id",
                "shots",
                shot.shot_id,
                "character_id",
                "characters",
                shot.character_ids,
            )
            self._ordered_external(
                connection,
                ids,
                "shot_props",
                "shot_id",
                "shots",
                shot.shot_id,
                "prop_id",
                "props",
                shot.prop_ids,
            )
            self._ordered_external(
                connection,
                ids,
                "shot_reference_assets",
                "shot_id",
                "shots",
                shot.shot_id,
                "asset_id",
                "assets",
                shot.reference_asset_ids,
            )

        for character_version in pb.character_versions:
            self._ordered_external(
                connection,
                ids,
                "character_version_reference_assets",
                "character_version_id",
                "character_versions",
                character_version.character_version_id,
                "asset_id",
                "assets",
                character_version.canonical_reference_asset_ids,
            )
            for look in character_version.looks:
                self._ordered_external(
                    connection,
                    ids,
                    "character_look_reference_assets",
                    "character_look_id",
                    "character_looks",
                    look.look_id,
                    "asset_id",
                    "assets",
                    look.reference_asset_ids,
                )

        for world in pb.worlds:
            self._ordered_external(
                connection,
                ids,
                "world_reference_assets",
                "world_id",
                "worlds",
                world.world_id,
                "asset_id",
                "assets",
                world.canonical_reference_asset_ids,
            )
        for location in pb.locations:
            self._ordered_external(
                connection,
                ids,
                "location_reference_assets",
                "location_id",
                "locations",
                location.location_id,
                "asset_id",
                "assets",
                location.canonical_reference_asset_ids,
            )
        for prop in pb.props:
            self._ordered_external(
                connection,
                ids,
                "prop_reference_assets",
                "prop_id",
                "props",
                prop.prop_id,
                "asset_id",
                "assets",
                prop.canonical_reference_asset_ids,
            )
        for asset in bundle.assets:
            self._ordered_external(
                connection,
                ids,
                "asset_parents",
                "child_asset_id",
                "assets",
                asset.asset_id,
                "parent_asset_id",
                "assets",
                asset.parent_asset_ids,
            )
        for attempt in bundle.attempts:
            self._ordered_external(
                connection,
                ids,
                "generation_attempt_input_assets",
                "attempt_id",
                "generation_attempts",
                attempt.attempt_id,
                "asset_id",
                "assets",
                attempt.request.input_asset_ids,
            )
            self._ordered_external(
                connection,
                ids,
                "generation_attempt_qa_records",
                "attempt_id",
                "generation_attempts",
                attempt.attempt_id,
                "qa_record_id",
                "qa_records",
                attempt.qa_record_ids,
            )
        for take in pb.takes:
            self._ordered_external(
                connection,
                ids,
                "take_qa_records",
                "take_id",
                "takes",
                take.take_id,
                "qa_record_id",
                "qa_records",
                take.qa_record_ids,
            )
        for job in bundle.jobs:
            self._ordered_external(
                connection,
                ids,
                "job_dependencies",
                "job_id",
                "jobs",
                job.job_id,
                "dependency_job_id",
                "jobs",
                job.dependency_job_ids,
            )

        timeline_id = ids.require("timelines", pb.timeline.timeline_id)
        self.db.insert_ordered(
            connection,
            "timeline_marker_assets",
            "timeline_id",
            timeline_id,
            "asset_id",
            [ids.require("assets", value) for value in pb.timeline.marker_asset_ids],
        )
        for track in pb.timeline.tracks:
            self.db.insert_ordered_scalars(
                connection,
                "timeline_track_items",
                "track_id",
                ids.require("timeline_tracks", track.track_id),
                "item_external_id",
                track.item_ids,
            )

    def _ordered_external(
        self,
        connection: Connection,
        ids: IdMap,
        join_table: str,
        owner_column: str,
        owner_table: str,
        owner_external_id: str,
        target_column: str,
        target_table: str,
        target_external_ids: list[str],
    ) -> None:
        self.db.insert_ordered(
            connection,
            join_table,
            owner_column,
            ids.require(owner_table, owner_external_id),
            target_column,
            [ids.require(target_table, value) for value in target_external_ids],
        )

    def _apply_immediate_pointer_updates(
        self,
        connection: Connection,
        bundle: ProductionLineageBundle,
        ids: IdMap,
    ) -> None:
        timeline = bundle.project_bundle.timeline
        if timeline.otio_asset_id is not None:
            self.db.update_by_id(
                connection,
                "timelines",
                ids.require("timelines", timeline.timeline_id),
                {"otio_asset_id": ids.require("assets", timeline.otio_asset_id)},
            )
        for shot in bundle.project_bundle.shots:
            values: dict[str, Any] = {}
            if shot.first_frame_asset_id is not None:
                values["first_frame_asset_id"] = ids.require(
                    "assets", shot.first_frame_asset_id
                )
            if shot.end_frame_asset_id is not None:
                values["end_frame_asset_id"] = ids.require("assets", shot.end_frame_asset_id)
            if values:
                self.db.update_by_id(
                    connection,
                    "shots",
                    ids.require("shots", shot.shot_id),
                    values,
                )
        for job in bundle.jobs:
            if job.parent_job_id is not None:
                self.db.update_by_id(
                    connection,
                    "jobs",
                    ids.require("jobs", job.job_id),
                    {"parent_job_id": ids.require("jobs", job.parent_job_id)},
                )

    def _project_values(self, project: Project, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("projects", project.project_id),
            "external_id": project.project_id,
            "schema_version": project.schema_version,
            "title": project.title,
            "status": project.status.value,
            "audience": self._json(project.audience),
            "cast": self._json(project.cast),
            "content_format": project.content_format,
            "custom_content_format": project.custom_content_format,
            "language": project.language,
            "target_duration_seconds": project.target_duration_seconds,
            "output": self._json(project.output),
            "creative": self._json(project.creative),
            "provider_policy": self._json(project.provider_policy),
            "content_id": ids.optional("contents", project.content_id),
            "active_timeline_id": ids.optional("timelines", project.active_timeline_id),
            "tags": project.tags,
            **self._audit(project.audit),
        }

    def _content_version_values(
        self,
        version: ContentVersion,
        ids: IdMap,
    ) -> dict[str, Any]:
        return {
            "id": ids.require("content_versions", version.content_version_id),
            "external_id": version.content_version_id,
            "schema_version": version.schema_version,
            "content_id": ids.require("contents", version.content_id),
            "version": version.version,
            "title": version.title,
            "content_format": version.content_format,
            "custom_content_format": version.custom_content_format,
            "language": version.language,
            "target_duration_seconds": version.target_duration_seconds,
            "objective": self._json(version.objective),
            "premise": version.premise,
            "hook": version.hook,
            "script_or_lyrics": version.script_or_lyrics,
            "structure_map": version.structure_map,
            "pronunciation_notes": version.pronunciation_notes,
            "tags": version.tags,
            "originality_fingerprint": version.originality_fingerprint,
            **self._audit(version.audit),
        }

    def _character_values(self, character: Character, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("characters", character.character_id),
            "external_id": character.character_id,
            "schema_version": character.schema_version,
            "name": character.name,
            "active_version_id": ids.require(
                "character_versions", character.active_version_id
            ),
            "reusable": character.reusable,
            "rights_record_id": ids.optional("rights_records", character.rights_record_id),
            "tags": character.tags,
            **self._audit(character.audit),
        }

    def _character_version_values(
        self,
        connection: Connection,
        version: CharacterVersion,
        ids: IdMap,
    ) -> dict[str, Any]:
        voice_id = self.db.resolve_shared_external(
            connection,
            "voice_profiles",
            version.voice_profile_id,
        )
        return {
            "id": ids.require("character_versions", version.character_version_id),
            "external_id": version.character_version_id,
            "schema_version": version.schema_version,
            "character_id": ids.require("characters", version.character_id),
            "version": version.version,
            "display_name": version.display_name,
            "character_type": version.character_type,
            "species": version.species,
            "apparent_age": version.apparent_age,
            "gender_presentation": version.gender_presentation,
            "personality_traits": version.personality_traits,
            "movement_style": version.movement_style,
            "voice_profile_id": voice_id,
            "identity_constraints": version.identity_constraints,
            "status": version.status.value,
            **self._audit(version.audit),
        }

    def _look_values(
        self,
        look: CharacterLook,
        version: CharacterVersion,
        position: int,
        ids: IdMap,
    ) -> dict[str, Any]:
        return {
            "id": ids.require("character_looks", look.look_id),
            "external_id": look.look_id,
            "character_version_id": ids.require(
                "character_versions", version.character_version_id
            ),
            "position": position,
            "name": look.name,
            "wardrobe": look.wardrobe,
            "accessories": look.accessories,
            "hair": look.hair,
            "eyes": look.eyes,
            "palette": look.palette,
            "expression_defaults": look.expression_defaults,
            "body_notes": look.body_notes,
            "prohibited_mutations": look.prohibited_mutations,
        }

    def _lock_values(self, character: Character, ids: IdMap) -> dict[str, Any]:
        lock = character.lock
        return {
            "id": uuid4(),
            "character_id": ids.require("characters", character.character_id),
            "scope": lock.scope.value,
            "pinned_character_version_id": ids.optional(
                "character_versions", lock.pinned_character_version_id
            ),
            "pinned_look_id": ids.optional("character_looks", lock.pinned_look_id),
            "project_id": ids.optional("projects", lock.project_id),
            "scene_id": ids.optional("scenes", lock.scene_id),
        }

    def _world_values(
        self,
        connection: Connection,
        world: World,
        ids: IdMap,
    ) -> dict[str, Any]:
        style_id = self.db.resolve_shared_external(
            connection,
            "style_profiles",
            world.style_profile_id,
        )
        return {
            "id": ids.require("worlds", world.world_id),
            "external_id": world.world_id,
            "schema_version": world.schema_version,
            "name": world.name,
            "description": world.description,
            "style_profile_id": style_id,
            "rules": world.rules,
            "forbidden_mutations": world.forbidden_mutations,
            **self._audit(world.audit),
        }

    def _location_values(self, location: Location, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("locations", location.location_id),
            "external_id": location.location_id,
            "schema_version": location.schema_version,
            "world_id": ids.optional("worlds", location.world_id),
            "name": location.name,
            "description": location.description,
            "environment_constraints": location.environment_constraints,
            **self._audit(location.audit),
        }

    def _prop_values(self, prop: Prop, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("props", prop.prop_id),
            "external_id": prop.prop_id,
            "schema_version": prop.schema_version,
            "name": prop.name,
            "description": prop.description,
            "identity_constraints": prop.identity_constraints,
            **self._audit(prop.audit),
        }

    def _timeline_values(self, timeline: Timeline, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("timelines", timeline.timeline_id),
            "external_id": timeline.timeline_id,
            "schema_version": timeline.schema_version,
            "project_id": ids.require("projects", timeline.project_id),
            "version": timeline.version,
            "duration_seconds": timeline.duration_seconds,
            "fps": timeline.fps,
            "otio_asset_id": None,
            **self._audit(timeline.audit),
        }

    def _act_values(self, act: Act, timeline: Timeline, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("acts", act.act_id),
            "external_id": act.act_id,
            "schema_version": act.schema_version,
            "project_id": ids.require("projects", act.project_id),
            "timeline_id": ids.require("timelines", timeline.timeline_id),
            "order": act.order,
            "title": act.title,
            "target_duration_seconds": act.target_duration_seconds,
            **self._audit(act.audit),
        }

    def _sequence_values(self, sequence: Sequence, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("sequences", sequence.sequence_id),
            "external_id": sequence.sequence_id,
            "schema_version": sequence.schema_version,
            "act_id": ids.require("acts", sequence.act_id),
            "order": sequence.order,
            "title": sequence.title,
            "target_duration_seconds": sequence.target_duration_seconds,
            **self._audit(sequence.audit),
        }

    def _scene_values(self, scene: Scene, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("scenes", scene.scene_id),
            "external_id": scene.scene_id,
            "schema_version": scene.schema_version,
            "sequence_id": ids.require("sequences", scene.sequence_id),
            "order": scene.order,
            "title": scene.title,
            "summary": scene.summary,
            "location_id": ids.optional("locations", scene.location_id),
            "target_duration_seconds": scene.target_duration_seconds,
            "incoming_state": self._json(scene.incoming_state),
            "outgoing_state": self._json(scene.outgoing_state),
            **self._audit(scene.audit),
        }

    def _shot_values(self, shot: Shot, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("shots", shot.shot_id),
            "external_id": shot.shot_id,
            "schema_version": shot.schema_version,
            "scene_id": ids.require("scenes", shot.scene_id),
            "order": shot.order,
            "start_seconds": shot.time_range.start_seconds,
            "duration_seconds": shot.time_range.duration_seconds,
            "purpose": shot.purpose,
            "action": shot.action,
            "location_id": ids.optional("locations", shot.location_id),
            "camera": shot.camera,
            "incoming_state": self._json(shot.incoming_state),
            "outgoing_state": self._json(shot.outgoing_state),
            "first_frame_asset_id": None,
            "end_frame_asset_id": None,
            "selected_take_id": ids.optional("takes", shot.selected_take_id),
            "transition_in": shot.transition_in,
            "transition_out": shot.transition_out,
            "handles_seconds": shot.handles_seconds,
            "generation_notes": shot.generation_notes,
            **self._audit(shot.audit),
        }

    def _job_values(self, job: Job, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("jobs", job.job_id),
            "external_id": job.job_id,
            "schema_version": job.schema_version,
            "project_id": ids.require("projects", job.project_id),
            "job_type": job.job_type,
            "status": job.status.value,
            "priority": job.priority,
            "idempotency_key": job.idempotency_key,
            "parent_job_id": None,
            "shot_id": ids.optional("shots", job.shot_id),
            "content_id": ids.optional("contents", job.content_id),
            "selected_attempt_id": ids.optional(
                "generation_attempts", job.selected_attempt_id
            ),
            "retry_budget_remaining": job.retry_budget_remaining,
            "blocked_reason": job.blocked_reason,
            "claimed_by": job.claimed_by,
            "lease_expires_at": job.lease_expires_at,
            **self._audit(job.audit),
        }

    def _attempt_values(
        self,
        attempt: GenerationAttempt,
        ids: IdMap,
    ) -> dict[str, Any]:
        request = attempt.request
        provider = attempt.provider
        return {
            "id": ids.require("generation_attempts", attempt.attempt_id),
            "external_id": attempt.attempt_id,
            "schema_version": attempt.schema_version,
            "job_id": ids.require("jobs", attempt.job_id),
            "attempt_number": attempt.attempt_number,
            "provider_id": provider.provider_id,
            "model_provider_id": provider.model_provider_id,
            "model_id": provider.model_id,
            "capability": provider.capability,
            "access_class": provider.access_class,
            "registry_verified_at": provider.registry_verified_at,
            "request_project_id": ids.require("projects", request.project_id),
            "request_shot_id": ids.optional("shots", request.shot_id),
            "request_content_id": ids.optional("contents", request.content_id),
            "prompt_id": request.prompt_id,
            "prompt_version": request.prompt_version,
            "request_constraints": request.constraints,
            "target_duration_seconds": request.target_duration_seconds,
            "requires_commercial_rights": request.requires_commercial_rights,
            "requires_character_continuity": request.requires_character_continuity,
            "request_idempotency_key": request.idempotency_key,
            "provider_generation_id": attempt.provider_generation_id,
            "started_at": attempt.started_at,
            "finished_at": attempt.finished_at,
            "status": attempt.status.value,
            "normalized_error_code": attempt.normalized_error_code,
            "error_detail": attempt.error_detail,
            "free_credits_used": attempt.free_credits_used,
            "paid_cost": attempt.paid_cost,
            "currency": attempt.currency,
        }

    def _asset_values(
        self,
        asset: Asset,
        ids: IdMap,
        output_positions: dict[tuple[str, str], int],
    ) -> dict[str, Any]:
        output_position = None
        if asset.generation_attempt_id is not None:
            key = (asset.generation_attempt_id, asset.asset_id)
            if key not in output_positions:
                raise PersistenceShapeError(
                    f"asset {asset.asset_id} is not ordered in its attempt outputs"
                )
            output_position = output_positions[key]
        return {
            "id": ids.require("assets", asset.asset_id),
            "external_id": asset.asset_id,
            "schema_version": asset.schema_version,
            "project_id": ids.optional("projects", asset.project_id),
            "kind": asset.kind.value,
            "uri": asset.uri,
            "sha256": asset.sha256,
            "mime_type": asset.mime_type,
            "size_bytes": asset.size_bytes,
            "duration_seconds": asset.duration_seconds,
            "width": asset.width,
            "height": asset.height,
            "provider_id": asset.provider_id,
            "model_provider_id": asset.model_provider_id,
            "provider_model_id": asset.provider_model_id,
            "generation_attempt_id": ids.optional(
                "generation_attempts", asset.generation_attempt_id
            ),
            "generation_output_position": output_position,
            "rights_record_id": ids.optional("rights_records", asset.rights_record_id),
            "canonical_status": asset.canonical_status.value,
            "retention_class": asset.retention_class,
            **self._audit(asset.audit),
        }

    def _take_values(
        self,
        take: Take,
        ids: IdMap,
        positions: dict[str, int],
    ) -> dict[str, Any]:
        if take.take_id not in positions:
            raise PersistenceShapeError(f"take {take.take_id} is not ordered by its shot")
        return {
            "id": ids.require("takes", take.take_id),
            "external_id": take.take_id,
            "schema_version": take.schema_version,
            "shot_id": ids.require("shots", take.shot_id),
            "position": positions[take.take_id],
            "attempt_id": ids.optional("generation_attempts", take.attempt_id),
            "asset_id": ids.optional("assets", take.asset_id),
            "canonical_status": take.canonical_status.value,
            "continuity_score": take.continuity_score,
            **self._audit(take.audit),
        }

    def _qa_values(self, record: QARecord, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("qa_records", record.qa_record_id),
            "external_id": record.qa_record_id,
            "schema_version": record.schema_version,
            "subject_type": record.subject_type,
            "subject_id": record.subject_id,
            "gate": record.gate,
            "passed": record.passed,
            "critical": record.critical,
            "score": record.score,
            "findings": record.findings,
            "reviewer": record.reviewer,
            "created_at": record.created_at,
        }

    def _cost_values(self, record: CostRecord, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("cost_records", record.cost_record_id),
            "external_id": record.cost_record_id,
            "schema_version": record.schema_version,
            "project_id": ids.require("projects", record.project_id),
            "job_id": ids.optional("jobs", record.job_id),
            "attempt_id": ids.optional("generation_attempts", record.attempt_id),
            "provider_id": record.provider_id,
            "model_provider_id": record.model_provider_id,
            "model_id": record.model_id,
            "free_credits_used": record.free_credits_used,
            "paid_cost": record.paid_cost,
            "currency": record.currency,
            "estimated": record.estimated,
            "recorded_at": record.recorded_at,
        }

    def _rights_values(self, record: RightsRecord, ids: IdMap) -> dict[str, Any]:
        return {
            "id": ids.require("rights_records", record.rights_record_id),
            "external_id": record.rights_record_id,
            "schema_version": record.schema_version,
            "subject_type": record.subject_type,
            "subject_id": record.subject_id,
            "provider_id": record.provider_id,
            "model_provider_id": record.model_provider_id,
            "model_id": record.model_id,
            "plan_or_tier": record.plan_or_tier,
            "commercial_use": record.commercial_use.value,
            "watermark_required": record.watermark_required,
            "source_basis": record.source_basis,
            "consent_reference": record.consent_reference,
            "evidence_urls": record.evidence_urls,
            "verified_at": record.verified_at,
            "publication_blocked": record.publication_blocked,
            "notes": record.notes,
        }

    def _allocate_ids(self, bundle: ProductionLineageBundle) -> IdMap:
        pb = bundle.project_bundle
        looks = [look for version in pb.character_versions for look in version.looks]
        groups: dict[str, list[str]] = {
            "projects": [pb.project.project_id],
            "contents": [bundle.content.content_id],
            "content_versions": [bundle.content_version.content_version_id],
            "characters": [item.character_id for item in pb.characters],
            "character_versions": [item.character_version_id for item in pb.character_versions],
            "character_looks": [item.look_id for item in looks],
            "worlds": [item.world_id for item in pb.worlds],
            "locations": [item.location_id for item in pb.locations],
            "props": [item.prop_id for item in pb.props],
            "timelines": [pb.timeline.timeline_id],
            "timeline_tracks": [item.track_id for item in pb.timeline.tracks],
            "acts": [item.act_id for item in pb.acts],
            "sequences": [item.sequence_id for item in pb.sequences],
            "scenes": [item.scene_id for item in pb.scenes],
            "shots": [item.shot_id for item in pb.shots],
            "takes": [item.take_id for item in pb.takes],
            "jobs": [item.job_id for item in bundle.jobs],
            "generation_attempts": [item.attempt_id for item in bundle.attempts],
            "assets": [item.asset_id for item in bundle.assets],
            "qa_records": [item.qa_record_id for item in bundle.qa_records],
            "cost_records": [item.cost_record_id for item in bundle.cost_records],
            "rights_records": [item.rights_record_id for item in bundle.rights_records],
        }
        return IdMap(
            {
                table: {external_id: uuid4() for external_id in external_ids}
                for table, external_ids in groups.items()
            }
        )

    def _validate_derived_order(self, bundle: ProductionLineageBundle) -> None:
        pb = bundle.project_bundle
        expected_acts = [item.act_id for item in sorted(pb.acts, key=lambda item: item.order)]
        if pb.timeline.act_ids != expected_acts:
            raise PersistenceShapeError("timeline.act_ids must follow canonical Act.order")

        for act in pb.acts:
            children = sorted(
                [item for item in pb.sequences if item.act_id == act.act_id],
                key=lambda item: item.order,
            )
            if act.sequence_ids != [item.sequence_id for item in children]:
                raise PersistenceShapeError(
                    f"act {act.act_id} sequence_ids must follow Sequence.order"
                )
        for sequence in pb.sequences:
            children = sorted(
                [item for item in pb.scenes if item.sequence_id == sequence.sequence_id],
                key=lambda item: item.order,
            )
            if sequence.scene_ids != [item.scene_id for item in children]:
                raise PersistenceShapeError(
                    f"sequence {sequence.sequence_id} scene_ids must follow Scene.order"
                )
        for scene in pb.scenes:
            children = sorted(
                [item for item in pb.shots if item.scene_id == scene.scene_id],
                key=lambda item: item.order,
            )
            if scene.shot_ids != [item.shot_id for item in children]:
                raise PersistenceShapeError(
                    f"scene {scene.scene_id} shot_ids must follow Shot.order"
                )

        attempts_by_job: dict[str, list[GenerationAttempt]] = {}
        for attempt in bundle.attempts:
            attempts_by_job.setdefault(attempt.job_id, []).append(attempt)
        for job in bundle.jobs:
            expected = [
                item.attempt_id
                for item in sorted(
                    attempts_by_job.get(job.job_id, []),
                    key=lambda item: item.attempt_number,
                )
            ]
            if job.attempt_ids != expected:
                raise PersistenceShapeError(
                    f"job {job.job_id} attempt_ids must follow attempt_number order"
                )

        used_locations = {
            value
            for value in (
                [scene.location_id for scene in pb.scenes]
                + [shot.location_id for shot in pb.shots]
            )
            if value is not None
        }
        loaded_locations = {item.location_id for item in pb.locations}
        if used_locations != loaded_locations:
            raise PersistenceShapeError(
                "ProjectBundle.locations must equal the used location closure "
                "for lossless M01 reads"
            )

    @staticmethod
    def _attempt_output_positions(
        attempts: list[GenerationAttempt],
    ) -> dict[tuple[str, str], int]:
        return {
            (attempt.attempt_id, asset_id): position
            for attempt in attempts
            for position, asset_id in enumerate(attempt.output_asset_ids)
        }

    @staticmethod
    def _take_positions(shots: list[Shot]) -> dict[str, int]:
        return {
            take_id: position
            for shot in shots
            for position, take_id in enumerate(shot.take_ids)
        }

    @staticmethod
    def _json(model: BaseModel) -> dict[str, Any]:
        return model.model_dump(mode="json")

    @staticmethod
    def _audit(audit: AuditFields) -> dict[str, Any]:
        return {
            "created_at": audit.created_at,
            "updated_at": audit.updated_at,
            "created_by": audit.created_by,
            "revision": audit.revision,
        }
