"""UML Exo 2: ABCD Records, mail-order CDs & tapes for club members.

Diagrams: see README.md in this folder.
"""
from __future__ import annotations

import itertools
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

_ids = itertools.count(1)


# ---------------------------------------------------------------- items
class Item(ABC):
    def __init__(self, code: str, title: str, artist: str, price: float, stock: int = 0):
        self.code = code
        self.title = title
        self.artist = artist
        self.price = price
        self.stock = stock

    @property
    @abstractmethod
    def format(self) -> str: ...

    def is_available(self, quantity: int = 1) -> bool:
        return self.stock >= quantity

    def __repr__(self) -> str:
        return f"{self.format} {self.code} '{self.title}'"


class CD(Item):
    format = "CD"


class Tape(Item):
    format = "Tape"


# ---------------------------------------------------------------- members
class Customer:
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address


class NonMember(Customer):
    """Someone who isn't in the club yet: they can only receive an application form."""


class Member(Customer, ABC):
    def __init__(self, member_id: str, name: str, address: str):
        super().__init__(name, address)
        self.member_id = member_id

    @property
    @abstractmethod
    def discount_rate(self) -> float: ...

    @property
    @abstractmethod
    def has_priority(self) -> bool: ...

    @property
    @abstractmethod
    def can_order_unavailable(self) -> bool: ...


class RegularMember(Member):
    discount_rate = 0.0
    has_priority = False
    can_order_unavailable = False


class RoyalMember(Member):
    discount_rate = 0.10
    has_priority = True
    can_order_unavailable = True


@dataclass
class MembershipApplication:
    applicant: NonMember
    sent_on: date = field(default_factory=date.today)


# ---------------------------------------------------------------- orders
@dataclass
class OrderLine:
    item: Item
    quantity: int
    backordered: bool = False  # True = unavailable now, reordered for a Royal member

    @property
    def subtotal(self) -> float:
        return self.item.price * self.quantity


@dataclass
class Order:
    member: Member
    lines: list[OrderLine] = field(default_factory=list)
    id: str = field(default_factory=lambda: f"ORD-{next(_ids):04d}")
    placed_on: date = field(default_factory=date.today)
    status: str = "placed"

    def add(self, item: Item, quantity: int = 1) -> Order:
        self.lines.append(OrderLine(item, quantity))
        return self

    @property
    def gross_total(self) -> float:
        return sum(line.subtotal for line in self.lines)

    @property
    def discount(self) -> float:
        return round(self.gross_total * self.member.discount_rate, 2)

    @property
    def total(self) -> float:
        return round(self.gross_total - self.discount, 2)


@dataclass
class Invoice:
    order: Order
    amount: float
    paid: bool = False

    def print(self) -> str:
        lines = [f"INVOICE {self.order.id} - {self.order.member.name}"]
        for line in self.order.lines:
            flag = " (back-ordered)" if line.backordered else ""
            lines.append(f"  {line.quantity} x {line.item.title:<22} {line.subtotal:>7.2f}{flag}")
        if self.order.discount:
            lines.append(f"  Royal discount            -{self.order.discount:>6.2f}")
        lines.append(f"  TOTAL                     {self.amount:>7.2f}")
        return "\n".join(lines)


@dataclass
class ShippingList:
    order: Order

    @property
    def lines_to_ship(self) -> list[OrderLine]:
        return [line for line in self.order.lines if not line.backordered]

    def print(self) -> str:
        priority = " [PRIORITY]" if self.order.member.has_priority else ""
        rows = [f"SHIP TO {self.order.member.name}, {self.order.member.address}{priority}"]
        rows += [f"  {line.quantity} x {line.item!r}" for line in self.lines_to_ship]
        return "\n".join(rows)


# ---------------------------------------------------------------- payments
class Payment(ABC):
    def __init__(self, amount: float):
        self.amount = amount

    @abstractmethod
    def describe(self) -> str: ...


class CashPayment(Payment):
    def describe(self) -> str:
        return f"{self.amount:.2f}€ cash"


class CheckPayment(Payment):
    def __init__(self, amount: float, check_number: str, bank: str):
        super().__init__(amount)
        self.check_number = check_number
        self.bank = bank

    def describe(self) -> str:
        return f"{self.amount:.2f}€ check n°{self.check_number} ({self.bank})"


class BankDraftPayment(Payment):
    def __init__(self, amount: float, draft_number: str):
        super().__init__(amount)
        self.draft_number = draft_number

    def describe(self) -> str:
        return f"{self.amount:.2f}€ bank draft {self.draft_number}"


# ---------------------------------------------------------------- staff & records
class DailyRecords:
    """Every processed order is written to the record file of the day."""

    def __init__(self, folder: Path | None = None):
        self.folder = folder
        self.orders: list[Order] = []

    def save(self, order: Order) -> None:
        self.orders.append(order)
        if self.folder is not None:
            path = self.folder / f"orders_{order.placed_on.isoformat()}.jsonl"
            record = {"order": order.id, "member": order.member.member_id, "total": order.total,
                      "items": [[l.item.code, l.quantity, l.backordered] for l in order.lines]}
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")


class MembershipError(Exception):
    pass


class UnavailableItemError(Exception):
    pass


class OrderProcessingClerk:
    def __init__(self, records: DailyRecords):
        self.records = records
        self.applications_sent: list[MembershipApplication] = []
        self.reorders: list[OrderLine] = []

    def verify_membership(self, customer: Customer) -> Member:
        if not isinstance(customer, Member):
            # <<extend>> Send Membership Application
            if isinstance(customer, NonMember):
                self.applications_sent.append(MembershipApplication(customer))
            raise MembershipError(f"{customer.name} is not a member: application form sent")
        return customer

    def process(self, order: Order) -> tuple[Invoice, ShippingList]:
        member = self.verify_membership(order.member)          # <<include>>
        for line in order.lines:                               # <<include>> verify availability
            if line.item.is_available(line.quantity):
                line.item.stock -= line.quantity
            elif member.can_order_unavailable:                 # <<extend>> order unavailable items
                line.backordered = True
                self.reorders.append(line)
            else:
                raise UnavailableItemError(f"{line.item!r} is out of stock")
        order.status = "processed"
        self.records.save(order)
        return Invoice(order, order.total), ShippingList(order)   # <<include>> print docs


class CollectionClerk:
    def collect(self, invoice: Invoice, payment: Payment) -> str:
        if invoice.paid:
            raise ValueError("invoice already paid")
        if round(payment.amount, 2) != round(invoice.amount, 2):
            raise ValueError(f"expected {invoice.amount:.2f}€, got {payment.amount:.2f}€")
        invoice.paid = True
        invoice.order.status = "paid"
        return f"Received {payment.describe()} for {invoice.order.id}"


if __name__ == "__main__":
    # Scenario: Royal member orders 2 CDs (one unavailable), pays by check
    kind_of_blue = CD("CD-001", "Kind of Blue", "Miles Davis", 15.00, stock=4)
    abbey_road = CD("CD-002", "Abbey Road", "The Beatles", 18.00, stock=0)

    royal = RoyalMember("M-042", "Mathis", "1 rue de Paris, 75001 Paris")
    order = Order(royal).add(kind_of_blue).add(abbey_road)

    clerk = OrderProcessingClerk(DailyRecords())
    invoice, shipping = clerk.process(order)
    print(invoice.print(), "\n")
    print(shipping.print(), "\n")
    print("Back-orders:", [l.item.title for l in clerk.reorders])
    print(CollectionClerk().collect(invoice, CheckPayment(invoice.amount, "0012345", "BNP")))

    try:
        clerk.verify_membership(NonMember("Bob", "Lyon"))
    except MembershipError as e:
        print("\n", e)
