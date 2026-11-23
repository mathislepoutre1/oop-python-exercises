"""OOP problems: inheritance."""
from __future__ import annotations


# Problem 1: method overriding
class Vehicle:
    def drive(self) -> str:
        return "Driving a vehicle"


class Car(Vehicle):
    def drive(self) -> str:
        return "Driving a car"


class Bicycle(Vehicle):
    def drive(self) -> str:
        return "Riding a bicycle"


# Problem 2: Person -> Student / Employee, each with its own introduce()
class Person:
    def __init__(self, name: str, age: int, address: str):
        self.name = name
        self.age = age
        self.address = address

    def introduce(self) -> str:
        return f"Hi, I'm {self.name}, {self.age} years old, I live in {self.address}."


class Student(Person):
    def __init__(self, name: str, age: int, address: str, field_of_study: str):
        super().__init__(name, age, address)
        self.field_of_study = field_of_study

    def introduce(self) -> str:
        # reuse the parent sentence instead of copy-pasting it
        return f"{super().introduce()} I study {self.field_of_study}."


class Employee(Person):
    def __init__(self, name: str, age: int, address: str, company: str):
        super().__init__(name, age, address)
        self.company = company

    def introduce(self) -> str:
        return f"{super().introduce()} I work at {self.company}."


# Problem 3: BankAccount / SavingsAccount
class BankAccount:
    def __init__(self, account_number: str, balance: float = 0.0):
        self.account_number = account_number
        self._balance = balance  # "protected": change it through deposit/withdraw

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            return False
        self._balance -= amount
        return True

    def transfer(self, destination: BankAccount, amount: float) -> bool:
        """Move money to another account. False if the balance is too low."""
        if not self.withdraw(amount):
            return False
        destination.deposit(amount)
        return True

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.account_number!r}, balance={self._balance:.2f})"


class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, balance: float = 0.0, interest_rate: float = 0.02):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate

    def add_interest(self) -> float:
        interest = self._balance * self.interest_rate
        self._balance += interest
        return interest

    def check_balance(self) -> str:
        return f"Account {self.account_number}: {self._balance:.2f}€ (rate {self.interest_rate:.1%})"


if __name__ == "__main__":
    # Polymorphism: same call, different behaviour
    for v in (Vehicle(), Car(), Bicycle()):
        print(v.drive())

    print()
    for p in (Person("Ana", 40, "Lyon"),
              Student("Mathis", 20, "Paris", "Data Science"),
              Employee("Léa", 28, "Nantes", "Airbus")):
        print(p.introduce())

    print()
    checking = BankAccount("FR-001", 500)
    savings = SavingsAccount("FR-002", 1000, interest_rate=0.03)
    print("transfer 200 ->", checking.transfer(savings, 200))
    print("transfer 9999 ->", checking.transfer(savings, 9999))
    print("interest earned:", savings.add_interest())
    print(savings.check_balance())
