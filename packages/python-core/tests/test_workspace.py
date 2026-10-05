from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from lullabies_core.workspace import Workspace


def test_workspace_accepts_stable_slug_and_identity() -> None:
    now = datetime.now(UTC)
    workspace = Workspace(
        workspace_id="WSP-000017",
        external_id="workspace-bootstrap-legacy",
        name="Legacy Bootstrap Workspace",
        slug="legacy-bootstrap",
        audit={"created_at": now, "updated_at": now},
    )

    assert workspace.workspace_id == "WSP-000017"
    assert workspace.slug == "legacy-bootstrap"


def test_workspace_rejects_invalid_slug() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        Workspace(
            workspace_id="WSP-000017",
            external_id="workspace-bootstrap-legacy",
            name="Legacy Bootstrap Workspace",
            slug="Legacy Bootstrap",
            audit={"created_at": now, "updated_at": now},
        )
