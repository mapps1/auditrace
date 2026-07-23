import asyncio

from typer.testing import CliRunner

from auditrace.cli.main import app
from auditrace.core.event import AuditEvent
from auditrace.storage.sqlite import SQLiteStorage


def test_cli_report_generates_json(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    runner.invoke(app, ["init", "--project-name", "demo"])

    db = SQLiteStorage(db_path=(tmp_path / ".auditrace" / "auditrace.db"))

    async def seed() -> None:
        await db.initialize()
        await db.write(AuditEvent(provider="p", model_id="m", event_hash="h", signature="s"))
        await db.close()

    asyncio.run(seed())

    result = runner.invoke(app, ["report", "--format", "json"])
    assert result.exit_code == 0


def test_cli_report_invalid_since(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    runner.invoke(app, ["init", "--project-name", "demo"])
    result = runner.invoke(app, ["report", "--format", "json", "--since", "bad-date"])
    assert result.exit_code == 2
