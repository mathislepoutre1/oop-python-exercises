"""Factory pattern: payment system.

Problems with the original `process_payment()`:
1. One big if/elif: adding Apple Pay means editing a function that already works (Open/Closed violated).
2. Validation, fees and processing for 3 providers are mixed in one place (Single Responsibility).
3. You can't test one provider alone.

Refactoring: an ABC (the contract), one class per provider, and a factory that maps a string
to a class through a registry dict, so there's no if/elif left.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class PaymentError(ValueError):
    pass


class PaymentProcessor(ABC):
    """Contract every payment method must follow."""

    method: str = ""

    @abstractmethod
    def validate(self, details: dict) -> bool:
        """Raise PaymentError if the details are wrong, return True otherwise."""

    @abstractmethod
    def compute_fee(self, amount: float) -> float: ...

    # Template shared by all processors: validate -> fee -> result
    def process(self, amount: float, details: dict) -> dict:
        try:
            self.validate(details)
        except PaymentError as e:
            return {"success": False, "error": str(e)}
        fee = round(self.compute_fee(amount), 2)
        return {"success": True, "method": self.method, "amount": round(amount + fee, 2), "fee": fee}


class CreditCardProcessor(PaymentProcessor):
    method = "credit_card"

    def validate(self, details: dict) -> bool:
        card, cvv = details.get("card_number", ""), details.get("cvv", "")
        if len(card) != 16 or not card.isdigit():
            raise PaymentError("Invalid card number")
        if len(cvv) != 3 or not cvv.isdigit():
            raise PaymentError("Invalid CVV")
        return True

    def compute_fee(self, amount: float) -> float:
        return amount * 0.029  # 2.9 %


class BankTransferProcessor(PaymentProcessor):
    method = "bank_transfer"

    def validate(self, details: dict) -> bool:
        if len(details.get("iban", "")) < 15:
            raise PaymentError("Invalid IBAN")
        return True

    def compute_fee(self, amount: float) -> float:
        return 1.50  # flat fee


class PayPalProcessor(PaymentProcessor):
    method = "paypal"

    def validate(self, details: dict) -> bool:
        if "@" not in details.get("email", ""):
            raise PaymentError("Invalid PayPal email")
        return True

    def compute_fee(self, amount: float) -> float:
        return amount * 0.034 + 0.30  # 3.4 % + 0.30 €


class PaymentFactory:
    """Returns the right processor for a payment type string."""

    _registry: dict[str, type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "bank_transfer": BankTransferProcessor,
        "paypal": PayPalProcessor,
    }

    @classmethod
    def register(cls, name: str, processor: type[PaymentProcessor]) -> None:
        """Plug a new payment method in WITHOUT touching this class."""
        cls._registry[name] = processor

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._registry)

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        try:
            return self._registry[payment_type]()
        except KeyError:
            raise ValueError(f"Unknown payment type: {payment_type}") from None


# --- Proof it's open for extension: a new method, zero lines changed above ---
class CryptoProcessor(PaymentProcessor):
    method = "crypto"

    def validate(self, details: dict) -> bool:
        if not details.get("wallet", "").startswith("0x"):
            raise PaymentError("Invalid wallet address")
        return True

    def compute_fee(self, amount: float) -> float:
        return amount * 0.01


PaymentFactory.register("crypto", CryptoProcessor)


if __name__ == "__main__":
    factory = PaymentFactory()

    processor = factory.get_processor("credit_card")
    print(processor.process(100.0, {"card_number": "1234567890123456", "cvv": "123"}))

    print(factory.get_processor("bank_transfer").process(
        100.0, {"iban": "FR7630006000011234567890189", "bic": "BNPAFRPP"}))
    print(factory.get_processor("paypal").process(100.0, {"email": "me@mail.com"}))
    print(factory.get_processor("crypto").process(100.0, {"wallet": "0xABC"}))
    print(factory.get_processor("paypal").process(100.0, {"email": "nope"}))
    print("Available:", PaymentFactory.available())
