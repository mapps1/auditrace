# PostgreSQL Storage

PostgreSQL is recommended for multi-process or multi-node logging workloads.

Install:

```bash
pip install "auditrace[postgres]"
```

Configure:

```toml
[storage]
backend = "postgres"
postgres_dsn = "postgresql://user:pass@localhost:5432/auditrace"
```

You can also provide `AUDITRACE_POSTGRES_DSN` as an environment variable.
