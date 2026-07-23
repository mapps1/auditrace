# Anthropic Integration

Wrap an Anthropic client to capture signed audit events around completion calls.

## Example

```python
import anthropic
from auditrace import get_chain_writer, wrap_anthropic_client

client = wrap_anthropic_client(
	anthropic.Anthropic(),
	get_chain_writer(),
	user_id="operator-7",
	framework_tags=["hipaa"],
)

message = client.messages.create(
	model="claude-opus-4.1",
	max_tokens=512,
	messages=[{"role": "user", "content": "Draft a neutral summary"}],
)
```

The integration keeps API ergonomics intact while emitting append-only audit records.
