"""Small JSON serialization helpers for CLI and logs."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


class SerializationError(ValueError):
    """Raised when a record cannot be encoded or decoded."""


def _default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def dumps(value: Any, *, pretty: bool = False) -> str:
    try:
        return json.dumps(value, default=_default, sort_keys=True, indent=2 if pretty else None)
    except (TypeError, ValueError) as exc:
        raise SerializationError(str(exc)) from exc


def loads_object(value: str) -> dict[str, Any]:
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SerializationError(f"invalid JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise SerializationError("expected a JSON object")
    return decoded


def required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SerializationError(f"{key} must be a non-empty string")
    return value.strip()


def optional_text(data: dict[str, Any], key: str, default: str | None = None) -> str | None:
    value = data.get(key, default)
    if value is None:
        return None
    if not isinstance(value, str):
        raise SerializationError(f"{key} must be a string")
    return value


def text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SerializationError(f"{key} must be a list of strings")
    return [item.strip() for item in value if item.strip()]


def merge_object(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in updates.items():
        if value is not None:
            result[key] = value
    return result
