# Auditrace

Tamper-evident AI audit trails for EU AI Act, SOC 2, HIPAA, and NIST AI RMF evidence workflows.

Auditrace is a Python library and CLI that records append-only, hash-chained, signed AI operation events. It is designed for teams that need compliance evidence without operating a dedicated governance platform.

## Build Trust In AI Systems

Auditors, regulators, and enterprise buyers increasingly ask for verifiable AI operation records. Auditrace helps teams move from ad hoc logging to cryptographically verifiable evidence without adding new infrastructure.

## Why Auditrace

- Ed25519 signatures on each event hash.
- Chain-linking (`previous_hash`) for tamper evidence.
- Zero-infrastructure default via SQLite.
- Framework-specific evidence summaries and auditor-readable reports.
- Drop-in wrappers for common AI SDK call patterns.

## Install

```bash
pip install auditrace
```

Optional extras:

```bash
pip install "auditrace[pdf]"         # PDF rendering
pip install "auditrace[postgres]"    # PostgreSQL backend
pip install "auditrace[s3]"          # S3/MinIO/R2 backend
pip install "auditrace[dev]"         # lint/type/test/docs tooling
```

## Quickstart

```bash
auditrace init --project-name my-ai-service
auditrace log --provider openai --model-id gpt-5.3-codex --user-id analyst-17 --input-text "draft response"
auditrace verify
auditrace report --framework eu-ai-act --format html
```

Programmatic usage:

```python
from auditrace import AuditEvent, get_chain_writer

writer = get_chain_writer()

event = AuditEvent(
    provider="openai",
    model_id="gpt-5.3-codex",
    user_id="analyst-17",
    input_hash=AuditEvent.hash_content("prompt text"),
    output_hash=AuditEvent.hash_content("model output"),
)

import asyncio

async def main() -> None:
    await writer.storage.initialize()
    await writer.write(event)
    await writer.storage.close()

asyncio.run(main())
```

## Compliance Framework Coverage

- EU AI Act Article 12 / Annex IV evidence summary
- SOC 2 CC6.x traceability support
- HIPAA 164.312(b) audit-control evidence
- NIST AI RMF Govern/Map/Measure/Manage mapping

## Storage Backends

- `sqlite` (default)
- `file` (JSONL append-only)
- `postgres` (optional extra)
- `s3` (optional extra; works with S3-compatible APIs)

Configure in `auditrace.toml`:

```toml
[storage]
backend = "sqlite"
sqlite_path = "~/.auditrace/auditrace.db"
file_path = "~/.auditrace/events.jsonl"
# postgres_dsn = "postgresql://user:pass@localhost:5432/auditrace"
# s3_bucket = "auditrace-events"
# s3_prefix = "events"
```

## CLI Commands

- `auditrace init`
- `auditrace log`
- `auditrace verify`
- `auditrace report`
- `auditrace export`
- `auditrace serve` (placeholder for planned local dashboard mode)

Run command help:

```bash
auditrace --help
auditrace report --help
```

## Reports

Generate JSON, HTML, or PDF evidence packages:

```bash
auditrace report --framework all --format json
auditrace report --framework soc2 --format pdf
```

Each report includes:

- integrity verification summary
- control-by-control coverage
- findings list
- sampled evidence events

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,pdf,openai,anthropic,litellm,langchain]"
ruff check auditrace tests
mypy auditrace
pytest
```

## Join The Community

Auditrace is intentionally community-extensible. Contributions are welcome across:

- new compliance framework mappers
- report templates and auditor narratives
- additional integrations and storage backends
- test fixtures and reproducible compliance datasets

If you want to help expand standards coverage, open an issue or PR for mappings such as:

- ISO/IEC 42001 AI management system evidence
- PCI DSS logging controls for AI-assisted payment workflows
- NIS2 / DORA operational resilience evidence
- internal policy frameworks and sector-specific controls

Start with [CONTRIBUTING.md](CONTRIBUTING.md), then propose a framework map under `auditrace/compliance/` and a companion report template under `auditrace/reports/templates/`.

## Security and Privacy

- Store prompts/outputs as hashes by default.
- Keep private signing keys local and access-restricted.
- Rotate keys with documented change control.
- Use report exports as evidence artifacts, not as long-term backup storage.

## License

Apache-2.0. See [LICENSE](LICENSE).
