from auditrace.compliance.hipaa import map_event, summarize


def test_map_event_hipaa() -> None:
    out = map_event(
        {
            "event_id": "e",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "user_id": "u",
            "input_hash": "h",
            "event_hash": "eh",
            "signature": "sig",
        }
    )
    assert out["input_hash"] == "h"
    assert out["controls"]["164.312(b)-C"]


def test_summarize_hipaa() -> None:
    mapped = [
        map_event(
            {
                "event_id": "e",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "user_id": "u",
            }
        )
    ]
    summary = summarize(mapped)
    assert summary["framework"] == "hipaa"
    assert len(summary["controls"]) == 4
