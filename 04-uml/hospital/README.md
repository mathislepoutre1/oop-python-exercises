# Exo 1 · Hospital Management System 🏥

> https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb

All diagrams are written in [Mermaid](https://mermaid.js.org/), so GitHub renders them directly. The final model (Task 3) is implemented in [`hospital.py`](hospital.py) and tested in [`../tests/test_hospital.py`](../tests/test_hospital.py).

## Task 1: Basic class diagram

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

*Who talks to whom?* The patient never talks to the doctor directly: the **Organizer** sits in the middle of every exchange.

## Task 2: Full class diagram (6 classes)

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

- **Composition** (filled diamond): a `HealthProblem` only exists inside a patient's file, and a `Prescription` only exists as the answer to a problem.
- At this step the payment type is an **enumeration**. In Task 3 it becomes a class hierarchy (polymorphism).

### Sequence: a patient submits a problem, gets a prescription and pays

```mermaid
sequenceDiagram
    actor P as Patient
    participant O as Organizer
    participant D as Doctor
    P->>O: submitProblem("Headache")
    activate O
    O->>D: consult(problem)
    activate D
    D-->>O: Prescription
    deactivate D
    O-->>P: deliver(prescription)
    deactivate O
    P->>O: pay(prescription, CreditCard)
    activate O
    O->>D: forwardPayment(amount)
    deactivate O
```

## Task 3: Advanced model

Changes from Task 2:
- a `User` superclass holds `id`, `name`, `password` and `login/logout`
- `PaymentMethod` is an abstract class, and each payment type implements `charge()` its own way (Strategy pattern)
- `ProblemStatus`: pending → in-review → resolved
- timestamps everywhere, and every prescription keeps a reference to the patient's previous prescriptions

```mermaid
classDiagram
    class User {
        <<abstract>>
        +id: str
        +name: str
        -password_hash: str
        +logged_in: bool
        +login(password) bool
        +logout()
        +role* str
    }
    class Patient {
        +email: str
        +problems: list~HealthProblem~
        +inbox: list~Prescription~
        +submit_problem(description) HealthProblem
        +pay(prescription, method) Payment
        +past_prescriptions() list
    }
    class Doctor {
        +specialty: str
        +fee: float
        +earnings: float
        +write_prescription(problem, text) Prescription
        +receive_payment(amount)
    }
    class Organizer {
        +members: dict
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
        +created_at: datetime
    }
    class Prescription {
        +id
        +text
        +fee
        +created_at: datetime
        +previous: list~Prescription~
    }
    class Payment {
        +id
        +amount
        +status: PaymentStatus
        +paid_at
        +forwarded_at
        +process() Payment
    }
    class PaymentMethod {
        <<abstract>>
        +charge(amount)* str
    }
    class Cash
    class Check {
        +check_number
    }
    class CreditCard {
        +last4
    }
    PaymentMethod <|-- Cash
    PaymentMethod <|-- Check
    PaymentMethod <|-- CreditCard

    Organizer "1" o-- "0..*" User : manages
    Patient "1" *-- "0..*" HealthProblem
    HealthProblem --> ProblemStatus
    HealthProblem "1" *-- "0..1" Prescription
    HealthProblem "0..*" --> "0..1" Doctor : assigned to
    Doctor "1" -- "0..*" Prescription : writes
    Prescription "0..*" --> "0..*" Prescription : previous
    Payment "0..1" --> "1" Prescription : for
    Payment --> PaymentMethod : uses
```

### SSD 1: Patient registration

```mermaid
sequenceDiagram
    actor O as Organizer
    participant S as System
    O->>S: register_patient(name, email)
    S->>S: generate id + random password
    S->>S: store hash of the password
    S-->>O: (patient, password)
    O-->>O: send credentials to the patient
    Note over S: the plain password is never stored
```

### SSD 2: Consultation flow

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    actor O as Organizer
    actor D as Doctor
    P->>S: login(password)
    P->>S: submit_problem(description)
    S-->>P: problem (status = pending)
    O->>S: consult(problem, doctor)
    S-->>D: problem assigned (status = in-review)
    D->>S: write_prescription(problem, text)
    S-->>O: prescription ready
    O->>S: deliver(prescription)
    S-->>P: prescription (status = resolved)
```

### SSD 3: Payment processing

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as System
    participant M as PaymentMethod
    actor O as Organizer
    actor D as Doctor
    P->>S: pay(prescription, method)
    S->>M: charge(fee)
    alt payment accepted
        M-->>S: receipt
        S-->>P: payment (status = paid)
        O->>S: forward_payment(payment)
        S->>D: receive_payment(fee)
        S-->>O: payment (status = forwarded)
    else invalid card / check bounced
        M-->>S: error
        S-->>P: payment refused
    end
```

## Questions to consider

1. **A patient consulting several doctors?** Each `HealthProblem` gets its own assigned `Doctor`, so a patient with 3 problems can see 3 different doctors. To get a second opinion on *one* problem, I'd turn `HealthProblem → Doctor` into a list of `Consultation(doctor, problem, opinion)` objects (an association class).
2. **Should prescriptions be reusable?** Not by copying the same object: a prescription is a medical record linked to a date, a doctor and a problem. For a renewal, I'd create a **new** `Prescription` that points to the old one (`previous`). The history is kept and nothing gets overwritten.
3. **Design pattern for payments?** The **Strategy** pattern: `PaymentMethod` is the interface, and `Cash`/`Check`/`CreditCard` are interchangeable strategies, so a new type (PayPal…) means a new class and no change to `Payment`. A **Factory** could build the right method from a string sent by the web form.
4. **Data integrity for payments?** `Payment` is a small state machine (`created → paid → forwarded`) that refuses double processing and double forwarding. The amount comes from the prescription's fee, never from the patient. Only the last 4 digits of the card are stored. In a real system the "pay + update status" step would run in a single database transaction.
