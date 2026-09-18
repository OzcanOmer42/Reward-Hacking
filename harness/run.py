"""CLI: run one episode.

  python -m harness.run --env sandbox_score --level 5 --seed 0 --model scripted:exploit_only
  python -m harness.run --env sandbox_score --level 5 --seed 0 --model anthropic:<snapshot-id> --cap-usd 0.50

Scripted runs go to results/_scripted/ (gitignored: they are test data, not results).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import envs
from harness.contract import BudgetGuard, RunConfig
from harness.models import AnthropicModel, ScriptedModel, garbage_policy
from harness.runner import run_episode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--level", type=int, required=True, choices=[1, 2, 3, 4, 5])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--model", required=True, help="scripted:<name> or anthropic:<snapshot-id>")
    ap.add_argument("--replicate", type=int, default=0)
    ap.add_argument("--max-steps", type=int, default=30)
    ap.add_argument("--cap-usd", type=float, default=0.0,
                    help="hard spend cap for this invocation; real models need > 0")
    ap.add_argument("--results-dir", default="results")
    a = ap.parse_args(argv)

    provider, _, name = a.model.partition(":")
    if provider == "scripted":
        agents = dict(envs.scripted_agents(a.env))
        agents["garbage"] = lambda: ScriptedModel("garbage", garbage_policy)
        if name not in agents:
            ap.error(f"scripted agent must be one of {sorted(agents)}")
        model, sub = agents[name](), "_scripted"
    elif provider == "anthropic":
        if a.cap_usd <= 0:
            ap.error("--cap-usd must be set above 0 for a real model")
        model, sub = AnthropicModel(name), ""
    else:
        ap.error("model must be scripted:<name> or anthropic:<snapshot-id>")

    env = envs.make(a.env, level=a.level)
    out = os.path.join(a.results_dir, sub, a.env, model.model_id,
                       f"L{a.level}_s{a.seed}_r{a.replicate}.jsonl")
    if os.path.exists(out):
        print(f"refusing to overwrite {out}", file=sys.stderr)
        return 2
    o = run_episode(env, model, a.seed, RunConfig(max_steps=a.max_steps, replicate=a.replicate),
                    BudgetGuard(a.cap_usd), out)
    print(json.dumps({"transcript": out, "proxy": o.proxy, "shadow": o.shadow,
                      "label": o.label.value, "attempted": o.verdict.attempted,
                      "succeeded": o.verdict.succeeded, "termination": o.termination.value,
                      "steps": o.steps, "usd": o.usage_total.usd}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
