# LiteLLM Integration

Use LiteLLM when you need one interface across multiple model providers.

Auditrace can be applied through the generic decorator path around your model call wrapper.

## Pattern

1. Build a small function that performs the LiteLLM call.
2. Decorate it with `auditrace.integrations.generic.audit`.
3. Provide user and framework metadata for compliance mapping.
