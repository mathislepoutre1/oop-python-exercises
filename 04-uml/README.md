# 04 · UML

> Slide 68: https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb

I drew the diagrams in **Mermaid**, so they're text, version-controlled, and rendered by GitHub. Then I implemented the final model of each exercise in Python and tested it.

| Exercise | Diagrams + answers | Code |
|---|---|---|
| Exo 1: Hospital Management System 🏥 | [`hospital/README.md`](hospital/README.md): class diagrams (Tasks 1-3), 4 sequence diagrams, the 4 questions | [`hospital/hospital.py`](hospital/hospital.py) |
| Exo 2: ABCD Records 📼 | [`abcd_records/README.md`](abcd_records/README.md): use case diagrams (include/extend), class diagrams, 4 sequence diagrams | [`abcd_records/abcd_records.py`](abcd_records/abcd_records.py) |

```bash
python 04-uml/hospital/hospital.py
python 04-uml/abcd_records/abcd_records.py
pytest 04-uml
```

## UML relationships cheat-sheet (slides 46, 65-66)

| Relation | Mermaid | Meaning | Example here |
|---|---|---|---|
| Association | `A -- B` | A uses / knows B | `Doctor -- Prescription` |
| Dependency | `A ..> B` | weak link, e.g. a method parameter | `OrderProcessingClerk ..> Order` |
| Aggregation | `A o-- B` | whole/part, but B lives on its own | `Organizer o-- User` |
| Composition | `A *-- B` | B can't exist without A | `Order *-- OrderLine` |
| Inheritance | `A <\|-- B` | B is an A | `User <\|-- Patient` |
