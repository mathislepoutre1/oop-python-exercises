"""Tests for ask_groq with a fake Groq client (no real API call)."""
import os

import pytest

from groq_chat import MODEL, ask_groq


@pytest.mark.fast
def test_ask_groq_returns_the_answer(fake_groq):
    # Arrange
    client = fake_groq("4")
    # Act
    answer = ask_groq("What is 2+2?", client=client)
    # Assert
    assert answer == "4"


@pytest.mark.fast
def test_ask_groq_sends_the_right_request(fake_groq):
    client = fake_groq()
    ask_groq("What is 2+2?", client=client)
    client.chat.completions.create.assert_called_once_with(
        model=MODEL,
        messages=[{"role": "user", "content": "What is 2+2?"}],
        max_tokens=1024,
    )


@pytest.mark.fast
def test_ask_groq_propagates_api_failure(mocker):
    client = mocker.Mock()
    client.chat.completions.create.side_effect = Exception("API down")
    with pytest.raises(Exception, match="API down"):
        ask_groq("What is 2+2?", client=client)


@pytest.mark.fast
@pytest.mark.parametrize("question", ["", "   ", "\n"])
def test_empty_question_never_calls_the_api(fake_groq, question):
    client = fake_groq()
    with pytest.raises(ValueError, match="cannot be empty"):
        ask_groq(question, client=client)
    client.chat.completions.create.assert_not_called()


@pytest.mark.fast
def test_default_client_is_created_when_none_given(mocker, fake_groq):
    # patch the Groq class where it is USED (groq_chat), not where it is defined
    groq_class = mocker.patch("groq_chat.Groq", return_value=fake_groq("hi"))
    assert ask_groq("hello") == "hi"
    groq_class.assert_called_once_with()


@pytest.mark.slow
@pytest.mark.skipif(not os.environ.get("GROQ_API_KEY"), reason="needs a real GROQ_API_KEY")
def test_real_api_smoke():
    """The only test that hits the real API: skipped unless a key is set."""
    assert ask_groq("Reply with the single word: pong").strip()
