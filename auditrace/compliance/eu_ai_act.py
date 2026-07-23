"""EU AI Act Article 12 mapping."""

from __future__ import annotations

from typing import Any

CONTROL_TITLES = {
    "A12-TS": "Timestamp captured for each operation",
    "A12-OPID": "Unique operation identifier",
    "A12-IOD": "Input/output references recorded",
    "A12-HUM": "Human oversight event traceability",
    "A12-VERS": "System/model version evidence",
}


def framework_name() -> str:
    return "eu-ai-act"


def control_catalog() -> dict[str, str]:
    return dict(CONTROL_TITLES)


def map_event(event: dict[str, object]) -> dict[str, object]:
    mapped = {
        "event_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "provider": event.get("provider"),
        "model_id": event.get("model_id"),
        "system_version": event.get("system_version"),
        "user_id": event.get("user_id"),
        "input_hash": event.get("input_hash"),
        "output_hash": event.get("output_hash"),
        "human_review_status": event.get("human_review_status"),
        "human_reviewer_id": event.get("human_reviewer_id"),
        "framework_tags": event.get("framework_tags", []),
    }
    mapped["controls"] = evaluate_controls(mapped)
    return mapped


def evaluate_controls(mapped: dict[str, object]) -> dict[str, bool]:
    has_input_or_output = bool(mapped.get("input_hash") or mapped.get("output_hash"))
    review_status = str(mapped.get("human_review_status") or "")
    has_review_trace = review_status in {"approved", "overridden", "rejected", "not_required"}
    return {
        "A12-TS": bool(mapped.get("timestamp")),
        "A12-OPID": bool(mapped.get("event_id")),
        "A12-IOD": has_input_or_output,
        "A12-HUM": has_review_trace,
        "A12-VERS": bool(mapped.get("system_version") or mapped.get("model_id")),
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
                "expected at least 95% for high-risk AI logs."
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
