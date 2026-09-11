"""Health checks with no network dependency."""
# pyright: reportMissingImports=false

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from .models import HealthReport
from .registry import ProviderRegistry


@dataclass
class HealthChecker:
    component: str
    probe: Callable[[], None]

    def run(self) -> HealthReport:
        try:
            self.probe()
        except Exception as exc:
            return HealthReport(self.component, False, str(exc))
        return HealthReport(self.component, True, "ok")


def database_check(connection: sqlite3.Connection) -> HealthChecker:
    def probe() -> None:
        row = connection.execute("SELECT 1").fetchone()
        if row != (1,):
            raise RuntimeError("database probe returned an unexpected result")

    return HealthChecker("database", probe)


def providers_check(registry: ProviderRegistry) -> HealthChecker:
    def probe() -> None:
        if not registry.enabled():
            raise RuntimeError("no enabled providers")

    return HealthChecker("providers", probe)


def check_all(checkers: list[HealthChecker]) -> list[HealthReport]:
    return [checker.run() for checker in checkers]
