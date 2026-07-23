"""OpenAI client wrapper for automatic audit logging."""

from __future__ import annotations

import asyncio
import functools
import json
import logging
from typing import Any

from auditrace.core.chain import ChainWriter
from auditrace.core.event import AuditEvent

LOGGER = logging.getLogger(__name__)


def wrap_openai_client(client: Any, chain_writer: ChainWriter, **defaults: Any) -> Any:
    """Wrap client.chat.completions.create with best-effort logging."""
    original_create = client.chat.completions.create

    @functools.wraps(original_create)
    def logged_create(**kwargs: Any) -> Any:
        response = original_create(**kwargs)
        try:
            model = kwargs.get("model", "unknown")
            messages = kwargs.get("messages", [])
            input_text = json.dumps(messages, default=str)
            output_text = ""
            choices = getattr(response, "choices", None)
            if choices:
                first = choices[0]
                message = getattr(first, "message", None)
                output_text = getattr(message, "content", "") if message else ""

            usage = getattr(response, "usage", None)
            event = AuditEvent(
                provider="openai",
                model_id=model,
                input_hash=AuditEvent.hash_content(input_text),
                output_hash=AuditEvent.hash_content(output_text),
                input_token_count=getattr(usage, "prompt_tokens", None),
                output_token_count=getattr(usage, "completion_tokens", None),
                **defaults,
            )
            if event.input_token_count and event.output_token_count:
                event.total_token_count = event.input_token_count + event.output_token_count

            async def persist_event() -> None:
                await chain_writer.storage.initialize()
                await chain_writer.write(event)
                await chain_writer.storage.close()

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(persist_event())
                else:
                    loop.run_until_complete(persist_event())
            except RuntimeError:
                asyncio.run(persist_event())
        except Exception as exc:
            LOGGER.warning("OpenAI audit logging failed: %s", exc)
        return response

    client.chat.completions.create = logged_create
    return client
