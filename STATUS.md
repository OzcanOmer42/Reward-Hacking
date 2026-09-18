# STATUS

Last updated: 2026-09-17 (session 1)

## Current phase

**Phase 0 (contract): built, exit criterion met with scripted agents only.**
One thing remains before Phase 0 is closed for real: one episode with one real model.
That needs a model choice, a verified price entry, and a budget (see Blocked).

## Budget

- API budget ceiling: **NOT SET.** Omer to set. No real-model run happens before this line has a number.
- Spend to date: **$0.00** (no API call has been made).
- Rule: stop and re-plan when a phase exceeds its estimate by 50%.
- Enforcement: `BudgetGuard` is checked before every model call; the CLI refuses a real
  model without `--cap-usd`.

| Phase | Estimate | Spent |
|---|---|---|
| 0 | one episode, to be estimated from the chosen model's price | $0.00 |

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

1. Omer sets the API budget ceiling and picks the first model.
2. Add that model's price to `harness/prices.json` with source URL and date.
3. One real episode: sandbox_score L5 seed 0. Read the transcript by hand.
4. Phase 1: run sandbox_score across levels for the labelling sample; build
   `analysis/labelling.py`; hand-label; report precision and recall.

## Blocked

- First real-model run: blocked on budget ceiling, model choice, and an API key
  (none exists in the build environment).

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
