"""Export helpers for writing structured data to disk."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.models.items import ProductItem


class ExportManager:
    """Handle JSONL, CSV and Parquet exports for batches of items."""

    def __init__(self, output_path: str):
        self.base_path = Path(output_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def export_jsonl(self, items: Iterable[ProductItem], filename: str = "items.jsonl") -> Path:
        path = self.base_path / filename
        with path.open("w", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps(item.dict(), default=str, ensure_ascii=False) + "\n")
        return path

    def export_csv(self, items: Iterable[ProductItem], filename: str = "items.csv") -> Path:
        path = self.base_path / filename
        fieldnames = list(ProductItem.schema()["properties"].keys())
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for item in items:
                writer.writerow(item.dict())
        return path

    def export_parquet(
        self, items: Iterable[ProductItem], filename: str = "items.parquet"
    ) -> Path:
        path = self.base_path / filename
        dataframe = pd.DataFrame([item.dict() for item in items])
        dataframe.to_parquet(path, index=False)
        return path
