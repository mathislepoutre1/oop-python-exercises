# Exo 2 · ABCD Records 📼

> https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb

Mermaid has no real use-case diagram, so I draw them as flowcharts:
- 🧍 nodes = **actors**
- rounded nodes = **use cases**
- the box = **system boundary**
- dotted arrows = `<<include>>` / `<<extend>>`

The final model is implemented in [`abcd_records.py`](abcd_records.py) and tested in [`../tests/test_abcd_records.py`](../tests/test_abcd_records.py).

## Level 1

### 1.1 Use case diagram

```mermaid
flowchart LR
    M["🧍 Member"]
    C["🧍 Order Processing Clerk"]
    subgraph ABCD["ABCD Records system"]
        PO([Place Order])
        VM([Verify Membership])
        PR([Process Order])
        MP([Make Payment])
    end
    M --- PO
    M --- MP
    C --- VM
    C --- PR
```

### 1.2 Class diagram

```mermaid
classDiagram
    class Member {
        +memberId
        +name
        +address
        +placeOrder(items) Order
        +pay(order)
    }
    class Order {
        +orderId
        +date
        +items
        +total()
        +addItem(item)
    }
    class OrderProcessingClerk {
        +employeeId
        +name
        +verifyMembership(member) bool
        +processOrder(order)
    }
    Member "1" -- "0..*" Order : places
    OrderProcessingClerk "1" -- "0..*" Order : processes
```

## Level 2

### 2.1 Complete use case diagram

```mermaid
flowchart LR
    M["🧍 Member"]
    RM["🧍 Royal Member"]
    NM["🧍 Non-Member"]
    OC["🧍 Order Processing Clerk"]
    CC["🧍 Collection Dept. Clerk"]

    subgraph ABCD["ABCD Records system"]
        PO([Place Order])
        VM([Verify Membership])
        SA([Send Membership Application])
        PR([Process Order])
        VA([Verify Item Availability])
        AD([Apply Discount])
        OU([Order Unavailable Items])
        PI([Print Invoice])
        PS([Print Shipping List])
        MP([Make Payment])
    end

    RM -. is a .-> M
    M --- PO
    M --- MP
    NM --- PO
    OC --- PR
    CC --- MP

    PO -. "&lt;&lt;include&gt;&gt;" .-> VM
    SA -. "&lt;&lt;extend&gt;&gt; (not a member)" .-> VM
    PR -. "&lt;&lt;include&gt;&gt;" .-> VA
    PR -. "&lt;&lt;include&gt;&gt;" .-> PI
    PR -. "&lt;&lt;include&gt;&gt;" .-> PS
    AD -. "&lt;&lt;extend&gt;&gt; (Royal)" .-> PR
    OU -. "&lt;&lt;extend&gt;&gt; (Royal, out of stock)" .-> VA
    RM --- OU
```

- **include** = always happens. Placing an order *always* verifies membership, and processing *always* checks availability and prints the invoice and shipping list.
- **extend** = only sometimes. The application form is sent *only* to non-members, the discount *only* applies to Royal members, and unavailable items are ordered *only* for Royal members.

### 2.2 Complete class diagram

```mermaid
classDiagram
    class Customer {
        +name
        +address
    }
    class NonMember
    class Member {
        <<abstract>>
        +member_id
        +discount_rate* float
        +has_priority* bool
        +can_order_unavailable* bool
    }
    class RegularMember
    class RoyalMember
    Customer <|-- NonMember
    Customer <|-- Member
    Member <|-- RegularMember
    Member <|-- RoyalMember

    class MembershipApplication {
        +sent_on
    }
    NonMember "1" -- "0..1" MembershipApplication : receives

    class Item {
        <<abstract>>
        +code
        +title
        +artist
        +price
        +stock
        +is_available(qty) bool
    }
    class CD
    class Tape
    Item <|-- CD
    Item <|-- Tape

    class Order {
        +id
        +placed_on
        +status
        +gross_total()
        +discount()
        +total()
    }
    class OrderLine {
        +quantity
        +backordered: bool
        +subtotal()
    }
    Member "1" -- "0..*" Order : places
    Order "1" *-- "1..*" OrderLine
    OrderLine "0..*" --> "1" Item

    class Invoice {
        +amount
        +paid
        +print()
    }
    class ShippingList {
        +lines_to_ship()
        +print()
    }
    Order "1" -- "1" Invoice
    Order "1" -- "1" ShippingList

    class Payment {
        <<abstract>>
        +amount
        +describe()* str
    }
    class CashPayment
    class CheckPayment {
        +check_number
        +bank
    }
    class BankDraftPayment {
        +draft_number
    }
    Payment <|-- CashPayment
    Payment <|-- CheckPayment
    Payment <|-- BankDraftPayment
    Invoice "1" -- "0..1" Payment : settled by

    class OrderProcessingClerk {
        +verify_membership(customer) Member
        +process(order) (Invoice, ShippingList)
    }
    class CollectionClerk {
        +collect(invoice, payment)
    }
    class DailyRecords {
        +save(order)
    }
    OrderProcessingClerk ..> Order : processes
    OrderProcessingClerk --> DailyRecords : writes to
    CollectionClerk ..> Payment : handles
```

**Scenario: a Royal member orders 2 CDs (one unavailable) and pays by check.** This is the `__main__` of `abcd_records.py`:

```
INVOICE ORD-0001 - Mathis
  1 x Kind of Blue             15.00
  1 x Abbey Road               18.00 (back-ordered)
  Royal discount            -  3.30
  TOTAL                       29.70

SHIP TO Mathis, 1 rue de Paris, 75001 Paris [PRIORITY]
  1 x CD CD-001 'Kind of Blue'

Back-orders: ['Abbey Road']
Received 29.70€ check n°0012345 (BNP) for ORD-0001
```

## Level 3: Sequence diagrams

### 1. Complete order processing flow

```mermaid
sequenceDiagram
    actor M as Member
    participant OC as OrderProcessingClerk
    participant I as Item
    participant R as DailyRecords
    actor CC as CollectionClerk
    M->>OC: place order (items)
    OC->>OC: verify_membership(member)
    loop each order line
        OC->>I: is_available(qty)
        alt in stock
            I-->>OC: true
            OC->>I: stock -= qty
        else out of stock and Royal
            OC->>OC: mark back-ordered, add to reorders
        end
    end
    OC->>R: save(order)
    OC-->>M: Invoice + ShippingList
    M->>CC: payment
    CC-->>M: receipt
```

### 2. Membership verification (success and failure)

```mermaid
sequenceDiagram
    actor C as Customer
    participant OC as OrderProcessingClerk
    C->>OC: place order
    OC->>OC: verify_membership(customer)
    alt customer is a Member
        OC-->>C: order accepted
    else customer is a NonMember
        OC->>OC: create MembershipApplication
        OC-->>C: MembershipError + application form
    end
```

### 3. Payment processing (all types)

```mermaid
sequenceDiagram
    actor M as Member
    participant CC as CollectionClerk
    participant P as Payment
    participant INV as Invoice
    M->>CC: collect(invoice, payment)
    CC->>INV: already paid?
    alt amount matches and not paid
        alt Cash
            CC->>P: CashPayment.describe()
        else Check
            CC->>P: CheckPayment.describe() (number, bank)
        else Bank draft
            CC->>P: BankDraftPayment.describe() (draft number)
        end
        CC->>INV: paid = True
        CC-->>M: receipt
    else wrong amount or already paid
        CC-->>M: error
    end
```

### 4. Item reordering for Royal members

```mermaid
sequenceDiagram
    actor RM as RoyalMember
    participant OC as OrderProcessingClerk
    participant I as Item
    participant S as Supplier
    RM->>OC: order item X
    OC->>I: is_available(qty)
    I-->>OC: false
    OC->>RM: can_order_unavailable?
    RM-->>OC: true (Royal)
    OC->>OC: line.backordered = True
    OC->>S: reorder item X
    Note over OC,RM: invoice is issued now, X is shipped when it arrives
    S-->>OC: item X delivered
    OC-->>RM: ship item X (priority)
```
