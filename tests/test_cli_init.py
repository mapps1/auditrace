from typer.testing import CliRunner

from auditrace.cli.main import app


def test_cli_init(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--project-name", "demo"])
    assert result.exit_code == 0
    assert (tmp_path / "auditrace.toml").exists()
