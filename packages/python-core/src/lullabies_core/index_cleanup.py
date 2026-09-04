from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import AwareDatetime, Field, model_validator

from .common import AssetId, ProjectId, StrictModel
from .deletion_execution import DeletionPropagationExecutionResult


class IndexCleanupPlanningError(RuntimeError):
    """Vector/index cleanup work cannot be represented safely."""


class IndexCleanupReceiptError(RuntimeError):
    """Cleanup receipts do not prove the exact approved cleanup set."""


class IndexCleanupTargetKind(StrEnum):
    VECTOR_RECORD = "vector-record"
    SEARCH_DOCUMENT = "search-document"


class IndexCleanupTarget(StrictModel):
    """Provider-neutral identity of one vector/index record that should be removed."""

    kind: IndexCleanupTargetKind
    namespace: str = Field(min_length=1, max_length=200)
    record_key: str = Field(min_length=1, max_length=512)

    @model_validator(mode="after")
    def validate_identity(self) -> IndexCleanupTarget:
        for name, value in (("namespace", self.namespace), ("record_key", self.record_key)):
            if value != value.strip():
                raise ValueError(f"index cleanup {name} must not contain surrounding whitespace")
            if any(ord(character) < 32 for character in value):
                raise ValueError(f"index cleanup {name} must not contain control characters")
        return self

    def identity(self) -> tuple[str, str, str]:
        return (self.kind.value, self.namespace, self.record_key)


class IndexCleanupHook(StrictModel):
    """One deterministic, idempotent cleanup instruction for a future executor."""

    target: IndexCleanupTarget
    idempotency_key: str = Field(pattern=r"^index-cleanup:[a-f0-9]{64}$")


class AssetIndexCleanupPlan(StrictModel):
    """Auditable provider-neutral cleanup hooks bound to completed hard deletion."""

    asset_id: AssetId
    project_id: ProjectId
    deletion_plan_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    deletion_final_revision: int = Field(ge=2)
    planned_at: AwareDatetime
    hooks: list[IndexCleanupHook] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_hooks(self) -> AssetIndexCleanupPlan:
        identities = [hook.target.identity() for hook in self.hooks]
        if identities != sorted(identities):
            raise ValueError("index cleanup hooks must be ordered by canonical target identity")
        if len(identities) != len(set(identities)):
            raise ValueError("index cleanup hooks must not repeat a canonical target")
        for hook in self.hooks:
            expected = index_cleanup_idempotency_key(
                project_id=self.project_id,
                asset_id=self.asset_id,
                deletion_plan_fingerprint=self.deletion_plan_fingerprint,
                deletion_final_revision=self.deletion_final_revision,
                target=hook.target,
            )
            if hook.idempotency_key != expected:
                raise ValueError("index cleanup idempotency key does not match plan binding")
        return self

    def fingerprint(self) -> str:
        payload = self.model_dump(mode="json", exclude={"planned_at"})
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class IndexCleanupReceiptStatus(StrEnum):
    DELETED = "deleted"
    ALREADY_ABSENT = "already-absent"


class IndexCleanupReceipt(StrictModel):
    idempotency_key: str = Field(pattern=r"^index-cleanup:[a-f0-9]{64}$")
    status: IndexCleanupReceiptStatus


class IndexCleanupCompletion(StrictModel):
    plan_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    receipts: list[IndexCleanupReceipt]


def index_cleanup_idempotency_key(
    *,
    project_id: str,
    asset_id: str,
    deletion_plan_fingerprint: str,
    deletion_final_revision: int,
    target: IndexCleanupTarget,
) -> str:
    payload = {
        "asset_id": asset_id,
        "deletion_final_revision": deletion_final_revision,
        "deletion_plan_fingerprint": deletion_plan_fingerprint,
        "kind": target.kind.value,
        "namespace": target.namespace,
        "project_id": project_id,
        "record_key": target.record_key,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"index-cleanup:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def build_index_cleanup_plan(
    deletion: DeletionPropagationExecutionResult,
    *,
    targets: list[IndexCleanupTarget],
    planned_at: AwareDatetime,
) -> AssetIndexCleanupPlan:
    """Create explicit cleanup hooks after hard-delete propagation has succeeded.

    This function causes no provider mutation. The deletion result is the authority for
    project, asset, approved-plan fingerprint, and final lifecycle revision. A future
    executor can use each deterministic idempotency key and report either ``deleted`` or
    ``already-absent`` without widening this core contract to provider credentials.
    """

    identities = [target.identity() for target in targets]
    if len(identities) != len(set(identities)):
        raise IndexCleanupPlanningError("duplicate vector/index cleanup target")

    ordered = sorted(targets, key=lambda target: target.identity())
    hooks = [
        IndexCleanupHook(
            target=target,
            idempotency_key=index_cleanup_idempotency_key(
                project_id=deletion.project_id,
                asset_id=deletion.asset_id,
                deletion_plan_fingerprint=deletion.plan_fingerprint,
                deletion_final_revision=deletion.final_revision,
                target=target,
            ),
        )
        for target in ordered
    ]
    return AssetIndexCleanupPlan(
        asset_id=deletion.asset_id,
        project_id=deletion.project_id,
        deletion_plan_fingerprint=deletion.plan_fingerprint,
        deletion_final_revision=deletion.final_revision,
        planned_at=planned_at,
        hooks=hooks,
    )


def validate_index_cleanup_receipts(
    plan: AssetIndexCleanupPlan,
    receipts: list[IndexCleanupReceipt],
) -> IndexCleanupCompletion:
    """Accept only an exact, duplicate-free terminal receipt set for the approved hooks."""

    expected = [hook.idempotency_key for hook in plan.hooks]
    observed = [receipt.idempotency_key for receipt in receipts]
    if len(observed) != len(set(observed)):
        raise IndexCleanupReceiptError("index cleanup receipts repeat an idempotency key")
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        unexpected = sorted(set(observed) - set(expected))
        raise IndexCleanupReceiptError(
            f"index cleanup receipt set mismatch; missing={missing}; unexpected={unexpected}"
        )
    ordered = sorted(receipts, key=lambda receipt: receipt.idempotency_key)
    return IndexCleanupCompletion(plan_fingerprint=plan.fingerprint(), receipts=ordered)
