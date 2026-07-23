# Changelog

## [0.1.0] - 2026-07-22
- Initial Auditrace release.
- Added hash-chained, Ed25519-signed audit event model and verification.
- Added SQLite backend plus functional file, PostgreSQL, and S3 backend implementations.
- Added CLI commands: `init`, `log`, `verify`, `report`, `export`, and `serve` placeholder.
- Added framework mappers and control summaries for EU AI Act, SOC 2, HIPAA, and NIST AI RMF.
- Added JSON/HTML/PDF evidence report pipeline with integrity summaries and control coverage.
- Added integration wrappers for OpenAI, Anthropic, and generic callables.
- Added CI, publish, and docs workflows with lint/type/test gates.
