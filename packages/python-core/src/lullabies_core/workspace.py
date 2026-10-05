from __future__ import annotations

from pydantic import Field

from .common import SCHEMA_VERSION, AuditFields, SchemaVersion, StrictModel, WorkspaceId


class Workspace(StrictModel):
    """Stable tenant boundary used by owner-scoped repositories.

    This is intentionally not an authentication or RBAC model. Membership,
    identity and permission evaluation remain outside M04-WP1A.
    """

    schema_version: SchemaVersion = SCHEMA_VERSION
    workspace_id: WorkspaceId
    external_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=160)
    slug: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    audit: AuditFields
