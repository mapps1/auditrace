"""Compliance mapping implementations and framework registry."""

from __future__ import annotations

from collections.abc import Callable
from types import ModuleType
from typing import Any, cast

from auditrace.compliance import eu_ai_act, hipaa, nist_ai_rmf, soc2

FrameworkModule = ModuleType

FRAMEWORKS: dict[str, FrameworkModule] = {
    eu_ai_act.framework_name(): eu_ai_act,
    soc2.framework_name(): soc2,
    hipaa.framework_name(): hipaa,
    nist_ai_rmf.framework_name(): nist_ai_rmf,
}


def get_framework(name: str) -> FrameworkModule:
    """Resolve a framework module by CLI name."""
    if name not in FRAMEWORKS:
        valid = ", ".join(sorted(FRAMEWORKS))
        raise ValueError(f"Unknown framework '{name}'. Valid frameworks: {valid}")
    return FRAMEWORKS[name]


def summarize_framework(name: str, events: list[dict[str, object]]) -> dict[str, Any]:
    """Map and summarize events for one framework."""
    framework = get_framework(name)
    mapper = _require_callable(framework, "map_event")
    summarizer = _require_callable(framework, "summarize")
    mapped_events = [mapper(event) for event in events]
    summary = summarizer(mapped_events)
    if not isinstance(summary, dict):
        raise RuntimeError(f"Framework '{name}' returned non-dict summary")
    summary["mapped_events"] = mapped_events
    return cast(dict[str, Any], summary)


def summarize_all(events: list[dict[str, object]]) -> dict[str, Any]:
    """Summarize all supported frameworks for one event corpus."""
    per_framework = {
        framework_name: summarize_framework(framework_name, events)
        for framework_name in sorted(FRAMEWORKS)
    }
    total_findings = sum(len(item.get("findings", [])) for item in per_framework.values())
    return {
        "framework": "all",
        "frameworks": per_framework,
        "total_findings": total_findings,
    }


def _require_callable(module: ModuleType, name: str) -> Callable[[Any], Any]:
    value = getattr(module, name, None)
    if not callable(value):
        raise RuntimeError(f"Framework module '{module.__name__}' is missing callable '{name}'")
    return cast(Callable[[Any], Any], value)


__all__ = ["FRAMEWORKS", "get_framework", "summarize_all", "summarize_framework"]
