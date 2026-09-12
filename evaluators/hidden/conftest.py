"""External evaluator configuration; never copy this directory into a worker tree."""

from __future__ import annotations

import os
import sys
from pathlib import Path


candidate = Path(os.environ.get("AGENTBENCH_CANDIDATE", ""))
if not candidate.is_dir():
    raise RuntimeError("AGENTBENCH_CANDIDATE must point to a candidate worktree")
sys.path.insert(0, str(candidate / "src"))
