from typer.testing import CliRunner

from auditrace.cli.main import app


def test_cli_serve_and_export_and_log(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    runner.invoke(app, ["init", "--project-name", "demo"])

    serve_result = runner.invoke(app, ["serve"])
    assert serve_result.exit_code == 0

    log_result = runner.invoke(app, ["log", "--provider", "p", "--model-id", "m"])
    assert log_result.exit_code == 0

    export_result = runner.invoke(app, ["export", "--output", "events.jsonl"])
    assert export_result.exit_code == 0
