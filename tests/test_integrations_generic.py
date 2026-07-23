from auditrace.integrations.generic import audit


def test_generic_decorator_returns_original_result() -> None:
    @audit(provider="generic", model_id="call")
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
