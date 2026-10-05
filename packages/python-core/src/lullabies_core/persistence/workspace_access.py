from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.engine import Connection, RowMapping

from ._db import (
    DatabaseMap,
    PersistenceNotFoundError,
    PersistenceShapeError,
)

WorkspaceRootTable = Literal[
    "characters",
    "worlds",
    "locations",
    "props",
    "style_profiles",
    "voice_profiles",
]


class PostgresWorkspaceRepository:
    """Fail-closed workspace-scoped access to reusable root resources."""

    def __init__(self, database: DatabaseMap) -> None:
        self.database = database

    def get_workspace(
        self,
        connection: Connection,
        workspace_id: UUID,
    ) -> RowMapping:
        row = self.database.row_by_id(connection, "workspaces", workspace_id)
        if row is None:
            raise PersistenceNotFoundError(
                f"workspace {workspace_id} was not found"
            )
        return row

    def get_root(
        self,
        connection: Connection,
        table_name: WorkspaceRootTable,
        external_id: str,
        workspace_id: UUID,
    ) -> RowMapping:
        row = self.database.row_by_external_in_workspace(
            connection,
            table_name,
            external_id,
            workspace_id,
        )
        if row is None:
            raise PersistenceNotFoundError(
                f"{table_name} {external_id} was not found in workspace {workspace_id}"
            )
        return row

    def get_character_version(
        self,
        connection: Connection,
        external_id: str,
        workspace_id: UUID,
    ) -> RowMapping:
        """Resolve a character version only through its workspace-owned parent."""
        characters = self.database.table("characters")
        versions = self.database.table("character_versions")
        row = connection.execute(
            select(versions)
            .join(characters, versions.c.character_id == characters.c.id)
            .where(versions.c.external_id == external_id)
            .where(characters.c.workspace_id == workspace_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(
                f"character version {external_id} was not found in workspace {workspace_id}"
            )
        return row

    def get_character_look(
        self,
        connection: Connection,
        external_id: str,
        workspace_id: UUID,
    ) -> RowMapping:
        """Resolve a look only through its workspace-owned version and character."""
        characters = self.database.table("characters")
        versions = self.database.table("character_versions")
        looks = self.database.table("character_looks")
        row = connection.execute(
            select(looks)
            .join(versions, looks.c.character_version_id == versions.c.id)
            .join(characters, versions.c.character_id == characters.c.id)
            .where(looks.c.external_id == external_id)
            .where(characters.c.workspace_id == workspace_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(
                f"character look {external_id} was not found in workspace {workspace_id}"
            )
        return row

    def create_root(
        self,
        connection: Connection,
        table_name: WorkspaceRootTable,
        workspace_id: UUID,
        values: dict[str, object],
    ) -> RowMapping:
        """Create a root only after enforcing its canonical workspace scope."""
        self.get_workspace(connection, workspace_id)
        supplied_workspace = values.get("workspace_id")
        if supplied_workspace is not None and supplied_workspace != workspace_id:
            raise PersistenceShapeError(
                f"{table_name} workspace does not match requested workspace"
            )
        create_values = dict(values)
        create_values["workspace_id"] = workspace_id
        self.database.insert(connection, table_name, create_values)
        external_id = create_values.get("external_id")
        if not isinstance(external_id, str):
            raise PersistenceShapeError(
                f"{table_name} root creation requires an external_id"
            )
        return self.get_root(connection, table_name, external_id, workspace_id)

    def update_root(
        self,
        connection: Connection,
        table_name: WorkspaceRootTable,
        external_id: str,
        workspace_id: UUID,
        values: dict[str, object],
    ) -> RowMapping:
        """Update a root only after resolving it inside the requested workspace."""
        row = self.get_root(connection, table_name, external_id, workspace_id)
        supplied_workspace = values.get("workspace_id")
        if supplied_workspace is not None and supplied_workspace != workspace_id:
            raise PersistenceShapeError(
                f"{table_name} workspace does not match requested workspace"
            )
        update_values = dict(values)
        update_values.pop("id", None)
        update_values.pop("external_id", None)
        update_values["workspace_id"] = workspace_id
        self.database.update_by_id(connection, table_name, row["id"], update_values)
        return self.get_root(connection, table_name, external_id, workspace_id)

    def list_roots(
        self,
        connection: Connection,
        table_name: WorkspaceRootTable,
        workspace_id: UUID,
    ) -> list[RowMapping]:
        table = self.database.table(table_name)
        return list(
            connection.execute(
                select(table)
                .where(table.c.workspace_id == workspace_id)
                .order_by(table.c.external_id)
            ).mappings()
        )
