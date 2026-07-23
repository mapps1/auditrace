"""Verify event chain integrity and signatures."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console

from auditrace.core.chain import ChainVerifier
from auditrace.core.config import Config
from auditrace.core.signer import Signer
from auditrace.storage import create_storage

console = Console()


def verify_command() -> None:
    """Verify all stored audit events."""
    config = Config.load()
    storage = create_storage(config)
    signer = Signer()
    verifier = ChainVerifier(storage=storage, signer=signer)

    async def run_verify() -> int:
        await storage.initialize()
        result = await verifier.verify()
        await storage.close()

        console.print(f"Total events: {result.total_events}")
        console.print(f"Valid events: {result.valid_events}")
        if result.is_valid:
            console.print("[green]Chain valid.[/green]")
            return 0

        if result.broken_links:
            console.print("[red]Broken links:[/red]")
            for event_id, reason in result.broken_links:
                console.print(f"  - {event_id}: {reason}")
        if result.invalid_signatures:
            console.print("[red]Invalid signatures:[/red]")
            for event_id in result.invalid_signatures:
                console.print(f"  - {event_id}")
        return 1

    code = asyncio.run(run_verify())
    if code != 0:
        raise typer.Exit(code)
