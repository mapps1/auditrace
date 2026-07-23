"""Hash-chain write and verification utilities."""

from __future__ import annotations

from dataclasses import dataclass

from auditrace.core.event import AuditEvent
from auditrace.core.signer import Signer
from auditrace.storage.base import AbstractStorage


class ChainWriter:
    """Finalize and persist events as signed chain entries."""

    def __init__(self, storage: AbstractStorage, signer: Signer) -> None:
        self.storage = storage
        self.signer = signer

    async def write(self, event: AuditEvent) -> AuditEvent:
        """Populate chain fields, sign the event, and write it to storage."""
        last_event = await self.storage.get_last_event()
        event.previous_hash = last_event.event_hash if last_event else None
        event.event_hash = event.compute_hash()
        event.signature = self.signer.sign(event.event_hash)
        await self.storage.write(event)
        return event


@dataclass
class VerificationResult:
    total_events: int
    broken_links: list[tuple[str, str]]
    invalid_signatures: list[str]

    @property
    def valid_events(self) -> int:
        return self.total_events - len(self.broken_links) - len(self.invalid_signatures)

    @property
    def is_valid(self) -> bool:
        return not self.broken_links and not self.invalid_signatures


class ChainVerifier:
    """Verify hash continuity, content integrity, and signatures."""

    def __init__(self, storage: AbstractStorage, signer: Signer) -> None:
        self.storage = storage
        self.signer = signer

    async def verify(self) -> VerificationResult:
        """Verify all events in insertion order and return integrity status."""
        events = await self.storage.get_all_events_ordered()
        broken_links: list[tuple[str, str]] = []
        invalid_signatures: list[str] = []
        previous_hash: str | None = None

        for event in events:
            if event.previous_hash != previous_hash:
                broken_links.append(
                    (
                        event.event_id,
                        f"expected previous_hash={previous_hash}, got {event.previous_hash}",
                    )
                )

            stored_hash = event.event_hash
            recomputed_hash = event.compute_hash()
            if stored_hash != recomputed_hash:
                broken_links.append(
                    (
                        event.event_id,
                        f"hash mismatch: stored={stored_hash}, computed={recomputed_hash}",
                    )
                )

            if event.signature and event.event_hash:
                if not self.signer.verify(event.event_hash, event.signature):
                    invalid_signatures.append(event.event_id)

            previous_hash = event.event_hash

        return VerificationResult(
            total_events=len(events),
            broken_links=broken_links,
            invalid_signatures=invalid_signatures,
        )
