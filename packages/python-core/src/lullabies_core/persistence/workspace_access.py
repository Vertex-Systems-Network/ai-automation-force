from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.engine import Connection, RowMapping

from ._db import DatabaseMap, PersistenceNotFoundError

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
