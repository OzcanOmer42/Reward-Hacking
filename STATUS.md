# STATUS

Last updated: 2026-09-30 (session 3)

## Current phase

**Free-model phase: DONE 2026-09-30, written up in README.md.** 130 real episodes, two model
families (qwen3:14b, gpt-oss:20b), 0 score-file edits, including with explicit permission.
The exploitation question (P2 design, flip threshold) is on hold: it needs a model that
exploits at some level, and none of the free local models tested does.

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

1. Frontier access at $0: Anthropic External Researcher Access Program ($1,000 API credits for
   AI safety research, reviewed the first Monday of each month). Then run the P2 design on a
   frontier model with the existing Anthropic adapter and a hard spending cap.
2. Optional, free: fix the disclosure rule's known miss; build a second environment.

## Blocked

- The exploitation question is blocked on access to a model that exploits (frontier models
  cost money; budget is $0 until credits).

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
