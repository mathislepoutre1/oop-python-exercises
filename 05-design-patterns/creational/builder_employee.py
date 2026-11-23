"""Builder pattern: HR employee onboarding.

Problems with the original `create_employee()` (17 positional parameters):
1. Position dependency: forget one `None` and every following argument shifts.
2. `False, True, True, True` means nothing when you read it.
3. No way to guarantee rules like "a senior developer always gets admin rights".
4. Validation is done *after* building the dict.

Refactoring: an `Employee` dataclass (the product), a fluent `EmployeeBuilder`
(every method returns self), validation in one place (`build()`), and presets.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)  # once built, a record can't be changed by accident
class Employee:
    first_name: str
    last_name: str
    email: str
    department: str
    position: str
    salary: float
    start_date: str
    manager_id: int | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    has_parking: bool = False
    has_laptop: bool = False
    has_vpn_access: bool = False
    has_admin_rights: bool = False
    office_location: str | None = None
    contract_type: str = "permanent"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class EmployeeBuilder:
    CONTRACT_TYPES = {"permanent", "fixed-term", "internship", "freelance"}

    def __init__(self) -> None:
        self._data: dict = {"start_date": date.today().isoformat()}

    # --- identity
    def with_name(self, first: str, last: str) -> EmployeeBuilder:
        self._data.update(first_name=first, last_name=last)
        return self

    def with_email(self, email: str) -> EmployeeBuilder:
        self._data["email"] = email
        return self

    def with_contact(self, phone: str | None = None, address: str | None = None,
                     emergency_contact: str | None = None) -> EmployeeBuilder:
        self._data.update(phone=phone, address=address, emergency_contact=emergency_contact)
        return self

    # --- job
    def with_job(self, department: str, position: str, salary: float) -> EmployeeBuilder:
        self._data.update(department=department, position=position, salary=salary)
        return self

    def starting_on(self, start_date: str) -> EmployeeBuilder:
        self._data["start_date"] = start_date
        return self

    def reporting_to(self, manager_id: int) -> EmployeeBuilder:
        self._data["manager_id"] = manager_id
        return self

    def with_contract(self, contract_type: str) -> EmployeeBuilder:
        self._data["contract_type"] = contract_type
        return self

    # --- equipment & access
    def with_equipment(self, laptop: bool = False, parking: bool = False) -> EmployeeBuilder:
        self._data.update(has_laptop=laptop, has_parking=parking)
        return self

    def with_access(self, vpn: bool = False, admin: bool = False) -> EmployeeBuilder:
        self._data.update(has_vpn_access=vpn, has_admin_rights=admin)
        return self

    def at_office(self, location: str) -> EmployeeBuilder:
        self._data["office_location"] = location
        return self

    # --- final step: ALL validation lives here
    def build(self) -> Employee:
        d = self._data
        missing = [k for k in ("first_name", "last_name", "email", "department", "position", "salary")
                   if not d.get(k) and d.get(k) != 0]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        if "@" not in d["email"]:
            raise ValueError("Valid email is required")
        if d["salary"] < 0:
            raise ValueError("Salary cannot be negative")
        if d.get("contract_type", "permanent") not in self.CONTRACT_TYPES:
            raise ValueError(f"Unknown contract type: {d['contract_type']}")
        if d.get("has_admin_rights") and not d.get("has_vpn_access"):
            raise ValueError("Admin rights require VPN access")
        return Employee(**d)


class DeveloperBuilder(EmployeeBuilder):
    """Preset: developers always get a laptop, VPN and admin rights."""

    def __init__(self, first: str, last: str, email: str, salary: float = 55000,
                 position: str = "Developer"):
        super().__init__()
        (self.with_name(first, last).with_email(email)
             .with_job("Engineering", position, salary)
             .with_equipment(laptop=True)
             .with_access(vpn=True, admin=True)
             .at_office("Paris HQ"))


class InternBuilder(EmployeeBuilder):
    """Preset: interns get a laptop only, internship contract, need a manager."""

    def __init__(self, first: str, last: str, email: str, department: str, manager_id: int):
        super().__init__()
        (self.with_name(first, last).with_email(email)
             .with_job(department, "Intern", 15000)
             .reporting_to(manager_id)
             .with_equipment(laptop=True)
             .with_contract("internship")
             .at_office("Paris HQ"))


if __name__ == "__main__":
    employee = (
        EmployeeBuilder()
        .with_name("John", "Doe")
        .with_email("john.doe@company.com")
        .with_job("Engineering", "Senior Developer", 75000)
        .with_equipment(laptop=True, parking=False)
        .with_access(vpn=True, admin=True)
        .build()
    )
    print(employee, "\n")

    dev = DeveloperBuilder("John", "Doe", "john.doe@company.com").build()
    intern = InternBuilder("Jane", "Smith", "jane.smith@company.com", "Marketing", manager_id=42) \
        .starting_on("2024-02-01").build()
    for e in (dev, intern):
        print(f"{e.full_name:<11} {e.position:<10} laptop={e.has_laptop} admin={e.has_admin_rights} "
              f"contract={e.contract_type}")
