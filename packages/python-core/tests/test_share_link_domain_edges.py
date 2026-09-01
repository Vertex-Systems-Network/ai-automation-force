from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from ai_automation_force_core import DeliveryMode, ShareLinkConstraint

NOW = datetime(2026, 9, 1, 20, 30, tzinfo=UTC)


def test_share_link_constraint_rejects_duplicate_modes_and_usage_overflow() -> None:
    with pytest.raises(ValidationError, match="duplicates"):
        ShareLinkConstraint(
            share_link_id="SHARE-006301",
            project_id="PRJ-006301",
            asset_id="AST-006301",
            token_sha256="d" * 64,
            allowed_modes=[DeliveryMode.STREAM, DeliveryMode.STREAM],
            expires_at=NOW + timedelta(minutes=5),
        )

    with pytest.raises(ValidationError, match="use_count"):
        ShareLinkConstraint(
            share_link_id="SHARE-006302",
            project_id="PRJ-006301",
            asset_id="AST-006301",
            token_sha256="e" * 64,
            allowed_modes=[DeliveryMode.DOWNLOAD],
            expires_at=NOW + timedelta(minutes=5),
            max_uses=1,
            use_count=2,
        )
