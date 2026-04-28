"""Evaluate model and prompt combinations for the unresolved-content judge."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from experiments.unresolved_content_calibration.dataset import load_dataset
from experiments.unresolved_content_calibration.judge import judge

load_dotenv()

RESULTS_PATH = Path(__file__).resolve().parent / "results" / "runs.json"

MODELS = ["gpt-4o", "gpt-4.1", "gpt-4o-mini"]
PROMPT_KEYS = ["v1", "v2", "v3"]


def _compute_metrics(examples, predictions: list[str]) -> dict:
    """Compute alignment, precision, and recall for the fail class."""
    tp = fp = tn = fn = 0
    for example, prediction in zip(examples, predictions, strict=True):
        actual = example.human_decision
        if actual == "fail" and prediction == "fail":
            tp += 1
        elif actual == "pass" and prediction == "fail":
            fp += 1
        elif actual == "pass" and prediction == "pass":
            tn += 1
        elif actual == "fail" and prediction == "pass":
            fn += 1

    total = len(examples)
    alignment = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    return {
        "alignment": round(alignment, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


async def run_combination(model: str, prompt_key: str, examples) -> dict:
    """Run one model and prompt combination across all examples."""
    print(f"  Running {model} / prompt_{prompt_key} ({len(examples)} examples)...")

    per_example = []
    predictions = []
    total_input_tokens = total_output_tokens = total_cost = total_latency = 0

    for example in examples:
        try:
            output = await judge(example.input, model, prompt_key)
            predicted_decision = output["result"].decision
        except Exception as exc:
            print(f"    ERROR on {example.id}: {exc}")
            output = {
                "result": type(
                    "R",
                    (),
                    {"decision": "pass", "issues": [], "confidence": 0.0, "reasoning": str(exc)},
                )(),
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "latency_ms": 0,
            }
            predicted_decision = "pass"

        predictions.append(predicted_decision)
        total_input_tokens += output["input_tokens"]
        total_output_tokens += output["output_tokens"]
        total_cost += output["cost_usd"]
        total_latency += output["latency_ms"]

        per_example.append(
            {
                "id": example.id,
                "category": example.category,
                "human_label": example.human_label,
                "human_decision": example.human_decision,
                "predicted_decision": predicted_decision,
                "correct": predicted_decision == example.human_decision,
                "issues": output["result"].issues,
                "confidence": output["result"].confidence,
                "reasoning": output["result"].reasoning,
                "input_tokens": output["input_tokens"],
                "output_tokens": output["output_tokens"],
                "cost_usd": output["cost_usd"],
                "latency_ms": output["latency_ms"],
            }
        )

    metrics = _compute_metrics(examples, predictions)
    count = len(examples)

    return {
        "model": model,
        "prompt_key": prompt_key,
        "metrics": metrics,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_cost_usd": round(total_cost, 6),
        "avg_latency_ms": round(total_latency / count) if count else 0,
        "per_example": per_example,
    }


def _pick_winner(runs: list[dict]) -> tuple[dict, str]:
    """Pick the winner by alignment, then by lower cost."""
    ranked = sorted(
        runs,
        key=lambda run: (run["metrics"]["alignment"], -run["total_cost_usd"]),
        reverse=True,
    )
    winner = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None

    reasoning = (
        f"Winner: {winner['model']} with prompt_{winner['prompt_key']}. "
        f"Alignment {winner['metrics']['alignment']:.0%}, "
        f"precision {winner['metrics']['precision']:.0%}, "
        f"recall {winner['metrics']['recall']:.0%}. "
        f"Total cost for 32 examples: ${winner['total_cost_usd']:.4f}. "
        f"Average latency: {winner['avg_latency_ms']}ms."
    )
    if runner_up:
        reasoning += (
            f" Runner-up was {runner_up['model']}/prompt_{runner_up['prompt_key']} "
            f"(alignment {runner_up['metrics']['alignment']:.0%})."
        )
    return winner, reasoning


async def main():
    examples = load_dataset()
    print(f"Loaded {len(examples)} examples.")

    all_runs = []
    for model in MODELS:
        for prompt_key in PROMPT_KEYS:
            run = await run_combination(model, prompt_key, examples)
            all_runs.append(run)
            print(
                f"    alignment={run['metrics']['alignment']:.0%}  "
                f"precision={run['metrics']['precision']:.0%}  "
                f"recall={run['metrics']['recall']:.0%}  "
                f"cost=${run['total_cost_usd']:.4f}  "
                f"avg_latency={run['avg_latency_ms']}ms"
            )

    winner, winner_reasoning = _pick_winner(all_runs)
    output = {
        "runs": all_runs,
        "winner": {
            "model": winner["model"],
            "prompt_key": winner["prompt_key"],
            "metrics": winner["metrics"],
            "reasoning": winner_reasoning,
        },
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w") as file:
        json.dump(output, file, indent=2)

    print(f"\nResults saved to {RESULTS_PATH}")
    print(f"\nWinner: {winner['model']} / prompt_{winner['prompt_key']}")
    print(f"  {winner_reasoning}")

    print("\n" + "=" * 90)
    print(
        f"{'model':<15} {'prompt':<8} {'alignment':>10} {'precision':>10} {'recall':>8} {'cost($)':>9} {'avg_lat':>10}"
    )
    print("=" * 90)
    for run in sorted(all_runs, key=lambda item: -item["metrics"]["alignment"]):
        marker = " <-- WINNER" if (run["model"], run["prompt_key"]) == (winner["model"], winner["prompt_key"]) else ""
        print(
            f"{run['model']:<15} {run['prompt_key']:<8} "
            f"{run['metrics']['alignment']:>10.0%} "
            f"{run['metrics']['precision']:>10.0%} "
            f"{run['metrics']['recall']:>8.0%} "
            f"{run['total_cost_usd']:>9.4f} "
            f"{run['avg_latency_ms']:>8}ms"
            f"{marker}"
        )


if __name__ == "__main__":
    asyncio.run(main())
