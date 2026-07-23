"""Generate compliance evidence reports."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from auditrace.reports.generator import generate_report

console = Console()

VALID_FRAMEWORKS = ["eu-ai-act", "soc2", "hipaa", "nist-ai-rmf", "all"]
VALID_FORMATS = ["pdf", "html", "json"]


def report_command(
    framework: Annotated[
        str, typer.Option("--framework", "-f", help="Compliance framework")
    ] = "eu-ai-act",
    since: Annotated[str | None, typer.Option(help="Start date ISO format")] = None,
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
    format: Annotated[str, typer.Option(help="Output format: pdf, html, json")] = "pdf",
) -> None:
    """Generate a report for the selected framework."""
    if framework not in VALID_FRAMEWORKS:
        console.print(f"[red]Unknown framework: {framework}[/red]")
        console.print(f"Valid frameworks: {', '.join(VALID_FRAMEWORKS)}")
        raise typer.Exit(1)
    if format not in VALID_FORMATS:
        console.print(f"[red]Unknown format: {format}[/red]")
        console.print(f"Valid formats: {', '.join(VALID_FORMATS)}")
        raise typer.Exit(1)

    try:
        report_path = generate_report(
            framework=framework,
            output_format=format,
            since=since,
            output=output,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(2) from exc
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(2) from exc
    console.print(f"[green]Report generated: {report_path}[/green]")
