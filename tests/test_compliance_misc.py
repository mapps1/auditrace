from auditrace.compliance import summarize_all
from auditrace.compliance.base import AbstractFramework
from auditrace.compliance.nist_ai_rmf import map_event, summarize


class _DummyFramework(AbstractFramework):
    def framework_name(self) -> str:
        return "dummy"

    def map_event(self, event: dict[str, object]) -> dict[str, object]:
        return event


def test_base_protocol_and_nist_mapper() -> None:
    dummy = _DummyFramework()
    assert dummy.framework_name() == "dummy"
    mapped = map_event({"event_id": "e", "risk_level": "limited"})
    assert mapped["event_id"] == "e"


def test_nist_summary_and_all_summary() -> None:
    mapped = [
        map_event(
            {
                "event_id": "e",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "provider": "p",
                "model_id": "m",
            }
        )
    ]
    nist_summary = summarize(mapped)
    assert nist_summary["framework"] == "nist-ai-rmf"

    all_summary = summarize_all([{"event_id": "e", "provider": "p", "model_id": "m"}])
    assert all_summary["framework"] == "all"
