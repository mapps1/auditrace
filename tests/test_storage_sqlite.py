from auditrace.core.event import AuditEvent
from auditrace.storage.sqlite import SQLiteStorage


async def test_sqlite_storage_roundtrip(tmp_path) -> None:
    storage = SQLiteStorage(db_path=tmp_path / "audit.db")
    await storage.initialize()

    event = AuditEvent(
        provider="openai",
        model_id="gpt",
        input_hash="in",
        output_hash="out",
        event_hash="evt_hash",
        signature="sig",
    )
    await storage.write(event)

    last = await storage.get_last_event()
    assert last is not None
    assert last.event_id == event.event_id

    events = await storage.get_all_events_ordered()
    assert len(events) == 1

    count = await storage.count_events()
    assert count == 1

    await storage.close()
