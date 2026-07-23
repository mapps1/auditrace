"""Storage backends and backend selection helpers."""

from __future__ import annotations

from auditrace.core.config import Config, StorageBackend
from auditrace.storage.base import AbstractStorage
from auditrace.storage.file import FileStorage
from auditrace.storage.postgres import PostgresStorage
from auditrace.storage.s3 import S3Storage
from auditrace.storage.sqlite import SQLiteStorage


def create_storage(config: Config) -> AbstractStorage:
    """Create a storage backend from resolved runtime config."""
    if config.backend == StorageBackend.SQLITE:
        return SQLiteStorage(db_path=config.sqlite_path)
    if config.backend == StorageBackend.FILE:
        return FileStorage(file_path=config.file_path)
    if config.backend == StorageBackend.POSTGRES:
        return PostgresStorage(dsn=config.postgres_dsn)
    if config.backend == StorageBackend.S3:
        return S3Storage(bucket=config.s3_bucket, prefix=config.s3_prefix)
    raise ValueError(f"Unsupported backend: {config.backend}")


__all__ = [
    "AbstractStorage",
    "SQLiteStorage",
    "FileStorage",
    "PostgresStorage",
    "S3Storage",
    "create_storage",
]
