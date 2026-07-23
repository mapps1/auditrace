# Generic Integration

The generic decorator supports any callable where you can infer provider/model/user context.

## Example

```python
from auditrace.integrations.generic import audit

@audit(provider="custom", model_id="internal-router", user_id="ops-1")
def run_inference(prompt: str) -> str:
	return "result"
```

The decorator writes signed events automatically while preserving the wrapped function signature.
