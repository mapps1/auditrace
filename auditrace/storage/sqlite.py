"""SQLite storage backend (default, zero-infrastructure option)."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from auditrace.core.event import AuditEvent

DEFAULT_DB_PATH = Path.home() / ".auditrace" / "auditrace.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL,
    session_id TEXT,
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    system_version TEXT,
    user_id TEXT,
    user_role TEXT,
    input_hash TEXT,
    output_hash TEXT,
    input_content TEXT,
    output_content TEXT,
    input_token_count INTEGER,
    output_token_count INTEGER,
    total_token_count INTEGER,
    human_review_status TEXT NOT NULL DEFAULT 'not_required',
    human_reviewer_id TEXT,
    human_review_timestamp TEXT,
    human_review_notes TEXT,
    risk_level TEXT,
    framework_tags TEXT NOT NULL DEFAULT '[]',
    metadata TEXT NOT NULL DEFAULT '{}',
    previous_hash TEXT,
    event_hash TEXT NOT NULL,
    signature TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_session_id ON audit_events(session_id);
CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id);
CREATE INDEX IF NOT EXISTS idx_model_id ON audit_events(model_id);
"""

INSERT_EVENT_SQL = """
INSERT INTO audit_events (
    event_id,
    timestamp,
    session_id,
    provider,
    model_id,
    system_version,
    user_id,
    user_role,
    input_hash,
    output_hash,
    input_content,
    output_content,
    input_token_count,
    output_token_count,
    total_token_count,
    human_review_status,
    human_reviewer_id,
    human_review_timestamp,
    human_review_notes,
    risk_level,
    framework_tags,
    metadata,
    previous_hash,
    event_hash,
    signature
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
"""


class SQLiteStorage:
    """Append-only sqlite-backed storage for AuditEvent records."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    async def initialize(self) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.executescript(CREATE_TABLE_SQL)
            conn.commit()

    async def write(self, event: AuditEvent) -> None:
        row = event.model_dump()
        row["timestamp"] = event.timestamp.isoformat()
        row["framework_tags"] = json.dumps(event.framework_tags)
        row["metadata"] = json.dumps(event.metadata)
        if event.human_review_timestamp:
            row["human_review_timestamp"] = event.human_review_timestamp.isoformat()
        row["human_review_status"] = event.human_review_status.value

        values = [
            row.get("event_id"),
            row.get("timestamp"),
            row.get("session_id"),
            row.get("provider"),
            row.get("model_id"),
            row.get("system_version"),
            row.get("user_id"),
            row.get("user_role"),
            row.get("input_hash"),
            row.get("output_hash"),
            row.get("input_content"),
            row.get("output_content"),
            row.get("input_token_count"),
            row.get("output_token_count"),
            row.get("total_token_count"),
            row.get("human_review_status"),
            row.get("human_reviewer_id"),
            row.get("human_review_timestamp"),
            row.get("human_review_notes"),
            row.get("risk_level"),
            row.get("framework_tags"),
            row.get("metadata"),
            row.get("previous_hash"),
            row.get("event_hash"),
            row.get("signature"),
        ]

        with self._lock:
            conn = self._get_conn()
            conn.execute(INSERT_EVENT_SQL, values)
            conn.commit()

    async def get_last_event(self) -> AuditEvent | None:
        row = (
            self._get_conn()
            .execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 1")
            .fetchone()
        )
        return _row_to_event(row) if row else None

    async def get_all_events_ordered(self) -> list[AuditEvent]:
        rows = self._get_conn().execute("SELECT * FROM audit_events ORDER BY id ASC").fetchall()
        return [_row_to_event(row) for row in rows]

    async def get_events_since(self, since_iso: str) -> list[AuditEvent]:
        rows = (
            self._get_conn()
            .execute(
                "SELECT * FROM audit_events WHERE timestamp >= ? ORDER BY id ASC",
                (since_iso,),
            )
            .fetchall()
        )
        return [_row_to_event(row) for row in rows]

    async def count_events(self) -> int:
        row = self._get_conn().execute("SELECT COUNT(*) AS c FROM audit_events").fetchone()
        return int(row["c"]) if row else 0

    async def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


def _row_to_event(row: sqlite3.Row) -> AuditEvent:
    data = dict(row)
    data["framework_tags"] = json.loads(data.get("framework_tags") or "[]")
    data["metadata"] = json.loads(data.get("metadata") or "{}")
    return AuditEvent(**data)
