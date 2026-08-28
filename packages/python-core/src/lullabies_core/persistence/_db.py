from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping

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
class IdMap:
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


REQUIRED_TABLES = {
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
    "style_profiles",
    "take_qa_records",
    "takes",
    "timeline_marker_assets",
    "timeline_track_items",
    "timeline_tracks",
    "timelines",
    "voice_profiles",
    "world_reference_assets",
    "worlds",
}


class DatabaseMap:
    """Reflected M01 schema with stable helper operations."""

    def __init__(self, engine: Engine) -> None:
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        self.tables: dict[str, Table] = {}
        for name in REQUIRED_TABLES:
            key = f"core.{name}"
            if key not in metadata.tables:
                raise PersistenceError(f"required migrated table is missing: {key}")
            self.tables[name] = metadata.tables[key]

    def table(self, name: str) -> Table:
        try:
            return self.tables[name]
        except KeyError as exc:
            raise PersistenceError(f"unmapped persistence table: {name}") from exc

    def insert(self, connection: Connection, table_name: str, values: dict[str, Any]) -> None:
        connection.execute(insert(self.table(table_name)).values(**values))

    def update_by_id(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID,
        values: dict[str, Any],
    ) -> None:
        table = self.table(table_name)
        connection.execute(update(table).where(table.c.id == internal_id).values(**values))

    def row_by_external(
        self,
        connection: Connection,
        table_name: str,
        external_id: str,
    ) -> RowMapping | None:
        table = self.table(table_name)
        return connection.execute(
            select(table).where(table.c.external_id == external_id)
        ).mappings().one_or_none()

    def require_row_by_external(
        self,
        connection: Connection,
        table_name: str,
        external_id: str,
    ) -> RowMapping:
        row = self.row_by_external(connection, table_name, external_id)
        if row is None:
            raise PersistenceReferenceError(f"missing {table_name}:{external_id}")
        return row

    def row_by_id(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID | None,
    ) -> RowMapping | None:
        if internal_id is None:
            return None
        table = self.table(table_name)
        return connection.execute(
            select(table).where(table.c.id == internal_id)
        ).mappings().one_or_none()

    def require_row_by_id(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID,
    ) -> RowMapping:
        row = self.row_by_id(connection, table_name, internal_id)
        if row is None:
            raise PersistenceReferenceError(f"missing {table_name} internal row {internal_id}")
        return row

    def external_for_internal(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID | None,
    ) -> str | None:
        row = self.row_by_id(connection, table_name, internal_id)
        return str(row["external_id"]) if row is not None else None

    def require_external_for_internal(
        self,
        connection: Connection,
        table_name: str,
        internal_id: UUID,
    ) -> str:
        value = self.external_for_internal(connection, table_name, internal_id)
        if value is None:
            raise PersistenceReferenceError(
                f"missing external ID for {table_name}:{internal_id}"
            )
        return value

    def resolve_shared_external(
        self,
        connection: Connection,
        table_name: str,
        external_id: str | None,
    ) -> UUID | None:
        if external_id is None:
            return None
        row = self.row_by_external(connection, table_name, external_id)
        if row is None:
            raise PersistenceReferenceError(
                f"shared reference {table_name}:{external_id} is not persisted"
            )
        return row["id"]

    def insert_ordered(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        target_column: str,
        target_ids: list[UUID],
    ) -> None:
        for position, target_id in enumerate(target_ids):
            self.insert(
                connection,
                table_name,
                {
                    owner_column: owner_id,
                    target_column: target_id,
                    "position": position,
                },
            )

    def insert_ordered_scalars(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        value_column: str,
        values: list[str],
    ) -> None:
        for position, value in enumerate(values):
            self.insert(
                connection,
                table_name,
                {
                    owner_column: owner_id,
                    value_column: value,
                    "position": position,
                },
            )

    def ordered_target_ids(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        target_column: str,
    ) -> list[UUID]:
        table = self.table(table_name)
        return list(
            connection.execute(
                select(table.c[target_column])
                .where(table.c[owner_column] == owner_id)
                .order_by(table.c.position)
            ).scalars()
        )

    def ordered_external_ids(
        self,
        connection: Connection,
        join_table: str,
        owner_column: str,
        owner_id: UUID,
        target_column: str,
        target_table: str,
    ) -> list[str]:
        internal_ids = self.ordered_target_ids(
            connection,
            join_table,
            owner_column,
            owner_id,
            target_column,
        )
        return [
            self.require_external_for_internal(connection, target_table, internal_id)
            for internal_id in internal_ids
        ]

    def ordered_scalar_values(
        self,
        connection: Connection,
        table_name: str,
        owner_column: str,
        owner_id: UUID,
        value_column: str,
    ) -> list[str]:
        table = self.table(table_name)
        values = connection.execute(
            select(table.c[value_column])
            .where(table.c[owner_column] == owner_id)
            .order_by(table.c.position)
        ).scalars()
        return [str(value) for value in values]
