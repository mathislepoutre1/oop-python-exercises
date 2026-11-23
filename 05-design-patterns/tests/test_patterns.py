import json

import pytest

from adapter_report import (AnalyticsDashboard, LegacyReportAdapter, LegacyReportGenerator,
                            ReportGeneratorInterface, show_report)
from builder_employee import DeveloperBuilder, EmployeeBuilder, InternBuilder
from decorator_order import (BaseOrder, DiscountDecorator, ExpressShippingDecorator,
                             GiftWrapDecorator, InsuranceDecorator, PremiumMemberDecorator)
from factory_payment import PaymentFactory, PaymentProcessor
from singleton_config import ConfigManager, connect_database, process_payment
from strategy_report import (CSVFormatStrategy, FormatStrategy, HTMLFormatStrategy,
                             JSONFormatStrategy, PDFFormatStrategy, ReportGenerator)
from template_etl import APIPipeline, CSVPipeline, DatabasePipeline, DataPipeline, XMLPipeline

CARD = {"card_number": "1234567890123456", "cvv": "123"}


# ======================= Factory
@pytest.mark.parametrize("kind, details, total, fee", [
    ("credit_card", CARD, 102.9, 2.9),
    ("bank_transfer", {"iban": "FR7630006000011234567890189"}, 101.5, 1.5),
    ("paypal", {"email": "a@b.c"}, 103.7, 3.7),
])
def test_factory_returns_right_processor(kind, details, total, fee):
    result = PaymentFactory().get_processor(kind).process(100.0, details)
    assert result == {"success": True, "method": kind, "amount": total, "fee": fee}


@pytest.mark.parametrize("kind, details, error", [
    ("credit_card", {"card_number": "123", "cvv": "123"}, "Invalid card number"),
    ("credit_card", {"card_number": "1234567890123456"}, "Invalid CVV"),
    ("bank_transfer", {"iban": "FR76"}, "Invalid IBAN"),
    ("paypal", {"email": "nope"}, "Invalid PayPal email"),
])
def test_factory_validation_errors(kind, details, error):
    assert PaymentFactory().get_processor(kind).process(100, details) == {"success": False, "error": error}


def test_factory_unknown_type():
    with pytest.raises(ValueError, match="Unknown payment type"):
        PaymentFactory().get_processor("cheque")


def test_factory_is_open_for_extension():
    class ApplePay(PaymentProcessor):
        method = "apple_pay"
        def validate(self, details): return True
        def compute_fee(self, amount): return 0

    PaymentFactory.register("apple_pay", ApplePay)
    assert PaymentFactory().get_processor("apple_pay").process(10, {})["amount"] == 10


# ======================= Builder
def test_builder_fluent_chain():
    e = (EmployeeBuilder().with_name("John", "Doe").with_email("john@co.com")
         .with_job("Engineering", "Senior Developer", 75000)
         .with_equipment(laptop=True).with_access(vpn=True, admin=True).build())
    assert (e.full_name, e.has_laptop, e.has_admin_rights, e.has_parking) == ("John Doe", True, True, False)


def test_builder_presets():
    dev = DeveloperBuilder("A", "B", "a@b.c").build()
    intern = InternBuilder("C", "D", "c@d.e", "Marketing", manager_id=42).build()
    assert dev.has_admin_rights and dev.department == "Engineering"
    assert intern.contract_type == "internship" and intern.manager_id == 42
    assert not intern.has_admin_rights


@pytest.mark.parametrize("builder, message", [
    (EmployeeBuilder().with_email("a@b.c").with_job("X", "Y", 1), "Missing required fields: first_name"),
    (EmployeeBuilder().with_name("A", "B").with_email("bad").with_job("X", "Y", 1), "Valid email"),
    (EmployeeBuilder().with_name("A", "B").with_email("a@b.c").with_job("X", "Y", -1), "negative"),
    (EmployeeBuilder().with_name("A", "B").with_email("a@b.c").with_job("X", "Y", 1)
        .with_access(admin=True), "Admin rights require VPN"),
])
def test_builder_validation(builder, message):
    with pytest.raises(ValueError, match=message):
        builder.build()


def test_built_employee_is_immutable():
    e = DeveloperBuilder("A", "B", "a@b.c").build()
    with pytest.raises(AttributeError):
        e.salary = 1


# ======================= Singleton
@pytest.fixture
def fresh_config():
    ConfigManager.reset()
    yield
    ConfigManager.reset()


def test_singleton_same_instance_loaded_once(fresh_config):
    a = ConfigManager.get_instance()
    connect_database()
    process_payment(10)
    assert a is ConfigManager.get_instance()
    assert a.load_count == 1


def test_singleton_nested_get_and_default(fresh_config):
    config = ConfigManager.get_instance()
    assert config.get("database.host") == "localhost"
    assert config.get("app.debug") is True
    assert config.get("app.missing", "x") == "x"
    with pytest.raises(KeyError):
        config.get("nope.nothing")


def test_singleton_changes_are_shared(fresh_config):
    ConfigManager.get_instance().set("database.host", "db.prod")
    assert "db.prod" in connect_database()


def test_singleton_with_test_config(fresh_config, tmp_path):
    fake = tmp_path / "config.json"
    fake.write_text(json.dumps({"payment": {"environment": "test"}}))
    ConfigManager.get_instance(fake)
    assert process_payment(5) == "Processing 5€ in test mode"


def test_singleton_direct_constructor_forbidden(fresh_config):
    ConfigManager.get_instance()
    with pytest.raises(RuntimeError):
        ConfigManager()


# ======================= Adapter
def test_adapter_really_converts_the_xml():
    adapter = LegacyReportAdapter(LegacyReportGenerator())
    assert isinstance(adapter, ReportGeneratorInterface)
    assert json.loads(adapter.generate({"total_sales": 150000, "avg_order": 121.55, "region": "EU"})) == \
        {"total_sales": 150000, "avg_order": 121.55, "region": "EU"}


def test_adapter_uses_the_legacy_object(mocker):
    legacy = LegacyReportGenerator()
    spy = mocker.spy(legacy, "generate_report")
    LegacyReportAdapter(legacy).generate({"a": 1})
    spy.assert_called_once_with({"a": 1})


def test_dashboard_through_adapter(capsys):
    out = show_report(LegacyReportAdapter(LegacyReportGenerator()), AnalyticsDashboard(), {"orders": 1234})
    assert "orders: 1234" in out


# ======================= Decorator
def test_decorators_match_original_calculation():
    order = PremiumMemberDecorator(DiscountDecorator(GiftWrapDecorator(InsuranceDecorator(
        ExpressShippingDecorator(BaseOrder(100.0)))), percent=15))
    # 100 + 15 + 5 + 5 = 125 ; -15% = 106.25 ; -10% = 95.625
    assert order.get_cost() == pytest.approx(95.625)
    assert order.get_description().splitlines() == [
        "Base price: 100.00€", "Express shipping: +15.00€", "Insurance (5%): +5.00€",
        "Gift wrap: +5.00€", "Discount (15%): -18.75€", "Premium member (10%): -10.62€"]


def test_decorator_order_changes_result():
    discount_first = ExpressShippingDecorator(DiscountDecorator(BaseOrder(100), 10))
    shipping_first = DiscountDecorator(ExpressShippingDecorator(BaseOrder(100)), 10)
    assert discount_first.get_cost() == 105
    assert shipping_first.get_cost() == pytest.approx(103.5)


def test_simple_order_and_bad_discount():
    assert BaseOrder(42).get_cost() == 42
    with pytest.raises(ValueError):
        DiscountDecorator(BaseOrder(1), 150)


# ======================= Strategy
DATA = [{"name": "Sales Q1", "value": 15000}, {"name": "Sales Q2", "value": 18000}]


def test_strategy_switch_at_runtime():
    gen = ReportGenerator(DATA)
    gen.set_strategy(CSVFormatStrategy())
    assert gen.generate_report() == "name,value\nSales Q1,15000\nSales Q2,18000\n"
    gen.set_strategy(JSONFormatStrategy())
    assert json.loads(gen.generate_report()) == DATA
    gen.set_strategy(PDFFormatStrategy())
    assert gen.generate_report().startswith("PDF REPORT")


def test_strategy_html_added_without_changes():
    assert "<td>Sales Q1</td><td>15000</td>" in ReportGenerator(DATA, HTMLFormatStrategy()).generate_report()


def test_strategy_new_format_in_test():
    class Upper(FormatStrategy):
        extension = ".txt"
        def format(self, data): return " ".join(d["name"].upper() for d in data)
    assert ReportGenerator(DATA, Upper()).generate_report() == "SALES Q1 SALES Q2"


def test_strategy_save_uses_extension(tmp_path):
    path = ReportGenerator(DATA, CSVFormatStrategy()).save_report(tmp_path / "sales")
    assert path.name == "sales.csv" and path.read_text().startswith("name,value")


def test_strategy_missing():
    with pytest.raises(RuntimeError):
        ReportGenerator(DATA).generate_report()


# ======================= Template method
@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(DataPipeline, "delay", 0)


@pytest.mark.parametrize("cls, expected", [
    (CSVPipeline, "CSV Pipeline finished"), (APIPipeline, "API Pipeline finished"),
    (DatabasePipeline, "Database Pipeline finished"), (XMLPipeline, "XML Pipeline finished"),
])
def test_every_pipeline_runs_the_same_workflow(cls, expected, capsys):
    p = cls("src")
    assert p.run() == expected
    assert p.data is None  # cleanup ran
    assert p.steps.index("Validation passed") < p.steps.index("Cleanup complete")


def test_transforms():
    assert CSVPipeline("x").transform(CSVPipeline("x").extract())[0] == {"id": 1, "name": "ALICE", "age": 30}
    api = APIPipeline("x")
    assert [r["grade"] for r in api.transform(api.extract())] == ["B", "A"]
    xml = XMLPipeline("x")
    assert xml.transform(xml.extract())[1] == {"order_id": 9002, "customer": "Bob", "total": 120.0}


def test_validation_fails_but_cleanup_still_runs(capsys):
    class Broken(CSVPipeline):
        def extract(self):
            return [{"name": "no id", "age": "1"}]

    p = Broken("x")
    with pytest.raises(ValueError, match="missing"):
        p.run()
    assert p.steps[-1] == "Cleanup complete"


def test_cannot_create_pipeline_without_steps():
    with pytest.raises(TypeError):
        DataPipeline("x")
