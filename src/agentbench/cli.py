"""Command-line entry point."""
# pyright: reportMissingImports=false

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentbench")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--request-timeout-ms", type=int, dest="request_timeout_ms")
    parser.add_argument("--database-path", dest="database_path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = vars(build_parser().parse_args(argv))
    config_path = args.pop("config")
    settings = load_settings(config_path, overrides=args)
    print(json.dumps(settings.__dict__, sort_keys=True))
    return 0
