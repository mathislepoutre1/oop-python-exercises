"""E-commerce demo app from the course page (used to practise the testing pyramid).

https://courses.dallard.tech/ci_cd/testing_python_intro/
"""
from __future__ import annotations


# ============================================== Domain layer (unit tests)
def calculate_discount(price: float, discount_percent: float) -> float:
    """Return the discounted price."""
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    return round(price * (1 - discount_percent / 100), 2)


def calculate_tax(price: float, tax_rate: float = 0.20) -> float:
    """Return the tax amount."""
    return round(price * tax_rate, 2)


def calculate_total(prices: list[float], tax_rate: float = 0.20) -> float:
    """Return the grand total including tax."""
    subtotal = sum(prices)
    tax = calculate_tax(subtotal, tax_rate)
    return round(subtotal + tax, 2)


# ============================================== Service / repository layer (integration tests)
class ProductRepository:
    """Simulates a database of products."""

    def __init__(self):
        self._products = {
            "SHIRT": {"name": "T-Shirt", "price": 25.00, "stock": 50},
            "MUG": {"name": "Coffee Mug", "price": 12.00, "stock": 100},
            "HAT": {"name": "Cap", "price": 18.00, "stock": 30},
        }

    def get_product(self, sku: str) -> dict | None:
        return self._products.get(sku)

    def update_stock(self, sku: str, quantity: int) -> bool:
        product = self._products.get(sku)
        if product and product["stock"] >= quantity:
            product["stock"] -= quantity
            return True
        return False


class OrderService:
    """Business logic that coordinates repo + calculations."""

    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def place_order(self, sku: str, quantity: int) -> dict:
        if quantity <= 0:  # added: the course version accepted 0 or negative quantities
            return {"success": False, "error": "Quantity must be positive"}
        product = self.repo.get_product(sku)
        if product is None:
            return {"success": False, "error": "Product not found"}
        if product["stock"] < quantity:
            return {"success": False, "error": "Not enough stock"}

        total = calculate_total([product["price"] * quantity])
        self.repo.update_stock(sku, quantity)

        return {"success": True, "item": product["name"], "quantity": quantity, "total": total}
