"""Fixtures shared by every test file in 06-testing."""
import pytest

from shop import OrderService, ProductRepository


@pytest.fixture
def order_service():
    """Fresh repository + service for each test (tests must not share stock)."""
    return OrderService(ProductRepository())


@pytest.fixture
def fake_groq(mocker):
    """Build a fake Groq client whose create() returns `answer`.

    Same shape as the real response: response.choices[0].message.content
    """
    def _make(answer: str = "4"):
        choice = mocker.Mock()
        choice.message.content = answer
        response = mocker.Mock()
        response.choices = [choice]
        client = mocker.Mock()
        client.chat.completions.create.return_value = response
        return client

    return _make
