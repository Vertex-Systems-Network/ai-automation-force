from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.engine import Connection, Engine, RowMapping
from sqlalchemy.exc import IntegrityError

from ..common import SCHEMA_VERSION
from ..delivery import (
    DeliveryAuthorization,
    DeliveryAuthorizationError,
    DeliveryAuthorizationKind,
    DeliveryMode,
    DeliverySubject,
    ShareLinkConstraint,
    authorize_delivery,
)
from ._db import PersistenceConflictError, PersistenceNotFoundError, PersistenceReferenceError

ShareLinkPersistAction = Literal["created", "reused", "revoked"]


@dataclass(frozen=True)
class ShareLinkPersistResult:
    action: ShareLinkPersistAction
    share_link_id: str
    use_count: int
    revision: int
    revoked_at: datetime | None


@dataclass(frozen=True)
class ShareLinkAuthorizationResult:
    authorization: DeliveryAuthorization
    share_link_id: str
    use_count: int
    revision: int


class ShareLinkPersistenceConflictError(PersistenceConflictError):
    """Persisted share-link state conflicts with the requested mutation."""


class PostgresShareLinkRepository:
    """Durable share-link authority with atomic use accounting for M03/WP6."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        metadata = MetaData()
        metadata.reflect(bind=engine, schema="core")
        required = {"delivery_share_links", "projects", "assets"}
        missing = [name for name in required if f"core.{name}" not in metadata.tables]
        if missing:
            raise PersistenceReferenceError(
                f"share-link persistence tables are not migrated: {', '.join(sorted(missing))}"
            )
        self.links = metadata.tables["core.delivery_share_links"]
        self.projects = metadata.tables["core.projects"]
        self.assets = metadata.tables["core.assets"]

    def create(
        self,
        link: ShareLinkConstraint,
        *,
        created_at: datetime,
    ) -> ShareLinkPersistResult:
        if link.revoked_at is not None or link.use_count != 0:
            raise ShareLinkPersistenceConflictError(
                "new share link must be unrevoked with use_count 0"
            )
        if created_at >= link.expires_at:
            raise ShareLinkPersistenceConflictError(
                "share link expiry must follow creation time"
            )

        try:
            with self.engine.begin() as connection:
                project = self._require_external(
                    connection,
                    self.projects,
                    link.project_id,
                    "project",
                )
                asset = self._require_external(
                    connection,
                    self.assets,
                    link.asset_id,
                    "asset",
                )
                self._require_same_project(link, project, asset)

                existing_by_id = connection.execute(
                    select(self.links)
                    .where(self.links.c.external_id == link.share_link_id)
                    .with_for_update()
                ).mappings().one_or_none()
                if existing_by_id is not None:
                    restored = self._from_row(connection, existing_by_id)
                    self._assert_creation_semantics(restored, link)
                    return self._result_from_row("reused", existing_by_id)

                existing_by_token = connection.execute(
                    select(self.links)
                    .where(self.links.c.token_sha256 == link.token_sha256)
                    .with_for_update()
                ).mappings().one_or_none()
                if existing_by_token is not None:
                    restored = self._from_row(connection, existing_by_token)
                    if restored.share_link_id != link.share_link_id:
                        raise ShareLinkPersistenceConflictError(
                            "share-link token digest is already bound to another link"
                        )
                    self._assert_creation_semantics(restored, link)
                    return self._result_from_row("reused", existing_by_token)

                connection.execute(
                    insert(self.links).values(
                        id=uuid4(),
                        external_id=link.share_link_id,
                        schema_version=SCHEMA_VERSION,
                        project_id=project["id"],
                        asset_id=asset["id"],
                        token_sha256=link.token_sha256,
                        allow_download=DeliveryMode.DOWNLOAD in link.allowed_modes,
                        allow_stream=DeliveryMode.STREAM in link.allowed_modes,
                        expires_at=link.expires_at,
                        revoked_at=None,
                        max_uses=link.max_uses,
                        use_count=0,
                        created_at=created_at,
                        updated_at=created_at,
                        revision=1,
                    )
                )
                return ShareLinkPersistResult(
                    action="created",
                    share_link_id=link.share_link_id,
                    use_count=0,
                    revision=1,
                    revoked_at=None,
                )
        except (ShareLinkPersistenceConflictError, PersistenceReferenceError):
            raise
        except IntegrityError as exc:
            reconciled = self._reconcile_create_race(link)
            if reconciled is not None:
                return reconciled
            raise ShareLinkPersistenceConflictError(
                f"database rejected share link {link.share_link_id}: {exc.orig}"
            ) from exc

    def load(self, share_link_id: str) -> ShareLinkConstraint:
        with self.engine.connect() as connection:
            row = self._row_by_external(connection, share_link_id)
            if row is None:
                raise PersistenceNotFoundError(
                    f"share link {share_link_id} was not found"
                )
            return self._from_row(connection, row)

    def load_by_token_sha256(self, token_sha256: str) -> ShareLinkConstraint:
        self._validate_token_sha256(token_sha256)
        with self.engine.connect() as connection:
            row = self._row_by_token(connection, token_sha256)
            if row is None:
                raise PersistenceNotFoundError("share link token digest was not found")
            return self._from_row(connection, row)

    def revoke(
        self,
        share_link_id: str,
        *,
        revoked_at: datetime,
    ) -> ShareLinkPersistResult:
        with self.engine.begin() as connection:
            row = self._require_for_update(connection, share_link_id)
            link = self._from_row(connection, row)
            if link.revoked_at is not None:
                if link.revoked_at != revoked_at:
                    raise ShareLinkPersistenceConflictError(
                        "share link is already revoked with different revocation evidence"
                    )
                return self._result_from_row("reused", row)

            created_at = cast(datetime, row["created_at"])
            updated_at = cast(datetime, row["updated_at"])
            if revoked_at < created_at:
                raise ShareLinkPersistenceConflictError(
                    "share-link revocation cannot predate creation"
                )
            if revoked_at < updated_at:
                raise ShareLinkPersistenceConflictError(
                    "share-link revocation cannot predate the latest mutation"
                )
            if revoked_at > link.expires_at:
                raise ShareLinkPersistenceConflictError(
                    "share-link revocation cannot follow expiry"
                )

            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.links)
                .where(self.links.c.id == row["id"])
                .values(
                    revoked_at=revoked_at,
                    updated_at=revoked_at,
                    revision=revision,
                )
            )
            return ShareLinkPersistResult(
                action="revoked",
                share_link_id=share_link_id,
                use_count=link.use_count,
                revision=revision,
                revoked_at=revoked_at,
            )

    def authorize_and_consume(
        self,
        subject: DeliverySubject,
        mode: DeliveryMode,
        *,
        token_sha256: str,
        now: datetime,
    ) -> ShareLinkAuthorizationResult:
        """Authorize one share-link request and consume exactly one use atomically."""

        self._validate_token_sha256(token_sha256)
        with self.engine.begin() as connection:
            row = connection.execute(
                select(self.links)
                .where(self.links.c.token_sha256 == token_sha256)
                .with_for_update()
            ).mappings().one_or_none()
            if row is None:
                raise DeliveryAuthorizationError("share link token is invalid")

            created_at = cast(datetime, row["created_at"])
            updated_at = cast(datetime, row["updated_at"])
            if now < created_at:
                raise DeliveryAuthorizationError("share link is not active yet")
            if now < updated_at:
                raise DeliveryAuthorizationError(
                    "share link request time predates the latest mutation"
                )

            link = self._from_row(connection, row)
            authorization = authorize_delivery(
                subject,
                mode,
                now=now,
                share_link=link,
            )
            if authorization.kind is not DeliveryAuthorizationKind.SHARE_LINK:
                raise DeliveryAuthorizationError(
                    "share-link consumption requires share-link authorization"
                )

            next_use_count = link.use_count + 1
            revision = int(row["revision"]) + 1
            connection.execute(
                update(self.links)
                .where(self.links.c.id == row["id"])
                .values(
                    use_count=next_use_count,
                    updated_at=now,
                    revision=revision,
                )
            )
            return ShareLinkAuthorizationResult(
                authorization=authorization,
                share_link_id=link.share_link_id,
                use_count=next_use_count,
                revision=revision,
            )

    def _reconcile_create_race(
        self,
        link: ShareLinkConstraint,
    ) -> ShareLinkPersistResult | None:
        with self.engine.connect() as connection:
            existing_by_id = self._row_by_external(connection, link.share_link_id)
            if existing_by_id is not None:
                restored = self._from_row(connection, existing_by_id)
                self._assert_creation_semantics(restored, link)
                return self._result_from_row("reused", existing_by_id)

            existing_by_token = self._row_by_token(connection, link.token_sha256)
            if existing_by_token is None:
                return None
            restored = self._from_row(connection, existing_by_token)
            if restored.share_link_id != link.share_link_id:
                raise ShareLinkPersistenceConflictError(
                    "share-link token digest is already bound to another link"
                )
            self._assert_creation_semantics(restored, link)
            return self._result_from_row("reused", existing_by_token)

    @staticmethod
    def _assert_creation_semantics(
        persisted: ShareLinkConstraint,
        requested: ShareLinkConstraint,
    ) -> None:
        if not PostgresShareLinkRepository._same_creation_semantics(
            persisted,
            requested,
        ):
            raise ShareLinkPersistenceConflictError(
                "share link is already bound to different creation semantics"
            )

    @staticmethod
    def _same_creation_semantics(
        left: ShareLinkConstraint,
        right: ShareLinkConstraint,
    ) -> bool:
        return (
            left.project_id == right.project_id
            and left.asset_id == right.asset_id
            and left.token_sha256 == right.token_sha256
            and set(left.allowed_modes) == set(right.allowed_modes)
            and left.expires_at == right.expires_at
            and left.max_uses == right.max_uses
        )

    @staticmethod
    def _require_same_project(
        link: ShareLinkConstraint,
        project: RowMapping,
        asset: RowMapping,
    ) -> None:
        if asset["project_id"] != project["id"]:
            raise ShareLinkPersistenceConflictError(
                f"asset {link.asset_id} is outside share-link project {link.project_id}"
            )

    def _from_row(
        self,
        connection: Connection,
        row: RowMapping,
    ) -> ShareLinkConstraint:
        persisted_schema_version = int(row["schema_version"])
        if persisted_schema_version != SCHEMA_VERSION:
            raise PersistenceReferenceError(
                "unsupported share-link schema version "
                f"{persisted_schema_version}; expected {SCHEMA_VERSION}"
            )

        allowed_modes: list[DeliveryMode] = []
        if bool(row["allow_download"]):
            allowed_modes.append(DeliveryMode.DOWNLOAD)
        if bool(row["allow_stream"]):
            allowed_modes.append(DeliveryMode.STREAM)

        return ShareLinkConstraint(
            share_link_id=str(row["external_id"]),
            project_id=self._external_for_internal(
                connection,
                self.projects,
                cast(UUID, row["project_id"]),
                "project",
            ),
            asset_id=self._external_for_internal(
                connection,
                self.assets,
                cast(UUID, row["asset_id"]),
                "asset",
            ),
            token_sha256=str(row["token_sha256"]),
            allowed_modes=allowed_modes,
            expires_at=row["expires_at"],
            revoked_at=row["revoked_at"],
            max_uses=(int(row["max_uses"]) if row["max_uses"] is not None else None),
            use_count=int(row["use_count"]),
        )

    def _row_by_external(
        self,
        connection: Connection,
        share_link_id: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.links).where(self.links.c.external_id == share_link_id)
        ).mappings().one_or_none()

    def _row_by_token(
        self,
        connection: Connection,
        token_sha256: str,
    ) -> RowMapping | None:
        return connection.execute(
            select(self.links).where(self.links.c.token_sha256 == token_sha256)
        ).mappings().one_or_none()

    def _require_for_update(
        self,
        connection: Connection,
        share_link_id: str,
    ) -> RowMapping:
        row = connection.execute(
            select(self.links)
            .where(self.links.c.external_id == share_link_id)
            .with_for_update()
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceNotFoundError(
                f"share link {share_link_id} was not found"
            )
        return row

    @staticmethod
    def _require_external(
        connection: Connection,
        table: Table,
        external_id: str,
        label: str,
    ) -> RowMapping:
        row = connection.execute(
            select(table).where(table.c.external_id == external_id)
        ).mappings().one_or_none()
        if row is None:
            raise PersistenceReferenceError(f"missing {label}:{external_id}")
        return row

    @staticmethod
    def _external_for_internal(
        connection: Connection,
        table: Table,
        internal_id: UUID,
        label: str,
    ) -> str:
        value = connection.execute(
            select(table.c.external_id).where(table.c.id == internal_id)
        ).scalar_one_or_none()
        if value is None:
            raise PersistenceReferenceError(
                f"missing {label} external identity for {internal_id}"
            )
        return str(value)

    @staticmethod
    def _validate_token_sha256(token_sha256: str) -> None:
        if len(token_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in token_sha256
        ):
            raise ValueError("token_sha256 must be exactly 64 lowercase hexadecimal characters")

    @staticmethod
    def _result_from_row(
        action: ShareLinkPersistAction,
        row: RowMapping,
    ) -> ShareLinkPersistResult:
        return ShareLinkPersistResult(
            action=action,
            share_link_id=str(row["external_id"]),
            use_count=int(row["use_count"]),
            revision=int(row["revision"]),
            revoked_at=cast(datetime | None, row["revoked_at"]),
        )
