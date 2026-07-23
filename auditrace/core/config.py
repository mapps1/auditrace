"""Configuration loading for Auditrace."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


class StorageBackend(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    S3 = "s3"
    FILE = "file"


@dataclass
class Config:
    """Resolved runtime config with secure defaults."""

    backend: StorageBackend = StorageBackend.SQLITE
    sqlite_path: Path = field(default_factory=lambda: Path.home() / ".auditrace" / "auditrace.db")
    file_path: Path = field(default_factory=lambda: Path.home() / ".auditrace" / "events.jsonl")
    postgres_dsn: str | None = None
    s3_bucket: str | None = None
    s3_prefix: str = "events"
    store_content: bool = False
    default_framework_tags: list[str] = field(default_factory=list)
    report_output_dir: Path = field(default_factory=lambda: Path("auditrace-reports"))
    report_retention_days: int = 180

    @classmethod
    def load(cls, config_path: Path | None = None) -> Config:
        """Load config from auditrace.toml, falling back to defaults."""
        default = cls()
        path = config_path or Path("auditrace.toml")
        if not path.exists():
            return default

        data = tomllib.loads(path.read_text(encoding="utf-8"))
        storage = _as_dict(data.get("storage"))
        logging = _as_dict(data.get("logging"))
        report = _as_dict(data.get("report"))

        backend_raw = storage.get("backend", default.backend.value)
        backend = StorageBackend(backend_raw)

        sqlite_raw = storage.get("sqlite_path", str(default.sqlite_path))
        sqlite_path = Path(sqlite_raw).expanduser()
        file_raw = storage.get("file_path", str(default.file_path))
        file_path = Path(file_raw).expanduser()

        postgres_dsn = storage.get("postgres_dsn")
        postgres_dsn_value = str(postgres_dsn) if isinstance(postgres_dsn, str) else None

        s3_bucket = storage.get("s3_bucket")
        s3_bucket_value = str(s3_bucket) if isinstance(s3_bucket, str) else None
        s3_prefix_raw = storage.get("s3_prefix", default.s3_prefix)
        s3_prefix = str(s3_prefix_raw)

        tags_raw = logging.get("default_framework_tags", [])
        tags = [str(tag) for tag in tags_raw] if isinstance(tags_raw, list) else []

        output_dir_raw = report.get("output_dir", str(default.report_output_dir))
        output_dir = Path(str(output_dir_raw)).expanduser()
        retention_raw = report.get("retention_reminder_days", default.report_retention_days)
        retention_days = _as_positive_int(retention_raw, default.report_retention_days)

        return cls(
            backend=backend,
            sqlite_path=sqlite_path,
            file_path=file_path,
            postgres_dsn=postgres_dsn_value,
            s3_bucket=s3_bucket_value,
            s3_prefix=s3_prefix,
            store_content=bool(logging.get("store_content", False)),
            default_framework_tags=tags,
            report_output_dir=output_dir,
            report_retention_days=retention_days,
        )


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_positive_int(value: Any, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback
