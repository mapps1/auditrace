"""NIST AI RMF traceability mapping."""

from __future__ import annotations

from typing import Any

CONTROL_TITLES = {
    "GOVERN": "Govern function evidence (accountability and oversight)",
    "MAP": "Map function evidence (context and intended use)",
    "MEASURE": "Measure function evidence (performance and risk signals)",
    "MANAGE": "Manage function evidence (risk response and review)",
}


def framework_name() -> str:
    return "nist-ai-rmf"


def control_catalog() -> dict[str, str]:
    return dict(CONTROL_TITLES)


def map_event(event: dict[str, object]) -> dict[str, object]:
    mapped = {
        "event_id": event.get("event_id"),
        "timestamp": event.get("timestamp"),
        "framework_tags": event.get("framework_tags", []),
        "risk_level": event.get("risk_level"),
        "metadata": event.get("metadata", {}),
        "human_review_status": event.get("human_review_status"),
        "provider": event.get("provider"),
        "model_id": event.get("model_id"),
    }
    mapped["controls"] = evaluate_controls(mapped)
    return mapped


def evaluate_controls(mapped: dict[str, object]) -> dict[str, bool]:
    tags = mapped.get("framework_tags")
    tag_set = set(tags) if isinstance(tags, list) else set()
    metadata = mapped.get("metadata")
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    review_status = str(mapped.get("human_review_status") or "")

    return {
        "GOVERN": bool(mapped.get("event_id") and mapped.get("timestamp")),
        "MAP": bool(mapped.get("provider") and mapped.get("model_id")),
        "MEASURE": bool(mapped.get("risk_level") or "risk_score" in metadata_dict),
        "MANAGE": bool(
            review_status in {"approved", "overridden", "rejected", "pending"}
            or "manage" in tag_set
        ),
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
        if coverage < 0.85:
            findings.append(
                f"{control_id} coverage is {coverage:.0%}; "
                "expand traceability metadata for this RMF function."
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
