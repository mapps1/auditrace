from dataclasses import dataclass

from auditrace.core.chain import ChainVerifier, ChainWriter
from auditrace.core.event import AuditEvent
from auditrace.core.signer import Signer


@dataclass
class MemoryStorage:
    events: list[AuditEvent]

    async def initialize(self) -> None:
        return None

    async def write(self, event: AuditEvent) -> None:
        self.events.append(event)

    async def get_last_event(self) -> AuditEvent | None:
        return self.events[-1] if self.events else None

    async def get_all_events_ordered(self) -> list[AuditEvent]:
        return self.events

    async def get_events_since(self, since_iso: str) -> list[AuditEvent]:
        return self.events

    async def count_events(self) -> int:
        return len(self.events)

    async def close(self) -> None:
        return None


async def test_chain_write_and_verify(tmp_path) -> None:
    storage = MemoryStorage(events=[])
    signer = Signer(key_dir=tmp_path)
    signer.generate_keypair()
    writer = ChainWriter(storage=storage, signer=signer)
    verifier = ChainVerifier(storage=storage, signer=signer)

    e1 = AuditEvent(provider="p", model_id="m", input_hash="1", output_hash="2")
    e2 = AuditEvent(provider="p", model_id="m", input_hash="3", output_hash="4")

    await writer.write(e1)
    await writer.write(e2)

    result = await verifier.verify()
    assert result.is_valid
    assert result.total_events == 2
