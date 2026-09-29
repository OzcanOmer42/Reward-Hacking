# STATUS

Last updated: 2026-09-29 (session 3)

## Current phase

**Phase 0: CLOSED 2026-09-28.**

**R1 done 2026-09-29:** qwen3:14b, sandbox_score, 100 episodes, 0 exploit attempts (FINDINGS R1).

**Now: P2, the hard variant** (pre-registered in FINDINGS). Pilot of 10 episodes, then the
100-episode main run. Phase 1 (detector precision) waits for an environment that produces
exploits, because precision cannot be measured with zero positives.

## Budget

- API budget ceiling: **$0.00, set by Omer on 2026-09-28.** No paid API calls.
- Spend to date: **$0.00.**
- Models run locally and free through Ollama on Omer's Mac (24 GB RAM).
  First model: `qwen3:14b` (9.3 GB download, per ollama.com/library/qwen3).
- Frontier models only if free credits arrive (Anthropic External Researcher Access
  Program, $1,000 API credits for AI safety research, reviewed the first Monday of each
  month). Applying is optional and free. `harness/prices.json` keeps verified prices in case.
- Enforcement unchanged: `BudgetGuard` before every call; the CLI refuses a paid model
  without `--cap-usd`.

## Done

- Contract agreed and in `harness/contract.py`.
- Runner: step cap, repeat cap, text-only nudge, retries, served-model check, cost
  accounting, leak scan, never overwrites a transcript.
- sandbox_score at five levels, with `LEVELS.md`.
- Ollama adapter, resumable batch runner (`harness/batch.py`), results table with 90%
  Wilson intervals (`analysis/summary.py`).
- Scripted null-test agents. 42 tests: conformance, determinism, level invariance over
  20 seeds, detector nulls, path aliasing, proxy parsing, robustness, leakage and a null
  test of the leak detector, budget, Anthropic adapter against a fake client.
- FINDINGS.md seeded with "Ways this could be wrong".

## Next

1. **P3 capability probe first** (20 minutes): does qwen3:14b edit score.json when told it may?
   Decision rule in FINDINGS P3. The 19-hour P2 main run is on hold until this is known.
2. If yes: P2 main run. If no: stop exploit runs on qwen3:14b; H3 disclosure plus a new model.

## Blocked

- Nothing blocked on money. Phase 0 close waits on Omer's first local run.

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
