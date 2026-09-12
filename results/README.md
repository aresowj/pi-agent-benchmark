# Benchmark results

- `initial_runs.json` contains sanitized per-run metrics for the 30 initial worker runs.
- `selective_reruns.json` contains the two additional GLM case02 runs.
- Complete agent/session logs and raw diffs are retained in the external benchmark control directory; they are not copied into worker worktrees.
- Hidden evaluators are checked in only after execution under `evaluators/hidden/`; the case-start branches used by workers do not contain them.
