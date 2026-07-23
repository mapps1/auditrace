"""Typer CLI entrypoint."""

from __future__ import annotations

import typer

from auditrace.cli.commands.export import export_command
from auditrace.cli.commands.init import init_command
from auditrace.cli.commands.log import log_command
from auditrace.cli.commands.report import report_command
from auditrace.cli.commands.serve import serve_command
from auditrace.cli.commands.verify import verify_command

app = typer.Typer(help="Tamper-evident AI audit trails.")
app.command("init")(init_command)
app.command("log")(log_command)
app.command("verify")(verify_command)
app.command("report")(report_command)
app.command("export")(export_command)
app.command("serve")(serve_command)


if __name__ == "__main__":
    app()
