from typer.testing import CliRunner

from auditrace.cli.main import app


def test_cli_verify_runs(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    runner.invoke(app, ["init", "--project-name", "demo"])
    result = runner.invoke(app, ["verify"])
    assert result.exit_code == 0
