# 03 - OOP

- `operator_overloading.py`: Complex (+, -), Person (>), Vector (* for dot product), Circle (all comparisons), Point (compared by distance to origin), Matrix (* for matrix product)
- `inheritance.py`: Vehicle / Car / Bicycle, Person / Student / Employee, BankAccount / SavingsAccount
- `abstraction.py`: small example of an abstract class and a Protocol

```bash
python operator_overloading.py
python inheritance.py
python abstraction.py
```

Notes:
- In operator methods, return `NotImplemented` when the other object is the wrong type.
- If you define `__eq__`, you also need `__hash__` to put the object in a set.
- `@total_ordering` generates the missing comparisons from `__eq__` and `__lt__`.
