"""Property-based tests (table of contents, part 4) with Hypothesis.

Instead of picking examples by hand, I state rules that must hold for ANY input
and Hypothesis generates hundreds of inputs trying to break them.
"""
from hypothesis import given
from hypothesis import strategies as st

from shop import OrderService, ProductRepository, calculate_discount, calculate_total

prices = st.floats(min_value=0, max_value=1_000_000, allow_nan=False)
percents = st.floats(min_value=0, max_value=100, allow_nan=False)


@given(prices, percents)
def test_discount_never_increases_price_nor_goes_negative(price, percent):
    result = calculate_discount(price, percent)
    assert 0 <= result <= round(price, 2) + 0.01


@given(st.lists(prices, max_size=20))
def test_total_is_at_least_the_subtotal(items):
    assert calculate_total(items) >= round(sum(items), 2) - 0.01


@given(st.sampled_from(["SHIRT", "MUG", "HAT"]), st.integers(min_value=1, max_value=200))
def test_stock_never_goes_negative(sku, quantity):
    service = OrderService(ProductRepository())
    before = service.repo.get_product(sku)["stock"]
    result = service.place_order(sku, quantity)
    after = service.repo.get_product(sku)["stock"]
    assert after >= 0
    assert after == (before - quantity if result["success"] else before)
