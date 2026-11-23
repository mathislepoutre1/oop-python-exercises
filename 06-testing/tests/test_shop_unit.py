"""Unit tests: one function at a time, no I/O, very fast (bottom of the pyramid)."""
import pytest

from shop import calculate_discount, calculate_tax, calculate_total

pytestmark = pytest.mark.fast


class TestUnitDiscount:
    @pytest.mark.parametrize("price, percent, expected", [
        (100, 10, 90.0),
        (50, 0, 50.0),      # no discount
        (75, 100, 0.0),     # free
        (19.99, 15, 16.99), # decimals are rounded to cents
        (0, 50, 0.0),
    ])
    def test_discount(self, price, percent, expected):
        assert calculate_discount(price, percent) == expected

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            calculate_discount(-10, 20)

    @pytest.mark.parametrize("percent", [-1, 100.01, 150])
    def test_invalid_discount_raises(self, percent):
        with pytest.raises(ValueError, match="Discount must be between"):
            calculate_discount(100, percent)


class TestUnitTax:
    def test_default_20_percent(self):
        assert calculate_tax(100) == 20.0

    def test_custom_rate(self):
        assert calculate_tax(100, 0.10) == 10.0

    def test_zero_price(self):
        assert calculate_tax(0) == 0.0


class TestUnitTotal:
    def test_single_item(self):
        assert calculate_total([50.0]) == 60.0      # 50 + 20 %

    def test_multiple_items(self):
        assert calculate_total([10.0, 20.0, 30.0]) == 72.0

    def test_empty_cart(self):
        assert calculate_total([]) == 0.0

    def test_custom_tax_rate(self):
        assert calculate_total([100.0], tax_rate=0.055) == 105.5
