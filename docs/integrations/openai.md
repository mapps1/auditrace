# OpenAI Integration

Use Auditrace wrappers to record OpenAI request/response metadata as signed events.

## Example

```python
from auditrace import get_chain_writer, wrap_openai_client
from openai import OpenAI

client = wrap_openai_client(
	OpenAI(),
	get_chain_writer(),
	user_id="analyst-01",
	framework_tags=["eu_ai_act", "soc2"],
)

response = client.responses.create(
	model="gpt-5.3-codex",
	input="Summarize incident notes",
)
```

The wrapper performs best-effort logging and does not change OpenAI response types.
