"""Publication-friendly visual diagnostics."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .analysis import RunMetrics
from .config import SimulationConfig
from .simulation import SimulationResult

COLORS = {
    "ink": "#132238",
    "wave": "#00A6A6",
    "shell": "#F26419",
    "bulk": "#6C4AB6",
    "measure": "#E9C46A",
    "null": "#7A8793",
}


def plot_dashboard(result: SimulationResult, output: str | Path) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(13, 10), sharex=True)
    fig.suptitle("WIOS v0.1 — one stochastic trajectory", fontsize=16, weight="bold")

    axes[0].plot(result.time, result.observed_signal, color=COLORS["ink"], lw=0.7, label="observed")
    axes[0].plot(result.time, result.coherent_signal, color=COLORS["wave"], lw=1.2, label="latent coherent trace")
    axes[0].set_ylabel("signal")
    axes[0].legend(loc="upper right", ncol=2)

    axes[1].plot(result.time, result.shell, color=COLORS["shell"], label="shell state σ")
    axes[1].plot(result.time, result.bulk, color=COLORS["bulk"], label="bulk occupancy q")
    axes[1].set_ylim(-0.03, 1.05)
    axes[1].set_ylabel("latent state")
    axes[1].legend(loc="upper right", ncol=2)

    axes[2].plot(result.time, result.direct_visibility, color=COLORS["ink"], label="direct visibility")
    axes[2].plot(result.time, result.residual_visibility, color=COLORS["wave"], label="wave visibility")
    axes[2].set_ylim(-0.03, 1.05)
    axes[2].set_ylabel("coupling")
    axes[2].legend(loc="upper right", ncol=2)

    click_times = result.time[result.clicks > 0]
    axes[3].vlines(click_times, 0.0, 0.65, color=COLORS["ink"], lw=0.7, label="detector click")
    axes[3].fill_between(result.time, 0.0, result.measurement, color=COLORS["measure"], alpha=0.7, label="measurement pulse")
    axes[3].set_ylim(0.0, 1.1)
    axes[3].set_ylabel("events")
    axes[3].set_xlabel("normalized time")
    axes[3].legend(loc="upper right", ncol=2)

    for axis in axes:
        axis.grid(alpha=0.18)
        axis.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)


def pulse_response(
    results: list[SimulationResult], config: SimulationConfig, window: float = 5.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    length = round(window / config.dt)
    relative = np.arange(length) * config.dt
    traces: list[np.ndarray] = []
    for result in results:
        for pulse in np.arange(config.pulse_start, config.duration, config.pulse_interval):
            start = round(pulse / config.dt)
            stop = start + length
            if stop <= len(result.time):
                # Smooth absolute signal energy so phase cancellation does not hide response.
                kernel = np.ones(max(1, int(0.16 / config.dt)))
                kernel /= kernel.sum()
                energy = np.convolve(np.abs(result.coherent_signal[start:stop]), kernel, mode="same")
                traces.append(energy)
    data = np.asarray(traces)
    return relative, np.mean(data, axis=0), np.percentile(data, [5, 95], axis=0)


def plot_response_comparison(
    result_sets: dict[str, list[SimulationResult]],
    config: SimulationConfig,
    output: str | Path,
) -> None:
    fig, axis = plt.subplots(figsize=(11, 5.5))
    styles = {
        "wios": (COLORS["shell"], "WIOS hypothesis"),
        "instrumental_null": (COLORS["null"], "Instrumental null"),
    }
    for model, results in result_sets.items():
        relative, mean, bounds = pulse_response(results, config)
        color, label = styles[model]
        axis.plot(relative, mean, color=color, lw=2.0, label=label)
        axis.fill_between(relative, bounds[0], bounds[1], color=color, alpha=0.14)
    axis.axvspan(0, config.pulse_duration, color=COLORS["measure"], alpha=0.3, label="measurement on")
    axis.set(title="Ensemble response after a measurement pulse", xlabel="time since pulse", ylabel="coherent trace magnitude")
    axis.grid(alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(ncol=3)
    fig.tight_layout()
    fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)


def plot_metric_comparison(
    metrics: dict[str, list[RunMetrics]], output: str | Path
) -> None:
    names = [
        "post_pulse_click_suppression",
        "post_pulse_coherence_retention",
        "direct_to_residual_ratio",
        "bulk_mean",
    ]
    labels = ["click suppression", "coherence retention", "direct/residual", "bulk occupancy"]
    x = np.arange(len(names))
    width = 0.35
    fig, axis = plt.subplots(figsize=(11, 5.5))
    for offset, (model, color, label) in enumerate([
        ("wios", COLORS["shell"], "WIOS"),
        ("instrumental_null", COLORS["null"], "instrumental null"),
    ]):
        means = [np.nanmean([getattr(row, name) for row in metrics[model]]) for name in names]
        stds = [np.nanstd([getattr(row, name) for row in metrics[model]]) for name in names]
        axis.bar(x + (offset - 0.5) * width, means, width, yerr=stds, color=color, alpha=0.82, capsize=3, label=label)
    axis.axhline(0, color=COLORS["ink"], lw=0.8)
    axis.set_xticks(x, labels)
    axis.set_ylabel("normalized metric")
    axis.set_title("The hypothesis must beat a strong instrumental baseline")
    axis.grid(axis="y", alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)
