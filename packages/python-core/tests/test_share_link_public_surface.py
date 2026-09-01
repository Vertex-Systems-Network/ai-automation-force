from ai_automation_force_core import (
    PostgresShareLinkRepository,
    ShareLinkAuthorizationResult,
    ShareLinkPersistenceConflictError,
    ShareLinkPersistResult,
)


def test_share_link_persistence_contracts_are_public() -> None:
    assert PostgresShareLinkRepository.__name__ == "PostgresShareLinkRepository"
    assert ShareLinkAuthorizationResult.__name__ == "ShareLinkAuthorizationResult"
    assert ShareLinkPersistenceConflictError.__name__ == "ShareLinkPersistenceConflictError"
    assert ShareLinkPersistResult.__name__ == "ShareLinkPersistResult"
