# Contributing

Auditrace values correctness, transparency, and practical compliance evidence.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,pdf,openai,anthropic,litellm,langchain]"
```

## Required Checks

```bash
ruff check auditrace tests
mypy auditrace
pytest --cov=auditrace --cov-report=term-missing
```

## Pull Requests

Include:

- a concise summary
- test evidence
- any compatibility notes
- docs/changelog updates for user-visible behavior changes

See the repository root CONTRIBUTING guide for full process policy details.
