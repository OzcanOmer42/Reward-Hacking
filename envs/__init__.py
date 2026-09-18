"""Environment registry."""
from __future__ import annotations

from harness.contract import Environment, LevelFactors


def make(name: str, level: int | None = None, factors: LevelFactors | None = None) -> Environment:
    if name == "sandbox_score":
        from envs.sandbox_score.env import SandboxScore
        return SandboxScore(level=level, factors=factors)
    raise KeyError(f"unknown environment: {name}")


def scripted_agents(name: str) -> dict:
    if name == "sandbox_score":
        from envs.sandbox_score.scripted import AGENTS
        return AGENTS
    raise KeyError(f"unknown environment: {name}")
