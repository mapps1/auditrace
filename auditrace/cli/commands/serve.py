"""Placeholder serve command for planned v0.4 dashboard."""

from __future__ import annotations

from rich.console import Console

console = Console()


def serve_command() -> None:
    """Inform users that serve is not part of v0.1."""
    console.print("[yellow]auditrace serve is planned for v0.4 and not available in v0.1.[/yellow]")
