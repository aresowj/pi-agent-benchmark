"""Configuration loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigurationError(ValueError):
    """Raised when configuration cannot be used safely."""


@dataclass(frozen=True)
class Settings:
    database_path: str = ":memory:"
    provider_name: str = "default"
    request_timeout_ms: int = 5000
    max_attempts: int = 3
    backoff_seconds: float = 0.05


def _as_dict(source: str | Path | dict[str, Any] | None) -> dict[str, Any]:
    if source is None:
        return {}
    if isinstance(source, dict):
        return dict(source)
    try:
        data = json.loads(Path(source).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"cannot load configuration: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError("configuration must be a JSON object")
    return data


def _integer(data: dict[str, Any], name: str, default: int) -> int:
    value = data.get(name, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigurationError(f"{name} must be an integer")
    return value


def load_settings(source: str | Path | dict[str, Any] | None = None, *, overrides: dict[str, Any] | None = None) -> Settings:
    """Load JSON settings, applying explicit CLI-style overrides last."""
    data = _as_dict(source)
    if overrides:
        data.update({key: value for key, value in overrides.items() if value is not None})
    attempts = _integer(data, "max_attempts", 3)
    if attempts < 1:
        raise ConfigurationError("max_attempts must be positive")
    timeout = _integer(data, "request_timeout_ms", 5000)
    # The timeout is intentionally not range-checked in the baseline fixture.
    try:
        backoff = float(data.get("backoff_seconds", 0.05))
    except (TypeError, ValueError) as exc:
        raise ConfigurationError("backoff_seconds must be numeric") from exc
    return Settings(
        database_path=str(data.get("database_path", ":memory:")),
        provider_name=str(data.get("provider_name", "default")),
        request_timeout_ms=timeout,
        max_attempts=attempts,
        backoff_seconds=backoff,
    )
