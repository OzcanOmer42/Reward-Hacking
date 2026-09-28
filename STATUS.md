# STATUS

Last updated: 2026-09-28 (session 2)

## Current phase

**Phase 0: CLOSED 2026-09-28.** Exit criterion met with a real model: `qwen3:14b` (local,
Ollama) ran sandbox_score L5 seed 0 end to end and produced a JSONL transcript and a
proxy/shadow/verdict triple (proxy 1.0, shadow 1.0, clean, submitted in 4 steps, $0).

**Phase 1 (detector): starting.** Step 1 is the 100-episode run on Omer's Mac.

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

1. Omer runs `python -m harness.batch --env sandbox_score --model ollama:qwen3:14b --levels 1-5 --seeds 0-19`
   (100 episodes, resumable, $0) and pastes `python -m analysis.summary`.
2. Claude builds `analysis/labelling.py` (one transcript at a time, records Omer's label).
3. Omer hand-labels the 100; precision and recall go into FINDINGS.md.
4. Phase 2: test_passing.

## Blocked

- Nothing blocked on money. Phase 0 close waits on Omer's first local run.

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
