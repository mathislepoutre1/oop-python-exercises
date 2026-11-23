"""OOP problems: operator overloading."""
from __future__ import annotations

import math
from functools import total_ordering


# Problem 1: complex numbers with + and -
class Complex:
    def __init__(self, real: float, imag: float = 0.0):
        self.real = real
        self.imag = imag

    def __add__(self, other: Complex) -> Complex:
        if not isinstance(other, Complex):
            return NotImplemented
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: Complex) -> Complex:
        if not isinstance(other, Complex):
            return NotImplemented
        return Complex(self.real - other.real, self.imag - other.imag)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Complex):
            return NotImplemented
        return self.real == other.real and self.imag == other.imag

    def __repr__(self) -> str:
        sign = "+" if self.imag >= 0 else "-"
        return f"({self.real} {sign} {abs(self.imag)}i)"


# Problem 2: compare persons by age with >
class Person:
    def __init__(self, name: str, age: int, gender: str):
        self.name = name
        self.age = age
        self.gender = gender

    def __gt__(self, other: Person) -> bool:
        if not isinstance(other, Person):
            return NotImplemented
        return self.age > other.age

    def __repr__(self) -> str:
        return f"Person({self.name!r}, {self.age})"


# Problem 4: vector dot product with *
class Vector:
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __mul__(self, other: Vector) -> float:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y}, {self.z})"


# Problem 5: all comparison operators on a circle, based on the radius.
# I wrote the six of them by hand to practise; @total_ordering is used for Point below.
class Circle:
    def __init__(self, radius: float):
        if radius < 0:
            raise ValueError("radius cannot be negative")
        self.radius = radius

    def _check(self, other):
        return isinstance(other, Circle)

    def __eq__(self, other):
        return self.radius == other.radius if self._check(other) else NotImplemented

    def __ne__(self, other):
        return self.radius != other.radius if self._check(other) else NotImplemented

    def __lt__(self, other):
        return self.radius < other.radius if self._check(other) else NotImplemented

    def __le__(self, other):
        return self.radius <= other.radius if self._check(other) else NotImplemented

    def __gt__(self, other):
        return self.radius > other.radius if self._check(other) else NotImplemented

    def __ge__(self, other):
        return self.radius >= other.radius if self._check(other) else NotImplemented

    # __eq__ is defined, so Python removes __hash__ unless we give it back
    def __hash__(self):
        return hash(self.radius)

    def __repr__(self) -> str:
        return f"Circle(r={self.radius})"


# Problem 6: 2D points compared by their distance to the origin.
# @total_ordering writes <=, >, >= for me from __eq__ and __lt__.
@total_ordering
class Point:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    @property
    def distance(self) -> float:
        """Euclidean distance to the origin: sqrt(x² + y²)."""
        return math.hypot(self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return math.isclose(self.distance, other.distance)

    def __lt__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.distance < other.distance and not self == other

    def __hash__(self):
        return hash(round(self.distance, 9))

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


# Problem 7: matrix multiplication with *
class Matrix:
    def __init__(self, rows: list[list[float]]):
        if not rows or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError("all rows must have the same, non-zero length")
        self.rows = [list(r) for r in rows]

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.rows[0])

    def __mul__(self, other: Matrix) -> Matrix:
        if not isinstance(other, Matrix):
            return NotImplemented
        n, m = self.shape
        m2, p = other.shape
        if m != m2:
            raise ValueError(f"cannot multiply {self.shape} by {other.shape}")
        cols = list(zip(*other.rows))
        return Matrix([[sum(a * b for a, b in zip(row, col)) for col in cols] for row in self.rows])

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.rows == other.rows

    def __repr__(self) -> str:
        return "Matrix(" + ", ".join(str(r) for r in self.rows) + ")"


if __name__ == "__main__":
    print("Complex :", Complex(3, 2) + Complex(1, 7), Complex(3, 2) - Complex(1, 7))
    alice, bob = Person("Alice", 30, "F"), Person("Bob", 25, "M")
    print("Person  : alice > bob ?", alice > bob)
    print("Vector  : dot product =", Vector(1, 2, 3) * Vector(4, 5, 6))
    c1, c2 = Circle(2), Circle(5)
    print("Circle  :", c1 < c2, c1 <= c2, c1 > c2, c1 >= c2, c1 == c2, c1 != c2)
    print("Point   : (3,4) == (5,0) ?", Point(3, 4) == Point(5, 0), "| (1,1) < (3,4) ?", Point(1, 1) < Point(3, 4))
    print("Matrix  :", Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]]))
