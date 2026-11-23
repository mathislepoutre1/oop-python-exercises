# 06 · Testing & QA

> Slides 88-93: https://courses.dallard.tech/ci_cd/testing_python_intro/

| File | What it is |
|---|---|
| [`shop.py`](shop.py) | the e-commerce demo from the course (domain functions + repository + service) |
| [`groq_chat.py`](groq_chat.py) | `ask_groq()`, the LLM call from the Mocking section |
| [`chat_api.py`](chat_api.py) | FastAPI `/status` + `/chat` endpoint (slide 93), made testable with `Depends` |
| [`tests/conftest.py`](tests/conftest.py) | shared fixtures: a fresh `order_service`, and a `fake_groq` client factory |

## The tests, by level of the pyramid

| Level | File | What it shows |
|---|---|---|
| Unit | [`test_shop_unit.py`](tests/test_shop_unit.py) | one function at a time, `@pytest.mark.parametrize`, `pytest.raises(match=...)` |
| Integration | [`test_shop_integration.py`](tests/test_shop_integration.py) | service + repository together, a fixture gives a fresh repo each test |
| Property-based | [`test_shop_properties.py`](tests/test_shop_properties.py) | Hypothesis generates hundreds of inputs: "stock never goes negative", "a discount never raises the price" |
| Mocking | [`test_groq_chat.py`](tests/test_groq_chat.py) | fake client, `assert_called_once_with` (we send the right request), `side_effect` (API down), `mocker.patch` |
| API | [`test_chat_api.py`](tests/test_chat_api.py) | FastAPI `TestClient` + `app.dependency_overrides`; each Groq error → 500 / 429 / 503; bad bodies → 422 |

```bash
pytest 06-testing                    # no network, no API key needed
pytest -m fast                       # only tests marked fast
pytest -m "not slow"                 # skip slow ones
pytest --markers                     # list markers (declared in pyproject.toml)
pytest --cov --cov-report=term-missing
```

## What I learned

- **Mock what you don't own, test what you own.** The test doesn't check that the LLM answers "4". It checks that *my* code sends the right model, messages and `max_tokens`, refuses an empty question *before* calling the API, and handles errors.
- **Dependency injection makes code testable.** `ask_groq(question, client=None)` and FastAPI's `Depends(get_client)` let tests swap in a fake without patching internals.
- **`mocker.patch` patches where the name is used** (`groq_chat.Groq`), not where it's defined (`groq.Groq`).
- **Testing finds bugs.** The course's `place_order` accepted a quantity of 0 (selling nothing for 0 €). I added a check and a test for it.
- **Arrange / Act / Assert** keeps each test readable.
- The API key only lives in the `GROQ_API_KEY` environment variable, and `.env` is in `.gitignore`. The single test that would hit the real API is marked `slow` and skipped when no key is set.
