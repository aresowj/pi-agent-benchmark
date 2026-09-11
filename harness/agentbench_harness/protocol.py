"""Stable JSON contract between the benchmark and worker-harness adapters."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


class ProtocolError(ValueError):
    """Raised for an invalid adapter request or result."""


@dataclass(frozen=True)
class ModelSpec:
    slot: str
    provider: str
    model: str
    thinking: str | None = None
    temperature: float | None = None
    temperature_supported: bool | None = None
    context_limit: int | None = None


@dataclass(frozen=True)
class RunRequest:
    run_id: str
    case_id: str
    start_sha: str
    worktree: str
    prompt: str
    model: ModelSpec
    session_dir: str
    timeout_seconds: int = 3600
    tool_policy: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        required = {
            "run_id": self.run_id,
            "case_id": self.case_id,
            "start_sha": self.start_sha,
            "worktree": self.worktree,
            "prompt": self.prompt,
            "session_dir": self.session_dir,
        }
        for name, value in required.items():
            if not value.strip():
                raise ProtocolError(f"{name} cannot be empty")
        if self.timeout_seconds <= 0:
            raise ProtocolError("timeout_seconds must be positive")
        if not Path(self.worktree).is_dir():
            raise ProtocolError(f"worktree does not exist: {self.worktree}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunRequest:
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ProtocolError("unsupported or missing schema_version")
        try:
            model_data = data["model"]
            model = ModelSpec(**model_data)
            request = cls(
                run_id=data["run_id"],
                case_id=data["case_id"],
                start_sha=data["start_sha"],
                worktree=data["worktree"],
                prompt=data["prompt"],
                model=model,
                session_dir=data["session_dir"],
                timeout_seconds=data.get("timeout_seconds", 3600),
                tool_policy=data.get("tool_policy", {}),
                environment=data.get("environment", {}),
            )
        except (KeyError, TypeError) as exc:
            raise ProtocolError(f"invalid run request: {exc}") from exc
        request.validate()
        return request

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


@dataclass
class Usage:
    fresh_input_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float | None = None


@dataclass
class RunResult:
    run_id: str
    adapter: str
    model: ModelSpec
    exit_state: str
    started_at: str
    ended_at: str
    wall_seconds: float
    log_path: str
    session_path: str | None = None
    usage: Usage = field(default_factory=Usage)
    tool_calls: int | None = None
    test_invocations: int | None = None
    stopped_reason: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, **asdict(self)}


def read_request(path: str | Path) -> RunRequest:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ProtocolError(f"cannot read request: {exc}") from exc
    if not isinstance(data, dict):
        raise ProtocolError("request must be a JSON object")
    return RunRequest.from_dict(data)


def write_result(path: str | Path, result: RunResult) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n")
