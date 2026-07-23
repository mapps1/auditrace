# Configuration

Auditrace reads `auditrace.toml` from the current working directory.

## Example

```toml
[project]
name = "my-service"
risk_level = "limited"

[storage]
backend = "sqlite"
sqlite_path = "~/.auditrace/auditrace.db"
file_path = "~/.auditrace/events.jsonl"
# postgres_dsn = "postgresql://user:pass@localhost:5432/auditrace"
# s3_bucket = "auditrace-events"
# s3_prefix = "events"

[logging]
store_content = false
default_framework_tags = ["eu_ai_act"]

[report]
output_dir = "./auditrace-reports"
retention_reminder_days = 180
include_public_key = true
```

## Backend Selection

- `sqlite`: default and zero-setup.
- `file`: append-only JSONL file.
- `postgres`: requires `auditrace[postgres]` extra and DSN.
- `s3`: requires `auditrace[s3]` extra and bucket configuration.

## Data Minimization

Use hash-only logging for sensitive data flows:

- keep `store_content = false`
- provide `input_hash` and `output_hash`
- avoid storing plaintext prompts/responses unless strictly needed
