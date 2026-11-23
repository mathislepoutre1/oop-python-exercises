"""Strategy pattern: report formats.

Problems with the original `ReportGenerator`:
1. Two if/elif chains (generate_report AND save_report) that must stay in sync.
2. Adding XML or Markdown means editing the class (Open/Closed violated).
3. You can't test one format alone, and an unknown format silently returns "Unknown format".
4. The format is a string passed on every call: you can't plug one in at runtime.
5. Duplicated code: the four `with open(...)` blocks differ only by the extension.

Refactoring: one strategy class per format (it knows its text AND its file extension),
and a context `ReportGenerator` that holds one strategy and can swap it at any time.
"""
from __future__ import annotations

import html
import json
from abc import ABC, abstractmethod
from pathlib import Path


class FormatStrategy(ABC):
    extension: str = ""

    @abstractmethod
    def format(self, data: list[dict]) -> str: ...


class PDFFormatStrategy(FormatStrategy):
    extension = ".pdf"

    def format(self, data):
        rows = [f"| {item['name']:20} | {item['value']:10} |" for item in data]
        return "\n".join(["PDF REPORT", "=" * 50, *rows, "=" * 50, "End of PDF Report"])


class ExcelFormatStrategy(FormatStrategy):
    extension = ".xlsx"

    def format(self, data):
        rows = [f"{item['name']}\t{item['value']}" for item in data]
        return "\n".join(["EXCEL REPORT", "-" * 50, "Name\tValue", *rows, "-" * 50]) + "\n"


class CSVFormatStrategy(FormatStrategy):
    extension = ".csv"

    def format(self, data):
        return "name,value\n" + "".join(f"{item['name']},{item['value']}\n" for item in data)


class JSONFormatStrategy(FormatStrategy):
    extension = ".json"

    def format(self, data):
        return json.dumps(data, indent=2)


# Added at the end WITHOUT touching any class above: proof of Open/Closed
class HTMLFormatStrategy(FormatStrategy):
    extension = ".html"

    def format(self, data):
        rows = "\n".join(f"    <tr><td>{html.escape(str(i['name']))}</td><td>{i['value']}</td></tr>"
                         for i in data)
        return ("<table>\n    <tr><th>Name</th><th>Value</th></tr>\n"
                f"{rows}\n</table>")


class MarkdownFormatStrategy(FormatStrategy):
    extension = ".md"

    def format(self, data):
        return "\n".join(["| Name | Value |", "|---|---:|",
                          *(f"| {i['name']} | {i['value']} |" for i in data)])


class ReportGenerator:
    """The context: it uses a strategy without knowing which one."""

    def __init__(self, data: list[dict], strategy: FormatStrategy | None = None):
        self.data = data
        self._strategy = strategy

    def set_strategy(self, strategy: FormatStrategy) -> None:
        self._strategy = strategy

    def generate_report(self) -> str:
        if self._strategy is None:
            raise RuntimeError("No format strategy set: call set_strategy() first")
        return self._strategy.format(self.data)

    def save_report(self, filename: str | Path) -> Path:
        path = Path(filename).with_suffix(self._strategy.extension)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_report(), encoding="utf-8")
        return path


if __name__ == "__main__":
    data = [
        {"name": "Sales Q1", "value": 15000},
        {"name": "Sales Q2", "value": 18000},
        {"name": "Sales Q3", "value": 22000},
        {"name": "Sales Q4", "value": 25000},
    ]
    generator = ReportGenerator(data)
    for title, strategy in [("PDF", PDFFormatStrategy()), ("CSV", CSVFormatStrategy()),
                            ("JSON", JSONFormatStrategy()), ("HTML (NEW!)", HTMLFormatStrategy())]:
        print(f"=== {title} FORMAT ===")
        generator.set_strategy(strategy)
        print(generator.generate_report())
        print("\n" + "=" * 60 + "\n")

    generator.set_strategy(CSVFormatStrategy())
    saved = generator.save_report(Path(__file__).parent / "output" / "sales_report")
    print("Saved:", saved.name)
