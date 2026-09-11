"""Pi CLI adapter for the harness-neutral benchmark protocol."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .protocol import RunResult, Usage, read_request, write_result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_file(session_dir: Path) -> Path | None:
    files = list(session_dir.rglob("*.jsonl")) if session_dir.exists() else []
    return max(files, key=lambda path: path.stat().st_mtime_ns) if files else None


def _int_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError, OverflowError):
        return 0


def _float_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return None


def _usage(session_path: Path | None) -> tuple[Usage, int, int]:
    usage = Usage()
    tool_calls = 0
    test_invocations = 0
    if session_path is None:
        return usage, tool_calls, test_invocations
    for line in session_path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message", {})
        if not isinstance(message, dict):
            continue
        if message.get("role") == "assistant":
            values = message.get("usage", {})
            if isinstance(values, dict):
                usage.fresh_input_tokens += _int_value(values.get("input"))
                usage.cache_read_tokens += _int_value(values.get("cacheRead"))
                usage.cache_write_tokens += _int_value(values.get("cacheWrite"))
                usage.output_tokens += _int_value(values.get("output"))
                usage.reasoning_tokens += _int_value(values.get("reasoning"))
                cost = values.get("cost", {})
                if isinstance(cost, dict):
                    amount = _float_value(cost.get("total"))
                    if amount is not None:
                        usage.cost_usd = (usage.cost_usd or 0.0) + amount
            content = message.get("content", [])
            if isinstance(content, list):
                tool_calls += sum(
                    1 for item in content
                    if isinstance(item, dict) and item.get("type") in {"toolCall", "tool_call"}
                )
        text = json.dumps(event, sort_keys=True)
        if re.search(r"(?:pytest|python(?:3)?\s+-m\s+unittest)", text):
            test_invocations += 1
    return usage, tool_calls, test_invocations


def _command(request: Any) -> list[str]:
    llama_extension = os.environ.get(
        "AGENTBENCH_PI_LLAMA_EXTENSION",
        "/home/kagami/.pi/agent/npm/node_modules/pi-llama-cpp/src/index.ts",
    )
    command = [
        "pi",
        "--provider", request.model.provider,
        "--model", request.model.model,
        "--mode", "text",
        "--print",
        "--session-dir", request.session_dir,
        "--session-id", request.run_id,
        "--no-context-files",
        "--no-extensions",
        "--extension", llama_extension,
        "--no-skills",
        "--no-prompt-templates",
        "--no-themes",
        "--no-approve",
        "--tools", "read,bash,edit,write",
    ]
    if request.model.thinking:
        command.extend(["--thinking", request.model.thinking])
    return [*command, "--", request.prompt]


def run(request_path: str, result_path: str) -> int:
    request = read_request(request_path)
    result_file = Path(result_path)
    result_file.parent.mkdir(parents=True, exist_ok=True)
    session_dir = Path(request.session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    log_path = result_file.parent / f"{request.run_id}.pi.log"
    started = _now()
    monotonic = time.monotonic()
    exit_state = "completed"
    stopped_reason: str | None = None
    error: str | None = None
    try:
        worker_environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {
                "PI_SESSION_FILE",
                "PI_SESSION_ID",
                "PI_SUBAGENT_PARENT_SESSION",
                "PI_PROVIDER",
                "PI_MODEL",
                "PI_REASONING_LEVEL",
            }
        }
        worker_environment.update(request.environment)
        with log_path.open("w", encoding="utf-8") as log:
            completed = subprocess.run(
                _command(request),
                cwd=request.worktree,
                env=worker_environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=request.timeout_seconds,
                text=True,
            )
        if completed.returncode != 0:
            exit_state = "crashed"
            stopped_reason = f"pi exited with status {completed.returncode}"
    except subprocess.TimeoutExpired:
        exit_state = "timed_out"
        stopped_reason = f"exceeded {request.timeout_seconds}s timeout"
    except OSError as exc:
        exit_state = "infrastructure_error"
        error = str(exc)
    session_path = _session_file(session_dir)
    usage, tool_calls, test_invocations = _usage(session_path)
    result = RunResult(
        run_id=request.run_id,
        adapter="pi",
        model=request.model,
        exit_state=exit_state,
        started_at=started,
        ended_at=_now(),
        wall_seconds=time.monotonic() - monotonic,
        log_path=str(log_path),
        session_path=str(session_path) if session_path else None,
        usage=usage,
        tool_calls=tool_calls,
        test_invocations=test_invocations,
        stopped_reason=stopped_reason,
        error=error,
    )
    write_result(result_path, result)
    return 0 if exit_state == "completed" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args(argv)
    try:
        return run(args.request, args.result)
    except Exception as exc:
        print(f"pi adapter failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
