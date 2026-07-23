from auditrace.compliance.soc2 import map_event, summarize


def test_map_event_soc2() -> None:
    out = map_event(
        {
            "event_id": "e",
            "user_id": "u",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "provider": "p",
            "model_id": "m",
            "metadata": {"change_ticket": "INC-1"},
        }
    )
    assert out["event_id"] == "e"
    assert out["controls"]["CC6.1"]


def test_summarize_soc2() -> None:
    mapped = [
        map_event(
            {
                "event_id": "e",
                "user_id": "u",
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        )
    ]
    summary = summarize(mapped)
    assert summary["framework"] == "soc2"
    assert len(summary["controls"]) == 4
