# LangChain Integration

LangChain integration can be handled by wrapping the call boundary where prompts and responses are available.

Recommended approach:

- wrap chain invocation functions with the generic `audit` decorator
- pass user/session context in decorator kwargs
- include framework tags for report segmentation

This keeps Auditrace independent of specific LangChain versions while preserving audit fidelity.
