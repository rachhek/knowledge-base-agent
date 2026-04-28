"""Calibration-time judge runner for unresolved-content detection."""

from __future__ import annotations

import json
import time
from pathlib import Path

from experiments.unresolved_content_calibration.prompts import PROMPTS
from quality_agent_demo.backend import build_agent
from quality_agent_demo.models import QCResult

RESULTS_PATH = Path(__file__).resolve().parent / "results" / "runs.json"

_FALLBACK_MODEL = "gpt-4.1"
_FALLBACK_PROMPT = "v2"
_COST_RATES = {
    "gpt-4.1": {"input": 0.002, "output": 0.008},
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}


def load_winner() -> tuple[str, str]:
    """Return the winning model and prompt key from the last run, if present."""
    if not RESULTS_PATH.exists():
        return _FALLBACK_MODEL, _FALLBACK_PROMPT

    with RESULTS_PATH.open() as file:
        data = json.load(file)

    winner = data.get("winner", {})
    return winner.get("model", _FALLBACK_MODEL), winner.get("prompt_key", _FALLBACK_PROMPT)


def _calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    rates = _COST_RATES.get(model_name, {"input": 0.0, "output": 0.0})
    return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])


async def judge(text: str, model_name: str, prompt_key: str) -> dict:
    """Run the judge with an explicit model and prompt."""
    agent = build_agent(model_name, PROMPTS[prompt_key], QCResult)

    start = time.monotonic()
    result = await agent.run(f"Inspect this policy snippet:\n\n{text}")
    latency_ms = int((time.monotonic() - start) * 1000)

    usage = result.usage()
    input_tokens = usage.input_tokens or 0
    output_tokens = usage.output_tokens or 0
    cost_usd = _calculate_cost(model_name, input_tokens, output_tokens)

    return {
        "result": result.output,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost_usd, 6),
        "latency_ms": latency_ms,
    }


async def run(text: str) -> dict:
    """Run the judge using the currently selected winning configuration."""
    model_name, prompt_key = load_winner()
    result = await judge(text, model_name, prompt_key)
    return {"model": model_name, "prompt_key": prompt_key, **result}
