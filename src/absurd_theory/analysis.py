"""Metrics designed to compare WIOS against instrumental artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .config import SimulationConfig
from .simulation import SimulationResult, simulate


@dataclass(frozen=True)
class RunMetrics:
    click_rate: float
    coherent_rms: float
    direct_to_residual_ratio: float
    post_pulse_click_suppression: float
    post_pulse_coherence_retention: float
    shell_mean: float
    bulk_mean: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def _safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if abs(denominator) > 1e-12 else float("nan")


def _pulse_masks(result: SimulationResult, config: SimulationConfig) -> tuple[np.ndarray, np.ndarray]:
    pre = np.zeros(len(result.time), dtype=bool)
    post = np.zeros(len(result.time), dtype=bool)
    for pulse in np.arange(config.pulse_start, config.duration, config.pulse_interval):
        pre |= (result.time >= pulse - 1.5) & (result.time < pulse)
        post |= (
            (result.time >= pulse + config.pulse_duration)
            & (result.time < pulse + config.pulse_duration + 1.5)
        )
    return pre, post


def lock_in_amplitude(
    signal: np.ndarray, time: np.ndarray, frequency: float, mask: np.ndarray | None = None
) -> float:
    if mask is None:
        mask = np.ones(len(time), dtype=bool)
    if not np.any(mask):
        return float("nan")
    phase = 2.0 * np.pi * frequency * time[mask]
    values = signal[mask]
    sine = 2.0 * np.mean(values * np.sin(phase))
    cosine = 2.0 * np.mean(values * np.cos(phase))
    return float(np.hypot(sine, cosine))


def summarize(result: SimulationResult, config: SimulationConfig) -> RunMetrics:
    pre, post = _pulse_masks(result, config)
    pre_click = float(np.mean(result.clicks[pre]))
    post_click = float(np.mean(result.clicks[post]))
    pre_coherence = lock_in_amplitude(
        result.observed_signal, result.time, config.wave_frequency, pre
    )
    post_coherence = lock_in_amplitude(
        result.observed_signal, result.time, config.wave_frequency, post
    )
    return RunMetrics(
        click_rate=float(np.mean(result.clicks) / config.dt),
        coherent_rms=float(np.sqrt(np.mean(result.coherent_signal**2))),
        direct_to_residual_ratio=_safe_ratio(
            float(np.mean(result.direct_visibility)),
            float(np.mean(result.residual_visibility)),
        ),
        post_pulse_click_suppression=1.0 - _safe_ratio(post_click, pre_click),
        post_pulse_coherence_retention=_safe_ratio(post_coherence, pre_coherence),
        shell_mean=float(np.mean(result.shell)),
        bulk_mean=float(np.mean(result.bulk)),
    )


def ensemble(
    config: SimulationConfig,
    *,
    runs: int,
    seed: int,
    empirical_noise: np.ndarray | None = None,
) -> dict[str, list[RunMetrics]]:
    if runs <= 0:
        raise ValueError("runs must be positive")
    output: dict[str, list[RunMetrics]] = {"wios": [], "instrumental_null": []}
    for offset in range(runs):
        for model, model_rows in output.items():
            result = simulate(
                config,
                seed=seed + offset,
                model=model,
                empirical_noise=empirical_noise,
            )
            model_rows.append(summarize(result, config))
    return output


def aggregate(metrics: dict[str, list[RunMetrics]]) -> dict[str, dict[str, dict[str, float]]]:
    summary: dict[str, dict[str, dict[str, float]]] = {}
    for model, rows in metrics.items():
        model_summary: dict[str, dict[str, float]] = {}
        for name in RunMetrics.__dataclass_fields__:
            values = np.array([getattr(row, name) for row in rows], dtype=float)
            finite = values[np.isfinite(values)]
            model_summary[name] = {
                "mean": float(np.mean(finite)) if len(finite) else float("nan"),
                "std": float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0,
            }
        summary[model] = model_summary
    return summary
