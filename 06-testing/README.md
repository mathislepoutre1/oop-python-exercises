# 06 - Testing

- `shop.py`: small e-commerce app (discount, tax, orders)
- `groq_chat.py`: `ask_groq()` function that calls the Groq API
- `chat_api.py`: FastAPI app with `/status` and `/chat`

Tests (in `tests/`):
- `test_shop_unit.py`: unit tests for each function
- `test_shop_integration.py`: tests of OrderService with the repository
- `test_shop_properties.py`: property-based tests with Hypothesis
- `test_groq_chat.py`: tests of `ask_groq()` with a fake client (mock)
- `test_chat_api.py`: tests of the API with FastAPI's TestClient
- `conftest.py`: shared fixtures

```bash
pytest
pytest -m fast        # only the fast tests
pytest --cov          # with coverage
```

The tests don't call the real API, so no API key is needed. The key goes in the `GROQ_API_KEY` environment variable and is never committed.

While testing I found that an order with quantity 0 was accepted, so I fixed it.
