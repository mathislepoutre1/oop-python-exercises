"""Template Method pattern: ETL pipelines.

Problems with the original 3 classes:
1. Connect, validate, load and cleanup are copy-pasted 3 times (~70% duplicated code).
2. Validation is written 3 times and only differs by the required keys.
3. Adding logging or timing to every pipeline = editing 3 classes.
4. Changing the workflow order = editing 3 classes, and one will be forgotten.
5. Nothing stops a new pipeline from skipping validation.

Refactoring: `DataPipeline.run()` is the template method. It fixes the order of the
steps once. Subclasses only write what's unique (`extract`, `transform`, the keys to check)
and can optionally override the hooks `before_run()` / `after_run()`.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    source_type: str = "source"
    required_keys: tuple[str, ...] = ()
    delay: float = 0.5  # simulated network / disk time; tests set it to 0

    def __init__(self, source: str):
        self.source = source
        self.data: list[dict] | None = None
        self.steps: list[str] = []  # trace of what ran, handy for tests

    # ---------------- the template method: final workflow, do not override
    def run(self) -> str:
        self.before_run()
        try:
            self.connect()
            self.data = self.extract()
            self._log(f"Extracted {len(self.data)} records")
            self.data = self.transform(self.data)
            self._log("Transformation complete")
            self.validate()
            self.load()
        finally:
            self.cleanup()  # always runs, even if validation fails
        self.after_run()
        return f"{self.source_type} Pipeline finished"

    # ---------------- steps every subclass MUST write
    @abstractmethod
    def extract(self) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    # ---------------- common steps, written once
    def connect(self) -> None:
        self._log(f"Connecting to {self.source_type}: {self.source}")
        time.sleep(self.delay)
        self._log(f"{self.source_type} connection established")

    def validate(self) -> None:
        self._log("Validating data...")
        for record in self.data:
            missing = [k for k in self.required_keys if k not in record]
            if missing:
                raise ValueError(f"Invalid record structure, missing {missing}: {record}")
        self._log("Validation passed")

    def load(self) -> None:
        self._log("Loading data to destination...")
        time.sleep(self.delay)
        self._log(f"Loaded {len(self.data)} records successfully")

    def cleanup(self) -> None:
        self.data = None
        self._log("Cleanup complete")

    # ---------------- hooks: empty by default, override if needed
    def before_run(self) -> None:
        pass

    def after_run(self) -> None:
        pass

    def _log(self, message: str) -> None:
        self.steps.append(message)
        print(message)


class CSVPipeline(DataPipeline):
    source_type = "CSV"
    required_keys = ("id", "name")

    def extract(self):
        return [{"id": 1, "name": "Alice", "age": "30"}, {"id": 2, "name": "Bob", "age": "25"}]

    def transform(self, data):
        return [{**r, "age": int(r["age"]), "name": r["name"].upper()} for r in data]


class APIPipeline(DataPipeline):
    source_type = "API"
    required_keys = ("user_id", "username")

    def extract(self):
        return [{"user_id": 101, "username": "Charlie", "score": "85"},
                {"user_id": 102, "username": "DIANA", "score": "92"}]

    def transform(self, data):
        out = []
        for r in data:
            score = int(r["score"])
            out.append({**r, "score": score, "username": r["username"].lower(),
                        "grade": "A" if score >= 90 else "B"})
        return out


class DatabasePipeline(DataPipeline):
    source_type = "Database"
    required_keys = ("product_id", "price")

    def extract(self):
        return [{"product_id": 501, "product_name": "laptop", "price": 1200},
                {"product_id": 502, "product_name": "wireless mouse", "price": 25}]

    def transform(self, data):
        return [{**r, "price": float(r["price"]), "product_name": r["product_name"].title(),
                 "tax": round(float(r["price"]) * 0.2, 2)} for r in data]


# New pipeline to validate the design: only the XML-specific parts are written
class XMLPipeline(DataPipeline):
    source_type = "XML"
    required_keys = ("order_id", "total")

    SAMPLE = """<orders>
        <order id="9001"><customer>alice</customer><total>59.90</total></order>
        <order id="9002"><customer>bob</customer><total>120.00</total></order>
    </orders>"""

    def extract(self):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(self.SAMPLE)
        return [{"order_id": o.get("id"), "customer": o.findtext("customer"),
                 "total": o.findtext("total")} for o in root.iter("order")]

    def transform(self, data):
        return [{**r, "order_id": int(r["order_id"]), "total": float(r["total"]),
                 "customer": r["customer"].capitalize()} for r in data]

    # hook example: time the run
    def before_run(self):
        self._started = time.perf_counter()

    def after_run(self):
        self._log(f"XML pipeline took {time.perf_counter() - self._started:.2f}s")


if __name__ == "__main__":
    DataPipeline.delay = 0.1
    for title, pipeline in [("CSV", CSVPipeline("data/users.csv")),
                            ("API", APIPipeline("https://api.example.com/users")),
                            ("DATABASE", DatabasePipeline("postgresql://localhost/mydb")),
                            ("XML (NEW!)", XMLPipeline("data/orders.xml"))]:
        print(f"RUNNING {title} PIPELINE")
        print("=" * 70)
        print(f"\n{pipeline.run()}\n")
