# Harness adapter contract

The benchmark owns the frozen repository, case-start SHA, exact prompt, clean worktree, hidden evaluators, and scoring. A worker harness is an external command adapter, so the same case can be run by Pi, another coding-agent CLI, or a custom runner without changing the fixture or prompt.

An adapter command receives:

```text
<adapter> --request REQUEST.json --result RESULT.json
```

`REQUEST.json` has `schema_version: 1`, a `run_id`, `case_id`, `start_sha`, worker `worktree`, exact `prompt`, `model` (`slot`, `provider`, `model`, optional `thinking`, temperature metadata, and context limit), isolated `session_dir`, timeout, tool policy, and adapter environment.

The adapter must start a fresh worker session, use the assigned worktree as its working directory, pass the prompt unchanged, and write `RESULT.json` even for a worker crash or timeout. The result records adapter identity, selected model, exit state, timestamps, wall time, complete log/session paths, token/cache/cost usage when available, tool calls, test invocations, and a factual stop/error reason.

The public Pi adapter is runnable from the repository root:

```sh
python -m harness.agentbench_harness.pi_adapter \
  --request /path/to/request.json \
  --result /path/to/result.json
```

Other harnesses only need to implement the same command contract. They must not receive hidden evaluator paths or expected implementations. The orchestrator treats unsupported metrics as `null` rather than estimating them.
