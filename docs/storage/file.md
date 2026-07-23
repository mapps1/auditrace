# File Storage

File backend writes one JSON event per line in append-only order.

```toml
[storage]
backend = "file"
file_path = "~/.auditrace/events.jsonl"
```

Use when:

- you need plaintext files for offline archival
- you want git-friendly or pipeline-friendly evidence transfer
- SQLite is unavailable in your environment
