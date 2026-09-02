"""Result serialization."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .simulation import SimulationResult


def write_trace(result: SimulationResult, path: str | Path) -> None:
    columns = result.as_columns()
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(zip(*columns.values()))


def write_json(payload: Any, path: str | Path) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
