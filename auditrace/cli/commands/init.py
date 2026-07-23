"""Initialize Auditrace in the current project."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from auditrace.core.signer import Signer

console = Console()

DEFAULT_CONFIG = """\
# auditrace.toml — Auditrace configuration
[project]
name = "{project_name}"
risk_level = "limited"

[storage]
backend = "sqlite"
sqlite_path = "~/.auditrace/auditrace.db"

[logging]
store_content = false
default_framework_tags = ["eu_ai_act"]

[report]
output_dir = "./auditrace-reports"
include_public_key = true
retention_reminder_days = 180
"""


def init_command(
    storage: Annotated[
        str, typer.Option(help="Storage backend: sqlite, postgres, s3, file")
    ] = "sqlite",
    project_name: Annotated[str, typer.Option(help="Project name for reports and config")] = "",
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite existing config")] = False,
) -> None:
    """Initialize local keys and auditrace.toml."""
    config_path = Path("auditrace.toml")
    if config_path.exists() and not force:
        console.print("[yellow]auditrace.toml already exists. Use --force to overwrite.[/yellow]")
        raise typer.Exit(1)

    if storage not in {"sqlite", "postgres", "s3", "file"}:
        console.print("[red]Invalid storage backend.[/red]")
        raise typer.Exit(1)

    if not project_name:
        project_name = Path.cwd().name

    console.print("[bold blue]Generating Ed25519 signing keypair...[/bold blue]")
    signer = Signer()
    signer.generate_keypair()
    console.print("  ✅ Private key: ~/.auditrace/signing_key.pem")
    console.print("  ✅ Public key: ~/.auditrace/verify_key.pem")

    console.print("[bold blue]Writing auditrace.toml...[/bold blue]")
    config = DEFAULT_CONFIG.format(project_name=project_name).replace(
        'backend = "sqlite"', f'backend = "{storage}"'
    )
    config_path.write_text(config, encoding="utf-8")
    console.print("  ✅ Config written to auditrace.toml")

    quickstart = """\
from auditrace import wrap_anthropic_client, get_chain_writer
import anthropic

client = wrap_anthropic_client(
    anthropic.Anthropic(),
    get_chain_writer(),
    user_id="your_user_id",
    framework_tags=["eu_ai_act"],
)
"""
    console.print(
        Panel(
            Syntax(quickstart, "python", theme="monokai"),
            title="[bold green]Quickstart[/bold green]",
        )
    )
    console.print("[bold green]Auditrace initialized.[/bold green]")
