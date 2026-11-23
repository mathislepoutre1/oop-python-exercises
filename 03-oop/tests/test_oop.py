import pytest

from abstraction import Disc, Logo, Shape, Square, render
from inheritance import (Bicycle, BankAccount, Car, Employee, Person, SavingsAccount,
                         Student, Vehicle)
from operator_overloading import Circle, Complex, Matrix, Person as P, Point, Vector


# ---------- operator overloading ----------
def test_complex_add_and_sub():
    assert Complex(3, 2) + Complex(1, 7) == Complex(4, 9)
    assert Complex(3, 2) - Complex(1, 7) == Complex(2, -5)


def test_complex_with_wrong_type_raises():
    with pytest.raises(TypeError):
        Complex(1, 1) + 5


def test_person_greater_than_by_age():
    assert P("A", 30, "F") > P("B", 25, "M")
    assert not P("A", 20, "F") > P("B", 25, "M")


def test_vector_dot_product():
    assert Vector(1, 2, 3) * Vector(4, 5, 6) == 32


@pytest.mark.parametrize("a, b, lt, le, gt, ge, eq, ne", [
    (2, 5, True, True, False, False, False, True),
    (5, 5, False, True, False, True, True, False),
    (7, 5, False, False, True, True, False, True),
])
def test_circle_all_comparisons(a, b, lt, le, gt, ge, eq, ne):
    c1, c2 = Circle(a), Circle(b)
    assert (c1 < c2, c1 <= c2, c1 > c2, c1 >= c2, c1 == c2, c1 != c2) == (lt, le, gt, ge, eq, ne)


def test_circle_negative_radius():
    with pytest.raises(ValueError):
        Circle(-1)


def test_points_compared_by_distance():
    assert Point(3, 4) == Point(5, 0) == Point(0, -5)
    assert Point(1, 1) < Point(3, 4)
    assert Point(3, 4) >= Point(-4, 3)
    assert sorted([Point(3, 4), Point(0, 1)]) [0] == Point(1, 0)


def test_matrix_product():
    assert Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]]) == Matrix([[19, 22], [43, 50]])
    assert (Matrix([[1, 2, 3]]) * Matrix([[1], [2], [3]])).rows == [[14]]


def test_matrix_bad_shapes():
    with pytest.raises(ValueError):
        Matrix([[1, 2]]) * Matrix([[1, 2]])


# ---------- inheritance ----------
def test_vehicles_override_drive():
    assert [v.drive() for v in (Vehicle(), Car(), Bicycle())] == [
        "Driving a vehicle", "Driving a car", "Riding a bicycle"]


def test_introductions():
    s = Student("Mathis", 20, "Paris", "Data Science")
    e = Employee("Léa", 28, "Nantes", "Airbus")
    assert isinstance(s, Person) and isinstance(e, Person)
    assert s.introduce().endswith("I study Data Science.")
    assert "Airbus" in e.introduce() and "Nantes" in e.introduce()


def test_transfer_ok_and_insufficient():
    a, b = BankAccount("A", 100), SavingsAccount("B", 0)
    assert a.transfer(b, 60) is True
    assert (a.balance, b.balance) == (40, 60)
    assert a.transfer(b, 1000) is False
    assert (a.balance, b.balance) == (40, 60)  # nothing moved


def test_savings_interest():
    s = SavingsAccount("S", 1000, interest_rate=0.05)
    assert s.add_interest() == pytest.approx(50)
    assert s.balance == pytest.approx(1050)
    assert "1050.00" in s.check_balance()


def test_negative_deposit_rejected():
    with pytest.raises(ValueError):
        BankAccount("X").deposit(-5)


# ---------- abstraction ----------
def test_abc_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Shape()


def test_shapes_and_protocol():
    assert Square(3).area() == 9
    assert Disc(1).describe() == "Disc with area 3.14"
    assert render(Logo()) == "<logo>"
