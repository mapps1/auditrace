"""Storage interface that all backends must implement."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from auditrace.core.event import AuditEvent


@runtime_checkable
class AbstractStorage(Protocol):
    """Protocol for append-only audit event storage backends."""

    async def initialize(self) -> None: ...

    async def write(self, event: AuditEvent) -> None: ...

    async def get_last_event(self) -> AuditEvent | None: ...

    async def get_all_events_ordered(self) -> list[AuditEvent]: ...

    async def get_events_since(self, since_iso: str) -> list[AuditEvent]: ...

    async def count_events(self) -> int: ...

    async def close(self) -> None: ...
