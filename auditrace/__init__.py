"""Public package API for Auditrace."""

from __future__ import annotations

from pathlib import Path

from auditrace.core.chain import ChainVerifier, ChainWriter
from auditrace.core.config import Config
from auditrace.core.event import AuditEvent, HumanReviewStatus
from auditrace.core.signer import Signer
from auditrace.integrations.anthropic import wrap_anthropic_client
from auditrace.integrations.generic import audit
from auditrace.integrations.openai import wrap_openai_client
from auditrace.storage import create_storage
from auditrace.storage.sqlite import SQLiteStorage


def get_chain_writer(config_path: Path | None = None) -> ChainWriter:
    """Return a configured chain writer from local config or defaults."""
    config = Config.load(config_path)
    storage = create_storage(config)
    signer = Signer()
    return ChainWriter(storage=storage, signer=signer)


__version__ = "0.1.0"

__all__ = [
    "AuditEvent",
    "HumanReviewStatus",
    "ChainWriter",
    "ChainVerifier",
    "Signer",
    "SQLiteStorage",
    "wrap_anthropic_client",
    "wrap_openai_client",
    "audit",
    "get_chain_writer",
]
