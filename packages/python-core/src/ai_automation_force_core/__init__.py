"""Canonical public import surface for AI Automation Force core contracts.

The underlying `lullabies_core` module remains temporarily available as a compatibility
namespace for pre-M01 repository code. New consumers should import this package.
"""

from lullabies_core import *  # noqa: F403
from lullabies_core import __all__ as _legacy_all
from lullabies_core.persistence import PostgresStorageObjectRepository, StorageObjectPersistResult
from lullabies_core.storage import (
    FilesystemStorageAdapter,
    StorageAdapter,
    StorageBackend,
    StorageBlobStat,
    StorageConflictError,
    StorageError,
    StorageIntegrityError,
    StorageNotFoundError,
    StorageObject,
    StorageObjectId,
    StorageWriteResult,
    build_object_key,
    sha256_bytes,
    storage_object_from_write,
    validate_object_key,
)

__all__ = [
    *_legacy_all,
    "FilesystemStorageAdapter",
    "PostgresStorageObjectRepository",
    "StorageAdapter",
    "StorageBackend",
    "StorageBlobStat",
    "StorageConflictError",
    "StorageError",
    "StorageIntegrityError",
    "StorageNotFoundError",
    "StorageObject",
    "StorageObjectId",
    "StorageObjectPersistResult",
    "StorageWriteResult",
    "build_object_key",
    "sha256_bytes",
    "storage_object_from_write",
    "validate_object_key",
]
