"""UML Exo 1: Hospital Management System (Task 3 model, implemented in Python).

Diagrams: see README.md in this folder.
"""
from __future__ import annotations

import hashlib
import itertools
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

_ids = itertools.count(1)


def _next_id(prefix: str) -> str:
    return f"{prefix}-{next(_ids):04d}"


# ---------------------------------------------------------------- users
class User(ABC):
    """Shared attributes and login/logout for every member of the platform."""

    def __init__(self, user_id: str, name: str, password: str):
        self.id = user_id
        self.name = name
        self._password_hash = self._hash(password)  # never store the plain password
        self.logged_in = False

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, password: str) -> bool:
        self.logged_in = self._hash(password) == self._password_hash
        return self.logged_in

    def logout(self) -> None:
        self.logged_in = False

    @property
    @abstractmethod
    def role(self) -> str: ...

    def __repr__(self) -> str:
        return f"{self.role}({self.id}, {self.name!r})"


class Patient(User):
    role = "Patient"

    def __init__(self, user_id: str, name: str, password: str, email: str):
        super().__init__(user_id, name, password)
        self.email = email
        self.problems: list[HealthProblem] = []
        self.inbox: list[Prescription] = []

    def submit_problem(self, description: str) -> HealthProblem:
        problem = HealthProblem(patient=self, description=description)
        self.problems.append(problem)
        return problem

    def receive_prescription(self, prescription: Prescription) -> None:
        self.inbox.append(prescription)

    def pay(self, prescription: Prescription, method: PaymentMethod) -> Payment:
        return Payment(prescription=prescription, method=method).process()

    @property
    def past_prescriptions(self) -> list[Prescription]:
        return [p.prescription for p in self.problems if p.prescription]


class Doctor(User):
    role = "Doctor"

    def __init__(self, user_id: str, name: str, password: str, specialty: str, fee: float):
        super().__init__(user_id, name, password)
        self.specialty = specialty
        self.fee = fee
        self.earnings = 0.0

    def write_prescription(self, problem: HealthProblem, text: str) -> Prescription:
        if problem.doctor is not self:
            raise PermissionError("this problem was not assigned to this doctor")
        prescription = Prescription(problem=problem, doctor=self, text=text, fee=self.fee,
                                    previous=list(problem.patient.past_prescriptions))
        problem.prescription = prescription
        return prescription

    def receive_payment(self, amount: float) -> None:
        self.earnings += amount


class Organizer(User):
    """Reads problems, consults doctors, delivers prescriptions, forwards payments.
    Also the administrator: registers members and issues their ids and passwords."""

    role = "Organizer"

    def __init__(self, user_id: str, name: str, password: str):
        super().__init__(user_id, name, password)
        self.members: dict[str, User] = {}

    # --- admin
    def register_patient(self, name: str, email: str) -> tuple[Patient, str]:
        password = secrets.token_urlsafe(8)
        patient = Patient(_next_id("PAT"), name, password, email)
        self.members[patient.id] = patient
        return patient, password

    def register_doctor(self, name: str, specialty: str, fee: float) -> tuple[Doctor, str]:
        password = secrets.token_urlsafe(8)
        doctor = Doctor(_next_id("DOC"), name, password, specialty, fee)
        self.members[doctor.id] = doctor
        return doctor, password

    # --- workflow
    def consult(self, problem: HealthProblem, doctor: Doctor) -> None:
        if problem.status is not ProblemStatus.PENDING:
            raise ValueError(f"problem is already {problem.status.value}")
        problem.doctor = doctor
        problem.status = ProblemStatus.IN_REVIEW

    def deliver(self, prescription: Prescription) -> None:
        prescription.problem.patient.receive_prescription(prescription)
        prescription.problem.status = ProblemStatus.RESOLVED

    def forward_payment(self, payment: Payment) -> None:
        if payment.status is not PaymentStatus.PAID:
            raise ValueError(f"cannot forward a payment that is {payment.status.value}")
        payment.prescription.doctor.receive_payment(payment.amount)
        payment.status = PaymentStatus.FORWARDED
        payment.forwarded_at = datetime.now()


# ---------------------------------------------------------------- consultation
class ProblemStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in-review"
    RESOLVED = "resolved"


@dataclass(eq=False)
class HealthProblem:
    patient: Patient
    description: str
    id: str = field(default_factory=lambda: _next_id("HP"))
    status: ProblemStatus = ProblemStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    doctor: Doctor | None = None
    prescription: Prescription | None = None


@dataclass(eq=False)
class Prescription:
    problem: HealthProblem
    doctor: Doctor
    text: str
    fee: float
    previous: list[Prescription] = field(default_factory=list)  # patient's past prescriptions
    id: str = field(default_factory=lambda: _next_id("RX"))
    created_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------- payment (Strategy)
class PaymentMethod(ABC):
    @abstractmethod
    def charge(self, amount: float) -> str:
        """Charge the amount, return a receipt line."""


class Cash(PaymentMethod):
    def charge(self, amount: float) -> str:
        return f"{amount:.2f}€ paid in cash"


class Check(PaymentMethod):
    def __init__(self, check_number: str):
        self.check_number = check_number

    def charge(self, amount: float) -> str:
        return f"{amount:.2f}€ paid by check n°{self.check_number}"


class CreditCard(PaymentMethod):
    def __init__(self, card_number: str):
        if not (card_number.isdigit() and len(card_number) == 16):
            raise ValueError("card number must have 16 digits")
        self.last4 = card_number[-4:]  # keep only what we need

    def charge(self, amount: float) -> str:
        return f"{amount:.2f}€ paid by card ****{self.last4}"


class PaymentStatus(Enum):
    CREATED = "created"
    PAID = "paid"
    FORWARDED = "forwarded"


@dataclass(eq=False)
class Payment:
    prescription: Prescription
    method: PaymentMethod
    id: str = field(default_factory=lambda: _next_id("PAY"))
    status: PaymentStatus = PaymentStatus.CREATED
    receipt: str = ""
    paid_at: datetime | None = None
    forwarded_at: datetime | None = None

    @property
    def amount(self) -> float:
        return self.prescription.fee

    def process(self) -> Payment:
        if self.status is not PaymentStatus.CREATED:
            raise ValueError("payment already processed")
        self.receipt = self.method.charge(self.amount)
        self.status = PaymentStatus.PAID
        self.paid_at = datetime.now()
        return self


if __name__ == "__main__":
    admin = Organizer("ORG-1", "Olivia", "admin-pass")
    alice, alice_pw = admin.register_patient("Alice", "alice@mail.com")
    house, _ = admin.register_doctor("Dr House", "Diagnostics", fee=40.0)
    print("Registered:", alice, house, "| Alice can log in:", alice.login(alice_pw))

    problem = alice.submit_problem("Headache for 3 days")
    print(problem.id, problem.status.value)
    admin.consult(problem, house)
    print(problem.id, problem.status.value, "->", house.name)
    rx = house.write_prescription(problem, "Rest, water, paracetamol 1g")
    admin.deliver(rx)
    print(problem.id, problem.status.value, "| Alice received:", alice.inbox[0].text)

    payment = alice.pay(rx, CreditCard("4970101234567890"))
    print(payment.receipt, "-", payment.status.value)
    admin.forward_payment(payment)
    print("Forwarded to", house.name, "| earnings:", house.earnings, "| status:", payment.status.value)
