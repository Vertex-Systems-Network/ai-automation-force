from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.engine import Connection, RowMapping

from ..aggregate import ProjectBundle
from ..character import Character, CharacterLock, CharacterLook, CharacterVersion
from ..common import AuditFields, TimeRange
from ..content import Content, ContentObjective, ContentVersion
from ..entities import Location, Prop, World
from ..lineage import ProductionLineageBundle
from ..production import (
    Asset,
    CostRecord,
    GenerationAttempt,
    GenerationRequest,
    Job,
    ProviderModelRef,
    QARecord,
    RightsRecord,
)
from ..project import (
    AudienceProfile,
    CastProfile,
    CreativeProfile,
    OutputProfile,
    Project,
    ProviderPolicyRef,
)
from ..timeline import (
    Act,
    ContinuityState,
    Scene,
    Sequence,
    Shot,
    Take,
    Timeline,
    TimelineTrack,
)
from ._db import DatabaseMap, PersistenceNotFoundError, PersistenceShapeError


class BundleReader:
    def __init__(self, database: DatabaseMap) -> None:
        self.db = database

    def load(self, connection: Connection, project_id: str) -> ProductionLineageBundle:
        project_row = self.db.row_by_external(connection, "projects", project_id)
        if project_row is None:
            raise PersistenceNotFoundError(f"project {project_id} was not found")
        project_internal = project_row["id"]
        project = self._project(connection, project_row)
        if project_row["content_id"] is None or project_row["active_timeline_id"] is None:
            raise PersistenceShapeError(
                f"project {project_id} is not a complete production lineage aggregate"
            )

        content_row = self.db.require_row_by_id(
            connection,
            "contents",
            project_row["content_id"],
        )
        content = self.content_from_row(connection, content_row)
        version_row = self.db.require_row_by_id(
            connection,
            "content_versions",
            content_row["active_version_id"],
        )
        content_version = self.content_version_from_row(connection, version_row)

        timeline_row = self.db.require_row_by_id(
            connection,
            "timelines",
            project_row["active_timeline_id"],
        )
        timeline = self._timeline(connection, timeline_row)
        acts = self._acts(connection, timeline_row["id"])
        sequences = self._sequences(connection, acts)
        scenes = self._scenes(connection, sequences)
        shots = self._shots(connection, scenes)
        takes = self._takes(connection, shots)
        jobs = self._jobs(connection, project_internal)
        attempts = self._attempts(connection, jobs)
        characters, character_versions = self._characters(connection, project_internal)
        worlds = self._worlds(connection, project_internal)
        props = self._props(connection, project_internal)
        locations = self._locations(connection, scenes, shots)

        subject_ids = self._subject_ids(
            project,
            content,
            content_version,
            timeline,
            acts,
            sequences,
            scenes,
            shots,
            takes,
            jobs,
            attempts,
            characters,
            character_versions,
            worlds,
            locations,
            props,
        )
        assets = self._assets(
            connection,
            project_internal,
            timeline,
            shots,
            takes,
            attempts,
            character_versions,
            worlds,
            locations,
            props,
        )
        subject_ids.update(asset.asset_id for asset in assets)
        qa_records = self._qa_records(connection, subject_ids, attempts, takes)
        cost_records = self._cost_records(connection, project_internal)
        rights_records = self._rights_records(connection, subject_ids, characters, assets)

        project_bundle = ProjectBundle(
            project=project,
            timeline=timeline,
            acts=acts,
            sequences=sequences,
            scenes=scenes,
            shots=shots,
            takes=takes,
            characters=characters,
            character_versions=character_versions,
            worlds=worlds,
            locations=locations,
            props=props,
        )
        return ProductionLineageBundle(
            project_bundle=project_bundle,
            content=content,
            content_version=content_version,
            jobs=jobs,
            attempts=attempts,
            assets=assets,
            qa_records=qa_records,
            cost_records=cost_records,
            rights_records=rights_records,
        )

    def content_from_row(self, connection: Connection, row: RowMapping) -> Content:
        return Content(
            schema_version=row["schema_version"],
            content_id=row["external_id"],
            active_version_id=self.db.require_external_for_internal(
                connection,
                "content_versions",
                row["active_version_id"],
            ),
            project_id=self.db.external_for_internal(
                connection,
                "projects",
                row["project_id"],
            ),
            status=row["status"],
            source_legacy_package_path=row["source_legacy_package_path"],
            audit=self._audit(row),
        )

    def content_version_from_row(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> ContentVersion:
        return ContentVersion(
            schema_version=row["schema_version"],
            content_version_id=row["external_id"],
            content_id=self.db.require_external_for_internal(
                connection,
                "contents",
                row["content_id"],
            ),
            version=row["version"],
            title=row["title"],
            content_format=row["content_format"],
            custom_content_format=row["custom_content_format"],
            language=row["language"],
            target_duration_seconds=row["target_duration_seconds"],
            objective=ContentObjective.model_validate(row["objective"]),
            premise=row["premise"],
            hook=row["hook"],
            script_or_lyrics=row["script_or_lyrics"],
            structure_map=list(row["structure_map"]),
            character_ids=self.db.ordered_external_ids(
                connection,
                "content_version_characters",
                "content_version_id",
                row["id"],
                "character_id",
                "characters",
            ),
            world_ids=self.db.ordered_external_ids(
                connection,
                "content_version_worlds",
                "content_version_id",
                row["id"],
                "world_id",
                "worlds",
            ),
            prop_ids=self.db.ordered_external_ids(
                connection,
                "content_version_props",
                "content_version_id",
                row["id"],
                "prop_id",
                "props",
            ),
            pronunciation_notes=list(row["pronunciation_notes"]),
            tags=list(row["tags"]),
            originality_fingerprint=row["originality_fingerprint"],
            audit=self._audit(row),
        )

    def _project(self, connection: Connection, row: RowMapping) -> Project:
        return Project(
            schema_version=row["schema_version"],
            project_id=row["external_id"],
            title=row["title"],
            status=row["status"],
            audience=AudienceProfile.model_validate(row["audience"]),
            cast=CastProfile.model_validate(row["cast"]),
            content_format=row["content_format"],
            custom_content_format=row["custom_content_format"],
            language=row["language"],
            target_duration_seconds=row["target_duration_seconds"],
            output=OutputProfile.model_validate(row["output"]),
            creative=CreativeProfile.model_validate(row["creative"]),
            provider_policy=ProviderPolicyRef.model_validate(row["provider_policy"]),
            character_ids=self.db.ordered_external_ids(
                connection,
                "project_characters",
                "project_id",
                row["id"],
                "character_id",
                "characters",
            ),
            world_ids=self.db.ordered_external_ids(
                connection,
                "project_worlds",
                "project_id",
                row["id"],
                "world_id",
                "worlds",
            ),
            prop_ids=self.db.ordered_external_ids(
                connection,
                "project_props",
                "project_id",
                row["id"],
                "prop_id",
                "props",
            ),
            content_id=self.db.external_for_internal(
                connection,
                "contents",
                row["content_id"],
            ),
            active_timeline_id=self.db.external_for_internal(
                connection,
                "timelines",
                row["active_timeline_id"],
            ),
            tags=list(row["tags"]),
            audit=self._audit(row),
        )

    def _timeline(self, connection: Connection, row: RowMapping) -> Timeline:
        tracks_table = self.db.table("timeline_tracks")
        track_rows = list(
            connection.execute(
                select(tracks_table)
                .where(tracks_table.c.timeline_id == row["id"])
                .order_by(tracks_table.c.position)
            ).mappings()
        )
        tracks = [
            TimelineTrack(
                track_id=track["external_id"],
                kind=track["kind"],
                name=track["name"],
                item_ids=self.db.ordered_scalar_values(
                    connection,
                    "timeline_track_items",
                    "track_id",
                    track["id"],
                    "item_external_id",
                ),
                muted=track["muted"],
                locked=track["locked"],
            )
            for track in track_rows
        ]
        acts_table = self.db.table("acts")
        act_ids = connection.execute(
            select(acts_table.c.external_id)
            .where(acts_table.c.timeline_id == row["id"])
            .order_by(acts_table.c["order"])
        ).scalars()
        return Timeline(
            schema_version=row["schema_version"],
            timeline_id=row["external_id"],
            project_id=self.db.require_external_for_internal(
                connection,
                "projects",
                row["project_id"],
            ),
            version=row["version"],
            duration_seconds=float(row["duration_seconds"]),
            fps=float(row["fps"]),
            act_ids=[str(value) for value in act_ids],
            tracks=tracks,
            marker_asset_ids=self.db.ordered_external_ids(
                connection,
                "timeline_marker_assets",
                "timeline_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            otio_asset_id=self.db.external_for_internal(
                connection,
                "assets",
                row["otio_asset_id"],
            ),
            audit=self._audit(row),
        )

    def _acts(self, connection: Connection, timeline_id: UUID) -> list[Act]:
        table = self.db.table("acts")
        rows = connection.execute(
            select(table)
            .where(table.c.timeline_id == timeline_id)
            .order_by(table.c["order"])
        ).mappings()
        return [self._act(connection, row) for row in rows]

    def _act(self, connection: Connection, row: RowMapping) -> Act:
        table = self.db.table("sequences")
        sequence_ids = connection.execute(
            select(table.c.external_id)
            .where(table.c.act_id == row["id"])
            .order_by(table.c["order"])
        ).scalars()
        return Act(
            schema_version=row["schema_version"],
            act_id=row["external_id"],
            project_id=self.db.require_external_for_internal(
                connection,
                "projects",
                row["project_id"],
            ),
            order=row["order"],
            title=row["title"],
            sequence_ids=[str(value) for value in sequence_ids],
            target_duration_seconds=float(row["target_duration_seconds"]),
            audit=self._audit(row),
        )

    def _sequences(self, connection: Connection, acts: list[Act]) -> list[Sequence]:
        result: list[Sequence] = []
        table = self.db.table("sequences")
        for act in acts:
            act_row = self.db.require_row_by_external(connection, "acts", act.act_id)
            rows = connection.execute(
                select(table)
                .where(table.c.act_id == act_row["id"])
                .order_by(table.c["order"])
            ).mappings()
            result.extend(self._sequence(connection, row) for row in rows)
        return result

    def _sequence(self, connection: Connection, row: RowMapping) -> Sequence:
        table = self.db.table("scenes")
        scene_ids = connection.execute(
            select(table.c.external_id)
            .where(table.c.sequence_id == row["id"])
            .order_by(table.c["order"])
        ).scalars()
        return Sequence(
            schema_version=row["schema_version"],
            sequence_id=row["external_id"],
            act_id=self.db.require_external_for_internal(
                connection,
                "acts",
                row["act_id"],
            ),
            order=row["order"],
            title=row["title"],
            scene_ids=[str(value) for value in scene_ids],
            target_duration_seconds=float(row["target_duration_seconds"]),
            audit=self._audit(row),
        )

    def _scenes(self, connection: Connection, sequences: list[Sequence]) -> list[Scene]:
        result: list[Scene] = []
        table = self.db.table("scenes")
        for sequence in sequences:
            owner = self.db.require_row_by_external(
                connection,
                "sequences",
                sequence.sequence_id,
            )
            rows = connection.execute(
                select(table)
                .where(table.c.sequence_id == owner["id"])
                .order_by(table.c["order"])
            ).mappings()
            result.extend(self._scene(connection, row) for row in rows)
        return result

    def _scene(self, connection: Connection, row: RowMapping) -> Scene:
        table = self.db.table("shots")
        shot_ids = connection.execute(
            select(table.c.external_id)
            .where(table.c.scene_id == row["id"])
            .order_by(table.c["order"])
        ).scalars()
        return Scene(
            schema_version=row["schema_version"],
            scene_id=row["external_id"],
            sequence_id=self.db.require_external_for_internal(
                connection,
                "sequences",
                row["sequence_id"],
            ),
            order=row["order"],
            title=row["title"],
            summary=row["summary"],
            location_id=self.db.external_for_internal(
                connection,
                "locations",
                row["location_id"],
            ),
            character_ids=self.db.ordered_external_ids(
                connection,
                "scene_characters",
                "scene_id",
                row["id"],
                "character_id",
                "characters",
            ),
            shot_ids=[str(value) for value in shot_ids],
            target_duration_seconds=float(row["target_duration_seconds"]),
            incoming_state=ContinuityState.model_validate(row["incoming_state"]),
            outgoing_state=ContinuityState.model_validate(row["outgoing_state"]),
            audit=self._audit(row),
        )

    def _shots(self, connection: Connection, scenes: list[Scene]) -> list[Shot]:
        result: list[Shot] = []
        table = self.db.table("shots")
        for scene in scenes:
            owner = self.db.require_row_by_external(connection, "scenes", scene.scene_id)
            rows = connection.execute(
                select(table)
                .where(table.c.scene_id == owner["id"])
                .order_by(table.c["order"])
            ).mappings()
            result.extend(self._shot(connection, row) for row in rows)
        return result

    def _shot(self, connection: Connection, row: RowMapping) -> Shot:
        table = self.db.table("takes")
        take_ids = connection.execute(
            select(table.c.external_id)
            .where(table.c.shot_id == row["id"])
            .order_by(table.c.position)
        ).scalars()
        return Shot(
            schema_version=row["schema_version"],
            shot_id=row["external_id"],
            scene_id=self.db.require_external_for_internal(
                connection,
                "scenes",
                row["scene_id"],
            ),
            order=row["order"],
            time_range=TimeRange(
                start_seconds=float(row["start_seconds"]),
                duration_seconds=float(row["duration_seconds"]),
            ),
            purpose=row["purpose"],
            action=row["action"],
            character_ids=self.db.ordered_external_ids(
                connection,
                "shot_characters",
                "shot_id",
                row["id"],
                "character_id",
                "characters",
            ),
            location_id=self.db.external_for_internal(
                connection,
                "locations",
                row["location_id"],
            ),
            prop_ids=self.db.ordered_external_ids(
                connection,
                "shot_props",
                "shot_id",
                row["id"],
                "prop_id",
                "props",
            ),
            camera=dict(row["camera"]),
            incoming_state=ContinuityState.model_validate(row["incoming_state"]),
            outgoing_state=ContinuityState.model_validate(row["outgoing_state"]),
            first_frame_asset_id=self.db.external_for_internal(
                connection,
                "assets",
                row["first_frame_asset_id"],
            ),
            end_frame_asset_id=self.db.external_for_internal(
                connection,
                "assets",
                row["end_frame_asset_id"],
            ),
            reference_asset_ids=self.db.ordered_external_ids(
                connection,
                "shot_reference_assets",
                "shot_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            take_ids=[str(value) for value in take_ids],
            selected_take_id=self.db.external_for_internal(
                connection,
                "takes",
                row["selected_take_id"],
            ),
            transition_in=row["transition_in"],
            transition_out=row["transition_out"],
            handles_seconds=float(row["handles_seconds"]),
            generation_notes=list(row["generation_notes"]),
            audit=self._audit(row),
        )

    def _takes(self, connection: Connection, shots: list[Shot]) -> list[Take]:
        result: list[Take] = []
        table = self.db.table("takes")
        for shot in shots:
            owner = self.db.require_row_by_external(connection, "shots", shot.shot_id)
            rows = connection.execute(
                select(table)
                .where(table.c.shot_id == owner["id"])
                .order_by(table.c.position)
            ).mappings()
            result.extend(self._take(connection, row) for row in rows)
        return result

    def _take(self, connection: Connection, row: RowMapping) -> Take:
        return Take(
            schema_version=row["schema_version"],
            take_id=row["external_id"],
            shot_id=self.db.require_external_for_internal(
                connection,
                "shots",
                row["shot_id"],
            ),
            attempt_id=self.db.external_for_internal(
                connection,
                "generation_attempts",
                row["attempt_id"],
            ),
            asset_id=self.db.external_for_internal(
                connection,
                "assets",
                row["asset_id"],
            ),
            canonical_status=row["canonical_status"],
            continuity_score=(
                float(row["continuity_score"])
                if row["continuity_score"] is not None
                else None
            ),
            qa_record_ids=self.db.ordered_external_ids(
                connection,
                "take_qa_records",
                "take_id",
                row["id"],
                "qa_record_id",
                "qa_records",
            ),
            audit=self._audit(row),
        )

    def _jobs(self, connection: Connection, project_id: UUID) -> list[Job]:
        table = self.db.table("jobs")
        rows = list(
            connection.execute(
                select(table)
                .where(table.c.project_id == project_id)
                .order_by(table.c.external_id)
            ).mappings()
        )
        attempt_table = self.db.table("generation_attempts")
        result: list[Job] = []
        for row in rows:
            attempt_ids = connection.execute(
                select(attempt_table.c.external_id)
                .where(attempt_table.c.job_id == row["id"])
                .order_by(attempt_table.c.attempt_number)
            ).scalars()
            result.append(
                Job(
                    schema_version=row["schema_version"],
                    job_id=row["external_id"],
                    project_id=self.db.require_external_for_internal(
                        connection,
                        "projects",
                        row["project_id"],
                    ),
                    job_type=row["job_type"],
                    status=row["status"],
                    priority=row["priority"],
                    idempotency_key=row["idempotency_key"],
                    parent_job_id=self.db.external_for_internal(
                        connection,
                        "jobs",
                        row["parent_job_id"],
                    ),
                    dependency_job_ids=self.db.ordered_external_ids(
                        connection,
                        "job_dependencies",
                        "job_id",
                        row["id"],
                        "dependency_job_id",
                        "jobs",
                    ),
                    shot_id=self.db.external_for_internal(
                        connection,
                        "shots",
                        row["shot_id"],
                    ),
                    content_id=self.db.external_for_internal(
                        connection,
                        "contents",
                        row["content_id"],
                    ),
                    attempt_ids=[str(value) for value in attempt_ids],
                    selected_attempt_id=self.db.external_for_internal(
                        connection,
                        "generation_attempts",
                        row["selected_attempt_id"],
                    ),
                    retry_budget_remaining=row["retry_budget_remaining"],
                    blocked_reason=row["blocked_reason"],
                    claimed_by=row["claimed_by"],
                    lease_expires_at=row["lease_expires_at"],
                    audit=self._audit(row),
                )
            )
        return result

    def _attempts(self, connection: Connection, jobs: list[Job]) -> list[GenerationAttempt]:
        result: list[GenerationAttempt] = []
        table = self.db.table("generation_attempts")
        for job in jobs:
            owner = self.db.require_row_by_external(connection, "jobs", job.job_id)
            rows = connection.execute(
                select(table)
                .where(table.c.job_id == owner["id"])
                .order_by(table.c.attempt_number)
            ).mappings()
            result.extend(self._attempt(connection, row) for row in rows)
        return result

    def _attempt(self, connection: Connection, row: RowMapping) -> GenerationAttempt:
        asset_table = self.db.table("assets")
        output_ids = connection.execute(
            select(asset_table.c.external_id)
            .where(asset_table.c.generation_attempt_id == row["id"])
            .order_by(asset_table.c.generation_output_position)
        ).scalars()
        return GenerationAttempt(
            schema_version=row["schema_version"],
            attempt_id=row["external_id"],
            job_id=self.db.require_external_for_internal(
                connection,
                "jobs",
                row["job_id"],
            ),
            attempt_number=row["attempt_number"],
            provider=ProviderModelRef(
                provider_id=row["provider_id"],
                model_provider_id=row["model_provider_id"],
                model_id=row["model_id"],
                capability=row["capability"],
                access_class=row["access_class"],
                registry_verified_at=row["registry_verified_at"],
            ),
            request=GenerationRequest(
                capability=row["capability"],
                project_id=self.db.require_external_for_internal(
                    connection,
                    "projects",
                    row["request_project_id"],
                ),
                shot_id=self.db.external_for_internal(
                    connection,
                    "shots",
                    row["request_shot_id"],
                ),
                content_id=self.db.external_for_internal(
                    connection,
                    "contents",
                    row["request_content_id"],
                ),
                prompt_id=row["prompt_id"],
                prompt_version=row["prompt_version"],
                input_asset_ids=self.db.ordered_external_ids(
                    connection,
                    "generation_attempt_input_assets",
                    "attempt_id",
                    row["id"],
                    "asset_id",
                    "assets",
                ),
                constraints=dict(row["request_constraints"]),
                target_duration_seconds=(
                    float(row["target_duration_seconds"])
                    if row["target_duration_seconds"] is not None
                    else None
                ),
                requires_commercial_rights=row["requires_commercial_rights"],
                requires_character_continuity=row["requires_character_continuity"],
                idempotency_key=row["request_idempotency_key"],
            ),
            provider_generation_id=row["provider_generation_id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            output_asset_ids=[str(value) for value in output_ids],
            status=row["status"],
            normalized_error_code=row["normalized_error_code"],
            error_detail=row["error_detail"],
            free_credits_used=self._decimal(row["free_credits_used"]),
            paid_cost=self._decimal(row["paid_cost"]),
            currency=str(row["currency"]),
            qa_record_ids=self.db.ordered_external_ids(
                connection,
                "generation_attempt_qa_records",
                "attempt_id",
                row["id"],
                "qa_record_id",
                "qa_records",
            ),
        )

    def _characters(
        self,
        connection: Connection,
        project_id: UUID,
    ) -> tuple[list[Character], list[CharacterVersion]]:
        internal_ids = self.db.ordered_target_ids(
            connection,
            "project_characters",
            "project_id",
            project_id,
            "character_id",
        )
        characters: list[Character] = []
        versions: list[CharacterVersion] = []
        version_table = self.db.table("character_versions")
        for internal_id in internal_ids:
            row = self.db.require_row_by_id(connection, "characters", internal_id)
            characters.append(self._character(connection, row))
            version_rows = connection.execute(
                select(version_table)
                .where(version_table.c.character_id == internal_id)
                .order_by(version_table.c.version)
            ).mappings()
            versions.extend(self._character_version(connection, item) for item in version_rows)
        return characters, versions

    def _character(self, connection: Connection, row: RowMapping) -> Character:
        lock_table = self.db.table("character_locks")
        lock = connection.execute(
            select(lock_table).where(lock_table.c.character_id == row["id"])
        ).mappings().one_or_none()
        if lock is None:
            raise PersistenceShapeError(f"character {row['external_id']} has no lock row")
        return Character(
            schema_version=row["schema_version"],
            character_id=row["external_id"],
            name=row["name"],
            active_version_id=self.db.require_external_for_internal(
                connection,
                "character_versions",
                row["active_version_id"],
            ),
            lock=CharacterLock(
                scope=lock["scope"],
                pinned_character_version_id=self.db.external_for_internal(
                    connection,
                    "character_versions",
                    lock["pinned_character_version_id"],
                ),
                pinned_look_id=self.db.external_for_internal(
                    connection,
                    "character_looks",
                    lock["pinned_look_id"],
                ),
                project_id=self.db.external_for_internal(
                    connection,
                    "projects",
                    lock["project_id"],
                ),
                scene_id=self.db.external_for_internal(
                    connection,
                    "scenes",
                    lock["scene_id"],
                ),
            ),
            reusable=row["reusable"],
            rights_record_id=self.db.external_for_internal(
                connection,
                "rights_records",
                row["rights_record_id"],
            ),
            tags=list(row["tags"]),
            audit=self._audit(row),
        )

    def _character_version(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> CharacterVersion:
        look_table = self.db.table("character_looks")
        look_rows = connection.execute(
            select(look_table)
            .where(look_table.c.character_version_id == row["id"])
            .order_by(look_table.c.position)
        ).mappings()
        looks = [self._look(connection, look) for look in look_rows]
        return CharacterVersion(
            schema_version=row["schema_version"],
            character_version_id=row["external_id"],
            character_id=self.db.require_external_for_internal(
                connection,
                "characters",
                row["character_id"],
            ),
            version=row["version"],
            display_name=row["display_name"],
            character_type=row["character_type"],
            species=row["species"],
            apparent_age=row["apparent_age"],
            gender_presentation=row["gender_presentation"],
            personality_traits=list(row["personality_traits"]),
            movement_style=row["movement_style"],
            voice_profile_id=self.db.external_for_internal(
                connection,
                "voice_profiles",
                row["voice_profile_id"],
            ),
            looks=looks,
            canonical_reference_asset_ids=self.db.ordered_external_ids(
                connection,
                "character_version_reference_assets",
                "character_version_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            identity_constraints=list(row["identity_constraints"]),
            status=row["status"],
            audit=self._audit(row),
        )

    def _look(self, connection: Connection, row: RowMapping) -> CharacterLook:
        return CharacterLook(
            look_id=row["external_id"],
            name=row["name"],
            wardrobe=list(row["wardrobe"]),
            accessories=list(row["accessories"]),
            hair=row["hair"],
            eyes=row["eyes"],
            palette=list(row["palette"]),
            expression_defaults=list(row["expression_defaults"]),
            body_notes=list(row["body_notes"]),
            prohibited_mutations=list(row["prohibited_mutations"]),
            reference_asset_ids=self.db.ordered_external_ids(
                connection,
                "character_look_reference_assets",
                "character_look_id",
                row["id"],
                "asset_id",
                "assets",
            ),
        )

    def _worlds(self, connection: Connection, project_id: UUID) -> list[World]:
        ids = self.db.ordered_target_ids(
            connection,
            "project_worlds",
            "project_id",
            project_id,
            "world_id",
        )
        return [
            self._world(connection, self.db.require_row_by_id(connection, "worlds", item))
            for item in ids
        ]

    def _world(self, connection: Connection, row: RowMapping) -> World:
        return World(
            schema_version=row["schema_version"],
            world_id=row["external_id"],
            name=row["name"],
            description=row["description"],
            style_profile_id=self.db.external_for_internal(
                connection,
                "style_profiles",
                row["style_profile_id"],
            ),
            canonical_reference_asset_ids=self.db.ordered_external_ids(
                connection,
                "world_reference_assets",
                "world_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            rules=list(row["rules"]),
            forbidden_mutations=list(row["forbidden_mutations"]),
            audit=self._audit(row),
        )

    def _props(self, connection: Connection, project_id: UUID) -> list[Prop]:
        ids = self.db.ordered_target_ids(
            connection,
            "project_props",
            "project_id",
            project_id,
            "prop_id",
        )
        return [
            self._prop(connection, self.db.require_row_by_id(connection, "props", item))
            for item in ids
        ]

    def _prop(self, connection: Connection, row: RowMapping) -> Prop:
        return Prop(
            schema_version=row["schema_version"],
            prop_id=row["external_id"],
            name=row["name"],
            description=row["description"],
            canonical_reference_asset_ids=self.db.ordered_external_ids(
                connection,
                "prop_reference_assets",
                "prop_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            identity_constraints=list(row["identity_constraints"]),
            audit=self._audit(row),
        )

    def _locations(
        self,
        connection: Connection,
        scenes: list[Scene],
        shots: list[Shot],
    ) -> list[Location]:
        external_ids = {
            value
            for value in (
                [scene.location_id for scene in scenes]
                + [shot.location_id for shot in shots]
            )
            if value is not None
        }
        return [
            self._location(
                connection,
                self.db.require_row_by_external(connection, "locations", external_id),
            )
            for external_id in sorted(external_ids)
        ]

    def _location(self, connection: Connection, row: RowMapping) -> Location:
        return Location(
            schema_version=row["schema_version"],
            location_id=row["external_id"],
            world_id=self.db.external_for_internal(
                connection,
                "worlds",
                row["world_id"],
            ),
            name=row["name"],
            description=row["description"],
            canonical_reference_asset_ids=self.db.ordered_external_ids(
                connection,
                "location_reference_assets",
                "location_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            environment_constraints=list(row["environment_constraints"]),
            audit=self._audit(row),
        )

    def _assets(
        self,
        connection: Connection,
        project_id: UUID,
        timeline: Timeline,
        shots: list[Shot],
        takes: list[Take],
        attempts: list[GenerationAttempt],
        character_versions: list[CharacterVersion],
        worlds: list[World],
        locations: list[Location],
        props: list[Prop],
    ) -> list[Asset]:
        table = self.db.table("assets")
        direct = connection.execute(
            select(table.c.external_id).where(table.c.project_id == project_id)
        ).scalars()
        wanted = {str(value) for value in direct}
        wanted.update(timeline.marker_asset_ids)
        if timeline.otio_asset_id is not None:
            wanted.add(timeline.otio_asset_id)
        for shot in shots:
            wanted.update(shot.reference_asset_ids)
            if shot.first_frame_asset_id is not None:
                wanted.add(shot.first_frame_asset_id)
            if shot.end_frame_asset_id is not None:
                wanted.add(shot.end_frame_asset_id)
        for take in takes:
            if take.asset_id is not None:
                wanted.add(take.asset_id)
        for attempt in attempts:
            wanted.update(attempt.request.input_asset_ids)
            wanted.update(attempt.output_asset_ids)
        for version in character_versions:
            wanted.update(version.canonical_reference_asset_ids)
            for look in version.looks:
                wanted.update(look.reference_asset_ids)
        for world in worlds:
            wanted.update(world.canonical_reference_asset_ids)
        for location in locations:
            wanted.update(location.canonical_reference_asset_ids)
        for prop in props:
            wanted.update(prop.canonical_reference_asset_ids)

        loaded: dict[str, Asset] = {}
        pending = set(wanted)
        while pending:
            external_id = pending.pop()
            if external_id in loaded:
                continue
            row = self.db.require_row_by_external(connection, "assets", external_id)
            asset = self._asset(connection, row)
            loaded[asset.asset_id] = asset
            pending.update(set(asset.parent_asset_ids) - set(loaded))
        return [loaded[external_id] for external_id in sorted(loaded)]

    def _asset(self, connection: Connection, row: RowMapping) -> Asset:
        return Asset(
            schema_version=row["schema_version"],
            asset_id=row["external_id"],
            project_id=self.db.external_for_internal(
                connection,
                "projects",
                row["project_id"],
            ),
            kind=row["kind"],
            uri=row["uri"],
            sha256=str(row["sha256"]),
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            duration_seconds=(
                float(row["duration_seconds"])
                if row["duration_seconds"] is not None
                else None
            ),
            width=row["width"],
            height=row["height"],
            parent_asset_ids=self.db.ordered_external_ids(
                connection,
                "asset_parents",
                "child_asset_id",
                row["id"],
                "parent_asset_id",
                "assets",
            ),
            provider_id=row["provider_id"],
            model_provider_id=row["model_provider_id"],
            provider_model_id=row["provider_model_id"],
            generation_attempt_id=self.db.external_for_internal(
                connection,
                "generation_attempts",
                row["generation_attempt_id"],
            ),
            rights_record_id=self.db.external_for_internal(
                connection,
                "rights_records",
                row["rights_record_id"],
            ),
            canonical_status=row["canonical_status"],
            retention_class=row["retention_class"],
            audit=self._audit(row),
        )

    def _qa_records(
        self,
        connection: Connection,
        subject_ids: set[str],
        attempts: list[GenerationAttempt],
        takes: list[Take],
    ) -> list[QARecord]:
        wanted: set[str] = set()
        for attempt in attempts:
            wanted.update(attempt.qa_record_ids)
        for take in takes:
            wanted.update(take.qa_record_ids)
        table = self.db.table("qa_records")
        if subject_ids:
            rows = connection.execute(
                select(table).where(table.c.subject_id.in_(sorted(subject_ids)))
            ).mappings()
            wanted.update(str(row["external_id"]) for row in rows)
        return [
            self._qa(self.db.require_row_by_external(connection, "qa_records", qa_id))
            for qa_id in sorted(wanted)
        ]

    @staticmethod
    def _qa(row: RowMapping) -> QARecord:
        return QARecord(
            schema_version=row["schema_version"],
            qa_record_id=row["external_id"],
            subject_type=row["subject_type"],
            subject_id=row["subject_id"],
            gate=row["gate"],
            passed=row["passed"],
            critical=row["critical"],
            score=float(row["score"]) if row["score"] is not None else None,
            findings=list(row["findings"]),
            reviewer=row["reviewer"],
            created_at=row["created_at"],
        )

    def _cost_records(self, connection: Connection, project_id: UUID) -> list[CostRecord]:
        table = self.db.table("cost_records")
        rows = connection.execute(
            select(table)
            .where(table.c.project_id == project_id)
            .order_by(table.c.recorded_at, table.c.external_id)
        ).mappings()
        return [self._cost(connection, row) for row in rows]

    def _cost(self, connection: Connection, row: RowMapping) -> CostRecord:
        return CostRecord(
            schema_version=row["schema_version"],
            cost_record_id=row["external_id"],
            project_id=self.db.require_external_for_internal(
                connection,
                "projects",
                row["project_id"],
            ),
            job_id=self.db.external_for_internal(connection, "jobs", row["job_id"]),
            attempt_id=self.db.external_for_internal(
                connection,
                "generation_attempts",
                row["attempt_id"],
            ),
            provider_id=row["provider_id"],
            model_provider_id=row["model_provider_id"],
            model_id=row["model_id"],
            free_credits_used=Decimal(row["free_credits_used"]),
            paid_cost=Decimal(row["paid_cost"]),
            currency=str(row["currency"]),
            estimated=row["estimated"],
            recorded_at=row["recorded_at"],
        )

    def _rights_records(
        self,
        connection: Connection,
        subject_ids: set[str],
        characters: list[Character],
        assets: list[Asset],
    ) -> list[RightsRecord]:
        wanted = {
            value
            for value in (
                [character.rights_record_id for character in characters]
                + [asset.rights_record_id for asset in assets]
            )
            if value is not None
        }
        table = self.db.table("rights_records")
        if subject_ids:
            rows = connection.execute(
                select(table).where(table.c.subject_id.in_(sorted(subject_ids)))
            ).mappings()
            wanted.update(str(row["external_id"]) for row in rows)
        return [
            self._rights(
                self.db.require_row_by_external(connection, "rights_records", rights_id)
            )
            for rights_id in sorted(wanted)
        ]

    @staticmethod
    def _rights(row: RowMapping) -> RightsRecord:
        return RightsRecord(
            schema_version=row["schema_version"],
            rights_record_id=row["external_id"],
            subject_type=row["subject_type"],
            subject_id=row["subject_id"],
            provider_id=row["provider_id"],
            model_provider_id=row["model_provider_id"],
            model_id=row["model_id"],
            plan_or_tier=row["plan_or_tier"],
            commercial_use=row["commercial_use"],
            watermark_required=row["watermark_required"],
            source_basis=row["source_basis"],
            consent_reference=row["consent_reference"],
            evidence_urls=list(row["evidence_urls"]),
            verified_at=row["verified_at"],
            publication_blocked=row["publication_blocked"],
            notes=list(row["notes"]),
        )

    @staticmethod
    def _subject_ids(
        project: Project,
        content: Content,
        content_version: ContentVersion,
        timeline: Timeline,
        acts: list[Act],
        sequences: list[Sequence],
        scenes: list[Scene],
        shots: list[Shot],
        takes: list[Take],
        jobs: list[Job],
        attempts: list[GenerationAttempt],
        characters: list[Character],
        versions: list[CharacterVersion],
        worlds: list[World],
        locations: list[Location],
        props: list[Prop],
    ) -> set[str]:
        return {
            project.project_id,
            content.content_id,
            content_version.content_version_id,
            timeline.timeline_id,
            *[item.act_id for item in acts],
            *[item.sequence_id for item in sequences],
            *[item.scene_id for item in scenes],
            *[item.shot_id for item in shots],
            *[item.take_id for item in takes],
            *[item.job_id for item in jobs],
            *[item.attempt_id for item in attempts],
            *[item.character_id for item in characters],
            *[item.character_version_id for item in versions],
            *[item.world_id for item in worlds],
            *[item.location_id for item in locations],
            *[item.prop_id for item in props],
        }

    @staticmethod
    def _audit(row: RowMapping) -> AuditFields:
        return AuditFields(
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            created_by=row["created_by"],
            revision=row["revision"],
        )

    @staticmethod
    def _decimal(value: object) -> Decimal | None:
        return Decimal(str(value)) if value is not None else None
