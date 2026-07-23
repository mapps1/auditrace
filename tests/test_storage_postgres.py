import pytest

from auditrace.storage.postgres import PostgresStorage


def test_postgres_requires_dsn() -> None:
    storage = PostgresStorage(dsn=None)
    with pytest.raises(RuntimeError):
        storage._get_conn()
