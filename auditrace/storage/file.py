"""Append-only JSONL file backend."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from auditrace.core.event import AuditEvent

DEFAULT_FILE_PATH = Path.home() / ".auditrace" / "events.jsonl"


class FileStorage:
    """Append-only JSONL storage backend with deterministic ordering by insertion."""

    def __init__(self, file_path: Path = DEFAULT_FILE_PATH) -> None:
        self.file_path = file_path

    async def initialize(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    async def write(self, event: AuditEvent) -> None:
        line = json.dumps(event.model_dump(mode="json"), sort_keys=True)
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")

    async def get_last_event(self) -> AuditEvent | None:
        events = await self.get_all_events_ordered()
        return events[-1] if events else None

    async def get_all_events_ordered(self) -> list[AuditEvent]:
        if not self.file_path.exists():
            return []

        events: list[AuditEvent] = []
        for line in self.file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            events.append(AuditEvent(**payload))
        return events

    async def get_events_since(self, since_iso: str) -> list[AuditEvent]:
        since = _parse_iso_datetime(since_iso)
        events = await self.get_all_events_ordered()
        return [event for event in events if event.timestamp >= since]

    async def count_events(self) -> int:
        events = await self.get_all_events_ordered()
        return len(events)

    async def close(self) -> None:
        return None


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
