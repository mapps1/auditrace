# Auditrace Documentation

Auditrace provides a library and CLI for tamper-evident AI operation logs.

## Core Concepts

- Each event is a structured `AuditEvent`.
- Each event includes a deterministic SHA-256 `event_hash`.
- Each event references the prior event hash via `previous_hash`.
- Each event hash is signed with a local Ed25519 private key.
- Verification checks continuity and signature validity across the chain.

## What You Can Do

- integrate with AI calls using wrappers/decorators
- write manual events for external workflows
- verify integrity status with one command
- generate framework-specific evidence reports
- export append-only records for archival or downstream analysis

## Documentation Map

- [Quickstart](quickstart.md)
- [Configuration](configuration.md)
- [Integrations](integrations/openai.md)
- [Compliance](compliance/eu-ai-act.md)
- [Storage](storage/sqlite.md)
- [Contributing](contributing.md)
- [Changelog](changelog.md)
