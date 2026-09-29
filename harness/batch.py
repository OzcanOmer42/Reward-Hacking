"""Run many episodes in a row, skipping any that already finished. Safe to stop and restart.

  python -m harness.batch --env sandbox_score --model ollama:qwen3:14b --levels 1-5 --seeds 0-19
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from harness import run


def _range(text: str) -> list[int]:
    out: list[int] = []
    for part in text.split(","):
        lo, _, hi = part.partition("-")
        out.extend(range(int(lo), int(hi or lo) + 1))
    return sorted(set(out))


def _finished(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as fh:
            last = fh.read().rstrip().rsplit("\n", 1)[-1]
        return json.loads(last).get("kind") == "outcome"
    except (OSError, ValueError):
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--levels", default="1-5")
    ap.add_argument("--seeds", default="0-19")
    ap.add_argument("--results-dir", default="results")
    ap.add_argument("--cap-usd", type=float, default=0.0)
    a, extra = ap.parse_known_args(argv)

    provider, _, name = a.model.partition(":")
    safe = name.replace(":", "_").replace("/", "_")
    cells = [(lv, s) for lv in _range(a.levels) for s in _range(a.seeds)]
    done = failed = 0
    t0 = time.time()
    for i, (level, seed) in enumerate(cells, 1):
        sub = "_scripted" if provider == "scripted" else ""
        path = os.path.join(a.results_dir, sub, a.env, f"{provider}__{safe}", f"L{level}_s{seed}_r0.jsonl")
        if _finished(path):
            done += 1
            continue
        if os.path.exists(path):   # an interrupted run: no outcome line, never counted
            aside = os.path.join(a.results_dir, "_failed", "interrupted", os.path.relpath(path, a.results_dir))
            os.makedirs(os.path.dirname(aside), exist_ok=True)
            os.replace(path, aside)
        print(f"[{i}/{len(cells)}] L{level} seed {seed} ...", flush=True)
        try:
            code = run.main(["--env", a.env, "--level", str(level), "--seed", str(seed),
                             "--model", a.model, "--results-dir", a.results_dir,
                             "--cap-usd", str(a.cap_usd), *extra])
        except SystemExit as e:        # argparse error: every cell would fail the same way
            print(f"stopping: bad arguments (exit {e.code}). Nothing else was run.", flush=True)
            return 2
        except KeyError as e:          # unknown environment name
            print(f"stopping: {e}. Is your code up to date?", flush=True)
            return 2
        done += code == 0
        failed += code != 0
    mins = (time.time() - t0) / 60
    print(f"finished: {done}/{len(cells)} complete, {failed} failed this pass, {mins:.1f} min", flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
