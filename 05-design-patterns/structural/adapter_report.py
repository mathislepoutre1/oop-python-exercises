"""Adapter pattern: XML reports -> JSON dashboard.

Problems with the original code:
1. Incompatible interfaces: the legacy generator returns XML, the dashboard wants JSON.
2. The conversion is repeated in every show_*_report() function.
3. It "cheats": it calls json.dumps(report_data) on the original dict and throws the XML
   away, so the legacy output is never really used.
4. Business logic and format conversion are mixed together.

Refactoring: the dashboard depends on an interface (`ReportGeneratorInterface`).
`LegacyReportAdapter` implements it, wraps the legacy object (composition) and REALLY
converts its XML to JSON. The legacy class is left untouched.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod


# Legacy reporting system (can't modify, external library)
class LegacyReportGenerator:
    def generate_report(self, data: dict) -> str:
        """Returns XML format - old system"""
        xml = "<report>\n"
        for key, value in data.items():
            xml += f"  <{key}>{value}</{key}>\n"
        xml += "</report>"
        return xml


# New analytics dashboard expects JSON
class AnalyticsDashboard:
    def display(self, json_data: str) -> str:
        data = json.loads(json_data)
        lines = ["=== Analytics Dashboard ==="] + [f"  {k}: {v}" for k, v in data.items()]
        output = "\n".join(lines)
        print(output)
        return output


# ---------------------------------------------------------------- the pattern
class ReportGeneratorInterface(ABC):
    """What the dashboard side expects: data in, JSON string out."""

    @abstractmethod
    def generate(self, data: dict) -> str: ...


class LegacyReportAdapter(ReportGeneratorInterface):
    def __init__(self, legacy: LegacyReportGenerator):
        self._legacy = legacy

    def generate(self, data: dict) -> str:
        xml = self._legacy.generate_report(data)
        return json.dumps(self._xml_to_dict(xml))

    @staticmethod
    def _xml_to_dict(xml: str) -> dict:
        root = ET.fromstring(xml)
        return {child.tag: LegacyReportAdapter._parse_value(child.text or "") for child in root}

    @staticmethod
    def _parse_value(text: str):
        """XML only has text: give back ints and floats their real type."""
        for cast in (int, float):
            try:
                return cast(text)
            except ValueError:
                pass
        return text


# Business code: knows nothing about XML anymore
def show_report(generator: ReportGeneratorInterface, dashboard: AnalyticsDashboard, data: dict) -> str:
    return dashboard.display(generator.generate(data))


if __name__ == "__main__":
    report_generator = LegacyReportAdapter(LegacyReportGenerator())
    dashboard = AnalyticsDashboard()

    show_report(report_generator, dashboard, {"total_sales": 150000, "orders": 1234, "avg_order": 121.55})
    print()
    show_report(report_generator, dashboard, {"total_items": 5000, "low_stock": 45, "out_of_stock": 12})
