# HIPAA

For systems interacting with ePHI, Auditrace supports audit-control evidence for 164.312(b) through signed operation logs.

Recommended practice:

- keep plaintext content storage disabled
- log only `input_hash` / `output_hash`
- retain actor, timestamp, and operation identifiers
- verify chain integrity regularly

Generate:

```bash
auditrace report --framework hipaa --format pdf
```
