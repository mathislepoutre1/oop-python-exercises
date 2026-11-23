"""Decorator pattern: order pricing.

Problems with the original `calculate_total(5 boolean flags)`:
1. Flag explosion: every new option is one more parameter.
2. One method does everything (Single Responsibility violated).
3. Adding an option means modifying existing code (Open/Closed violated).
4. The insurance logic can't be reused anywhere else.
5. The order of operations is hidden (is the discount before or after shipping?).

Refactoring: every option is a decorator that wraps an `OrderComponent` and adds its
cost/description, then delegates to the wrapped object. The order you wrap them in IS
the order of the calculation, and you can read it.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class OrderComponent(ABC):
    @abstractmethod
    def get_cost(self) -> float: ...

    @abstractmethod
    def get_description(self) -> str: ...


class BaseOrder(OrderComponent):
    def __init__(self, base_price: float):
        if base_price < 0:
            raise ValueError("price cannot be negative")
        self.base_price = base_price

    def get_cost(self) -> float:
        return self.base_price

    def get_description(self) -> str:
        return f"Base price: {self.base_price:.2f}€"


class OrderDecorator(OrderComponent, ABC):
    """Holds the wrapped order. `_order` is protected so subclasses can use it (slide 87)."""

    def __init__(self, order: OrderComponent):
        self._order = order

    @property
    def base_price(self) -> float:
        """The original price, whatever the number of layers above it."""
        inner = self._order
        while isinstance(inner, OrderDecorator):
            inner = inner._order
        return inner.get_cost()


class ExpressShippingDecorator(OrderDecorator):
    COST = 15.00

    def get_cost(self) -> float:
        return self._order.get_cost() + self.COST

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nExpress shipping: +{self.COST:.2f}€"


class InsuranceDecorator(OrderDecorator):
    RATE = 0.05  # 5 % of the base price, like the original code

    def _amount(self) -> float:
        return self.base_price * self.RATE

    def get_cost(self) -> float:
        return self._order.get_cost() + self._amount()

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nInsurance (5%): +{self._amount():.2f}€"


class GiftWrapDecorator(OrderDecorator):
    COST = 5.00

    def get_cost(self) -> float:
        return self._order.get_cost() + self.COST

    def get_description(self) -> str:
        return f"{self._order.get_description()}\nGift wrap: +{self.COST:.2f}€"


class DiscountDecorator(OrderDecorator):
    def __init__(self, order: OrderComponent, percent: float):
        super().__init__(order)
        if not 0 <= percent <= 100:
            raise ValueError("percent must be between 0 and 100")
        self.percent = percent

    def _amount(self) -> float:
        return self._order.get_cost() * self.percent / 100

    def get_cost(self) -> float:
        return self._order.get_cost() - self._amount()

    def get_description(self) -> str:
        return f"{self._order.get_description()}\n{self._label()}: -{self._amount():.2f}€"

    def _label(self) -> str:
        return f"Discount ({self.percent:g}%)"


class PremiumMemberDecorator(DiscountDecorator):
    """A premium member gets 10% off: it's just a discount with a fixed rate."""

    def __init__(self, order: OrderComponent):
        super().__init__(order, percent=10)

    def _label(self) -> str:
        return "Premium member (10%)"


if __name__ == "__main__":
    print(BaseOrder(100.00).get_description(), "\n\n---\n")

    order = BaseOrder(100.00)
    order = ExpressShippingDecorator(order)
    order = InsuranceDecorator(order)
    order = GiftWrapDecorator(order)
    order = DiscountDecorator(order, percent=15)
    order = PremiumMemberDecorator(order)

    print(order.get_description())
    print(f"Total: {order.get_cost():.2f}€")
