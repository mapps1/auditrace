"""PostgreSQL storage backend."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from auditrace.core.event import AuditEvent

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL,
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
    human_review_status TEXT NOT NULL,
    human_reviewer_id TEXT,
    human_review_timestamp TIMESTAMPTZ,
    human_review_notes TEXT,
    risk_level TEXT,
    framework_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    previous_hash TEXT,
    event_hash TEXT NOT NULL,
    signature TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_session_id ON audit_events(session_id);
"""


class PostgresStorage:
    """PostgreSQL storage backend using psycopg2."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.getenv("AUDITRACE_POSTGRES_DSN")
        self._conn: Any = None

    def _get_conn(self) -> Any:
        if self._conn is None:
            if not self.dsn:
                raise RuntimeError(
                    "Postgres backend requires storage.postgres_dsn in auditrace.toml "
                    "or AUDITRACE_POSTGRES_DSN environment variable"
                )
            try:
                import psycopg2
                import psycopg2.extras
            except Exception as exc:  # pragma: no cover - depends on optional dependency
                raise RuntimeError(
                    "Postgres backend requires 'auditrace[postgres]' extra"
                ) from exc

            self._conn = psycopg2.connect(self.dsn)
            self._conn.autocommit = False
        return self._conn

    async def initialize(self) -> None:
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        conn.commit()

    async def write(self, event: AuditEvent) -> None:
        conn = self._get_conn()
        payload = event.model_dump()
        payload["timestamp"] = event.timestamp
        payload["framework_tags"] = json.dumps(event.framework_tags)
        payload["metadata"] = json.dumps(event.metadata)
        payload["human_review_status"] = event.human_review_status.value

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit_events (
                    event_id, timestamp, session_id, provider, model_id, system_version,
                    user_id, user_role, input_hash, output_hash, input_content, output_content,
                    input_token_count, output_token_count, total_token_count,
                    human_review_status, human_reviewer_id, human_review_timestamp,
                    human_review_notes, risk_level, framework_tags, metadata,
                    previous_hash, event_hash, signature
                ) VALUES (
                    %(event_id)s, %(timestamp)s, %(session_id)s, %(provider)s, %(model_id)s,
                    %(system_version)s, %(user_id)s, %(user_role)s, %(input_hash)s,
                    %(output_hash)s, %(input_content)s, %(output_content)s,
                    %(input_token_count)s, %(output_token_count)s, %(total_token_count)s,
                    %(human_review_status)s, %(human_reviewer_id)s, %(human_review_timestamp)s,
                    %(human_review_notes)s, %(risk_level)s, %(framework_tags)s::jsonb,
                    %(metadata)s::jsonb, %(previous_hash)s, %(event_hash)s, %(signature)s
                )
                """,
                payload,
            )
        conn.commit()

    async def get_last_event(self) -> AuditEvent | None:
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
        return _row_to_event(cur, row) if row else None

    async def get_all_events_ordered(self) -> list[AuditEvent]:
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM audit_events ORDER BY id ASC")
            rows = cur.fetchall()
            return [_row_to_event(cur, row) for row in rows]

    async def get_events_since(self, since_iso: str) -> list[AuditEvent]:
        conn = self._get_conn()
        since = _parse_iso_datetime(since_iso)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM audit_events WHERE timestamp >= %s ORDER BY id ASC",
                (since,),
            )
            rows = cur.fetchall()
            return [_row_to_event(cur, row) for row in rows]

    async def count_events(self) -> int:
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM audit_events")
            row = cur.fetchone()
        return int(row[0]) if row else 0

    async def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def _row_to_event(cursor: Any, row: Any) -> AuditEvent:
    columns = [col.name for col in cursor.description]
    data = dict(zip(columns, row, strict=False))
    data["framework_tags"] = _ensure_list(data.get("framework_tags"))
    data["metadata"] = _ensure_dict(data.get("metadata"))
    return AuditEvent(**data)


def _ensure_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    return []


def _ensure_dict(value: Any) -> dict[str, object]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return {str(k): parsed[k] for k in parsed}
    return {}


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
