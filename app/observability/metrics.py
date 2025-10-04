"""Simple metrics collector writing JSON snapshots."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Mapping


class MetricsCollector:
    """In-memory counter with flush-to-disk capability."""

    def __init__(self, output_path: str):
        self.path = Path(output_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.counters: Counter[str] = Counter()

    def incr(self, key: str, value: int = 1) -> None:
        self.counters[key] += value

    def flush(self) -> Path:
        payload: Mapping[str, int] = dict(self.counters)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        return self.path
