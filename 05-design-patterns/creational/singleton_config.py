"""Singleton pattern: configuration manager.

Problems with the original `load_config()` called in every module:
1. The file is read on every call: 4 disk reads for a single request.
2. No shared state: each module has its own copy.
3. A change made by one module isn't seen by the others.
4. Hard to mock in tests: there's no single place to override.

Refactoring: `ConfigManager.get_instance()` creates the object (and reads the file)
the first time, then always returns that same object.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(__file__).with_name("config.json")
_MISSING = object()


class ConfigManager:
    _instance: ConfigManager | None = None
    _lock = threading.Lock()  # two threads calling get_instance() at once still get ONE object

    def __init__(self, path: Path = DEFAULT_PATH):
        if ConfigManager._instance is not None:
            raise RuntimeError("Use ConfigManager.get_instance()")
        self.path = Path(path)
        self.load_count = 0
        self._config = self._load()

    def _load(self) -> dict:
        self.load_count += 1
        with self.path.open(encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def get_instance(cls, path: Path = DEFAULT_PATH) -> ConfigManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # double-checked locking
                    cls._instance = cls(path)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """For tests only: forget the instance so the next call reloads."""
        cls._instance = None

    def get(self, key: str, default: Any = _MISSING) -> Any:
        """Read a nested value with a dotted key: get("database.host")."""
        node: Any = self._config
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                if default is _MISSING:
                    raise KeyError(key)
                return default
            node = node[part]
        return node

    def set(self, key: str, value: Any) -> None:
        """Change a value in memory: every module sees it, because they share the instance."""
        *parents, last = key.split(".")
        node = self._config
        for part in parents:
            node = node.setdefault(part, {})
        node[last] = value


# ---- the 4 "modules" from the exercise, now using the singleton ----
def start_application() -> str:
    config = ConfigManager.get_instance()
    return f"Starting {config.get('app.name')} (debug={config.get('app.debug')})"


def connect_database() -> str:
    config = ConfigManager.get_instance()
    return f"Connecting to database at {config.get('database.host')}:{config.get('database.port')}"


def send_email(to: str, subject: str) -> str:
    config = ConfigManager.get_instance()
    return f"Sending '{subject}' to {to} from {config.get('email.sender')} via {config.get('email.smtp_host')}"


def process_payment(amount: float) -> str:
    config = ConfigManager.get_instance()
    return f"Processing {amount}€ in {config.get('payment.environment')} mode"


if __name__ == "__main__":
    for line in (start_application(), connect_database(),
                 send_email("user@test.com", "Welcome"), process_payment(99.99)):
        print(line)

    config = ConfigManager.get_instance()
    print("\nSame object everywhere:", config is ConfigManager.get_instance())
    print("File read", config.load_count, "time(s) for 4 modules")
