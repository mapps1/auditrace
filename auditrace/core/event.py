"""Core event schema and deterministic hashing utilities."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, cast

from pydantic import BaseModel, Field, field_validator


class HumanReviewStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"
    REJECTED = "rejected"


class AuditEvent(BaseModel):
    """A single auditable AI operation event."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str | None = None

    provider: str
    model_id: str
    system_version: str | None = None

    user_id: str | None = None
    user_role: str | None = None

    input_hash: str | None = None
    output_hash: str | None = None
    input_content: str | None = None
    output_content: str | None = None

    input_token_count: int | None = None
    output_token_count: int | None = None
    total_token_count: int | None = None

    human_review_status: HumanReviewStatus = HumanReviewStatus.NOT_REQUIRED
    human_reviewer_id: str | None = None
    human_review_timestamp: datetime | None = None
    human_review_notes: str | None = None

    risk_level: str | None = None
    framework_tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    previous_hash: str | None = None
    event_hash: str | None = None
    signature: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def ensure_utc(cls, value: Any) -> datetime:
        parsed = datetime.fromisoformat(value) if isinstance(value, str) else cast(datetime, value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def canonical_json(self) -> str:
        """Build a deterministic JSON document for hashing/signing."""
        data = self.model_dump(exclude={"event_hash", "signature"})
        data["timestamp"] = self.timestamp.isoformat()
        if self.human_review_timestamp:
            data["human_review_timestamp"] = self.human_review_timestamp.isoformat()
        return json.dumps(data, sort_keys=True, default=str)

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this event's canonical JSON representation."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    @staticmethod
    def hash_content(content: str) -> str:
        """Compute SHA-256 hash for arbitrary string content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
