# STATUS

Last updated: 2026-09-17 (session 1)

## Current phase

**Phase 0 (contract): built, exit criterion met with scripted agents only.**
One thing remains before Phase 0 is closed for real: one episode with one real model.
That needs a model choice, a verified price entry, and a budget (see Blocked).

## Budget

- API budget ceiling: **$20.00 total, PROPOSED by Claude on 2026-09-17, not yet confirmed by Omer.**
  Covers Phase 0 and Phase 1 with headroom. Re-plan with measured token counts before Phase 3.
- Spend to date: **$0.00** (no API call has been made).
- Rule: stop and re-plan when a phase exceeds its estimate by 50%.
- Enforcement: `BudgetGuard` is checked before every model call; the CLI refuses a real
  model without `--cap-usd`.
- First model: `claude-sonnet-5` ($2 in / $10 out per million tokens, verified 2026-09-17,
  source in `harness/prices.json`). Pinned snapshot id per Anthropic's model-ids page.

Estimates below come from real prompt sizes at 3 characters per token plus an ASSUMED 300
output tokens per turn. They are estimates, not measurements. Replace with measured
numbers after the first real episode.

| Phase | What | Estimate (claude-sonnet-5) | Spent |
|---|---|---|---|
| 0 | 1 episode, sandbox_score L5 seed 0 | $0.02 to $0.05, hard cap $0.50 | $0.00 |
| 1 | 100 episodes (5 levels x 20 seeds) for the labelling sample | $2 to $5 | $0.00 |

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

1. Omer confirms the $20 ceiling and creates an API key.
2. (done) Prices for claude-sonnet-5, claude-haiku-4-5-20251001, claude-opus-5 are in `harness/prices.json`.
3. One real episode on Omer's Mac: sandbox_score L5 seed 0. Read the transcript by hand.
4. Phase 1: run sandbox_score across levels for the labelling sample; build
   `analysis/labelling.py`; hand-label; report precision and recall.

## Blocked

- First real-model run: blocked on Omer confirming the ceiling and creating an API key.
  Runs happen on Omer's Mac; the build environment has no key.

## Plan of record

Environments in the original spec order (1 to 9), cut order 7, then 5, then 3; never
cut 1, 8, 9. Concerns about 5 and 6 are logged in FINDINGS.md item 11.
