import pytest

from auditrace.core.event import AuditEvent
from auditrace.storage.file import FileStorage
from auditrace.storage.s3 import S3Storage


@pytest.mark.asyncio
async def test_file_storage_round_trip(tmp_path) -> None:
    path = tmp_path / "events.jsonl"
    storage = FileStorage(file_path=path)
    await storage.initialize()

    event = AuditEvent(provider="p", model_id="m", event_hash="h", signature="s")
    await storage.write(event)

    assert await storage.count_events() == 1
    last = await storage.get_last_event()
    assert last is not None
    assert last.event_id == event.event_id

    events = await storage.get_events_since("1970-01-01T00:00:00+00:00")
    assert len(events) == 1
    await storage.close()


class _FakeBody:
    def __init__(self, text: str) -> None:
        self._text = text

    def read(self) -> bytes:
        return self._text.encode("utf-8")


class _FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[str, str] = {}

    def head_bucket(self, Bucket: str) -> None:  # noqa: N803
        _ = Bucket

    def put_object(
        self,
        Bucket: str,  # noqa: N803
        Key: str,  # noqa: N803
        Body: bytes,  # noqa: N803
        ContentType: str,  # noqa: N803
    ) -> None:
        _ = Bucket
        _ = ContentType
        self.objects[Key] = Body.decode("utf-8")

    def list_objects_v2(self, **kwargs):
        prefix = kwargs.get("Prefix", "")
        items = [{"Key": key} for key in self.objects if key.startswith(prefix)]
        return {"IsTruncated": False, "Contents": items}

    def get_object(self, Bucket: str, Key: str):  # noqa: N803
        _ = Bucket
        return {"Body": _FakeBody(self.objects[Key])}


@pytest.mark.asyncio
async def test_s3_storage_with_fake_client() -> None:
    client = _FakeS3Client()
    storage = S3Storage(bucket="b", prefix="events", client=client)
    await storage.initialize()

    event = AuditEvent(provider="p", model_id="m", event_hash="h", signature="s")
    await storage.write(event)

    assert await storage.count_events() == 1
    last = await storage.get_last_event()
    assert last is not None
    assert last.event_id == event.event_id
