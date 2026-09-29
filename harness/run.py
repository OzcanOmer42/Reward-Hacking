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
from harness.contract import BudgetGuard, RunConfig, Termination
from harness.models import AnthropicModel, OllamaModel, ScriptedModel, garbage_policy
from harness.runner import run_episode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--level", type=int, required=True, choices=[1, 2, 3, 4, 5])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--model", required=True,
                    help="scripted:<name>, ollama:<tag> (free, local) or anthropic:<snapshot-id>")
    ap.add_argument("--no-think", action="store_true", help="ollama: turn visible thinking off")
    ap.add_argument("--num-ctx", type=int, default=16384, help="ollama: context window")
    ap.add_argument("--max-tokens", type=int, default=4096,
                    help="ollama: max tokens generated per turn, thinking included")
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
    elif provider == "ollama":
        model, sub = OllamaModel(name, num_ctx=a.num_ctx, max_tokens=a.max_tokens,
                                 think=not a.no_think), ""
    else:
        ap.error("model must be scripted:<name>, ollama:<tag> or anthropic:<snapshot-id>")

    env = envs.make(a.env, level=a.level)
    safe_id = model.model_id.replace(":", "_").replace("/", "_")
    out = os.path.join(a.results_dir, sub, a.env, f"{model.provider}__{safe_id}",
                       f"L{a.level}_s{a.seed}_r{a.replicate}.jsonl")
    if os.path.exists(out):
        print(f"refusing to overwrite {out}", file=sys.stderr)
        return 2
    o = run_episode(env, model, a.seed, RunConfig(max_steps=a.max_steps, replicate=a.replicate),
                    BudgetGuard(a.cap_usd), out)
    print(json.dumps({"transcript": out, "proxy": o.proxy, "shadow": o.shadow,
                      "label": o.label.value, "attempted": o.verdict.attempted,
                      "succeeded": o.verdict.succeeded, "termination": o.termination.value,
                      "steps": o.steps, "usd": o.usage_total.usd, "detail": o.detail}))
    if o.termination in (Termination.MODEL_ERROR, Termination.BUDGET):
        failed = os.path.join(a.results_dir, "_failed", os.path.relpath(out, a.results_dir))
        os.makedirs(os.path.dirname(failed), exist_ok=True)
        os.replace(out, failed)
        print(f"FAILED RUN, not a result. Transcript moved to {failed}. Reason: {o.detail}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
