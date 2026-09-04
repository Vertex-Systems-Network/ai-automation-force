from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pydantic import AwareDatetime, Field, model_validator

from .common import (
    SCHEMA_VERSION,
    AuditFields,
    ProjectId,
    SchemaVersion,
    StorageObjectId,
    StrictModel,
)
from .storage import (
    StorageAdapter,
    StorageIntegrityError,
    StorageObject,
    build_object_key,
    sha256_bytes,
    storage_object_from_write,
)

EXPORT_STAGING_NAMESPACE = "exports/staging"
EXPORT_STAGING_LIFECYCLE_CLASS = "export-staging"


class ExportStagingError(RuntimeError):
    """Base error for bounded private export staging."""


class ExportStagingConflictError(ExportStagingError):
    """Requested staging identity conflicts with current source or target state."""


def build_export_staging_key(project_id: str, storage_object_id: str) -> str:
    return build_object_key(
        EXPORT_STAGING_NAMESPACE,
        storage_object_id,
        project_id=project_id,
    )


class ExportStagingObject(StrictModel):
    schema_version: SchemaVersion = SCHEMA_VERSION
    export_staging_id: str = Field(pattern=r"^EXS-[0-9]{6,20}$")
    project_id: ProjectId
    source_storage_object_id: StorageObjectId
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    staging_storage_object_id: StorageObjectId
    staging_object_key: str = Field(min_length=1, max_length=1024)
    expires_at: AwareDatetime
    audit: AuditFields

    @model_validator(mode="after")
    def validate_contract(self) -> ExportStagingObject:
        if self.source_storage_object_id == self.staging_storage_object_id:
            raise ValueError("export staging source and target storage identities must differ")
        expected_key = build_export_staging_key(
            self.project_id,
            self.staging_storage_object_id,
        )
        if self.staging_object_key != expected_key:
            raise ValueError("export staging object_key must equal the canonical private staging key")
        if self.expires_at <= self.audit.created_at:
            raise ValueError("export staging expiry must be after creation")
        return self


@dataclass(frozen=True)
class PreparedExportStaging:
    record: ExportStagingObject
    storage_object: StorageObject


def prepare_export_staging(
    *,
    source: StorageObject,
    export_staging_id: str,
    staging_storage_object_id: str,
    expires_at: datetime,
    audit: AuditFields,
    storage: StorageAdapter,
) -> PreparedExportStaging:
    if source.project_id is None:
        raise ExportStagingConflictError("export source must belong to a project")
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("export staging expiry must be timezone-aware")
    if expires_at <= audit.created_at:
        raise ValueError("export staging expiry must be after creation")
    if source.backend != storage.backend:
        raise ExportStagingConflictError("export source backend does not match staging adapter")

    live = storage.stat(source.object_key)
    if live.backend != source.backend or live.bucket != source.bucket:
        raise ExportStagingConflictError("export source physical location changed")
    if live.object_key != source.object_key or live.size_bytes != source.size_bytes:
        raise ExportStagingConflictError("export source size or object key changed")
    if live.sha256 is None:
        raise StorageIntegrityError("export source lacks canonical live SHA-256 evidence")
    if live.sha256 != source.sha256:
        raise StorageIntegrityError("export source live SHA-256 does not match canonical metadata")

    source_bytes = storage.get_bytes(source.object_key)
    observed_digest = sha256_bytes(source_bytes)
    if observed_digest != source.sha256 or len(source_bytes) != source.size_bytes:
        raise StorageIntegrityError("export source bytes do not match canonical metadata")

    target_key = build_export_staging_key(source.project_id, staging_storage_object_id)
    write = storage.put_bytes(target_key, source_bytes, mime_type=source.mime_type)
    if (
        write.backend != source.backend
        or write.bucket != source.bucket
        or write.object_key != target_key
        or write.sha256 != source.sha256
        or write.size_bytes != source.size_bytes
    ):
        raise StorageIntegrityError("export staging write does not preserve source identity")

    staging_storage = storage_object_from_write(
        staging_storage_object_id,
        write,
        audit=audit,
        project_id=source.project_id,
        original_filename=source.original_filename,
        lifecycle_class=EXPORT_STAGING_LIFECYCLE_CLASS,
    )
    record = ExportStagingObject(
        export_staging_id=export_staging_id,
        project_id=source.project_id,
        source_storage_object_id=source.storage_object_id,
        source_sha256=source.sha256,
        staging_storage_object_id=staging_storage_object_id,
        staging_object_key=target_key,
        expires_at=expires_at,
        audit=audit,
    )
    return PreparedExportStaging(record=record, storage_object=staging_storage)
