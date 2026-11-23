# Exo 2 - ABCD Records

The final model is coded in `abcd_records.py`.

Mermaid has no use case diagram, so I drew them as flowcharts (the box is the system, dotted arrows are include/extend).

## Level 1

### Use case diagram

```mermaid
flowchart LR
    M["Member"]
    C["Order Processing Clerk"]
    subgraph ABCD["ABCD Records"]
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

### Class diagram

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

### Use case diagram

```mermaid
flowchart LR
    M["Member"]
    RM["Royal Member"]
    NM["Non-Member"]
    OC["Order Processing Clerk"]
    CC["Collection Clerk"]

    subgraph ABCD["ABCD Records"]
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
    RM --- OU

    PO -. include .-> VM
    SA -. extend .-> VM
    PR -. include .-> VA
    PR -. include .-> PI
    PR -. include .-> PS
    AD -. extend .-> PR
    OU -. extend .-> VA
```

Include = always happens (placing an order always checks membership). Extend = only in some cases (the application form is only sent to non-members, the discount is only for Royal members).

### Class diagram

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
        +discount_rate
        +can_order_unavailable
    }
    class RegularMember
    class RoyalMember
    Customer <|-- NonMember
    Customer <|-- Member
    Member <|-- RegularMember
    Member <|-- RoyalMember

    class MembershipApplication
    NonMember "1" -- "0..1" MembershipApplication : receives

    class Item {
        <<abstract>>
        +code
        +title
        +price
        +stock
    }
    class CD
    class Tape
    Item <|-- CD
    Item <|-- Tape

    class Order {
        +id
        +placed_on
        +total()
    }
    class OrderLine {
        +quantity
        +backordered
    }
    Member "1" -- "0..*" Order : places
    Order "1" *-- "1..*" OrderLine
    OrderLine "0..*" --> "1" Item

    class Invoice {
        +amount
        +paid
    }
    class ShippingList
    Order "1" -- "1" Invoice
    Order "1" -- "1" ShippingList

    class Payment {
        <<abstract>>
        +amount
    }
    class CashPayment
    class CheckPayment
    class BankDraftPayment
    Payment <|-- CashPayment
    Payment <|-- CheckPayment
    Payment <|-- BankDraftPayment
    Invoice "1" -- "0..1" Payment : paid by
```

Scenario: a Royal member orders 2 CDs, one is out of stock, and pays by check. Output of `python abcd_records.py`:

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

## Level 3 - Sequence diagrams

### Order processing

```mermaid
sequenceDiagram
    actor M as Member
    participant OC as OrderProcessingClerk
    participant I as Item
    participant R as DailyRecords
    M->>OC: place order
    OC->>OC: verify_membership(member)
    loop each item
        OC->>I: is_available(qty)
        alt in stock
            OC->>I: remove from stock
        else out of stock and Royal
            OC->>OC: mark as back-ordered
        end
    end
    OC->>R: save(order)
    OC-->>M: invoice + shipping list
```

### Membership verification

```mermaid
sequenceDiagram
    actor C as Customer
    participant OC as OrderProcessingClerk
    C->>OC: place order
    alt is a member
        OC-->>C: order accepted
    else not a member
        OC-->>C: membership application form
    end
```

### Payment

```mermaid
sequenceDiagram
    actor M as Member
    participant CC as CollectionClerk
    participant INV as Invoice
    M->>CC: payment (cash, check or bank draft)
    alt right amount and not paid yet
        CC->>INV: mark as paid
        CC-->>M: receipt
    else wrong amount or already paid
        CC-->>M: error
    end
```

### Reordering for Royal members

```mermaid
sequenceDiagram
    actor RM as RoyalMember
    participant OC as OrderProcessingClerk
    participant S as Supplier
    RM->>OC: order item X
    OC->>OC: X is out of stock
    OC->>OC: Royal member, so mark X as back-ordered
    OC->>S: reorder X
    S-->>OC: X delivered
    OC-->>RM: ship X
```
