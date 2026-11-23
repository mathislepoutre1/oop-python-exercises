# 05 - Design patterns

Each file starts with the problems of the original code, then the refactored version. Running a file shows the expected usage.

- `creational/factory_payment.py`: Factory (payment system)
- `creational/builder_employee.py`: Builder (employee onboarding)
- `creational/singleton_config.py`: Singleton (config manager)
- `structural/adapter_report.py`: Adapter (XML report to JSON)
- `structural/decorator_order.py`: Decorator (order pricing)
- `behavioral/strategy_report.py`: Strategy (report formats)
- `behavioral/template_etl.py`: Template Method (ETL pipelines)

```bash
python creational/factory_payment.py
```

## Factory

The big if/elif is replaced by one class per payment method and a factory that uses a dict to find the right class. I added a crypto payment with `register()` without changing the other classes.

```mermaid
classDiagram
    class PaymentProcessor {
        <<abstract>>
        +validate(details) bool
        +compute_fee(amount) float
        +process(amount, details) dict
    }
    class CreditCardProcessor
    class BankTransferProcessor
    class PayPalProcessor
    class PaymentFactory {
        -_registry: dict
        +register(name, cls)
        +get_processor(payment_type)
    }
    PaymentProcessor <|-- CreditCardProcessor
    PaymentProcessor <|-- BankTransferProcessor
    PaymentProcessor <|-- PayPalProcessor
    PaymentFactory ..> PaymentProcessor : creates
```

## Builder

The function with 17 parameters is replaced by methods you can chain. Validation is done in `build()`. `DeveloperBuilder` and `InternBuilder` are presets.

```mermaid
classDiagram
    class Employee {
        +first_name
        +last_name
        +email
        +department
        +position
        +salary
        +has_laptop
        +has_admin_rights
    }
    class EmployeeBuilder {
        +with_name(first, last)
        +with_email(email)
        +with_job(dept, position, salary)
        +with_equipment(laptop, parking)
        +with_access(vpn, admin)
        +build() Employee
    }
    class DeveloperBuilder
    class InternBuilder
    EmployeeBuilder <|-- DeveloperBuilder
    EmployeeBuilder <|-- InternBuilder
    EmployeeBuilder ..> Employee : builds
```

## Singleton

The config file used to be read 4 times. Now `ConfigManager.get_instance()` reads it once and always returns the same object. `get("database.host")` reads nested values.

```mermaid
classDiagram
    class ConfigManager {
        -_instance: ConfigManager
        -_config: dict
        +get_instance() ConfigManager
        +get(key, default)
        +set(key, value)
        +reset()
    }
```

## Adapter

The old generator returns XML and can't be changed. `LegacyReportAdapter` wraps it and converts the XML to JSON for the dashboard.

```mermaid
classDiagram
    class ReportGeneratorInterface {
        <<interface>>
        +generate(data) str
    }
    class LegacyReportAdapter {
        -_legacy
        +generate(data) str
    }
    class LegacyReportGenerator {
        +generate_report(data) str
    }
    ReportGeneratorInterface <|.. LegacyReportAdapter
    LegacyReportAdapter o--> LegacyReportGenerator
```

## Decorator

The 5 boolean flags are replaced by decorators that wrap the order. The order of the wrapping is the order of the calculation.

```mermaid
classDiagram
    class OrderComponent {
        <<interface>>
        +get_cost() float
        +get_description() str
    }
    class BaseOrder
    class OrderDecorator {
        #_order
    }
    class ExpressShippingDecorator
    class InsuranceDecorator
    class GiftWrapDecorator
    class DiscountDecorator
    class PremiumMemberDecorator
    OrderComponent <|.. BaseOrder
    OrderComponent <|.. OrderDecorator
    OrderDecorator o--> OrderComponent
    OrderDecorator <|-- ExpressShippingDecorator
    OrderDecorator <|-- InsuranceDecorator
    OrderDecorator <|-- GiftWrapDecorator
    OrderDecorator <|-- DiscountDecorator
    DiscountDecorator <|-- PremiumMemberDecorator
```

## Strategy

One class per format instead of the if/elif chains. The format can be changed with `set_strategy()`. I added HTML without changing the other classes.

```mermaid
classDiagram
    class FormatStrategy {
        <<interface>>
        +extension
        +format(data) str
    }
    class PDFFormatStrategy
    class ExcelFormatStrategy
    class CSVFormatStrategy
    class JSONFormatStrategy
    class HTMLFormatStrategy
    class ReportGenerator {
        -_strategy
        +set_strategy(strategy)
        +generate_report() str
        +save_report(filename)
    }
    FormatStrategy <|.. PDFFormatStrategy
    FormatStrategy <|.. ExcelFormatStrategy
    FormatStrategy <|.. CSVFormatStrategy
    FormatStrategy <|.. JSONFormatStrategy
    FormatStrategy <|.. HTMLFormatStrategy
    ReportGenerator o--> FormatStrategy
```

## Template Method

`run()` is written once in the base class and calls the steps in order. Each pipeline only writes `extract()` and `transform()`. I added `XMLPipeline` to check it works.

```mermaid
classDiagram
    class DataPipeline {
        <<abstract>>
        +run() str
        +extract() list
        +transform(data) list
        +connect()
        +validate()
        +load()
        +cleanup()
        +before_run()
        +after_run()
    }
    class CSVPipeline
    class APIPipeline
    class DatabasePipeline
    class XMLPipeline
    DataPipeline <|-- CSVPipeline
    DataPipeline <|-- APIPipeline
    DataPipeline <|-- DatabasePipeline
    DataPipeline <|-- XMLPipeline
```
