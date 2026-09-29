"""Environment registry."""
from __future__ import annotations

from harness.contract import Environment, LevelFactors


# Honest-task difficulty for the sandbox_score family (rows to total by hand).
# Pre-registered in FINDINGS.md (section P2) before any run of the hard variant.
# name -> (rows, submit_alone). sandbox_score keeps the R1 protocol unchanged.
SANDBOX = {
    "sandbox_score": (12, False),
    "sandbox_score_v2": (12, True),
    "sandbox_score_hard": (200, True),
}
SANDBOX_ROWS = {k: v[0] for k, v in SANDBOX.items()}


def make(name: str, level: int | None = None, factors: LevelFactors | None = None) -> Environment:
    if name in SANDBOX_ROWS:
        from envs.sandbox_score.env import SandboxScore
        rows, alone = SANDBOX[name]
        return SandboxScore(level=level, factors=factors, n_rows=rows, name=name,
                            submit_alone=alone)
    raise KeyError(f"unknown environment: {name}")


def scripted_agents(name: str) -> dict:
    if name in SANDBOX_ROWS:
        from envs.sandbox_score.scripted import AGENTS
        return AGENTS
    raise KeyError(f"unknown environment: {name}")
