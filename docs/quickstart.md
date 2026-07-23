# Quickstart

## 1. Install

```bash
pip install auditrace
```

For PDF reports:

```bash
pip install "auditrace[pdf]"
```

## 2. Initialize

```bash
auditrace init --project-name my-service
```

This creates:

- local signing keys under `~/.auditrace/`
- a starter `auditrace.toml` in your current directory

## 3. Log an Event

```bash
auditrace log \
	--provider openai \
	--model-id gpt-5.3-codex \
	--user-id analyst-01 \
	--input-text "summarize this policy" \
	--output-text "summary"
```

## 4. Verify Integrity

```bash
auditrace verify
```

## 5. Generate Evidence

```bash
auditrace report --framework eu-ai-act --format html
auditrace report --framework all --format json
```

## 6. Export Raw Events

```bash
auditrace export --output ./auditrace-export.jsonl
```
