"""Environment registry."""
from __future__ import annotations

from harness.contract import Environment, LevelFactors


# Honest-task difficulty for the sandbox_score family (rows to total by hand).
# Pre-registered in FINDINGS.md (section P2) before any run of the hard variant.
SANDBOX_ROWS = {"sandbox_score": 12, "sandbox_score_hard": 200}


def make(name: str, level: int | None = None, factors: LevelFactors | None = None) -> Environment:
    if name in SANDBOX_ROWS:
        from envs.sandbox_score.env import SandboxScore
        return SandboxScore(level=level, factors=factors, n_rows=SANDBOX_ROWS[name], name=name)
    raise KeyError(f"unknown environment: {name}")


def scripted_agents(name: str) -> dict:
    if name in SANDBOX_ROWS:
        from envs.sandbox_score.scripted import AGENTS
        return AGENTS
    raise KeyError(f"unknown environment: {name}")
