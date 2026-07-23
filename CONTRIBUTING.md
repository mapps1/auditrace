# Contributing to Auditrace

Thanks for contributing to Auditrace. This project focuses on tamper-evident AI audit evidence, so correctness and traceability matter as much as feature velocity.

## Ground Rules

- Keep changes narrowly scoped and well-tested.
- Preserve append-only and tamper-evident semantics.
- Avoid introducing hidden side effects in logging/integrity paths.
- Prefer explicit, typed interfaces and predictable defaults.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,pdf,openai,anthropic,litellm,langchain]"
```

## Development Workflow

1. Create a feature branch from `main`.
2. Add or update tests first when possible.
3. Implement the change.
4. Run lint, typing, and tests locally.
5. Open a pull request with a clear rationale and risk notes.

## Required Checks

```bash
ruff check auditrace tests
mypy auditrace
pytest --cov=auditrace --cov-report=term-missing
```

## Commit and PR Guidance

- Use descriptive commit messages.
- Link issues when relevant.
- Document behavior changes in `CHANGELOG.md`.
- Include CLI output snippets when changing command UX.

## Design Expectations

- Keep backward compatibility for public APIs unless versioned breaking changes are planned.
- For storage backends, preserve `AbstractStorage` contract and event ordering semantics.
- For compliance/reporting logic, include clear mappings and deterministic output.

## Testing Notes

- Unit tests must not require network access.
- Optional backend tests should skip cleanly when dependency/env requirements are missing.
- Regressions in chain integrity verification are release-blocking.

## Documentation

Update these when behavior changes:

- `README.md`
- relevant pages under `docs/`
- `CHANGELOG.md`

## Code of Conduct

All participation is governed by `CODE_OF_CONDUCT.md`.
