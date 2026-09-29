"""Rollout loop: step cap, repeat cap, retries, cost accounting, transcript writing."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import subprocess
from typing import Any

from harness.contract import (
    NUDGE_TEXT,
    BudgetExceeded,
    BudgetGuard,
    Environment,
    Event,
    Header,
    Model,
    Outcome,
    RunConfig,
    Termination,
    Usage,
    find_leaks,
    to_json_line,
)


class ShadowLeak(RuntimeError):
    """Environment-originated text contained a leak term. The run is void."""


def git_sha() -> str:
    """HEAD sha, with -dirty if the tree has uncommitted changes. 'unknown' outside git."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=here, capture_output=True,
                             text=True, timeout=10, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=here, capture_output=True,
                               text=True, timeout=10, check=True).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _add(a: Usage, b: Usage) -> Usage:
    return Usage(a.input_tokens + b.input_tokens, a.output_tokens + b.output_tokens,
                 a.cached_input_tokens + b.cached_input_tokens, a.usd + b.usd)


def _call_key(name: str, arguments: Any) -> str:
    try:
        return name + "|" + json.dumps(arguments, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return name + "|" + repr(arguments)


def run_episode(
    env: Environment,
    model: Model,
    seed: int,
    cfg: RunConfig,
    budget: BudgetGuard,
    out_path: str,
    started_at: str | None = None,
    harness_sha: str | None = None,
) -> Outcome:
    """Run one episode and write its JSONL transcript to out_path.

    Refuses to overwrite out_path. On a leak, raises ShadowLeak and leaves the
    transcript without an outcome line, which analysis/ treats as void.
    """
    obs = env.reset(seed)
    header = Header(
        env=env.name, level=env.level, factors=env.factors, seed=seed,
        replicate=cfg.replicate, provider=model.provider, model_id=model.model_id,
        params=dict(model.params),
        prompt_sha256=hashlib.sha256(
            (obs.system_prompt + "\x00" + obs.task_prompt).encode()).hexdigest(),
        fixture_sha256=env.fixture_sha256(),
        harness_git_sha=harness_sha if harness_sha is not None else git_sha(),
        started_at=started_at or _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    )
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    events: list[Event] = []
    messages: list[dict[str, Any]] = [{"role": "user", "text": obs.task_prompt}]
    total = Usage()
    termination: Termination | None = None
    detail = ""
    call_index = 0
    last_key, repeats, textonly = None, 0, 0

    with open(out_path, "x", encoding="utf-8") as fh:   # "x": never overwrite evidence
        def emit(ev: Event) -> None:
            events.append(ev)
            fh.write(to_json_line(ev) + "\n")
            fh.flush()

        fh.write(to_json_line(header) + "\n")
        emit(Event(0, "system", obs.system_prompt, True))
        emit(Event(0, "user", obs.task_prompt, True))

        turn_no = 0
        while termination is None:
            if turn_no >= cfg.max_steps:
                termination = Termination.STEP_CAP
                break
            try:
                budget.check(model.estimate_usd(obs.system_prompt, messages))
            except BudgetExceeded as e:
                termination, detail = Termination.BUDGET, str(e)
                break
            turn, last_err = None, ""
            for _ in range(max(1, cfg.model_retries)):
                try:
                    turn = model.complete(obs.system_prompt, messages, env.tools())
                    break
                except Exception as e:  # provider errors are arbitrary; all are retried
                    last_err = f"{type(e).__name__}: {e}"
            if turn is None:
                termination, detail = Termination.MODEL_ERROR, last_err
                break
            budget.charge(turn.usage.usd)
            total = _add(total, turn.usage)
            if turn.served_model != model.model_id:
                termination = Termination.MODEL_ERROR
                detail = f"asked for {model.model_id}, served {turn.served_model}"
                break

            emit(Event(turn_no, "assistant", turn.text, False, usage=turn.usage,
                       reasoning=turn.reasoning))
            messages.append({"role": "assistant", "text": turn.text,
                             "tool_calls": list(turn.tool_calls)})

            if not turn.tool_calls:
                textonly += 1
                if textonly >= 2:
                    termination = Termination.NO_TOOL_CALL
                    break
                messages.append({"role": "user", "text": NUDGE_TEXT})
                emit(Event(turn_no, "user", NUDGE_TEXT, True))
                turn_no += 1
                continue
            textonly = 0

            results = []
            begin_turn = getattr(env, "begin_turn", None)
            if callable(begin_turn):
                begin_turn()
            for call in turn.tool_calls:
                key = _call_key(call.name, call.arguments)
                repeats = repeats + 1 if key == last_key else 1
                last_key = key
                emit(Event(turn_no, "tool_call", call.raw_arguments, False,
                           tool_call=call, call_index=call_index))
                res = env.step(call)
                emit(Event(turn_no, "tool_result", res.content, not res.echo,
                           tool_error=res.error, call_index=call_index))
                results.append(res)
                call_index += 1
            messages.append({"role": "tool", "results": results})

            if env.is_done():
                termination = Termination.SUBMITTED
            elif repeats >= cfg.max_identical_repeats:
                termination = Termination.REPEAT_CAP
            turn_no += 1

        leaks = find_leaks(events, env.leak_terms())
        if leaks:
            raise ShadowLeak(f"{out_path}: {leaks[:5]}")

        verdict = env.exploit_signature()
        outcome = Outcome(
            run_id=header.run_id, proxy=env.proxy_reward(), shadow=env.shadow_reward(),
            verdict=verdict, label=verdict.label, termination=termination,
            steps=turn_no, usage_total=total, final_report=env.final_report(),
            detail=detail,
        )
        fh.write(to_json_line(outcome) + "\n")
    return outcome
