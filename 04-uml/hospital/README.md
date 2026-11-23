# Exo 1 - Hospital Management System

The final model (task 3) is coded in `hospital.py`.

## Task 1 - Class diagram

```mermaid
classDiagram
    class Patient {
        +id: str
        +name: str
        +password: str
        +email: str
        +submitProblem(description)
        +pay(amount, method)
        +viewPrescription()
    }
    class Organizer {
        +id: str
        +name: str
        +password: str
        +readProblem(problem)
        +consultDoctor(doctor, problem)
        +sendPrescription(patient)
        +forwardPayment(doctor)
        +registerMember()
    }
    class Doctor {
        +id: str
        +name: str
        +password: str
        +specialty: str
        +writePrescription(problem)
        +receivePayment(amount)
    }
    Patient "1..*" -- "1" Organizer : submits problems to / pays
    Organizer "1" -- "1..*" Doctor : consults / forwards payment
    Organizer "1" --> "0..*" Patient : registers
```

The patient never talks to the doctor directly, everything goes through the organizer.

## Task 2 - Class diagram with the 6 classes

```mermaid
classDiagram
    class Patient {
        +id
        +name
        +email
        +submitProblem(description) HealthProblem
        +pay(prescription, method) Payment
    }
    class Doctor {
        +id
        +name
        +specialty
        +fee
        +writePrescription(problem, text) Prescription
    }
    class Organizer {
        +id
        +name
        +consult(problem, doctor)
        +deliver(prescription)
        +forwardPayment(payment)
    }
    class HealthProblem {
        +id
        +description
        +createdAt
    }
    class Prescription {
        +id
        +text
        +fee
    }
    class Payment {
        +id
        +amount
        +method: PaymentType
    }
    class PaymentType {
        <<enumeration>>
        CHECK
        CASH
        CREDIT_CARD
    }

    Patient "1" *-- "0..*" HealthProblem : posts
    HealthProblem "1" *-- "0..1" Prescription : answered by
    Doctor "1" -- "0..*" Prescription : writes
    Prescription "1" -- "0..1" Payment : paid by
    Patient "1" -- "0..*" Payment : makes
    Payment --> PaymentType
    Organizer "1" -- "0..*" HealthProblem : handles
```

I used composition because a health problem belongs to one patient and a prescription only exists for one problem.

Sequence diagram: a patient submits a problem, gets a prescription and pays.

```mermaid
sequenceDiagram
    actor P as Patient
    participant O as Organizer
    participant D as Doctor
    P->>O: submitProblem("Headache")
    O->>D: consult(problem)
    D-->>O: Prescription
    O-->>P: deliver(prescription)
    P->>O: pay(prescription, CreditCard)
    O->>D: forwardPayment(amount)
```

## Task 3 - Advanced

Changes:
- a `User` superclass with id, name, password, login and logout
- payment types are classes that inherit from `PaymentMethod`
- `HealthProblem` has a status: pending, in-review, resolved
- timestamps, and each prescription keeps the patient's previous prescriptions

```mermaid
classDiagram
    class User {
        <<abstract>>
        +id: str
        +name: str
        -password_hash: str
        +login(password) bool
        +logout()
    }
    class Patient {
        +email: str
        +submit_problem(description) HealthProblem
        +pay(prescription, method) Payment
    }
    class Doctor {
        +specialty: str
        +fee: float
        +write_prescription(problem, text) Prescription
        +receive_payment(amount)
    }
    class Organizer {
        +register_patient(name, email)
        +register_doctor(name, specialty, fee)
        +consult(problem, doctor)
        +deliver(prescription)
        +forward_payment(payment)
    }
    User <|-- Patient
    User <|-- Doctor
    User <|-- Organizer

    class ProblemStatus {
        <<enumeration>>
        PENDING
        IN_REVIEW
        RESOLVED
    }
    class HealthProblem {
        +id
        +description
        +status: ProblemStatus
        +created_at
    }
    class Prescription {
        +id
        +text
        +fee
        +created_at
        +previous: list
    }
    class Payment {
        +id
        +amount
        +status
        +paid_at
        +process()
    }
    class PaymentMethod {
        <<abstract>>
        +charge(amount) str
    }
    class Cash
    class Check
    class CreditCard
    PaymentMethod <|-- Cash
    PaymentMethod <|-- Check
    PaymentMethod <|-- CreditCard

    Organizer "1" o-- "0..*" User : manages
    Patient "1" *-- "0..*" HealthProblem
    HealthProblem --> ProblemStatus
    HealthProblem "1" *-- "0..1" Prescription
    HealthProblem "0..*" --> "0..1" Doctor : assigned to
    Doctor "1" -- "0..*" Prescription : writes
    Payment --> Prescription : for
    Payment --> PaymentMethod : uses
```

### Patient registration

```mermaid
sequenceDiagram
    actor O as Organizer
    participant S as System
    O->>S: register_patient(name, email)
    S->>S: create id and password
    S-->>O: patient + password
```

### Consultation

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    actor O as Organizer
    actor D as Doctor
    P->>S: submit_problem(description)
    S-->>P: problem (pending)
    O->>S: consult(problem, doctor)
    S-->>D: problem (in-review)
    D->>S: write_prescription(problem, text)
    O->>S: deliver(prescription)
    S-->>P: prescription (resolved)
```

### Payment

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    actor O as Organizer
    actor D as Doctor
    P->>S: pay(prescription, method)
    alt payment ok
        S-->>P: payment (paid)
        O->>S: forward_payment(payment)
        S->>D: receive_payment(fee)
    else payment refused
        S-->>P: error
    end
```

## Questions

1. Multiple doctors: each problem has its own doctor, so a patient can see a different doctor for each problem.
2. Reusable prescriptions: I don't reuse the same object. For a renewal I create a new prescription that points to the old one, so the history is kept.
3. Design pattern for payments: Strategy. Each payment type is a class with its own `charge()`, so adding a new one doesn't change the rest.
4. Data integrity: a payment can only go created -> paid -> forwarded, it can't be paid or forwarded twice, and the amount comes from the prescription, not from the patient.
