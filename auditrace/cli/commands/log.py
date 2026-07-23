"""Manual event logging command."""

from __future__ import annotations

import asyncio
import json
from typing import Annotated

import typer
from rich.console import Console

from auditrace import get_chain_writer
from auditrace.core.event import AuditEvent

console = Console()


def log_command(
    provider: Annotated[str, typer.Option(help="AI provider name")] = "manual",
    model_id: Annotated[str, typer.Option(help="Model identifier")] = "manual",
    user_id: Annotated[str | None, typer.Option(help="User identifier")] = None,
    input_text: Annotated[str | None, typer.Option(help="Input text (hashed by default)")] = None,
    output_text: Annotated[str | None, typer.Option(help="Output text (hashed by default)")] = None,
    metadata: Annotated[str | None, typer.Option(help="JSON metadata")] = None,
) -> None:
    """Write a manual event into the audit chain."""
    writer = get_chain_writer()
    try:
        parsed_metadata = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid metadata JSON:[/red] {exc}")
        raise typer.Exit(2) from exc

    if not isinstance(parsed_metadata, dict):
        console.print("[red]Metadata must be a JSON object.[/red]")
        raise typer.Exit(2)

    event = AuditEvent(
        provider=provider,
        model_id=model_id,
        user_id=user_id,
        input_hash=AuditEvent.hash_content(input_text) if input_text else None,
        output_hash=AuditEvent.hash_content(output_text) if output_text else None,
        metadata=parsed_metadata,
    )

    async def run_write() -> None:
        await writer.storage.initialize()
        await writer.write(event)
        await writer.storage.close()

    asyncio.run(run_write())
    console.print(f"[green]Logged event {event.event_id}[/green]")
