# SOC 2

Auditrace provides evidence helpful for SOC 2 CC6.x logical access and activity traceability reviews.

Highlights:

- identity-attributed AI usage records
- provider/model operation context
- role/session metadata support
- signed, tamper-evident integrity chain

Generate:

```bash
auditrace report --framework soc2 --format html
```
