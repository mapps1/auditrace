from datetime import datetime

from auditrace.core.event import AuditEvent


def test_hash_content_is_deterministic() -> None:
    assert AuditEvent.hash_content("abc") == AuditEvent.hash_content("abc")


def test_event_hash_and_canonical_json() -> None:
    event = AuditEvent(provider="p", model_id="m", input_hash="i", output_hash="o")
    payload = event.canonical_json()
    assert '"provider": "p"' in payload
    assert len(event.compute_hash()) == 64


def test_event_timestamp_string_conversion() -> None:
    event = AuditEvent(provider="p", model_id="m", timestamp=datetime.now().isoformat())
    assert event.timestamp.tzinfo is not None
