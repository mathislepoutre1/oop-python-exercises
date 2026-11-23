import pytest

from hospital import (Cash, Check, CreditCard, Organizer, PaymentStatus, ProblemStatus,
                      User)


@pytest.fixture
def setup():
    admin = Organizer("ORG-1", "Olivia", "pw")
    patient, pw = admin.register_patient("Alice", "alice@mail.com")
    doctor, _ = admin.register_doctor("Dr House", "Diagnostics", fee=40.0)
    return admin, patient, pw, doctor


def test_user_is_abstract():
    with pytest.raises(TypeError):
        User("U-1", "x", "pw")


def test_registration_and_login(setup):
    admin, patient, pw, doctor = setup
    assert patient.id in admin.members and doctor.id in admin.members
    assert patient.login("wrong") is False
    assert patient.login(pw) is True
    assert pw not in vars(patient).values()  # only the hash is stored
    patient.logout()
    assert patient.logged_in is False


def test_full_consultation_and_payment(setup):
    admin, patient, _, doctor = setup
    problem = patient.submit_problem("Headache")
    assert problem.status is ProblemStatus.PENDING

    admin.consult(problem, doctor)
    assert problem.status is ProblemStatus.IN_REVIEW

    rx = doctor.write_prescription(problem, "Rest")
    admin.deliver(rx)
    assert problem.status is ProblemStatus.RESOLVED
    assert patient.inbox == [rx]

    payment = patient.pay(rx, Check("123"))
    assert payment.status is PaymentStatus.PAID and payment.amount == 40.0
    admin.forward_payment(payment)
    assert payment.status is PaymentStatus.FORWARDED
    assert doctor.earnings == 40.0


def test_payment_cannot_be_forwarded_twice(setup):
    admin, patient, _, doctor = setup
    problem = patient.submit_problem("Cough")
    admin.consult(problem, doctor)
    payment = patient.pay(doctor.write_prescription(problem, "Syrup"), Cash())
    admin.forward_payment(payment)
    with pytest.raises(ValueError):
        admin.forward_payment(payment)
    assert doctor.earnings == 40.0


def test_payment_methods_are_polymorphic():
    receipts = [m.charge(10) for m in (Cash(), Check("9"), CreditCard("1234567812345678"))]
    assert receipts == ["10.00€ paid in cash", "10.00€ paid by check n°9",
                        "10.00€ paid by card ****5678"]
    with pytest.raises(ValueError):
        CreditCard("12")


def test_other_doctor_cannot_prescribe(setup):
    admin, patient, _, doctor = setup
    other, _ = admin.register_doctor("Dr Who", "Time", 10)
    problem = patient.submit_problem("Fever")
    admin.consult(problem, doctor)
    with pytest.raises(PermissionError):
        other.write_prescription(problem, "x")


def test_prescription_keeps_history(setup):
    admin, patient, _, doctor = setup
    first = patient.submit_problem("A")
    admin.consult(first, doctor)
    rx1 = doctor.write_prescription(first, "one")
    second = patient.submit_problem("B")
    admin.consult(second, doctor)
    rx2 = doctor.write_prescription(second, "two")
    assert rx2.previous == [rx1]
