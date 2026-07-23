"""Generic decorator to audit arbitrary callables."""

from __future__ import annotations

import asyncio
import functools
import json
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from auditrace.core.chain import ChainWriter
from auditrace.core.config import Config
from auditrace.core.event import AuditEvent
from auditrace.core.signer import Signer
from auditrace.storage import create_storage

LOGGER = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _default_writer() -> ChainWriter:
    config = Config.load()
    return ChainWriter(storage=create_storage(config), signer=Signer())


def audit(**defaults: Any) -> Callable[[F], F]:
    """Decorate a function and log a best-effort audit event for each call."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            try:
                writer = _default_writer()
                input_text = json.dumps({"args": args, "kwargs": kwargs}, default=str)
                output_text = json.dumps({"result": result}, default=str)
                event = AuditEvent(
                    provider=str(defaults.get("provider", "generic")),
                    model_id=str(defaults.get("model_id", "callable")),
                    user_id=defaults.get("user_id"),
                    framework_tags=list(defaults.get("framework_tags", [])),
                    input_hash=AuditEvent.hash_content(input_text),
                    output_hash=AuditEvent.hash_content(output_text),
                )

                async def run_write() -> None:
                    await writer.storage.initialize()
                    await writer.write(event)
                    await writer.storage.close()

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(run_write())
                    else:
                        loop.run_until_complete(run_write())
                except RuntimeError:
                    asyncio.run(run_write())
            except Exception as exc:
                LOGGER.warning("Generic audit logging failed: %s", exc)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
