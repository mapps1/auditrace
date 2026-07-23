"""Compliance report generation orchestration."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from auditrace.compliance import summarize_all, summarize_framework
from auditrace.core.chain import ChainVerifier
from auditrace.core.config import Config
from auditrace.core.signer import Signer
from auditrace.storage import create_storage


def generate_report(
    framework: str,
    output_format: str,
    since: str | None = None,
    output: Path | None = None,
) -> Path:
    """Generate a compliance report and return the output path."""
    config = Config.load()
    storage = create_storage(config)
    signer = Signer()
    verifier = ChainVerifier(storage=storage, signer=signer)

    async def load_events() -> tuple[list[dict[str, object]], dict[str, Any]]:
        await storage.initialize()
        since_iso = since or _default_since(config.report_retention_days)
        if since:
            _parse_iso_datetime(since)
        events = await storage.get_events_since(since_iso)

        verification = await verifier.verify()
        await storage.close()
        integrity = {
            "is_valid": verification.is_valid,
            "total_events": verification.total_events,
            "valid_events": verification.valid_events,
            "broken_links": verification.broken_links,
            "invalid_signatures": verification.invalid_signatures,
        }
        return [event.model_dump(mode="json") for event in events], integrity

    events, integrity = asyncio.run(load_events())

    if output is None:
        base_dir = config.report_output_dir
        base_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        output = base_dir / f"{framework}-{stamp}.{output_format}"
    else:
        output.parent.mkdir(parents=True, exist_ok=True)

    framework_summary = (
        summarize_all(events) if framework == "all" else summarize_framework(framework, events)
    )

    payload = {
        "framework": framework,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_count": len(events),
        "since": since or _default_since(config.report_retention_days),
        "retention_window_days": config.report_retention_days,
        "integrity": integrity,
        "summary": framework_summary,
        "events": events[:5000],
        "stylesheet": (Path(__file__).parent / "assets" / "report.css").read_text(
            encoding="utf-8"
        ),
    }

    try:
        payload["public_key_pem"] = signer.public_key_pem()
    except Exception:
        payload["public_key_pem"] = None

    if output_format == "json":
        output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return output

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=True,
    )
    template_name = (
        "summary.html.jinja2"
        if framework == "all"
        else f"{framework.replace('-', '_')}.html.jinja2"
    )
    template = env.get_template(template_name)
    html = template.render(payload=payload)

    if output_format == "html":
        output.write_text(html, encoding="utf-8")
        return output

    try:
        from weasyprint import HTML
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PDF generation requires 'auditrace[pdf]' extra") from exc

    HTML(string=html).write_pdf(str(output))
    return output


def _default_since(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
