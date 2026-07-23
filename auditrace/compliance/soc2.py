"""SOC 2 CC6.x mapping."""

from __future__ import annotations

from typing import Any

CONTROL_TITLES = {
    "CC6.1": "Logical access activity is attributable to an identity",
    "CC6.2": "Privileged usage is traceable with role/context",
    "CC6.6": "Changes and operational activity are logged",
    "CC6.8": "Security-relevant metadata is retained",
}


def framework_name() -> str:
    return "soc2"


def control_catalog() -> dict[str, str]:
    return dict(CONTROL_TITLES)


def map_event(event: dict[str, object]) -> dict[str, object]:
    mapped = {
        "event_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "user_id": event.get("user_id"),
        "user_role": event.get("user_role"),
        "model_id": event.get("model_id"),
        "provider": event.get("provider"),
        "session_id": event.get("session_id"),
        "total_token_count": event.get("total_token_count"),
        "metadata": event.get("metadata", {}),
    }
    mapped["controls"] = evaluate_controls(mapped)
    return mapped


def evaluate_controls(mapped: dict[str, object]) -> dict[str, bool]:
    metadata = mapped.get("metadata")
    has_metadata = isinstance(metadata, dict) and len(metadata) > 0
    return {
        "CC6.1": bool(mapped.get("user_id") and mapped.get("timestamp") and mapped.get("event_id")),
        "CC6.2": bool(mapped.get("user_role") or mapped.get("session_id")),
        "CC6.6": bool(mapped.get("provider") and mapped.get("model_id")),
        "CC6.8": bool(has_metadata or mapped.get("total_token_count") is not None),
    }


def summarize(mapped_events: list[dict[str, object]]) -> dict[str, Any]:
    control_ids = list(CONTROL_TITLES)
    totals = {control_id: 0 for control_id in control_ids}
    findings: list[str] = []

    for mapped in mapped_events:
        controls = mapped.get("controls", {})
        if isinstance(controls, dict):
            for control_id in control_ids:
                if bool(controls.get(control_id)):
                    totals[control_id] += 1

    event_count = len(mapped_events)
    controls_summary = []
    for control_id in control_ids:
        pass_count = totals[control_id]
        coverage = (pass_count / event_count) if event_count else 0.0
        if coverage < 0.9:
            findings.append(
                f"{control_id} coverage is {coverage:.0%}; "
                "raise identity and metadata logging completeness."
            )
        controls_summary.append(
            {
                "control_id": control_id,
                "title": CONTROL_TITLES[control_id],
                "pass_count": pass_count,
                "total_count": event_count,
                "coverage": coverage,
            }
        )

    return {
        "framework": framework_name(),
        "controls": controls_summary,
        "findings": findings,
    }
