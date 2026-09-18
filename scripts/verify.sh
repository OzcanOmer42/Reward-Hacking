#!/usr/bin/env bash
# Everything that must hold before any number is believed. No network, no API spend.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest -q
out="$(mktemp -d)"
echo "smoke transcripts in: $out"
for level in 1 2 3 4 5; do
  for agent in honest exploit_only both garbage; do
    python3 -m harness.run --env sandbox_score --level "$level" --seed 0 \
      --model "scripted:$agent" --results-dir "$out"
  done
done
