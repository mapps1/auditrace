"""Compliance framework protocol and shared result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class AbstractFramework(Protocol):
    """Protocol for framework-specific mapping and scoring."""

    def framework_name(self) -> str: ...

    def map_event(self, event: dict[str, object]) -> dict[str, object]: ...


@dataclass(frozen=True)
class ControlScore:
    """Aggregated scoring information for a single control."""

    control_id: str
    title: str
    pass_count: int
    total_count: int

    @property
    def coverage(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.pass_count / self.total_count
