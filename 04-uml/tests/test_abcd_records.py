import json

import pytest

from abcd_records import (CD, BankDraftPayment, CashPayment, CheckPayment, CollectionClerk,
                          DailyRecords, MembershipError, NonMember, Order, OrderProcessingClerk,
                          RegularMember, RoyalMember, Tape, UnavailableItemError)


@pytest.fixture
def items():
    return CD("CD-1", "Kind of Blue", "Miles Davis", 15.0, stock=4), \
           CD("CD-2", "Abbey Road", "The Beatles", 18.0, stock=0), \
           Tape("T-1", "Thriller", "Michael Jackson", 8.0, stock=2)


def test_royal_scenario_one_cd_unavailable(items, tmp_path):
    blue, abbey, _ = items
    royal = RoyalMember("M-1", "Mathis", "Paris")
    clerk = OrderProcessingClerk(DailyRecords(tmp_path))
    invoice, shipping = clerk.process(Order(royal).add(blue).add(abbey))

    assert invoice.amount == 29.70                  # (15 + 18) - 10%
    assert [l.item for l in shipping.lines_to_ship] == [blue]
    assert [l.item for l in clerk.reorders] == [abbey]
    assert blue.stock == 3
    assert "[PRIORITY]" in shipping.print()

    receipt = CollectionClerk().collect(invoice, CheckPayment(29.70, "001", "BNP"))
    assert "check" in receipt and invoice.paid

    # order saved in the daily records file
    line = (tmp_path / f"orders_{invoice.order.placed_on}.jsonl").read_text().strip()
    assert json.loads(line)["total"] == 29.70


def test_regular_member_cannot_order_unavailable(items):
    _, abbey, _ = items
    clerk = OrderProcessingClerk(DailyRecords())
    with pytest.raises(UnavailableItemError):
        clerk.process(Order(RegularMember("M-2", "Bob", "Lyon")).add(abbey))


def test_regular_member_pays_full_price(items):
    blue, _, tape = items
    order = Order(RegularMember("M-2", "Bob", "Lyon")).add(blue, 2).add(tape)
    assert order.total == 38.0 and order.discount == 0


def test_non_member_gets_application(items):
    clerk = OrderProcessingClerk(DailyRecords())
    with pytest.raises(MembershipError):
        clerk.verify_membership(NonMember("Eve", "Nice"))
    assert clerk.applications_sent[0].applicant.name == "Eve"


@pytest.mark.parametrize("payment", [CashPayment(10), CheckPayment(10, "1", "SG"),
                                     BankDraftPayment(10, "D-9")])
def test_every_payment_type_is_accepted(items, payment):
    blue, _, _ = items
    blue.price = 10
    invoice, _ = OrderProcessingClerk(DailyRecords()).process(
        Order(RegularMember("M-3", "Zoe", "Lille")).add(blue))
    assert CollectionClerk().collect(invoice, payment).startswith("Received 10.00€")


def test_wrong_amount_or_double_payment(items):
    blue, _, _ = items
    invoice, _ = OrderProcessingClerk(DailyRecords()).process(
        Order(RegularMember("M-3", "Zoe", "Lille")).add(blue))
    collector = CollectionClerk()
    with pytest.raises(ValueError):
        collector.collect(invoice, CashPayment(1))
    collector.collect(invoice, CashPayment(15))
    with pytest.raises(ValueError):
        collector.collect(invoice, CashPayment(15))
