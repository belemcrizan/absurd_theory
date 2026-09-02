"""Instrument-noise generators and empirical background ingestion."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def standardize(values: FloatArray) -> FloatArray:
    values = np.asarray(values, dtype=float)
    centered = values - np.nanmean(values)
    scale = np.nanstd(centered)
    if not np.isfinite(scale) or scale == 0:
        raise ValueError("noise data must contain finite, non-constant values")
    return np.nan_to_num(centered / scale)


def load_empirical_noise(path: str | Path, column: str | None = None) -> FloatArray:
    """Load one numeric CSV column and normalize it to zero mean/unit variance."""

    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("noise CSV is empty or has no header")
    selected = column
    if selected is None:
        for candidate in rows[0]:
            try:
                float(rows[0][candidate])
            except (TypeError, ValueError):
                continue
            selected = candidate
            break
    if selected is None or selected not in rows[0]:
        raise ValueError("no usable numeric noise column found")
    try:
        values = np.array([float(row[selected]) for row in rows], dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"column {selected!r} contains non-numeric values") from exc
    return standardize(values)


def colored_background(
    size: int,
    rng: np.random.Generator,
    rho: float,
    white_scale: float,
    colored_scale: float,
    empirical: FloatArray | None = None,
) -> FloatArray:
    """Generate white + AR(1) noise, optionally resampling an empirical trace."""

    white = rng.normal(0.0, white_scale, size)
    innovation = rng.normal(0.0, 1.0, size)
    ar = np.zeros(size, dtype=float)
    normalization = np.sqrt(max(1.0 - rho * rho, 1e-12))
    for index in range(1, size):
        ar[index] = rho * ar[index - 1] + normalization * innovation[index]
    result = white + colored_scale * ar
    if empirical is not None:
        source = standardize(empirical)
        start = int(rng.integers(0, len(source)))
        indices = (start + np.arange(size)) % len(source)
        result += colored_scale * source[indices]
    return result


def add_glitches(
    noise: FloatArray,
    dt: float,
    rate: float,
    scale: float,
    rng: np.random.Generator,
) -> FloatArray:
    """Add sparse, decaying non-Gaussian transients."""

    output = noise.copy()
    triggers = np.flatnonzero(rng.random(len(output)) < rate * dt)
    width = max(2, int(0.2 / dt))
    envelope = np.exp(-np.arange(width) * dt / 0.06)
    for trigger in triggers:
        stop = min(trigger + width, len(output))
        amplitude = rng.laplace(0.0, scale)
        output[trigger:stop] += amplitude * envelope[: stop - trigger]
    return output
