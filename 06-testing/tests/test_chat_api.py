"""Testing the FastAPI chat endpoint with a mocked Groq client.

`app.dependency_overrides` replaces `get_client` by our fake: the route code is
tested for real, only the external API is fake.
"""
import groq
import httpx
import pytest
from fastapi.testclient import TestClient

from chat_api import app, get_client

REQUEST = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


@pytest.fixture
def api(fake_groq):
    """Yield (http client, fake groq client) and clean the override afterwards."""
    fake = fake_groq("Hello from the mock")
    app.dependency_overrides[get_client] = lambda: fake
    yield TestClient(app), fake
    app.dependency_overrides.clear()


def test_status(api):
    http, _ = api
    assert http.get("/status").json() == {"message": "OK"}


def test_chat_returns_model_answer(api):
    http, fake = api
    response = http.post("/chat", json={"prompt": "Hi"})
    assert response.status_code == 200
    assert response.json() == {"response": "Hello from the mock"}
    messages = fake.chat.completions.create.call_args.kwargs["messages"]
    assert messages[-1] == {"role": "user", "content": "Hi"}


@pytest.mark.parametrize("body", [{}, {"prompt": ""}, {"wrong": "field"}])
def test_invalid_body_is_rejected_before_calling_groq(api, body):
    http, fake = api
    assert http.post("/chat", json=body).status_code == 422
    fake.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("error, status", [
    (groq.APIConnectionError(request=REQUEST), 500),
    (groq.RateLimitError("slow down", response=httpx.Response(429, request=REQUEST), body=None), 429),
    (groq.InternalServerError("boom", response=httpx.Response(503, request=REQUEST), body=None), 503),
])
def test_groq_errors_become_http_errors(api, error, status):
    http, fake = api
    fake.chat.completions.create.side_effect = error
    assert http.post("/chat", json={"prompt": "Hi"}).status_code == status
