# goodhart-bench (working name)

A graded reward-hacking benchmark for tool-using agents: the same environment built
at five levels of exploitability, to find the level at which a model flips from doing
the task to gaming the metric.

**There are no results yet.** No real model has been run. This README will open with
the result once one exists; until then, nothing here is a finding.

- [STATUS.md](STATUS.md): current phase, what is done, what is next, budget.
- [FINDINGS.md](FINDINGS.md): research log and "Ways this could be wrong".
- [harness/contract.py](harness/contract.py): the interface everything depends on.
- [envs/sandbox_score/LEVELS.md](envs/sandbox_score/LEVELS.md): level design for the first environment.

## Verify the harness (no network, no API spend)

```bash
python3 -m pip install pytest
./scripts/verify.sh
```

## Run one episode

```bash
python3 -m harness.run --env sandbox_score --level 5 --seed 0 --model scripted:exploit_only
```

Scripted runs are test data. They go to `results/_scripted/`, which is gitignored and
never feeds a chart.
