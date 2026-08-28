from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from .aggregate import ProjectBundle
from .character import Character, CharacterLock, CharacterLook, CharacterVersion
from .common import AuditFields, TimeRange
from .content import Content, ContentObjective, ContentVersion
from .entities import Location, Prop, World
from .legacy_import import (
    LegacyContentImportResult,
    LegacyContentReconciliation,
    reconcile_legacy_content_import,
)
from .lineage import ProductionLineageBundle
from .production import (
    Asset,
    CostRecord,
    GenerationAttempt,
    GenerationRequest,
    Job,
    ProviderModelRef,
    QARecord,
    RightsRecord,
)
from .project import AudienceProfile, CastProfile, CreativeProfile, OutputProfile, Project, ProviderPolicyRef
from .timeline import Act, ContinuityState, Scene, Sequence, Shot, Take, Timeline, TimelineTrack

PersistenceAction = Literal["created", "noop"]


class PersistenceError(RuntimeError):
    """Base class for operational persistence failures."""


class PersistenceNotFoundError(PersistenceError):
    """Requested canonical aggregate does not exist."""


class PersistenceConflictError(PersistenceError):
    """Stable external identity is already bound to different canonical data."""


class PersistenceReferenceError(PersistenceError):
    """A referenced shared record is not available in PostgreSQL."""


class PersistenceShapeError(PersistenceError):
    """A valid domain bundle cannot be represented losslessly by the M01 mapping."""


@dataclass(frozen=True)
class PersistResult:
    action: PersistenceAction
    project_id: str


@dataclass(frozen=True)
class _Ids:
    values: dict[str, dict[str, UUID]]

    def require(self, table: str, external_id: str) -> UUID:
        try:
            return self.values[table][external_id]
        except KeyError as exc:
            raise PersistenceReferenceError(
                f"missing internal identity for {table}:{external_id}"
            ) from exc

    def optional(self, table: str, external_id: str | None) -> UUID | None:
        if external_id is None:
            return None
        return self.require(table, external_id)


class PostgresProductionRepository:
    """Persist one validated production lineage aggregate atomically.

    Domain/external IDs remain the public identity boundary. Internal PostgreSQL UUIDs are
    generated and consumed only inside this repository. The repository is deliberately
    provider-neutral and accepts an already-configured SQLAlchemy Engine rather than reading
    credentials or environment variables itself.
    """

    _required_tables = {
        "acts",
        "asset_parents",
        "assets",
        "character_look_reference_assets",
        "character_locks",
        "character_looks",
        "character_version_reference_assets",
        "character_versions",
        "characters",
        "content_version_characters",
        "content_version_props",
        "content_version_worlds",
        "content_versions",
        "contents",
        "cost_records",
        "generation_attempt_input_assets",
        "generation_attempt_qa_records",
        "generation_attempts",
        "job_dependencies",
        "jobs",
        "legacy_content_imports",
        "location_reference_assets",
        "locations",
        "project_characters",
        "project_props",
        "project_worlds",
        "projects",
        "prop_reference_assets",
        "props",
        "qa_records",
        "rights_records",
        "scene_characters",
        "scenes",
        "sequences",
        "shot_characters",
        "shot_props",
        "shot_reference_assets",
        "shots",
        "take_qa_records",
        "takes",
        "timeline_marker_assets",
        "timeline_track_items",
        "timeline_tracks",
        "timelines",
        "world_reference_assets",
        "worlds",
    }

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        self._tables: dict[str, Table] = {}
        for name in self._required_tables:
            key = f"core.{name}"
            if key not in metadata.tables:
                raise PersistenceError(f"required migrated table is missing: {key}")
            self._tables[name] = metadata.tables[key]

    def save_bundle(self, bundle: ProductionLineageBundle) -> PersistResult:
        canonical = ProductionLineageBundle.model_validate(bundle.model_dump())
        self._validate_derived_order(canonical)
        project_id = canonical.project_bundle.project.project_id

        try:
            with self.engine.begin() as connection:
                existing = self._row_by_external(connection, "projects", project_id)
                if existing is not None:
                    restored = self._load_bundle(connection, project_id)
                    if self._canonical_dump(restored) == self._canonical_dump(canonical):
                        return PersistResult(action="noop", project_id=project_id)
                    raise PersistenceConflictError(
                        f"project {project_id} already exists with different canonical data"
                    )
                self._insert_bundle(connection, canonical)
        except PersistenceError:
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database integrity rejected project {project_id}: {exc.orig}"
            ) from exc

        return PersistResult(action="created", project_id=project_id)

    def load_bundle(self, project_id: str) -> ProductionLineageBundle:
        with self.engine.connect() as connection:
            return self._load_bundle(connection, project_id)

    def import_legacy_content(
        self,
        imported: LegacyContentImportResult,
        *,
        imported_at: datetime,
    ) -> LegacyContentReconciliation:
        """Persist/reconcile one WP4 legacy import without mutating repository history."""

        try:
            with self.engine.begin() as connection:
                existing_content_row = self._row_by_external(
                    connection, "contents", imported.content.content_id
                )
                existing_version_row = self._row_by_external(
                    connection,
                    "content_versions",
                    imported.content_version.content_version_id,
                )
                existing_import_key = self._legacy_import_key(
                    connection,
                    imported.report.mapping_version,
                    imported.report.source_content_id,
                )

                existing_content = (
                    self._content_from_row(connection, existing_content_row)
                    if existing_content_row is not None
                    else None
                )
                existing_version = (
                    self._content_version_from_row(connection, existing_version_row)
                    if existing_version_row is not None
                    else None
                )
                decision = reconcile_legacy_content_import(
                    imported,
                    existing_content=existing_content,
                    existing_content_version=existing_version,
                    existing_import_key=existing_import_key,
                )
                if decision.action == "conflict":
                    return decision

                if decision.action == "create":
                    content_uuid = uuid4()
                    version_uuid = uuid4()
                    self._insert_content_pair(
                        connection,
                        imported.content,
                        imported.content_version,
                        content_uuid,
                        version_uuid,
                    )
                else:
                    if existing_content_row is None or existing_version_row is None:
                        raise PersistenceConflictError(
                            "legacy reconciliation returned noop without complete canonical rows"
                        )
                    content_uuid = existing_content_row["id"]
                    version_uuid = existing_version_row["id"]

                if existing_import_key is None:
                    self._insert_legacy_import_ledger(
                        connection,
                        imported,
                        content_uuid,
                        version_uuid,
                        imported_at,
                    )
                return decision
        except PersistenceError:
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database integrity rejected legacy import {imported.report.import_key}: {exc.orig}"
            ) from exc

    def _insert_bundle(self, connection: Connection, bundle: ProductionLineageBundle) -> None:
        ids = self._allocate_ids(bundle)
        project_bundle = bundle.project_bundle
        project = project_bundle.project

        for record in bundle.rights_records:
            self._insert(connection, "rights_records", self._rights_values(record, ids))

        self._insert(connection, "projects", self._project_values(project, ids))
        self._insert(
            connection,
            "contents",
            self._content_values(bundle.content, ids, project_required=True),
        )
        self._insert(
            connection,
            "content_versions",
            self._content_version_values(bundle.content_version, ids),
        )

        for character in project_bundle.characters:
            self._insert(connection, "characters", self._character_values(character, ids))
        for version in project_bundle.character_versions:
            self._insert(
                connection,
                "character_versions",
                self._character_version_values(connection, version, ids),
            )
            for position, look in enumerate(version.looks):
                self._insert(
                    connection,
                    "character_looks",
                    self._character_look_values(look, version, position, ids),
                )

        for world in project_bundle.worlds:
            self._insert(connection, "worlds", self._world_values(connection, world, ids))
        for location in project_bundle.locations:
            self._insert(connection, "locations", self._location_values(location, ids))
        for prop in project_bundle.props:
            self._insert(connection, "props", self._prop_values(prop, ids))

        timeline = project_bundle.timeline
        self._insert(connection, "timelines", self._timeline_values(timeline, ids))
        for position, track in enumerate(timeline.tracks):
            self._insert(
                connection,
                "timeline_tracks",
                {
                    "id": ids.require("timeline_tracks", track.track_id),
                    "external_id": track.track_id,
                    "timeline_id": ids.require("timelines", timeline.timeline_id),
                    "position": position,
                    "kind": track.kind,
                    "name": track.name,
                    "muted": track.muted,
                    "locked": track.locked,
                },
            )

        for act in project_bundle.acts:
            self._insert(connection, "acts", self._act_values(act, timeline, ids))
        for sequence in project_bundle.sequences:
            self._insert(connection, "sequences", self._sequence_values(sequence, ids))
        for scene in project_bundle.scenes:
            self._insert(connection, "scenes", self._scene_values(scene, ids))
        for shot in project_bundle.shots:
            self._insert(connection, "shots", self._shot_values(shot, ids))

        for job in bundle.jobs:
            self._insert(connection, "jobs", self._job_values(job, ids))
        for attempt in bundle.attempts:
            self._insert(connection, "generation_attempts", self._attempt_values(attempt, ids))

        output_positions = self._attempt_output_positions(bundle.attempts)
        for asset in bundle.assets:
            self._insert(
                connection,
                "assets",
                self._asset_values(asset, ids, output_positions),
            )

        take_positions = self._take_positions(project_bundle.shots)
        for take in project_bundle.takes:
            self._insert(
                connection,
                "takes",
                self._take_values(take, ids, take_positions),
            )

        for record in bundle.qa_records:
            self._insert(connection, "qa_records", self._qa_values(record, ids))
        for record in bundle.cost_records:
            self._insert(connection, "cost_records", self._cost_values(record, ids))

        for character in project_bundle.characters:
            self._insert(
                connection,
                "character_locks",
                self._character_lock_values(character, ids),
            )

        self._insert_relationships(connection, bundle, ids)
        self._apply_deferred_pointer_updates(connection, bundle, ids)

    def _insert_relationships(
        self,
        connection: Connection,
        bundle: ProductionLineageBundle,
        ids: _Ids,
    ) -> None:
        pb = bundle.project_bundle
        project = pb.project
        timeline = pb.timeline

        self._insert_ordered(
            connection,
            "project_characters",
            "project_id",
            ids.require("projects", project.project_id),
            "character_id",
            [ids.require("characters", value) for value in project.character_ids],
        )
        self._insert_ordered(
            connection,
            "project_worlds",
            "project_id",
            ids.require("projects", project.project_id),
            "world_id",
            [ids.require("worlds", value) for value in project.world_ids],
        )
        self._insert_ordered(
            connection,
            "project_props",
            "project_id",
            ids.require("projects", project.project_id),
            "prop_id",
            [ids.require("props", value) for value in project.prop_ids],
        )

        version = bundle.content_version
        version_uuid = ids.require("content_versions", version.content_version_id)
        self._insert_ordered(
            connection,
            "content_version_characters",
            "content_version_id",
            version_uuid,
            "character_id",
            [ids.require("characters", value) for value in version.character_ids],
        )
        self._insert_ordered(
            connection,
            "content_version_worlds",
            "content_version_id",
            version_uuid,
            "world_id",
            [ids.require("worlds", value) for value in version.world_ids],
        )
        self._insert_ordered(
            connection,
            "content_version_props",
            "content_version_id",
            version_uuid,
            "prop_id",
            [ids.require("props", value) for value in version.prop_ids],
        )

        for scene in pb.scenes:
            self._insert_ordered(
                connection,
                "scene_characters",
                "scene_id",
                ids.require("scenes", scene.scene_id),
                "character_id",
                [ids.require("characters", value) for value in scene.character_ids],
            )
        for shot in pb.shots:
            shot_uuid = ids.require("shots", shot.shot_id)
            self._insert_ordered(
                connection,
                "shot_characters",
                "shot_id",
                shot_uuid,
                "character_id",
                [ids.require("characters", value) for value in shot.character_ids],
            )
            self._insert_ordered(
                connection,
                "shot_props",
                "shot_id",
                shot_uuid,
                "prop_id",
                [ids.require("props", value) for value in shot.prop_ids],
            )
            self._insert_ordered(
                connection,
                "shot_reference_assets",
                "shot_id",
                shot_uuid,
                "asset_id",
                [ids.require("assets", value) for value in shot.reference_asset_ids],
            )

        for version in pb.character_versions:
            version_uuid = ids.require("character_versions", version.character_version_id)
            self._insert_ordered(
                connection,
                "character_version_reference_assets",
                "character_version_id",
                version_uuid,
                "asset_id",
                [ids.require("assets", value) for value in version.canonical_reference_asset_ids],
            )
            for look in version.looks:
                self._insert_ordered(
                    connection,
                    "character_look_reference_assets",
                    "character_look_id",
                    ids.require("character_looks", look.look_id),
                    "asset_id",
                    [ids.require("assets", value) for value in look.reference_asset_ids],
                )

        for world in pb.worlds:
            self._insert_ordered(
                connection,
                "world_reference_assets",
                "world_id",
                ids.require("worlds", world.world_id),
                "asset_id",
                [ids.require("assets", value) for value in world.canonical_reference_asset_ids],
            )
        for location in pb.locations:
            self._insert_ordered(
                connection,
                "location_reference_assets",
                "location_id",
                ids.require("locations", location.location_id),
                "asset_id",
                [ids.require("assets", value) for value in location.canonical_reference_asset_ids],
            )
        for prop in pb.props:
            self._insert_ordered(
                connection,
                "prop_reference_assets",
                "prop_id",
                ids.require("props", prop.prop_id),
                "asset_id",
                [ids.require("assets", value) for value in prop.canonical_reference_asset_ids],
            )

        for asset in bundle.assets:
            self._insert_ordered(
                connection,
                "asset_parents",
                "child_asset_id",
                ids.require("assets", asset.asset_id),
                "parent_asset_id",
                [ids.require("assets", value) for value in asset.parent_asset_ids],
            )

        for attempt in bundle.attempts:
            attempt_uuid = ids.require("generation_attempts", attempt.attempt_id)
            self._insert_ordered(
                connection,
                "generation_attempt_input_assets",
                "attempt_id",
                attempt_uuid,
                "asset_id",
                [ids.require("assets", value) for value in attempt.request.input_asset_ids],
            )
            self._insert_ordered(
                connection,
                "generation_attempt_qa_records",
                "attempt_id",
                attempt_uuid,
                "qa_record_id",
                [ids.require("qa_records", value) for value in attempt.qa_record_ids],
            )

        for take in pb.takes:
            self._insert_ordered(
                connection,
                "take_qa_records",
                "take_id",
                ids.require("takes", take.take_id),
                "qa_record_id",
                [ids.require("qa_records", value) for value in take.qa_record_ids],
            )

        for job in bundle.jobs:
            self._insert_ordered(
                connection,
                "job_dependencies",
                "job_id",
                ids.require("jobs", job.job_id),
                "dependency_job_id",
                [ids.require("jobs", value) for value in job.dependency_job_ids],
            )

        self._insert_ordered(
            connection,
            "timeline_marker_assets",
            "timeline_id",
            ids.require("timelines", timeline.timeline_id),
            "asset_id",
            [ids.require("assets", value) for value in timeline.marker_asset_ids],
        )
        for track in timeline.tracks:
            self._insert_ordered_external(
                connection,
                "timeline_track_items",
                "track_id",
                ids.require("timeline_tracks", track.track_id),
                "item_external_id",
                track.item_ids,
            )

    def _apply_deferred_pointer_updates(
        self,
        connection: Connection,
        bundle: ProductionLineageBundle,
        ids: _Ids,
    ) -> None:
        pb = bundle.project_bundle
        timeline = pb.timeline
        if timeline.otio_asset_id is not None:
            self._update_by_id(
                connection,
                "timelines",
                ids.require("timelines", timeline.timeline_id),
                {"otio_asset_id": ids.require("assets", timeline.otio_asset_id)},
            )

        for shot in pb.shots:
            values: dict[str, Any] = {}
            if shot.first_frame_asset_id is not None:
                values["first_frame_asset_id"] = ids.require("assets", shot.first_frame_asset_id)
            if shot.end_frame_asset_id is not None:
                values["end_frame_asset_id"] = ids.require("assets", shot.end_frame_asset_id)
            if values:
                self._update_by_id(connection, "shots", ids.require("shots", shot.shot_id), values)

        for job in bundle.jobs:
            if job.parent_job_id is not None:
                self._update_by_id(
                    connection,
                    "jobs",
                    ids.require("jobs", job.job_id),
                    {"parent_job_id": ids.require("jobs", job.parent_job_id)},
                )

    def _load_bundle(self, connection: Connection, project_id: str) -> ProductionLineageBundle:
        project_row = self._row_by_external(connection, "projects", project_id)
        if project_row is None:
            raise PersistenceNotFoundError(f"project {project_id} was not found")
        project_internal = project_row["id"]

        project = self._project_from_row(connection, project_row)
        if project.content_id is None or project.active_timeline_id is None:
            raise PersistenceShapeError(
                f"project {project_id} is not a complete production lineage aggregate"
            )

        content_row = self._row_by_id(connection, "contents", project_row["content_id"])
        if content_row is None:
            raise PersistenceShapeError(f"project {project_id} content row is missing")
        content = self._content_from_row(connection, content_row)
        version_row = self._row_by_id(connection, "content_versions", content_row["active_version_id"])
        if version_row is None:
            raise PersistenceShapeError(f"project {project_id} active content version is missing")
        content_version = self._content_version_from_row(connection, version_row)

        timeline_row = self._row_by_id(connection, "timelines", project_row["active_timeline_id"])
        if timeline_row is None:
            raise PersistenceShapeError(f"project {project_id} active timeline is missing")
        timeline, timeline_internal = self._timeline_from_row(connection, timeline_row)

        acts, act_internal = self._load_acts(connection, timeline_internal)
        sequences, sequence_internal = self._load_sequences(connection, act_internal)
        scenes, scene_internal = self._load_scenes(connection, sequence_internal)
        shots, shot_internal = self._load_shots(connection, scene_internal)

        jobs, job_internal, attempts, attempt_internal = self._load_jobs_and_attempts(
            connection, project_internal
        )
        takes, take_internal = self._load_takes(connection, shot_internal)

        characters, character_versions = self._load_characters(connection, project_internal)
        worlds = self._load_worlds(connection, project_internal)
        props = self._load_props(connection, project_internal)
        locations = self._load_used_locations(connection, scenes, shots)

        assets = self._load_assets(
            connection,
            project_internal,
            timeline,
            shots,
            takes,
            character_versions,
            worlds,
            locations,
            props,
            attempts,
        )
        qa_records = self._load_qa_records(connection, attempts, takes, assets)
        cost_records = self._load_cost_records(connection, project_internal)
        rights_records = self._load_rights_records(connection, characters, assets)

        # Rebuild take/attempt QA lists after QA rows are known. The models loaded above already
        # carry ordered relation IDs, so no mutation is required here.
        del job_internal, attempt_internal, take_internal

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

    def _load_acts(
        self, connection: Connection, timeline_id: UUID
    ) -> tuple[list[Act], dict[str, UUID]]:
        table = self._t("acts")
        rows = list(
            connection.execute(
                select(table).where(table.c.timeline_id == timeline_id).order_by(table.c["order"])
            ).mappings()
        )
        items = [self._act_from_row(connection, row) for row in rows]
        return items, {item.act_id: row["id"] for item, row in zip(items, rows, strict=True)}

    def _load_sequences(
        self, connection: Connection, act_ids: dict[str, UUID]
    ) -> tuple[list[Sequence], dict[str, UUID]]:
        if not act_ids:
            return [], {}
        table = self._t("sequences")
        rows = list(
            connection.execute(
                select(table)
                .where(table.c.act_id.in_(list(act_ids.values())))
                .order_by(table.c.act_id, table.c["order"])
            ).mappings()
        )
        items = [self._sequence_from_row(connection, row) for row in rows]
        return items, {item.sequence_id: row["id"] for item, row in zip(items, rows, strict=True)}

    def _load_scenes(
        self, connection: Connection, sequence_ids: dict[str, UUID]
    ) -> tuple[list[Scene], dict[str, UUID]]:
        if not sequence_ids:
            return [], {}
        table = self._t("scenes")
        rows = list(
            connection.execute(
                select(table)
                .where(table.c.sequence_id.in_(list(sequence_ids.values())))
                .order_by(table.c.sequence_id, table.c["order"])
            ).mappings()
        )
        items = [self._scene_from_row(connection, row) for row in rows]
        return items, {item.scene_id: row["id"] for item, row in zip(items, rows, strict=True)}

    def _load_shots(
        self, connection: Connection, scene_ids: dict[str, UUID]
    ) -> tuple[list[Shot], dict[str, UUID]]:
        if not scene_ids:
            return [], {}
        table = self._t("shots")
        rows = list(
            connection.execute(
                select(table)
                .where(table.c.scene_id.in_(list(scene_ids.values())))
                .order_by(table.c.scene_id, table.c["order"])
            ).mappings()
        )
        items = [self._shot_from_row(connection, row) for row in rows]
        return items, {item.shot_id: row["id"] for item, row in zip(items, rows, strict=True)}

    def _load_takes(
        self, connection: Connection, shot_ids: dict[str, UUID]
    ) -> tuple[list[Take], dict[str, UUID]]:
        if not shot_ids:
            return [], {}
        table = self._t("takes")
        rows = list(
            connection.execute(
                select(table)
                .where(table.c.shot_id.in_(list(shot_ids.values())))
                .order_by(table.c.shot_id, table.c.position)
            ).mappings()
        )
        items = [self._take_from_row(connection, row) for row in rows]
        return items, {item.take_id: row["id"] for item, row in zip(items, rows, strict=True)}

    def _load_jobs_and_attempts(
        self,
        connection: Connection,
        project_id: UUID,
    ) -> tuple[list[Job], dict[str, UUID], list[GenerationAttempt], dict[str, UUID]]:
        jobs_table = self._t("jobs")
        job_rows = list(
            connection.execute(
                select(jobs_table)
                .where(jobs_table.c.project_id == project_id)
                .order_by(jobs_table.c.external_id)
            ).mappings()
        )
        job_internal = {str(row["external_id"]): row["id"] for row in job_rows}

        attempts_table = self._t("generation_attempts")
        if job_internal:
            attempt_rows = list(
                connection.execute(
                    select(attempts_table)
                    .where(attempts_table.c.job_id.in_(list(job_internal.values())))
                    .order_by(attempts_table.c.job_id, attempts_table.c.attempt_number)
                ).mappings()
            )
        else:
            attempt_rows = []
        attempts = [self._attempt_from_row(connection, row) for row in attempt_rows]
        attempt_internal = {
            item.attempt_id: row["id"] for item, row in zip(attempts, attempt_rows, strict=True)
        }
        attempts_by_job: dict[UUID, list[str]] = {}
        for item, row in zip(attempts, attempt_rows, strict=True):
            attempts_by_job.setdefault(row["job_id"], []).append(item.attempt_id)

        jobs = [
            self._job_from_row(connection, row, attempts_by_job.get(row["id"], []))
            for row in job_rows
        ]
        return jobs, job_internal, attempts, attempt_internal

    def _load_characters(
        self,
        connection: Connection,
        project_id: UUID,
    ) -> tuple[list[Character], list[CharacterVersion]]:
        character_ids = self._ordered_target_ids(
            connection, "project_characters", "project_id", project_id, "character_id"
        )
        characters: list[Character] = []
        versions: list[CharacterVersion] = []
        for internal_id in character_ids:
            row = self._require_row_by_id(connection, "characters", internal_id)
            character = self._character_from_row(connection, row)
            characters.append(character)
            version_table = self._t("character_versions")
            version_rows = list(
                connection.execute(
                    select(version_table)
                    .where(version_table.c.character_id == internal_id)
                    .order_by(version_table.c.version)
                ).mappings()
            )
            versions.extend(self._character_version_from_row(connection, item) for item in version_rows)
        return characters, versions

    def _load_worlds(self, connection: Connection, project_id: UUID) -> list[World]:
        ids = self._ordered_target_ids(
            connection, "project_worlds", "project_id", project_id, "world_id"
        )
        return [self._world_from_row(connection, self._require_row_by_id(connection, "worlds", item)) for item in ids]

    def _load_props(self, connection: Connection, project_id: UUID) -> list[Prop]:
        ids = self._ordered_target_ids(
            connection, "project_props", "project_id", project_id, "prop_id"
        )
        return [self._prop_from_row(connection, self._require_row_by_id(connection, "props", item)) for item in ids]

    def _load_used_locations(
        self,
        connection: Connection,
        scenes: list[Scene],
        shots: list[Shot],
    ) -> list[Location]:
        external_ids = {
            value
            for value in [*[scene.location_id for scene in scenes], *[shot.location_id for shot in shots]]
            if value is not None
        }
        return [
            self._location_from_row(
                connection,
                self._require_row_by_external(connection, "locations", external_id),
            )
            for external_id in sorted(external_ids)
        ]

    def _load_assets(
        self,
        connection: Connection,
        project_id: UUID,
        timeline: Timeline,
        shots: list[Shot],
        takes: list[Take],
        versions: list[CharacterVersion],
        worlds: list[World],
        locations: list[Location],
        props: list[Prop],
        attempts: list[GenerationAttempt],
    ) -> list[Asset]:
        wanted: set[str] = set()
        table = self._t("assets")
        direct = list(
            connection.execute(
                select(table.c.external_id).where(table.c.project_id == project_id)
            ).scalars()
        )
        wanted.update(str(value) for value in direct)
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
        for version in versions:
            wanted.update(version.canonical_reference_asset_ids)
            for look in version.looks:
                wanted.update(look.reference_asset_ids)
        for world in worlds:
            wanted.update(world.canonical_reference_asset_ids)
        for location in locations:
            wanted.update(location.canonical_reference_asset_ids)
        for prop in props:
            wanted.update(prop.canonical_reference_asset_ids)
        for attempt in attempts:
            wanted.update(attempt.request.input_asset_ids)
            wanted.update(attempt.output_asset_ids)

        loaded: dict[str, Asset] = {}
        pending = set(wanted)
        while pending:
            external_id = pending.pop()
            if external_id in loaded:
                continue
            row = self._require_row_by_external(connection, "assets", external_id)
            asset = self._asset_from_row(connection, row)
            loaded[asset.asset_id] = asset
            pending.update(set(asset.parent_asset_ids) - set(loaded))
        return [loaded[key] for key in sorted(loaded)]

    def _load_qa_records(
        self,
        connection: Connection,
        attempts: list[GenerationAttempt],
        takes: list[Take],
        assets: list[Asset],
    ) -> list[QARecord]:
        wanted: set[str] = set()
        for attempt in attempts:
            wanted.update(attempt.qa_record_ids)
        for take in takes:
            wanted.update(take.qa_record_ids)

        subject_ids = {
            *[attempt.attempt_id for attempt in attempts],
            *[take.take_id for take in takes],
            *[asset.asset_id for asset in assets],
        }
        table = self._t("qa_records")
        if subject_ids:
            rows = list(
                connection.execute(
                    select(table).where(table.c.subject_id.in_(sorted(subject_ids)))
                ).mappings()
            )
            wanted.update(str(row["external_id"]) for row in rows)
        return [
            self._qa_from_row(self._require_row_by_external(connection, "qa_records", value))
            for value in sorted(wanted)
        ]

    def _load_cost_records(self, connection: Connection, project_id: UUID) -> list[CostRecord]:
        table = self._t("cost_records")
        rows = list(
            connection.execute(
                select(table)
                .where(table.c.project_id == project_id)
                .order_by(table.c.recorded_at, table.c.external_id)
            ).mappings()
        )
        return [self._cost_from_row(connection, row) for row in rows]

    def _load_rights_records(
        self,
        connection: Connection,
        characters: list[Character],
        assets: list[Asset],
    ) -> list[RightsRecord]:
        wanted = {
            value
            for value in [
                *[character.rights_record_id for character in characters],
                *[asset.rights_record_id for asset in assets],
            ]
            if value is not None
        }
        subject_ids = {*[character.character_id for character in characters], *[asset.asset_id for asset in assets]}
        table = self._t("rights_records")
        if subject_ids:
            rows = list(
                connection.execute(
                    select(table).where(table.c.subject_id.in_(sorted(subject_ids)))
                ).mappings()
            )
            wanted.update(str(row["external_id"]) for row in rows)
        return [
            self._rights_from_row(self._require_row_by_external(connection, "rights_records", value))
            for value in sorted(wanted)
        ]

    def _project_values(self, project: Project, ids: _Ids) -> dict[str, Any]:
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

    def _content_values(
        self,
        content: Content,
        ids: _Ids,
        *,
        project_required: bool,
    ) -> dict[str, Any]:
        project_uuid = ids.optional("projects", content.project_id)
        if project_required and project_uuid is None:
            raise PersistenceShapeError("production lineage content must belong to its project")
        return {
            "id": ids.require("contents", content.content_id),
            "external_id": content.content_id,
            "schema_version": content.schema_version,
            "active_version_id": ids.require("content_versions", content.active_version_id),
            "project_id": project_uuid,
            "status": content.status,
            "source_legacy_package_path": content.source_legacy_package_path,
            **self._audit(content.audit),
        }

    def _content_version_values(self, version: ContentVersion, ids: _Ids) -> dict[str, Any]:
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

    def _character_values(self, character: Character, ids: _Ids) -> dict[str, Any]:
        return {
            "id": ids.require("characters", character.character_id),
            "external_id": character.character_id,
            "schema_version": character.schema_version,
            "name": character.name,
            "active_version_id": ids.require("character_versions", character.active_version_id),
            "reusable": character.reusable,
            "rights_record_id": ids.optional("rights_records", character.rights_record_id),
            "tags": character.tags,
            **self._audit(character.audit),
        }

    def _character_version_values(
        self,
        connection: Connection,
        version: CharacterVersion,
        ids: _Ids,
    ) -> dict[str, Any]:
        voice_id = self._resolve_shared_external(
            connection, "voice_profiles", version.voice_profile_id
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

    def _character_look_values(
        self,
        look: CharacterLook,
        version: CharacterVersion,
        position: int,
        ids: _Ids,
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

    def _character_lock_values(self, character: Character, ids: _Ids) -> dict[str, Any]:
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
        ids: _Ids,
    ) -> dict[str, Any]:
        return {
            "id": ids.require("worlds", world.world_id),
            "external_id": world.world_id,
            "schema_version": world.schema_version,
            "name": world.name,
            "description": world.description,
            "style_profile_id": self._resolve_shared_external(
                connection, "style_profiles", world.style_profile_id
            ),
            "rules": world.rules,
            "forbidden_mutations": world.forbidden_mutations,
            **self._audit(world.audit),
        }

    def _location_values(self, location: Location, ids: _Ids) -> dict[str, Any]:
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

    def _prop_values(self, prop: Prop, ids: _Ids) -> dict[str, Any]:
        return {
            "id": ids.require("props", prop.prop_id),
            "external_id": prop.prop_id,
            "schema_version": prop.schema_version,
            "name": prop.name,
            "description": prop.description,
            "identity_constraints": prop.identity_constraints,
            **self._audit(prop.audit),
        }

    def _timeline_values(self, timeline: Timeline, ids: _Ids) -> dict[str, Any]:
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

    def _act_values(self, act: Act, timeline: Timeline, ids: _Ids) -> dict[str, Any]:
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

    def _sequence_values(self, sequence: Sequence, ids: _Ids) -> dict[str, Any]:
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

    def _scene_values(self, scene: Scene, ids: _Ids) -> dict[str, Any]:
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

    def _shot_values(self, shot: Shot, ids: _Ids) -> dict[str, Any]:
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

    def _job_values(self, job: Job, ids: _Ids) -> dict[str, Any]:
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
            "selected_attempt_id": ids.optional("generation_attempts", job.selected_attempt_id),
            "retry_budget_remaining": job.retry_budget_remaining,
            "blocked_reason": job.blocked_reason,
            "claimed_by": job.claimed_by,
            "lease_expires_at": job.lease_expires_at,
            **self._audit(job.audit),
        }

    def _attempt_values(self, attempt: GenerationAttempt, ids: _Ids) -> dict[str, Any]:
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
        ids: _Ids,
        output_positions: dict[tuple[str, str], int],
    ) -> dict[str, Any]:
        output_position = None
        if asset.generation_attempt_id is not None:
            key = (asset.generation_attempt_id, asset.asset_id)
            if key not in output_positions:
                raise PersistenceShapeError(
                    f"asset {asset.asset_id} is not ordered in its generation attempt outputs"
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
        ids: _Ids,
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

    def _qa_values(self, record: QARecord, ids: _Ids) -> dict[str, Any]:
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

    def _cost_values(self, record: CostRecord, ids: _Ids) -> dict[str, Any]:
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

    def _rights_values(self, record: RightsRecord, ids: _Ids) -> dict[str, Any]:
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

    def _project_from_row(self, connection: Connection, row: RowMapping) -> Project:
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
            character_ids=self._ordered_external_ids(
                connection,
                "project_characters",
                "project_id",
                row["id"],
                "character_id",
                "characters",
            ),
            world_ids=self._ordered_external_ids(
                connection,
                "project_worlds",
                "project_id",
                row["id"],
                "world_id",
                "worlds",
            ),
            prop_ids=self._ordered_external_ids(
                connection,
                "project_props",
                "project_id",
                row["id"],
                "prop_id",
                "props",
            ),
            content_id=self._external_for_internal(connection, "contents", row["content_id"]),
            active_timeline_id=self._external_for_internal(
                connection, "timelines", row["active_timeline_id"]
            ),
            tags=list(row["tags"]),
            audit=self._audit_from_row(row),
        )

    def _content_from_row(self, connection: Connection, row: RowMapping) -> Content:
        return Content(
            schema_version=row["schema_version"],
            content_id=row["external_id"],
            active_version_id=self._required_external_for_internal(
                connection, "content_versions", row["active_version_id"]
            ),
            project_id=self._external_for_internal(connection, "projects", row["project_id"]),
            status=row["status"],
            source_legacy_package_path=row["source_legacy_package_path"],
            audit=self._audit_from_row(row),
        )

    def _content_version_from_row(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> ContentVersion:
        return ContentVersion(
            schema_version=row["schema_version"],
            content_version_id=row["external_id"],
            content_id=self._required_external_for_internal(
                connection, "contents", row["content_id"]
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
            character_ids=self._ordered_external_ids(
                connection,
                "content_version_characters",
                "content_version_id",
                row["id"],
                "character_id",
                "characters",
            ),
            world_ids=self._ordered_external_ids(
                connection,
                "content_version_worlds",
                "content_version_id",
                row["id"],
                "world_id",
                "worlds",
            ),
            prop_ids=self._ordered_external_ids(
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
            audit=self._audit_from_row(row),
        )

    def _timeline_from_row(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> tuple[Timeline, UUID]:
        track_table = self._t("timeline_tracks")
        track_rows = list(
            connection.execute(
                select(track_table)
                .where(track_table.c.timeline_id == row["id"])
                .order_by(track_table.c.position)
            ).mappings()
        )
        tracks = [
            TimelineTrack(
                track_id=track["external_id"],
                kind=track["kind"],
                name=track["name"],
                item_ids=self._ordered_scalar_values(
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
        acts_table = self._t("acts")
        act_ids = list(
            connection.execute(
                select(acts_table.c.external_id)
                .where(acts_table.c.timeline_id == row["id"])
                .order_by(acts_table.c["order"])
            ).scalars()
        )
        return (
            Timeline(
                schema_version=row["schema_version"],
                timeline_id=row["external_id"],
                project_id=self._required_external_for_internal(
                    connection, "projects", row["project_id"]
                ),
                version=row["version"],
                duration_seconds=float(row["duration_seconds"]),
                fps=float(row["fps"]),
                act_ids=[str(value) for value in act_ids],
                tracks=tracks,
                marker_asset_ids=self._ordered_external_ids(
                    connection,
                    "timeline_marker_assets",
                    "timeline_id",
                    row["id"],
                    "asset_id",
                    "assets",
                ),
                otio_asset_id=self._external_for_internal(
                    connection, "assets", row["otio_asset_id"]
                ),
                audit=self._audit_from_row(row),
            ),
            row["id"],
        )

    def _act_from_row(self, connection: Connection, row: RowMapping) -> Act:
        table = self._t("sequences")
        sequence_ids = list(
            connection.execute(
                select(table.c.external_id)
                .where(table.c.act_id == row["id"])
                .order_by(table.c["order"])
            ).scalars()
        )
        return Act(
            schema_version=row["schema_version"],
            act_id=row["external_id"],
            project_id=self._required_external_for_internal(
                connection, "projects", row["project_id"]
            ),
            order=row["order"],
            title=row["title"],
            sequence_ids=[str(value) for value in sequence_ids],
            target_duration_seconds=float(row["target_duration_seconds"]),
            audit=self._audit_from_row(row),
        )

    def _sequence_from_row(self, connection: Connection, row: RowMapping) -> Sequence:
        table = self._t("scenes")
        scene_ids = list(
            connection.execute(
                select(table.c.external_id)
                .where(table.c.sequence_id == row["id"])
                .order_by(table.c["order"])
            ).scalars()
        )
        return Sequence(
            schema_version=row["schema_version"],
            sequence_id=row["external_id"],
            act_id=self._required_external_for_internal(connection, "acts", row["act_id"]),
            order=row["order"],
            title=row["title"],
            scene_ids=[str(value) for value in scene_ids],
            target_duration_seconds=float(row["target_duration_seconds"]),
            audit=self._audit_from_row(row),
        )

    def _scene_from_row(self, connection: Connection, row: RowMapping) -> Scene:
        table = self._t("shots")
        shot_ids = list(
            connection.execute(
                select(table.c.external_id)
                .where(table.c.scene_id == row["id"])
                .order_by(table.c["order"])
            ).scalars()
        )
        return Scene(
            schema_version=row["schema_version"],
            scene_id=row["external_id"],
            sequence_id=self._required_external_for_internal(
                connection, "sequences", row["sequence_id"]
            ),
            order=row["order"],
            title=row["title"],
            summary=row["summary"],
            location_id=self._external_for_internal(connection, "locations", row["location_id"]),
            character_ids=self._ordered_external_ids(
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
            audit=self._audit_from_row(row),
        )

    def _shot_from_row(self, connection: Connection, row: RowMapping) -> Shot:
        take_table = self._t("takes")
        take_ids = list(
            connection.execute(
                select(take_table.c.external_id)
                .where(take_table.c.shot_id == row["id"])
                .order_by(take_table.c.position)
            ).scalars()
        )
        return Shot(
            schema_version=row["schema_version"],
            shot_id=row["external_id"],
            scene_id=self._required_external_for_internal(connection, "scenes", row["scene_id"]),
            order=row["order"],
            time_range=TimeRange(
                start_seconds=float(row["start_seconds"]),
                duration_seconds=float(row["duration_seconds"]),
            ),
            purpose=row["purpose"],
            action=row["action"],
            character_ids=self._ordered_external_ids(
                connection,
                "shot_characters",
                "shot_id",
                row["id"],
                "character_id",
                "characters",
            ),
            location_id=self._external_for_internal(connection, "locations", row["location_id"]),
            prop_ids=self._ordered_external_ids(
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
            first_frame_asset_id=self._external_for_internal(
                connection, "assets", row["first_frame_asset_id"]
            ),
            end_frame_asset_id=self._external_for_internal(
                connection, "assets", row["end_frame_asset_id"]
            ),
            reference_asset_ids=self._ordered_external_ids(
                connection,
                "shot_reference_assets",
                "shot_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            take_ids=[str(value) for value in take_ids],
            selected_take_id=self._external_for_internal(
                connection, "takes", row["selected_take_id"]
            ),
            transition_in=row["transition_in"],
            transition_out=row["transition_out"],
            handles_seconds=float(row["handles_seconds"]),
            generation_notes=list(row["generation_notes"]),
            audit=self._audit_from_row(row),
        )

    def _take_from_row(self, connection: Connection, row: RowMapping) -> Take:
        return Take(
            schema_version=row["schema_version"],
            take_id=row["external_id"],
            shot_id=self._required_external_for_internal(connection, "shots", row["shot_id"]),
            attempt_id=self._external_for_internal(
                connection, "generation_attempts", row["attempt_id"]
            ),
            asset_id=self._external_for_internal(connection, "assets", row["asset_id"]),
            canonical_status=row["canonical_status"],
            continuity_score=(
                float(row["continuity_score"]) if row["continuity_score"] is not None else None
            ),
            qa_record_ids=self._ordered_external_ids(
                connection,
                "take_qa_records",
                "take_id",
                row["id"],
                "qa_record_id",
                "qa_records",
            ),
            audit=self._audit_from_row(row),
        )

    def _job_from_row(
        self,
        connection: Connection,
        row: RowMapping,
        attempt_ids: list[str],
    ) -> Job:
        return Job(
            schema_version=row["schema_version"],
            job_id=row["external_id"],
            project_id=self._required_external_for_internal(
                connection, "projects", row["project_id"]
            ),
            job_type=row["job_type"],
            status=row["status"],
            priority=row["priority"],
            idempotency_key=row["idempotency_key"],
            parent_job_id=self._external_for_internal(connection, "jobs", row["parent_job_id"]),
            dependency_job_ids=self._ordered_external_ids(
                connection,
                "job_dependencies",
                "job_id",
                row["id"],
                "dependency_job_id",
                "jobs",
            ),
            shot_id=self._external_for_internal(connection, "shots", row["shot_id"]),
            content_id=self._external_for_internal(connection, "contents", row["content_id"]),
            attempt_ids=attempt_ids,
            selected_attempt_id=self._external_for_internal(
                connection, "generation_attempts", row["selected_attempt_id"]
            ),
            retry_budget_remaining=row["retry_budget_remaining"],
            blocked_reason=row["blocked_reason"],
            claimed_by=row["claimed_by"],
            lease_expires_at=row["lease_expires_at"],
            audit=self._audit_from_row(row),
        )

    def _attempt_from_row(self, connection: Connection, row: RowMapping) -> GenerationAttempt:
        output_table = self._t("assets")
        output_ids = list(
            connection.execute(
                select(output_table.c.external_id)
                .where(output_table.c.generation_attempt_id == row["id"])
                .order_by(output_table.c.generation_output_position)
            ).scalars()
        )
        return GenerationAttempt(
            schema_version=row["schema_version"],
            attempt_id=row["external_id"],
            job_id=self._required_external_for_internal(connection, "jobs", row["job_id"]),
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
                project_id=self._required_external_for_internal(
                    connection, "projects", row["request_project_id"]
                ),
                shot_id=self._external_for_internal(
                    connection, "shots", row["request_shot_id"]
                ),
                content_id=self._external_for_internal(
                    connection, "contents", row["request_content_id"]
                ),
                prompt_id=row["prompt_id"],
                prompt_version=row["prompt_version"],
                input_asset_ids=self._ordered_external_ids(
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
            free_credits_used=self._decimal_or_none(row["free_credits_used"]),
            paid_cost=self._decimal_or_none(row["paid_cost"]),
            currency=str(row["currency"]),
            qa_record_ids=self._ordered_external_ids(
                connection,
                "generation_attempt_qa_records",
                "attempt_id",
                row["id"],
                "qa_record_id",
                "qa_records",
            ),
        )

    def _character_from_row(self, connection: Connection, row: RowMapping) -> Character:
        lock_table = self._t("character_locks")
        lock_row = connection.execute(
            select(lock_table).where(lock_table.c.character_id == row["id"])
        ).mappings().one_or_none()
        if lock_row is None:
            raise PersistenceShapeError(f"character {row['external_id']} has no lock row")
        return Character(
            schema_version=row["schema_version"],
            character_id=row["external_id"],
            name=row["name"],
            active_version_id=self._required_external_for_internal(
                connection, "character_versions", row["active_version_id"]
            ),
            lock=CharacterLock(
                scope=lock_row["scope"],
                pinned_character_version_id=self._external_for_internal(
                    connection,
                    "character_versions",
                    lock_row["pinned_character_version_id"],
                ),
                pinned_look_id=self._external_for_internal(
                    connection, "character_looks", lock_row["pinned_look_id"]
                ),
                project_id=self._external_for_internal(
                    connection, "projects", lock_row["project_id"]
                ),
                scene_id=self._external_for_internal(
                    connection, "scenes", lock_row["scene_id"]
                ),
            ),
            reusable=row["reusable"],
            rights_record_id=self._external_for_internal(
                connection, "rights_records", row["rights_record_id"]
            ),
            tags=list(row["tags"]),
            audit=self._audit_from_row(row),
        )

    def _character_version_from_row(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> CharacterVersion:
        look_table = self._t("character_looks")
        look_rows = list(
            connection.execute(
                select(look_table)
                .where(look_table.c.character_version_id == row["id"])
                .order_by(look_table.c.position)
            ).mappings()
        )
        looks = [
            CharacterLook(
                look_id=look["external_id"],
                name=look["name"],
                wardrobe=list(look["wardrobe"]),
                accessories=list(look["accessories"]),
                hair=look["hair"],
                eyes=look["eyes"],
                palette=list(look["palette"]),
                expression_defaults=list(look["expression_defaults"]),
                body_notes=list(look["body_notes"]),
                prohibited_mutations=list(look["prohibited_mutations"]),
                reference_asset_ids=self._ordered_external_ids(
                    connection,
                    "character_look_reference_assets",
                    "character_look_id",
                    look["id"],
                    "asset_id",
                    "assets",
                ),
            )
            for look in look_rows
        ]
        return CharacterVersion(
            schema_version=row["schema_version"],
            character_version_id=row["external_id"],
            character_id=self._required_external_for_internal(
                connection, "characters", row["character_id"]
            ),
            version=row["version"],
            display_name=row["display_name"],
            character_type=row["character_type"],
            species=row["species"],
            apparent_age=row["apparent_age"],
            gender_presentation=row["gender_presentation"],
            personality_traits=list(row["personality_traits"]),
            movement_style=row["movement_style"],
            voice_profile_id=self._external_for_internal(
                connection, "voice_profiles", row["voice_profile_id"]
            ),
            looks=looks,
            canonical_reference_asset_ids=self._ordered_external_ids(
                connection,
                "character_version_reference_assets",
                "character_version_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            identity_constraints=list(row["identity_constraints"]),
            status=row["status"],
            audit=self._audit_from_row(row),
        )

    def _world_from_row(self, connection: Connection, row: RowMapping) -> World:
        return World(
            schema_version=row["schema_version"],
            world_id=row["external_id"],
            name=row["name"],
            description=row["description"],
            style_profile_id=self._external_for_internal(
                connection, "style_profiles", row["style_profile_id"]
            ),
            canonical_reference_asset_ids=self._ordered_external_ids(
                connection,
                "world_reference_assets",
                "world_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            rules=list(row["rules"]),
            forbidden_mutations=list(row["forbidden_mutations"]),
            audit=self._audit_from_row(row),
        )

    def _location_from_row(self, connection: Connection, row: RowMapping) -> Location:
        return Location(
            schema_version=row["schema_version"],
            location_id=row["external_id"],
            world_id=self._external_for_internal(connection, "worlds", row["world_id"]),
            name=row["name"],
            description=row["description"],
            canonical_reference_asset_ids=self._ordered_external_ids(
                connection,
                "location_reference_assets",
                "location_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            environment_constraints=list(row["environment_constraints"]),
            audit=self._audit_from_row(row),
        )

    def _prop_from_row(self, connection: Connection, row: RowMapping) -> Prop:
        return Prop(
            schema_version=row["schema_version"],
            prop_id=row["external_id"],
            name=row["name"],
            description=row["description"],
            canonical_reference_asset_ids=self._ordered_external_ids(
                connection,
                "prop_reference_assets",
                "prop_id",
                row["id"],
                "asset_id",
                "assets",
            ),
            identity_constraints=list(row["identity_constraints"]),
            audit=self._audit_from_row(row),
        )

    def _asset_from_row(self, connection: Connection, row: RowMapping) -> Asset:
        return Asset(
            schema_version=row["schema_version"],
            asset_id=row["external_id"],
            project_id=self._external_for_internal(connection, "projects", row["project_id"]),
            kind=row["kind"],
            uri=row["uri"],
            sha256=str(row["sha256"]),
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            duration_seconds=(
                float(row["duration_seconds"]) if row["duration_seconds"] is not None else None
            ),
            width=row["width"],
            height=row["height"],
            parent_asset_ids=self._ordered_external_ids(
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
            generation_attempt_id=self._external_for_internal(
                connection, "generation_attempts", row["generation_attempt_id"]
            ),
            rights_record_id=self._external_for_internal(
                connection, "rights_records", row["rights_record_id"]
            ),
            canonical_status=row["canonical_status"],
            retention_class=row["retention_class"],
            audit=self._audit_from_row(row),
        )

    def _qa_from_row(self, row: RowMapping) -> QARecord:
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

    def _cost_from_row(self, connection: Connection, row: RowMapping) -> CostRecord:
        return CostRecord(
            schema_version=row["schema_version"],
            cost_record_id=row["external_id"],
            project_id=self._required_external_for_internal(
                connection, "projects", row["project_id"]
            ),
            job_id=self._external_for_internal(connection, "jobs", row["job_id"]),
            attempt_id=self._external_for_internal(
                connection, "generation_attempts", row["attempt_id"]
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

    def _rights_from_row(self, row: RowMapping) -> RightsRecord:
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

    def _insert_content_pair(
        self,
        connection: Connection,
        content: Content,
        version: ContentVersion,
        content_uuid: UUID,
        version_uuid: UUID,
    ) -> None:
        if content.project_id is not None:
            raise PersistenceShapeError(
                "standalone legacy content import cannot bind a project not owned by the import"
            )
        values = _Ids(
            {
                "contents": {content.content_id: content_uuid},
                "content_versions": {version.content_version_id: version_uuid},
                "projects": {},
                "characters": {},
                "worlds": {},
                "props": {},
            }
        )
        self._insert(
            connection,
            "contents",
            self._content_values(content, values, project_required=False),
        )
        self._insert(
            connection,
            "content_versions",
            self._content_version_values(version, values),
        )
        self._update_by_id(
            connection,
            "contents",
            content_uuid,
            {"active_version_id": version_uuid},
        )

    def _insert_legacy_import_ledger(
        self,
        connection: Connection,
        imported: LegacyContentImportResult,
        content_id: UUID,
        version_id: UUID,
        imported_at: datetime,
    ) -> None:
        report = imported.report
        self._insert(
            connection,
            "legacy_content_imports",
            {
                "id": uuid4(),
                "mapping_version": report.mapping_version,
                "source_schema_version": report.source_schema_version,
                "source_content_external_id": report.source_content_id,
                "source_fingerprint_sha256": report.source_fingerprint_sha256,
                "import_key": report.import_key,
                "source_run_id": report.source_run_id,
                "source_package_path": report.source_package_path,
                "content_id": content_id,
                "content_version_id": version_id,
                "imported_at": imported_at,
            },
        )

    def _legacy_import_key(
        self,
        connection: Connection,
        mapping_version: str,
        source_content_external_id: str,
    ) -> str | None:
        table = self._t("legacy_content_imports")
        value = connection.execute(
            select(table.c.import_key).where(
                table.c.mapping_version == mapping_version,
                table.c.source_content_external_id == source_content_external_id,
            )
        ).scalar_one_or_none()
        return str(value) if value is not None else None

    def _allocate_ids(self, bundle: ProductionLineageBundle) -> _Ids:
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
        return _Ids({table: {value: uuid4() for value in values} for table, values in groups.items()})

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
                    f"act {act.act_id} sequence_ids must follow canonical Sequence.order"
                )
        for sequence in pb.sequences:
            children = sorted(
                [item for item in pb.scenes if item.sequence_id == sequence.sequence_id],
                key=lambda item: item.order,
            )
            if sequence.scene_ids != [item.scene_id for item in children]:
                raise PersistenceShapeError(
                    f"sequence {sequence.sequence_id} scene_ids must follow canonical Scene.order"
                )
        for scene in pb.scenes:
            children = sorted(
                [item for item in pb.shots if item.scene_id == scene.scene_id],
                key=lambda item: item.order,
            )
            if scene.shot_ids != [item.shot_id for item in children]:
                raise PersistenceShapeError(
                    f"scene {scene.scene_id} shot_ids must follow canonical Shot.order"
                )

        attempts_by_job: dict[str, list[GenerationAttempt]] = {}
        for attempt in bundle.attempts:
            attempts_by_job.setdefault(attempt.job_id, []).append(attempt)
        for job in bundle.jobs:
            expected = [
                item.attempt_id
                for item in sorted(
                    attempts_by_job.get(job.job_id, []), key=lambda item: item.attempt_number
                )
            ]
            if job.attempt_ids != expected:
                raise PersistenceShapeError(
                    f"job {job.job_id} attempt_ids must follow attempt_number order"
                )

        used_locations = {
            value
            for value in [
                *[scene.location_id for scene in pb.scenes],
                *[shot.location_id for shot in pb.shots],
            ]
            if value is not None
        }
        loaded_locations = {item.location_id for item in pb.locations}
        if used_locations != loaded_locations:
            raise PersistenceShapeError(
                "ProjectBundle.locations must be the exact used location closure for lossless M01 reads"
            )

    def _attempt_output_positions(
        self,
        attempts: list[GenerationAttempt],
    ) -> dict[tuple[str, str], int]:
        return {
            (attempt.attempt_id, asset_id): position
            for attempt in attempts
            for position, asset_id in enumerate(attempt.output_asset_ids)
        }

    def _take_positions(self, shots: list[Shot]) -> dict[str, int]:
        return {
            take_id: position
            for shot in shots
            for position, take_id in enumerate(shot.take_ids)
        }

    def _insert_ordered(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        target_column: str,
        target_ids: list[UUID],
    ) -> None:
        for position, target_id in enumerate(target_ids):
            self._insert(
                connection,
                table_name,
                {owner_column: owner_id, target_column: target_id, "position": position},
            )

    def _insert_ordered_external(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        value_column: str,
        values: list[str],
    ) -> None:
        for position, value in enumerate(values):
            self._insert(
                connection,
                table_name,
                {owner_column: owner_id, value_column: value, "position": position},
            )

    def _ordered_target_ids(
        self,
        connection: Connection,
        join_table: str,
        owner_column: str,
        owner_id: UUID,
        target_column: str,
    ) -> list[UUID]:
        table = self._t(join_table)
        return list(
            connection.execute(
                select(table.c[target_column])
                .where(table.c[owner_column] == owner_id)
                .order_by(table.c.position)
            ).scalars()
        )

    def _ordered_external_ids(
        self,
        connection: Connection,
        join_table: str,
        owner_column: str,
        owner_id: UUID,
        target_column: str,
        target_table: str,
    ) -> list[str]:
        ids = self._ordered_target_ids(
            connection, join_table, owner_column, owner_id, target_column
        )
        return [self._required_external_for_internal(connection, target_table, value) for value in ids]

    def _ordered_scalar_values(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        value_column: str,
    ) -> list[str]:
        table = self._t(table_name)
        return [
            str(value)
            for value in connection.execute(
                select(table.c[value_column])
                .where(table.c[owner_column] == owner_id)
                .order_by(table.c.position)
            ).scalars()
        ]

    def _resolve_shared_external(
        self,
        connection: Connection,
        table_name: str,
        external_id: str | None,
    ) -> UUID | None:
        if external_id is None:
            return None
        row = self._row_by_external(connection, table_name, external_id)
        if row is None:
            raise PersistenceReferenceError(
                f"shared reference {table_name}:{external_id} is not persisted"
            )
        return row["id"]

    def _row_by_external(
        self,
        connection: Connection,
        table_name: str,
        external_id: str,
    ) -> RowMapping | None:
        table = self._t(table_name)
        return connection.execute(
            select(table).where(table.c.external_id == external_id)
        ).mappings().one_or_none()

    def _require_row_by_external(
        self,
        connection: Connection,
        table_name: str,
        external_id: str,
    ) -> RowMapping:
        row = self._row_by_external(connection, table_name, external_id)
        if row is None:
            raise PersistenceReferenceError(f"missing {table_name}:{external_id}")
        return row

    def _row_by_id(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID | None,
    ) -> RowMapping | None:
        if internal_id is None:
            return None
        table = self._t(table_name)
        return connection.execute(
            select(table).where(table.c.id == internal_id)
        ).mappings().one_or_none()

    def _require_row_by_id(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID,
    ) -> RowMapping:
        row = self._row_by_id(connection, table_name, internal_id)
        if row is None:
            raise PersistenceReferenceError(f"missing {table_name} internal row {internal_id}")
        return row

    def _external_for_internal(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID | None,
    ) -> str | None:
        row = self._row_by_id(connection, table_name, internal_id)
        return str(row["external_id"]) if row is not None else None

    def _required_external_for_internal(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID,
    ) -> str:
        value = self._external_for_internal(connection, table_name, internal_id)
        if value is None:
            raise PersistenceReferenceError(f"missing external ID for {table_name}:{internal_id}")
        return value

    def _insert(self, connection: Connection, table_name: str, values: dict[str, Any]) -> None:
        connection.execute(insert(self._t(table_name)).values(**values))

    def _update_by_id(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID,
        values: dict[str, Any],
    ) -> None:
        table = self._t(table_name)
        connection.execute(update(table).where(table.c.id == internal_id).values(**values))

    def _t(self, name: str) -> Table:
        try:
            return self._tables[name]
        except KeyError as exc:
            raise PersistenceError(f"unmapped persistence table: {name}") from exc

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

    @staticmethod
    def _audit_from_row(row: RowMapping) -> AuditFields:
        return AuditFields(
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            created_by=row["created_by"],
            revision=row["revision"],
        )

    @staticmethod
    def _decimal_or_none(value: Any) -> Decimal | None:
        return Decimal(value) if value is not None else None

    @staticmethod
    def _canonical_dump(bundle: ProductionLineageBundle) -> dict[str, Any]:
        return bundle.model_dump(mode="json")
