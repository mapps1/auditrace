# SQLite Storage

SQLite is the default backend and requires no external service.

```toml
[storage]
backend = "sqlite"
sqlite_path = "~/.auditrace/auditrace.db"
```

Use when:

- single-host deployments
- local development
- minimal operational overhead
