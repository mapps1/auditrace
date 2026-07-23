"""HIPAA 164.312(b) mapping."""

from __future__ import annotations

from typing import Any

CONTROL_TITLES = {
    "164.312(b)-A": "System activity captures actor identity",
    "164.312(b)-B": "Activity records include date/time and operation",
    "164.312(b)-C": "Accessed ePHI references are auditable via content hashes",
    "164.312(b)-D": "Audit records include tamper-evident integrity fields",
}


def framework_name() -> str:
    return "hipaa"


def control_catalog() -> dict[str, str]:
    return dict(CONTROL_TITLES)


def map_event(event: dict[str, object]) -> dict[str, object]:
    mapped = {
        "event_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "user_id": event.get("user_id"),
        "provider": event.get("provider"),
        "model_id": event.get("model_id"),
        "input_hash": event.get("input_hash"),
        "output_hash": event.get("output_hash"),
        "previous_hash": event.get("previous_hash"),
        "event_hash": event.get("event_hash"),
        "signature": event.get("signature"),
    }
    mapped["controls"] = evaluate_controls(mapped)
    return mapped


def evaluate_controls(mapped: dict[str, object]) -> dict[str, bool]:
    return {
        "164.312(b)-A": bool(mapped.get("user_id")),
        "164.312(b)-B": bool(mapped.get("timestamp") and mapped.get("event_id")),
        "164.312(b)-C": bool(mapped.get("input_hash") or mapped.get("output_hash")),
        "164.312(b)-D": bool(mapped.get("event_hash") and mapped.get("signature")),
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
        if coverage < 0.95:
            findings.append(
                f"{control_id} coverage is {coverage:.0%}; "
                "HIPAA audit controls require consistent logging."
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
