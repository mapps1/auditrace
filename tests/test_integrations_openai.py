from dataclasses import dataclass

from auditrace.core.chain import ChainWriter
from auditrace.core.event import AuditEvent
from auditrace.core.signer import Signer
from auditrace.integrations.openai import wrap_openai_client


@dataclass
class _MemStorage:
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


class _Message:
    content = "ok"


class _Choice:
    message = _Message()


class _Usage:
    prompt_tokens = 3
    completion_tokens = 4


class _Resp:
    choices = [_Choice()]
    usage = _Usage()


class _Completions:
    def create(self, **kwargs):
        return _Resp()


class _Chat:
    completions = _Completions()


class _Client:
    chat = _Chat()


def test_openai_wrapper_logs(tmp_path) -> None:
    storage = _MemStorage(events=[])
    signer = Signer(key_dir=tmp_path)
    signer.generate_keypair()
    writer = ChainWriter(storage=storage, signer=signer)
    client = wrap_openai_client(_Client(), writer, user_id="u")

    resp = client.chat.completions.create(model="gpt", messages=[{"role": "user", "content": "hi"}])
    assert isinstance(resp, _Resp)
