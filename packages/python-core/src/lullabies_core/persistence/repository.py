from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import IntegrityError

from ..common import AuditFields
from ..content import Content, ContentVersion
from ..legacy_import import (
    LegacyContentImportResult,
    LegacyContentReconciliation,
    reconcile_legacy_content_import,
)
from ..lineage import ProductionLineageBundle
from ._db import (
    DatabaseMap,
    PersistenceConflictError,
    PersistenceError,
    PersistenceShapeError,
    PersistResult,
)
from ._reader import BundleReader
from ._writer import BundleWriter


class PostgresProductionRepository:
    """Transactional M01 persistence boundary for canonical production aggregates.

    Callers supply an already configured SQLAlchemy Engine. Database UUIDs remain private;
    all public repository identity is expressed through stable external IDs.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.database = DatabaseMap(engine)
        self.reader = BundleReader(self.database)
        self.writer = BundleWriter(self.database)

    def save_bundle(self, bundle: ProductionLineageBundle) -> PersistResult:
        canonical = ProductionLineageBundle.model_validate(bundle.model_dump())
        project_id = canonical.project_bundle.project.project_id
        try:
            with self.engine.begin() as connection:
                existing = self.database.row_by_external(
                    connection,
                    "projects",
                    project_id,
                )
                if existing is not None:
                    restored = self.reader.load(connection, project_id)
                    if self._canonical_dump(restored) == self._canonical_dump(canonical):
                        return PersistResult(action="noop", project_id=project_id)
                    raise PersistenceConflictError(
                        f"project {project_id} already exists with different canonical data"
                    )
                self.writer.write(connection, canonical)
        except PersistenceError:
            raise
        except IntegrityError as exc:
            raise PersistenceConflictError(
                f"database integrity rejected project {project_id}: {exc.orig}"
            ) from exc
        return PersistResult(action="created", project_id=project_id)

    def load_bundle(self, project_id: str) -> ProductionLineageBundle:
        with self.engine.connect() as connection:
            return self.reader.load(connection, project_id)

    def import_legacy_content(
        self,
        imported: LegacyContentImportResult,
        *,
        imported_at: datetime,
    ) -> LegacyContentReconciliation:
        """Persist a WP4 import with deterministic CREATE/NOOP/CONFLICT semantics."""

        self._validate_standalone_legacy_shape(imported)
        try:
            with self.engine.begin() as connection:
                content_row = self.database.row_by_external(
                    connection,
                    "contents",
                    imported.content.content_id,
                )
                version_row = self.database.row_by_external(
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
                    self.reader.content_from_row(connection, content_row)
                    if content_row is not None
                    else None
                )
                existing_version = (
                    self.reader.content_version_from_row(connection, version_row)
                    if version_row is not None
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
                    content_id = uuid4()
                    version_id = uuid4()
                    self._insert_legacy_content_pair(
                        connection,
                        imported.content,
                        imported.content_version,
                        content_id,
                        version_id,
                    )
                else:
                    if content_row is None or version_row is None:
                        raise PersistenceConflictError(
                            "legacy noop requires complete canonical content rows"
                        )
                    content_id = content_row["id"]
                    version_id = version_row["id"]

                if existing_import_key is None:
                    self._insert_legacy_ledger(
                        connection,
                        imported,
                        content_id,
                        version_id,
                        imported_at,
                    )
                return decision
        except PersistenceError:
            raise
        except IntegrityError as exc:
            import_key = imported.report.import_key
            raise PersistenceConflictError(
                f"database integrity rejected legacy import {import_key}: {exc.orig}"
            ) from exc

    def _insert_legacy_content_pair(
        self,
        connection: Connection,
        content: Content,
        version: ContentVersion,
        content_id: UUID,
        version_id: UUID,
    ) -> None:
        self.database.insert(
            connection,
            "contents",
            {
                "id": content_id,
                "external_id": content.content_id,
                "schema_version": content.schema_version,
                "active_version_id": version_id,
                "project_id": None,
                "status": content.status,
                "source_legacy_package_path": content.source_legacy_package_path,
                **self._audit(content.audit),
            },
        )
        self.database.insert(
            connection,
            "content_versions",
            {
                "id": version_id,
                "external_id": version.content_version_id,
                "schema_version": version.schema_version,
                "content_id": content_id,
                "version": version.version,
                "title": version.title,
                "content_format": version.content_format,
                "custom_content_format": version.custom_content_format,
                "language": version.language,
                "target_duration_seconds": version.target_duration_seconds,
                "objective": version.objective.model_dump(mode="json"),
                "premise": version.premise,
                "hook": version.hook,
                "script_or_lyrics": version.script_or_lyrics,
                "structure_map": version.structure_map,
                "pronunciation_notes": version.pronunciation_notes,
                "tags": version.tags,
                "originality_fingerprint": version.originality_fingerprint,
                **self._audit(version.audit),
            },
        )

    def _insert_legacy_ledger(
        self,
        connection: Connection,
        imported: LegacyContentImportResult,
        content_id: UUID,
        version_id: UUID,
        imported_at: datetime,
    ) -> None:
        report = imported.report
        self.database.insert(
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
        table = self.database.table("legacy_content_imports")
        value = connection.execute(
            select(table.c.import_key)
            .where(table.c.mapping_version == mapping_version)
            .where(table.c.source_content_external_id == source_content_external_id)
        ).scalar_one_or_none()
        return str(value) if value is not None else None

    @staticmethod
    def _validate_standalone_legacy_shape(imported: LegacyContentImportResult) -> None:
        content = imported.content
        version = imported.content_version
        if content.project_id is not None:
            raise PersistenceShapeError(
                "standalone legacy import cannot bind an existing project"
            )
        if version.character_ids or version.world_ids or version.prop_ids:
            raise PersistenceShapeError(
                "standalone legacy import cannot fabricate unresolved entity relations"
            )

    @staticmethod
    def _audit(audit: AuditFields) -> dict[str, Any]:
        return {
            "created_at": audit.created_at,
            "updated_at": audit.updated_at,
            "created_by": audit.created_by,
            "revision": audit.revision,
        }

    @staticmethod
    def _canonical_dump(bundle: ProductionLineageBundle) -> dict[str, Any]:
        data = bundle.model_dump(mode="json")
        project_bundle = data["project_bundle"]
        nested_id_fields = {
            "acts": "act_id",
            "sequences": "sequence_id",
            "scenes": "scene_id",
            "shots": "shot_id",
            "takes": "take_id",
            "characters": "character_id",
            "character_versions": "character_version_id",
            "worlds": "world_id",
            "locations": "location_id",
            "props": "prop_id",
        }
        for field, id_field in nested_id_fields.items():
            project_bundle[field] = sorted(
                project_bundle[field],
                key=lambda item, key=id_field: item[key],
            )
        top_id_fields = {
            "jobs": "job_id",
            "attempts": "attempt_id",
            "assets": "asset_id",
            "qa_records": "qa_record_id",
            "cost_records": "cost_record_id",
            "rights_records": "rights_record_id",
        }
        for field, id_field in top_id_fields.items():
            data[field] = sorted(data[field], key=lambda item, key=id_field: item[key])
        return data
