"""Per (env, model, level) table from finished transcripts. Reads results/, skips
_scripted/ and _failed/. Every rate comes with a 90% Wilson interval.

  python -m analysis.summary
"""
from __future__ import annotations

import argparse
import json
import math
import os
from collections import defaultdict

Z90 = 1.6448536269514722


def wilson(k: int, n: int, z: float = Z90) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def load(results_dir: str) -> list[dict]:
    rows = []
    for root, dirs, files in os.walk(results_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith("_"))
        for f in sorted(files):
            if not f.endswith(".jsonl"):
                continue
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                lines = [json.loads(x) for x in fh if x.strip()]
            if len(lines) < 2 or lines[-1].get("kind") != "outcome":
                continue
            h, o = lines[0], lines[-1]
            rows.append({"env": h["env"], "model": f'{h["provider"]}:{h["model_id"]}',
                         "level": h["level"], "seed": h["seed"], **o})
    return rows


def table(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["env"], r["model"], r["level"])].append(r)
    out = []
    for (env, model, level), g in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 0)):
        n = len(g)
        att = sum(r["verdict"]["attempted"] for r in g)
        suc = sum(r["verdict"]["succeeded"] for r in g)
        comp = sum(r["shadow"] >= 1.0 for r in g)
        sub = sum(r["termination"] == "submitted" for r in g)
        out.append({"env": env, "model": model, "level": level, "n": n,
                    "attempt": att, "attempt_ci": wilson(att, n), "succeed": suc,
                    "complete": comp, "complete_ci": wilson(comp, n), "submitted": sub,
                    "mean_proxy": sum(r["proxy"] for r in g) / n,
                    "mean_shadow": sum(r["shadow"] for r in g) / n})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="results")
    a = ap.parse_args(argv)
    t = table(load(a.results_dir))
    if not t:
        print("no finished transcripts under", a.results_dir)
        return 0
    head = f'{"env":14} {"model":24} {"lvl":>3} {"n":>3}  {"cheat tried":>18}  {"task done":>18}  {"proxy":>5} {"shadow":>6}'
    print(head)
    print("-" * len(head))
    for r in t:
        lo, hi = r["attempt_ci"]
        clo, chi = r["complete_ci"]
        print(f'{r["env"]:14} {r["model"][:24]:24} {r["level"]!s:>3} {r["n"]:>3}  '
              f'{r["attempt"]:>3}/{r["n"]:<3} [{lo:.2f},{hi:.2f}]  '
              f'{r["complete"]:>3}/{r["n"]:<3} [{clo:.2f},{chi:.2f}]  '
              f'{r["mean_proxy"]:5.2f} {r["mean_shadow"]:6.2f}')
    print("\n[a,b] = 90% Wilson interval. 'cheat tried' counts attempts, including blocked ones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
