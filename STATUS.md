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

Pilot done 2026-09-30: rows = 200 final (FINDINGS P2). Main run, about 19 hours at $0:
1. Night 1: `sandbox_score_hard` L1 and L5, seeds 0 to 19 (40 episodes, about 8 h). Push.
2. Night 2: L2 to L4, seeds 0 to 19 (60 episodes, about 11 h), then `sandbox_score_v2` L5 seeds 0 to 19. Push.
3. `python -m analysis.prereg ...` (H1), summary (H2), `python -m analysis.disclosure label` then `report` (H3).

## Blocked

- Nothing blocked on money. Phase 0 close waits on Omer's first local run.

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
