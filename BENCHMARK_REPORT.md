# Agent benchmark report

Generated: 2026-09-12T06:44:25.646680+00:00
Frozen base/case SHA: `2d91e72b58ce134907ce083e5520e75e41a4c89e`
Repository: private `https://github.com/aresowj/pi-agent-benchmark`

## Scope and reproducibility

The original matrix was 4 models × 6 cases = 24 pass@1 runs. The requested `LUNA_MAX` and `SONNET_5` extensions added twelve independent pass@1 runs, for 36 initial runs total. Each run used a fresh session and clean worktree at the same case-start SHA; hidden evaluators and run artifacts stayed outside worker worktrees.
Evaluator integrity note: preflight exposed evaluator-only assumptions in the first implementation of cases 4–6. Before final scoring, those external evaluators were corrected without changing any worker worktree or prompts, then all 36 worktrees were evaluated. The exact corrected evaluator hashes and the correction note are in `evaluators/evaluator_manifest.json`; treat the case-5 scaling timing as a frozen-base calibration recorded in that manifest.

Model aliases:
- `LOCAL_QWEN_Q3`: `llama-server=http://127.0.0.1:8080/qwen3.8-27b`
- `DEEPSEEK`: `openrouter/deepseek/deepseek-v4.1-flash`
- `GLM`: `openrouter/z-ai/glm-5.3`
- `TERRA`: `openai-codex/gpt-5.6-terra`
- `LUNA_MAX`: `openai-codex/gpt-5.6-luna`
- `SONNET_5`: `openrouter/anthropic/claude-sonnet-5`

Temperature was provider-default for all slots because the configured catalogs expose no temperature control. Terra used requested `medium` reasoning; Luna used requested `max`; other slots used provider default reasoning. Unsupported metrics are not estimated.
Pass@1 is strict autonomous outcome: visible and hidden tests must pass **and** the worker must exit normally. Thus GLM is 5/6 operational pass@1 with one infrastructure failure; among its five completed workers, code correctness was 5/5. The infrastructure failure is not treated as a reasoning defect.

## Overall pass@1

Case 3 (duplicate delivery) is designated Medium/Hard and is counted in Hard here so the buckets remain disjoint. Aggregate times and costs use unrounded source values; displayed per-run rows are rounded.

| Model | Pass@1 | Easy | Medium | Hard | Very hard | Total time | Output tokens | Cloud cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LOCAL_QWEN_Q3 | 6/6 | 1/1 | 1/1 | 3/3 | 1/1 | 1145.7s | 45,370 | $0.0000 |
| DEEPSEEK | 6/6 | 1/1 | 1/1 | 3/3 | 1/1 | 1184.0s | 56,949 | $0.0668 |
| GLM | 5/6 | 1/1 | 0/1 | 3/3 | 1/1 | 374.5s | 39,821 | $0.4219 |
| TERRA | 6/6 | 1/1 | 1/1 | 3/3 | 1/1 | 384.5s | 16,375 | $0.4491 |

LUNA_MAX extension (requested after the original four-model matrix): `6/6` pass@1, 380.2s total, 14,027 output tokens, $0.0422 cloud cost. It is reported separately and does not alter the required four-model comparison.
SONNET_5 extension: `6/6` pass@1, 352.2s total, 28,468 output tokens, $0.6568 cloud cost. Token totals: 146 fresh input, 575,601 cache-read input, 28,468 output (575,747 total processed input). It is reported separately and does not alter the required four-model comparison.

## Detailed initial runs

| Case | Model | Pass | Visible tests | Hidden tests | Time | Fresh input | Cache read | Output | Cost | Diff +/- | Tools | Worker test invocations |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| case01 | LOCAL_QWEN_Q3 | PASS | 19 | 10 | 53.7s | 6,852 | 64,189 | 3,077 | $0.0000 | +58/-6 | 13 | 4 |
| case01 | DEEPSEEK | PASS | 25 | 10 | 117.0s | 10,647 | 98,560 | 3,510 | $0.0040 | +66/-6 | 21 | 5 |
| case01 | GLM | PASS | 32 | 10 | 17.0s | 5,372 | 72,832 | 2,662 | $0.0382 | +76/-6 | 17 | 5 |
| case01 | TERRA | PASS | 19 | 10 | 38.7s | 15,557 | 39,424 | 1,399 | $0.0558 | +33/-8 | 15 | 6 |
| case01 | LUNA_MAX | PASS | 20 | 10 | 55.0s | 16,919 | 51,712 | 2,243 | $0.0071 | +42/-5 | 18 | 8 |
| case01 | SONNET_5 | PASS | 22 | 10 | 56.9s | 27 | 125,135 | 4,809 | $0.1285 | +40/-5 | 15 | 3 |
| case02 | LOCAL_QWEN_Q3 | PASS | 16 | 3 | 34.1s | 2,993 | 38,488 | 1,974 | $0.0000 | +34/-2 | 9 | 4 |
| case02 | DEEPSEEK | PASS | 16 | 3 | 69.5s | 14,732 | 19,712 | 2,442 | $0.0037 | +35/-2 | 13 | 4 |
| case02 | GLM | FAIL | 17 | 3 | 24.9s | 2,573 | 9,280 | 923 | $0.0101 | +39/-2 | 7 | 2 |
| case02 | TERRA | PASS | 14 | 3 | 23.3s | 9,690 | 8,192 | 755 | $0.0301 | +11/-2 | 9 | 4 |
| case02 | LUNA_MAX | PASS | 14 | 3 | 34.8s | 13,389 | 10,752 | 974 | $0.0041 | +13/-2 | 8 | 2 |
| case02 | SONNET_5 | PASS | 14 | 3 | 16.3s | 11 | 18,348 | 938 | $0.0260 | +14/-2 | 6 | 2 |
| case03 | LOCAL_QWEN_Q3 | PASS | 21 | 3 | 106.2s | 5,438 | 133,877 | 5,614 | $0.0000 | +154/-4 | 21 | 5 |
| case03 | DEEPSEEK | PASS | 19 | 3 | 86.6s | 64,443 | 294,144 | 12,308 | $0.0179 | +122/-10 | 37 | 6 |
| case03 | GLM | PASS | 16 | 3 | 106.5s | 18,050 | 290,560 | 12,021 | $0.1537 | +89/-6 | 31 | 8 |
| case03 | TERRA | PASS | 15 | 3 | 75.9s | 18,981 | 101,376 | 2,977 | $0.0940 | +48/-5 | 19 | 5 |
| case03 | LUNA_MAX | PASS | 14 | 3 | 70.5s | 19,568 | 59,392 | 2,901 | $0.0086 | +42/-5 | 20 | 3 |
| case03 | SONNET_5 | PASS | 14 | 3 | 72.0s | 29 | 148,348 | 5,566 | $0.1439 | +54/-6 | 16 | 4 |
| case04 | LOCAL_QWEN_Q3 | PASS | 24 | 7 | 203.6s | 6,580 | 266,874 | 11,683 | $0.0000 | +203/-98 | 27 | 17 |
| case04 | DEEPSEEK | PASS | 27 | 7 | 515.5s | 39,703 | 450,304 | 17,528 | $0.0178 | +187/-88 | 30 | 13 |
| case04 | GLM | PASS | 22 | 7 | 56.2s | 6,356 | 159,168 | 7,494 | $0.0833 | +214/-104 | 22 | 7 |
| case04 | TERRA | PASS | 19 | 7 | 104.3s | 27,910 | 64,000 | 4,846 | $0.1268 | +125/-97 | 17 | 6 |
| case04 | LUNA_MAX | PASS | 13 | 7 | 68.3s | 28,430 | 40,960 | 2,915 | $0.0100 | +85/-94 | 15 | 3 |
| case04 | SONNET_5 | PASS | 18 | 7 | 70.9s | 27 | 120,553 | 6,492 | $0.1425 | +145/-105 | 16 | 5 |
| case05 | LOCAL_QWEN_Q3 | PASS | 16 | 3 | 392.2s | 5,038 | 108,296 | 7,253 | $0.0000 | +126/-4 | 16 | 6 |
| case05 | DEEPSEEK | PASS | 18 | 3 | 252.2s | 34,087 | 167,808 | 9,539 | $0.0113 | +201/-4 | 23 | 6 |
| case05 | GLM | PASS | 20 | 3 | 33.8s | 6,585 | 35,264 | 5,519 | $0.0427 | +142/-5 | 9 | 4 |
| case05 | TERRA | PASS | 14 | 3 | 60.3s | 13,379 | 27,136 | 2,634 | $0.0638 | +37/-3 | 12 | 5 |
| case05 | LUNA_MAX | PASS | 14 | 3 | 80.4s | 13,061 | 17,408 | 1,821 | $0.0051 | +25/-4 | 11 | 3 |
| case05 | SONNET_5 | PASS | 18 | 3 | 73.2s | 29 | 89,255 | 6,103 | $0.1159 | +96/-4 | 14 | 7 |
| case06 | LOCAL_QWEN_Q3 | PASS | 16 | 4 | 356.0s | 4,888 | 240,600 | 15,769 | $0.0000 | +152/-13 | 21 | 10 |
| case06 | DEEPSEEK | PASS | 14 | 4 | 143.1s | 28,940 | 228,736 | 11,622 | $0.0120 | +77/-9 | 26 | 8 |
| case06 | GLM | PASS | 16 | 4 | 136.1s | 5,713 | 141,312 | 11,202 | $0.0940 | +185/-12 | 17 | 7 |
| case06 | TERRA | PASS | 14 | 4 | 82.0s | 13,275 | 34,816 | 3,764 | $0.0787 | +71/-7 | 12 | 5 |
| case06 | LUNA_MAX | PASS | 14 | 4 | 71.2s | 14,219 | 31,232 | 3,173 | $0.0073 | +54/-9 | 14 | 3 |
| case06 | SONNET_5 | PASS | 14 | 4 | 62.9s | 23 | 73,962 | 4,560 | $0.1000 | +80/-11 | 11 | 4 |

## Successful-run efficiency

Only pass@1-successful runs are included below; failed/infrastructure-run costs are excluded from cost per successful task.

| Model | Successful tasks | Median time | Median output / task | Median fresh input / task | Median cache read / task | Cost / successful task | Successful tasks / hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| LOCAL_QWEN_Q3 | 6 | 154.9s | 6,434 | 5,238 | 121,086 | $0.0000 | 18.85 |
| DEEPSEEK | 6 | 130.1s | 10,580 | 31,514 | 198,272 | $0.0111 | 18.24 |
| GLM | 5 | 56.2s | 7,494 | 6,356 | 141,312 | $0.0824 | 51.50 |
| TERRA | 6 | 68.1s | 2,806 | 14,468 | 37,120 | $0.0748 | 56.18 |

LUNA_MAX extension efficiency: 6 successful tasks; median 69.4s; median output 2,572; cost per successful task $0.0070. It is supplementary, not part of the required four-model efficiency ranking.
SONNET_5 extension efficiency: 6 successful tasks; median 66.9s; median output 5,188; cost per successful task $0.1095. It is supplementary, not part of the required four-model efficiency ranking.

For local inference, API cost is $0. Its pass@1-successful aggregate was 39.6 output tokens/sec across the six runs; electricity is not estimated.

## Selective rerun / pass@3

Only GLM case02 was rerun because trial 1 hit an infrastructure rate limit. Trial 2 and trial 3 were fresh independent worktrees/sessions and both passed. Under the strict autonomous-attempt scoring used for pass@1, the requested GLM case02 pass@3 outcome is PASS (2 passing attempts after 1 failed infrastructure attempt). No other extra worker trials were run; non-rerun cases have no pass@3 estimate by design.

| Model | Case | Trial 1 | Trial 2 | Trial 3 | Pass@3 (attempt-based) |
|---|---|---:|---:|---:|---:|
| GLM | case02 | FAIL | PASS | PASS | PASS |

## Performance baseline

Case 5 frozen baseline timings: small workload `0.0923s`; original large workload `3.1083s`; scaling workload `1.0570s`. Correctness and the external performance ratio gate passed for every completed candidate run.

## Failure analysis

| Run | Dominant category | Factual explanation |
|---|---|---|
| GLM case02 trial1 | tool/infrastructure failure | OpenRouter returned HTTP 429 `new-account-rpm/z-ai/glm-5.3`; Pi exited status 1. The worktree left by the stopped worker passed visible and hidden tests, but it is not an autonomous pass@1. |

No correctness, performance, concurrency, loop/stall, or premature-stop failure occurred among the other completed initial runs.

## Conclusions

1. **Does LOCAL_QWEN_Q3 match cloud models on easy work?** Yes in this sample: 1/1 on case01, equal to DeepSeek, Terra, Luna, and Sonnet 5; GLM also passed its completed easy run.
2. **Where does LOCAL_QWEN_Q3 begin losing materially?** Nowhere observed: it passed all six cases. This is a six-case, one-trial result, not evidence of parity at larger difficulty or sample sizes.
3. **Do DeepSeek or Sonnet 5 materially improve quality over LOCAL_QWEN_Q3?** No observed quality improvement: both passed all six cases, as did Local. DeepSeek and Sonnet used cloud time/cost, so their operational advantage is not established by correctness here.
4. **Does GLM materially improve over DeepSeek?** No quality conclusion is supported. GLM passed its five completed cases, but case02 trial1 was an OpenRouter rate-limit failure; the two selective reruns passed.
5. **Does Terra Medium or Sonnet 5 materially outperform cheaper models on hard work?** No correctness advantage was observed: Terra, Local, DeepSeek, Luna, and Sonnet all passed cases03–06. Speed/cost differences are descriptive only, not a proven quality advantage.
6. **How many additional successful tasks does each more expensive tier buy?** Zero additional code-correct tasks were demonstrated among completed runs; every completed worker passed its case. GLM had one operational loss from infrastructure, not a measured reasoning failure.
7. **Does a slower stronger model finish sooner by making fewer mistakes?** Not demonstrated. All completed slots made no correctness mistakes in this matrix, so there is no error-avoidance effect to attribute.
8. **Operational recommendation (unvalidated policy suggestion, not a benchmark-derived quality winner):** default worker = LOCAL_QWEN_Q3; cheapest observed cloud option = LUNA_MAX; DEEPSEEK is an observed 6/6 alternate; Terra Medium, GLM, or Sonnet 5 are speed-oriented options only when their latency/capability policy justifies their higher observed cost. No slot earned a demonstrated quality-based escalation in this ceiling-effect sample.

## Review note

GPT-5.6 Sol at light thinking was reserved for reviewing this report and was not used as a worker benchmark slot, per the user’s instruction. Sonnet 5 was a separate six-case extension using provider-default reasoning.
