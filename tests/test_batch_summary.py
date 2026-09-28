"""Batch runner and summary table, using scripted agents. No network."""
from __future__ import annotations

import os

import pytest

from analysis.summary import load, table, wilson
from harness import batch


def test_wilson_known_values():
    lo, hi = wilson(14, 20)
    assert lo == pytest.approx(0.516, abs=1e-3)       # matches FINDINGS item 5
    assert wilson(0, 0) == (0.0, 1.0)
    lo, hi = wilson(0, 20)
    assert lo == 0.0 and 0 < hi < 0.2
    lo, hi = wilson(20, 20)
    assert hi == 1.0 and lo > 0.8


def test_batch_is_resumable_and_summary_counts(tmp_path):
    rd = str(tmp_path)
    args = ["--env", "sandbox_score", "--model", "scripted:exploit_only",
            "--levels", "1-5", "--seeds", "0-2", "--results-dir", rd]
    assert batch.main(args) == 0
    files = [os.path.join(r, f) for r, _, fs in os.walk(rd) for f in fs]
    assert len(files) == 15
    # summary skips _scripted by design, so read that folder directly
    t = table(load(os.path.join(rd, "_scripted")))
    assert [r["level"] for r in t] == [1, 2, 3, 4, 5]
    assert all(r["n"] == 3 and r["attempt"] == 3 and r["complete"] == 0 for r in t)
    assert t[0]["succeed"] == 0 and all(r["succeed"] == 3 for r in t[1:])   # L1 guard blocks


def test_summary_skips_failed_and_incomplete(tmp_path):
    d = tmp_path / "sandbox_score" / "ollama__m"
    d.mkdir(parents=True)
    (d / "L1_s0_r0.jsonl").write_text('{"kind": "header"}\n{"kind": "event"}\n')
    (tmp_path / "_failed").mkdir()
    assert load(str(tmp_path)) == []


def test_batch_resumes_and_moves_interrupted_run_aside(tmp_path):
    rd = str(tmp_path)
    args = ["--env", "sandbox_score", "--model", "scripted:honest",
            "--levels", "3", "--seeds", "0-1", "--results-dir", rd]
    d = tmp_path / "_scripted" / "sandbox_score" / "scripted__honest"
    d.mkdir(parents=True)
    (d / "L3_s0_r0.jsonl").write_text('{"kind": "header"}\n')      # killed mid-episode
    assert batch.main(args) == 0
    assert batch._finished(str(d / "L3_s0_r0.jsonl"))
    assert (tmp_path / "_failed" / "interrupted" / "_scripted" / "sandbox_score" / "scripted__honest" / "L3_s0_r0.jsonl").exists()
    before = (d / "L3_s1_r0.jsonl").read_bytes()
    assert batch.main(args) == 0                                     # second pass: nothing rerun
    assert (d / "L3_s1_r0.jsonl").read_bytes() == before
