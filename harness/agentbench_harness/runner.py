"""Invoke any harness adapter that implements the JSON command contract."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from collections.abc import Sequence

from .protocol import ProtocolError, read_request


def invoke_adapter(
    adapter_command: Sequence[str],
    request_path: str | Path,
    result_path: str | Path,
    *,
    timeout_seconds: int | None = None,
    environment: dict[str, str] | None = None,
) -> int:
    """Run an adapter without interpreting model- or harness-specific behavior."""
    request = read_request(request_path)
    command = [*adapter_command, "--request", str(request_path), "--result", str(result_path)]
    env = os.environ.copy()
    env.update(request.environment)
    if environment:
        env.update(environment)
    completed = subprocess.run(
        command,
        cwd=request.worktree,
        env=env,
        check=False,
        timeout=timeout_seconds or request.timeout_seconds,
    )
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, help="shell command for the harness adapter")
    parser.add_argument("--request", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args(argv)
    try:
        return invoke_adapter(
            shlex.split(args.adapter),
            args.request,
            args.result,
        )
    except (OSError, ProtocolError, subprocess.TimeoutExpired) as exc:
        print(f"adapter invocation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
