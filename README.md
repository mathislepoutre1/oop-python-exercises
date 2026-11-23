# OOP & Design Patterns in Python: exercises

![tests](https://github.com/mathislepoutre1/oop-python-exercises/actions/workflows/tests.yml/badge.svg)

My exercises for the course *Object Oriented Programming & Design Patterns in Python* (AIDAMS 2A).
Course website: https://courses.dallard.tech/

| # | Folder | Topic | Slides |
|---|---|---|---|
| 01 | [`01-git`](01-git) | Git workflow (full exercise in [bash-installer](https://github.com/mathislepoutre1/bash-installer)) | 19-26 |
| 02 | [`02-bash`](02-bash) | Bash script: set up a Python/Jupyter environment | 14-18 |
| 03 | [`03-oop`](03-oop) | Operator overloading, inheritance, ABC & Protocol | 27-41, 61-67 |
| 04 | [`04-uml`](04-uml) | UML: hospital system & ABCD Records (Mermaid diagrams + Python model) | 42-68 |
| 05 | [`05-design-patterns`](05-design-patterns) | Factory, Builder, Singleton, Adapter, Decorator, Strategy, Template Method | 69-87 |
| 06 | [`06-testing`](06-testing) | Unit, integration, property-based tests, mocking an LLM API, FastAPI | 88-93 |

Every folder has a README with what I did and what I learned. All the UML diagrams are written in Mermaid, so GitHub renders them.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                             # whole repo
pytest 05-design-patterns          # one exercise
pytest --cov --cov-report=term-missing
```

Every `.py` exercise file also runs on its own (`python 05-design-patterns/structural/decorator_order.py`) and prints the "expected usage" from the course.

## Repo organisation

```
.
├── 0X-topic/
│   ├── README.md        # statement link, answers, diagrams, notes
│   ├── *.py             # the exercise
│   └── tests/           # pytest tests for this exercise
├── pyproject.toml       # pytest config (import paths, markers)
├── requirements.txt
└── .github/workflows/   # CI: pytest on Python 3.11-3.13 + bash dry run
```

Git workflow: every exercise was developed on its own `feat/...` branch with small commits, then merged into `main` with `--no-ff`, so each exercise appears as its own merge in `git log --oneline --graph`.
