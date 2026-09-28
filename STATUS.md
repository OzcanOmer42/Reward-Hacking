# STATUS

Last updated: 2026-09-28 (session 2)

## Current phase

**Phase 0 (contract): built, exit criterion met with scripted agents only.**
One thing remains before Phase 0 is closed for real: one episode with one real model.
That needs a model choice, a verified price entry, and a budget (see Blocked).

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
- Scripted null-test agents. 42 tests: conformance, determinism, level invariance over
  20 seeds, detector nulls, path aliasing, proxy parsing, robustness, leakage and a null
  test of the leak detector, budget, Anthropic adapter against a fake client.
- FINDINGS.md seeded with "Ways this could be wrong".

## Next

1. Omer installs Ollama, pulls `qwen3:14b`, runs one episode (sandbox_score L5 seed 0).
   This closes Phase 0. The Ollama adapter is tested only against a fake server built
   from Ollama's documented API; the build environment cannot reach ollama.com.
2. Phase 1: labelling tool (`analysis/labelling.py`), then run 100 local episodes
   (5 levels x 20 seeds) and hand-label them.
3. Phase 2: test_passing next.

## Blocked

- Nothing blocked on money. Phase 0 close waits on Omer's first local run.

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
