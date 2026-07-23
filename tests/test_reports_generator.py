import asyncio

import pytest

from auditrace.core.event import AuditEvent
from auditrace.reports.generator import generate_report
from auditrace.storage.sqlite import SQLiteStorage


def test_report_generator_json_and_html(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    db = SQLiteStorage(db_path=(tmp_path / ".auditrace" / "auditrace.db"))

    async def seed() -> None:
        await db.initialize()
        await db.write(AuditEvent(provider="p", model_id="m", event_hash="h", signature="s"))
        await db.close()

    asyncio.run(seed())

    json_path = generate_report("eu-ai-act", "json")
    assert json_path.exists()
    payload = json_path.read_text(encoding="utf-8")
    assert "integrity" in payload
    assert "summary" in payload

    html_path = generate_report("all", "html")
    assert html_path.exists()


def test_report_generator_pdf_error_without_extra(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    with pytest.raises(RuntimeError):
        generate_report("eu-ai-act", "pdf")


def test_report_generator_rejects_invalid_since(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    with pytest.raises(ValueError):
        generate_report("eu-ai-act", "json", since="not-a-date")
