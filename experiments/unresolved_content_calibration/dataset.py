"""Dataset loader for unresolved-content judge calibration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "unresolved_content" / "dataset.json"


@dataclass
class Example:
    id: str
    input: str
    human_label: int
    human_reason: str
    category: str

    @property
    def human_decision(self) -> str:
        return "fail" if self.human_label == 1 else "pass"


def load_dataset() -> list[Example]:
    with DATA_PATH.open() as file:
        raw = json.load(file)
    return [Example(**item) for item in raw]


def dataset_stats(examples: list[Example]) -> dict:
    categories: dict[str, dict[str, int]] = {}
    for example in examples:
        categories.setdefault(example.category, {"total": 0, "pass": 0, "fail": 0})
        categories[example.category]["total"] += 1
        if example.human_label == 0:
            categories[example.category]["pass"] += 1
        else:
            categories[example.category]["fail"] += 1
    return {
        "total": len(examples),
        "pass_count": sum(1 for example in examples if example.human_label == 0),
        "fail_count": sum(1 for example in examples if example.human_label == 1),
        "by_category": categories,
    }
