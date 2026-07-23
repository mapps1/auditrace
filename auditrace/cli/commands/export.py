"""Export raw events for downstream processing."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from auditrace.core.config import Config
from auditrace.storage import create_storage

console = Console()


def export_command(
    output: Annotated[Path, typer.Option(help="Destination jsonl path")] = Path(
        "auditrace-export.jsonl"
    ),
) -> None:
    """Export events as JSONL."""
    config = Config.load()
    storage = create_storage(config)

    async def run_export() -> int:
        await storage.initialize()
        events = await storage.get_all_events_ordered()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event.model_dump(mode="json"), sort_keys=True))
                handle.write("\n")
        await storage.close()
        return len(events)

    count = asyncio.run(run_export())
    console.print(f"[green]Exported {count} events to {output}[/green]")
