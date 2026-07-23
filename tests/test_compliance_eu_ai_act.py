from auditrace.compliance.eu_ai_act import map_event, summarize


def test_map_event_eu_ai_act() -> None:
    out = map_event(
        {
            "event_id": "e",
            "provider": "p",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "model_id": "m",
            "input_hash": "h",
            "human_review_status": "approved",
        }
    )
    assert out["event_id"] == "e"
    assert out["controls"]["A12-OPID"]


def test_summarize_eu_ai_act() -> None:
    mapped = [
        map_event(
            {
                "event_id": "a",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "provider": "p",
                "model_id": "m",
                "input_hash": "h",
                "human_review_status": "approved",
            }
        )
    ]
    summary = summarize(mapped)
    assert summary["framework"] == "eu-ai-act"
    assert len(summary["controls"]) == 5
