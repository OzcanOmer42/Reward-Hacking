"""Model adapters.

ScriptedModel  zero-cost deterministic agents for null tests (provider "scripted").
AnthropicModel real API adapter. Refuses to run without a verified price entry
               in harness/prices.json, so cost accounting can never silently be 0.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from harness.contract import ModelTurn, ToolCall, ToolSpec, Usage

# A policy sees the neutral message list and returns (text, [(tool, args), ...]).
Policy = Callable[[list[dict[str, Any]]], tuple[str, list[tuple[str, Any]]]]


class ScriptedModel:
    provider = "scripted"

    def __init__(self, name: str, policy: Policy):
        self.model_id = name
        self.params: dict[str, Any] = {}
        self._policy = policy

    def estimate_usd(self, system: str, messages: list[dict[str, Any]]) -> float:
        return 0.0

    def complete(self, system: str, messages: list[dict[str, Any]],
                 tools: list[ToolSpec]) -> ModelTurn:
        text, calls = self._policy(messages)
        turn = sum(1 for m in messages if m["role"] == "assistant")
        tcs = tuple(
            ToolCall(id=f"c{turn}_{i}", name=n, arguments=a,
                     raw_arguments=json.dumps(a, sort_keys=True, default=str))
            for i, (n, a) in enumerate(calls)
        )
        return ModelTurn(text, tcs, Usage(), "tool_use" if tcs else "end_turn", self.model_id)


def turn_index(messages: list[dict[str, Any]]) -> int:
    return sum(1 for m in messages if m["role"] == "assistant")


def last_results(messages: list[dict[str, Any]]) -> list:
    for m in reversed(messages):
        if m["role"] == "tool":
            return m["results"]
    return []


def garbage_policy(messages: list[dict[str, Any]]) -> tuple[str, list[tuple[str, Any]]]:
    """Every malformed thing an agent can do, one per turn, then an endless repeat."""
    script: list[tuple[str, list[tuple[str, Any]]]] = [
        ("", [("no_such_tool", {})]),
        ("", [("read_file", None)]),                       # unparseable arguments
        ("", [("read_file", {"path": 7})]),                # wrong type
        ("", [("read_file", {})]),                         # missing argument
        ("", [("write_file", {"path": "../../etc/passwd", "content": "x"})]),
        ("", [("write_file", {"path": "output", "content": "x"})]),   # a directory
        ("", [("write_file", {"path": "a", "content": "x" * 200_000})]),
        ("", [("list_dir", {"path": "does/not/exist"})]),
        ("thinking out loud, no tool call", []),
        ("", [("read_file", {"path": ""}), ("list_dir", {"path": "\x00"})]),
    ]
    i = turn_index(messages)
    return script[i] if i < len(script) else ("", [("list_dir", {"path": "."})])


def silent_policy(messages: list[dict[str, Any]]) -> tuple[str, list[tuple[str, Any]]]:
    return ("I will not use tools.", [])


# ---------------------------------------------------------------------------
PRICES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json")


class AnthropicModel:
    provider = "anthropic"

    def __init__(self, model_id: str, max_tokens: int = 2048,
                 temperature: float | None = 1.0, client: Any = None,
                 prices_path: str = PRICES_PATH):
        if model_id.endswith("-latest"):
            raise ValueError("aliases are not allowed; pin a snapshot id")
        with open(prices_path, encoding="utf-8") as fh:
            table = json.load(fh).get("models", {})
        if model_id not in table:
            raise ValueError(
                f"no price entry for {model_id} in {prices_path}. Add usd_per_mtok "
                "input/output/cache_read with a source URL and date before running."
            )
        self._price = table[model_id]
        self.model_id = model_id
        self.params = {"max_tokens": max_tokens}
        if temperature is not None:
            self.params["temperature"] = temperature
        if client is None:
            import anthropic  # lazy: tests and scripted runs do not need the SDK
            client = anthropic.Anthropic()
        self._client = client

    def _usd(self, inp: int, out: int, cached: int) -> float:
        p = self._price
        return (inp * p["input"] + out * p["output"] + cached * p["cache_read"]) / 1e6

    def estimate_usd(self, system: str, messages: list[dict[str, Any]]) -> float:
        # Upper-ish bound: ~3 chars per token for input, full max_tokens for output.
        chars = len(system) + sum(len(json.dumps(self._wire([m]), default=str)) for m in messages)
        return self._usd(chars // 3 + 1, self.params["max_tokens"], 0)

    @staticmethod
    def _wire(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in messages:
            if m["role"] == "user":
                out.append({"role": "user", "content": m["text"]})
            elif m["role"] == "assistant":
                blocks: list[dict[str, Any]] = []
                if m["text"]:
                    blocks.append({"type": "text", "text": m["text"]})
                for tc in m["tool_calls"]:
                    blocks.append({"type": "tool_use", "id": tc.id, "name": tc.name,
                                   "input": tc.arguments if isinstance(tc.arguments, dict) else {}})
                out.append({"role": "assistant", "content": blocks or [{"type": "text", "text": "(no output)"}]})
            else:
                out.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": r.call_id,
                     "content": r.content or "(empty)", "is_error": r.error is not None}
                    for r in m["results"]]})
        # The API requires alternating roles; a nudge after tool results would
        # otherwise produce two user messages in a row.
        merged: list[dict[str, Any]] = []
        for w in out:
            if merged and merged[-1]["role"] == w["role"] == "user":
                prev = merged[-1]["content"]
                prev = [{"type": "text", "text": prev}] if isinstance(prev, str) else prev
                cur = w["content"]
                cur = [{"type": "text", "text": cur}] if isinstance(cur, str) else cur
                merged[-1] = {"role": "user", "content": prev + cur}
            else:
                merged.append(w)
        return merged

    def complete(self, system: str, messages: list[dict[str, Any]],
                 tools: list[ToolSpec]) -> ModelTurn:
        resp = self._client.messages.create(
            model=self.model_id, system=system, messages=self._wire(messages),
            tools=[{"name": t.name, "description": t.description,
                    "input_schema": t.parameters} for t in tools],
            **self.params,
        )
        text, calls = [], []
        for b in resp.content:
            if b.type == "text":
                text.append(b.text)
            elif b.type == "tool_use":
                args = b.input if isinstance(b.input, dict) else None
                calls.append(ToolCall(b.id, b.name, args, json.dumps(b.input, default=str)))
        u = resp.usage
        cached = getattr(u, "cache_read_input_tokens", 0) or 0
        usage = Usage(u.input_tokens, u.output_tokens, cached,
                      self._usd(u.input_tokens, u.output_tokens, cached))
        return ModelTurn("\n".join(text), tuple(calls), usage, resp.stop_reason or "", resp.model)
