"""Abstract base classes vs Protocols, with shapes.

- `Shape` is an ABC: you can't create it, and subclasses MUST implement area().
- `Drawable` is a Protocol: no inheritance needed, any object with draw() fits.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Protocol


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    # concrete method shared by every shape
    def describe(self) -> str:
        return f"{self.name} with area {self.area():.2f}"


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side ** 2

    @property
    def name(self) -> str:
        return "Square"


class Disc(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    @property
    def name(self) -> str:
        return "Disc"


class Drawable(Protocol):
    def draw(self) -> str: ...


class Logo:  # does NOT inherit from anything
    def draw(self) -> str:
        return "<logo>"


def render(item: Drawable) -> str:
    return item.draw()


if __name__ == "__main__":
    try:
        Shape()
    except TypeError as e:
        print("ABC:", e)
    for s in (Square(3), Disc(1)):
        print(s.describe())
    print("Protocol:", render(Logo()))
    print("MRO of Square:", [c.__name__ for c in Square.mro()])
