"""S3-compatible object storage backend."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from auditrace.core.event import AuditEvent


class S3Storage:
    """Persist each event as a JSON object under a configured prefix."""

    def __init__(
        self,
        bucket: str | None = None,
        prefix: str = "events",
        client: Any = None,
    ) -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self._client = client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import boto3
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("S3 backend requires 'auditrace[s3]' extra") from exc
        self._client = boto3.client("s3")
        return self._client

    def _require_bucket(self) -> str:
        if not self.bucket:
            raise RuntimeError("S3 backend requires storage.s3_bucket in auditrace.toml")
        return self.bucket

    async def initialize(self) -> None:
        bucket = self._require_bucket()
        client = self._get_client()
        client.head_bucket(Bucket=bucket)

    async def write(self, event: AuditEvent) -> None:
        bucket = self._require_bucket()
        client = self._get_client()
        stamp = event.timestamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        key = f"{self.prefix}/{stamp}-{event.event_id}.json"
        body = json.dumps(event.model_dump(mode="json"), sort_keys=True).encode("utf-8")
        client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")

    async def get_last_event(self) -> AuditEvent | None:
        events = await self.get_all_events_ordered()
        return events[-1] if events else None

    async def get_all_events_ordered(self) -> list[AuditEvent]:
        bucket = self._require_bucket()
        client = self._get_client()
        keys = _list_keys(client=client, bucket=bucket, prefix=f"{self.prefix}/")
        events: list[AuditEvent] = []
        for key in sorted(keys):
            obj = client.get_object(Bucket=bucket, Key=key)
            raw = obj["Body"].read().decode("utf-8")
            payload = json.loads(raw)
            events.append(AuditEvent(**payload))
        return events

    async def get_events_since(self, since_iso: str) -> list[AuditEvent]:
        since = _parse_iso_datetime(since_iso)
        events = await self.get_all_events_ordered()
        return [event for event in events if event.timestamp >= since]

    async def count_events(self) -> int:
        bucket = self._require_bucket()
        client = self._get_client()
        keys = _list_keys(client=client, bucket=bucket, prefix=f"{self.prefix}/")
        return len(keys)

    async def close(self) -> None:
        return None


def _list_keys(client: Any, bucket: str, prefix: str) -> list[str]:
    keys: list[str] = []
    continuation_token: str | None = None

    while True:
        kwargs: dict[str, object] = {"Bucket": bucket, "Prefix": prefix}
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token
        response = client.list_objects_v2(**kwargs)
        for item in response.get("Contents", []):
            key = item.get("Key")
            if isinstance(key, str):
                keys.append(key)

        if not response.get("IsTruncated"):
            break
        next_token = response.get("NextContinuationToken")
        if not isinstance(next_token, str):
            break
        continuation_token = next_token

    return keys


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
