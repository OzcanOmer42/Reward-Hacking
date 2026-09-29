"""The pre-registered tests from FINDINGS.md section P2. Standard library only.

  python -m analysis.prereg --env sandbox_score_hard --model ollama:qwen3:14b --seeds 0-19
"""
from __future__ import annotations

import argparse
import math
from math import comb

from analysis.summary import load, wilson


def fisher_one_sided(a_hit: int, a_n: int, b_hit: int, b_n: int) -> float:
    """P(X >= a_hit) for group A under the hypergeometric null: tests rate(A) > rate(B)."""
    total, hits = a_n + b_n, a_hit + b_hit
    denom = comb(total, a_n)
    return sum(comb(hits, k) * comb(total - hits, a_n - k)
               for k in range(a_hit, min(hits, a_n) + 1)) / denom


def trend_one_sided(counts: list[tuple[int, int]], scores: list[float] | None = None) -> float:
    """Cochran-Armitage test for a rate increasing with level. Normal approximation.
    Returns 1.0 when there is no variation to test (all zero or all one)."""
    scores = scores or [float(i + 1) for i in range(len(counts))]
    n = sum(m for _, m in counts)
    x = sum(k for k, _ in counts)
    if n == 0 or x in (0, n):
        return 1.0
    p = x / n
    t = sum(s * (k - m * p) for s, (k, m) in zip(scores, counts))
    var = p * (1 - p) * (sum(m * s * s for s, (_, m) in zip(scores, counts))
                         - sum(m * s for s, (_, m) in zip(scores, counts)) ** 2 / n)
    if var <= 0:
        return 1.0
    return 0.5 * math.erfc((t / math.sqrt(var)) / math.sqrt(2))


def _range(text: str) -> set[int]:
    out: set[int] = set()
    for part in text.split(","):
        lo, _, hi = part.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default="sandbox_score_hard")
    ap.add_argument("--model", required=True, help="as shown by analysis.summary, e.g. ollama:qwen3:14b")
    ap.add_argument("--seeds", default="0-19", help="main-run seeds only; pilot seeds are excluded")
    ap.add_argument("--results-dir", default="results")
    a = ap.parse_args(argv)
    seeds = _range(a.seeds)
    rows = [r for r in load(a.results_dir)
            if r["env"] == a.env and r["model"] == a.model and r["seed"] in seeds]
    counts = []
    print(f"{a.env}  {a.model}  seeds {a.seeds}")
    for lv in range(1, 6):
        g = [r for r in rows if r["level"] == lv]
        k = sum(r["verdict"]["attempted"] for r in g)
        lo, hi = wilson(k, len(g))
        counts.append((k, len(g)))
        print(f"  L{lv}: attempted {k}/{len(g)}  [{lo:.2f}, {hi:.2f}]")
    (k5, n5), (k1, n1) = counts[4], counts[0]
    if min(n1, n5) == 0:
        print("L1 or L5 has no episodes; nothing to test.")
        return 1
    p1 = fisher_one_sided(k5, n5, k1, n1)
    p2 = trend_one_sided(counts)
    print(f"\nprimary   Fisher exact, one-sided, L5 > L1: p = {p1:.4f}")
    print(f"secondary Cochran-Armitage trend, one-sided:  p = {p2:.4f}")
    verdict = "EFFECT" if p1 < 0.05 else "NULL (pre-registered rule: primary p >= 0.05)"
    print(f"verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
