"""Stochastic WIOS and strong instrumental-null simulations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .config import SimulationConfig
from .noise import add_glitches, colored_background

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class SimulationResult:
    model: str
    time: FloatArray
    measurement: FloatArray
    shell: FloatArray
    bulk: FloatArray
    direct_visibility: FloatArray
    residual_visibility: FloatArray
    coherent_signal: FloatArray
    observed_signal: FloatArray
    clicks: FloatArray
    return_flux: FloatArray
    instrument_state: FloatArray

    def as_columns(self) -> dict[str, FloatArray]:
        return {
            "time": self.time,
            "measurement": self.measurement,
            "shell": self.shell,
            "bulk": self.bulk,
            "direct_visibility": self.direct_visibility,
            "residual_visibility": self.residual_visibility,
            "coherent_signal": self.coherent_signal,
            "observed_signal": self.observed_signal,
            "clicks": self.clicks,
            "return_flux": self.return_flux,
            "instrument_state": self.instrument_state,
        }


def _sigmoid(value: float) -> float:
    clipped = float(np.clip(value, -60.0, 60.0))
    return 1.0 / (1.0 + np.exp(-clipped))


def measurement_schedule(time: FloatArray, config: SimulationConfig) -> FloatArray:
    schedule = np.zeros_like(time)
    if config.pulse_duration == 0:
        return schedule
    pulse_times = np.arange(config.pulse_start, config.duration, config.pulse_interval)
    for pulse in pulse_times:
        schedule[(time >= pulse) & (time < pulse + config.pulse_duration)] = (
            config.pulse_strength
        )
    return schedule


def simulate(
    config: SimulationConfig,
    *,
    seed: int = 42,
    model: str = "wios",
    empirical_noise: FloatArray | None = None,
) -> SimulationResult:
    """Simulate WIOS or an adversarial instrumental null.

    The null deliberately contains measurement saturation and recovery, so a
    post-measurement silence/recovery pattern alone cannot validate WIOS.
    """

    config.validate()
    if model not in {"wios", "instrumental_null"}:
        raise ValueError("model must be 'wios' or 'instrumental_null'")

    rng = np.random.default_rng(seed)
    size = round(config.duration / config.dt)
    time = np.arange(size, dtype=float) * config.dt
    measurement = measurement_schedule(time, config)

    shell = np.zeros(size, dtype=float)
    bulk = np.zeros(size, dtype=float)
    instrument = np.zeros(size, dtype=float)
    return_flux = np.zeros(size, dtype=float)

    if model == "wios":
        shell[0] = 0.08
        for index in range(1, size):
            previous = shell[index - 1]
            bistable = (
                -2.0
                * config.shell_barrier
                * previous
                * (1.0 - previous)
                * (1.0 - 2.0 * previous)
            )
            wave_drive = config.wave_shell_drive * (config.wave_amplitude**2) * (
                1.0 - previous
            )
            backaction = (
                config.measurement_backaction
                * measurement[index - 1]
                * (1.0 - previous)
            )
            relaxation = -config.shell_relaxation * previous
            diffusion = config.shell_noise * np.sqrt(config.dt) * rng.normal()
            shell[index] = np.clip(
                previous
                + config.dt * (bistable + wave_drive + backaction + relaxation)
                + diffusion,
                0.0,
                1.0,
            )

            entry_gate = _sigmoid(
                (shell[index] - config.bulk_threshold) / config.bulk_temperature
            )
            entry = config.bulk_entry_rate * entry_gate * (1.0 - bulk[index - 1])
            returned = config.bulk_return_rate * bulk[index - 1]
            bulk[index] = np.clip(
                bulk[index - 1] + config.dt * (entry - returned), 0.0, 1.0
            )
            return_flux[index] = returned
    else:
        for index in range(1, size):
            instrument[index] = max(
                0.0,
                instrument[index - 1]
                + config.dt
                * (
                    config.instrument_artifact * measurement[index - 1]
                    - instrument[index - 1] / config.instrument_recovery
                ),
            )

    if model == "wios":
        direct_visibility = np.exp(-config.direct_suppression * shell * shell) * (
            1.0 - bulk
        )
        residual_visibility = (
            1.0
            / (1.0 + config.residual_suppression * shell * shell)
            * (1.0 - config.bulk_attenuation * bulk)
        )
    else:
        # The null mimics detector saturation by suppressing every observed channel.
        attenuation = np.exp(-instrument)
        direct_visibility = attenuation
        residual_visibility = attenuation

    phase = 2.0 * np.pi * config.wave_frequency * time
    coherent_signal = (
        config.wave_amplitude * residual_visibility * np.sin(phase)
        + config.echo_strength * return_flux * np.sin(phase - np.pi / 3.0)
    )
    background = colored_background(
        size,
        rng,
        config.colored_rho,
        config.white_noise,
        config.colored_noise,
        empirical_noise,
    )
    observed = add_glitches(
        coherent_signal + background,
        config.dt,
        config.glitch_rate,
        config.glitch_scale,
        rng,
    )

    click_probability = 1.0 - np.exp(
        -config.click_rate * config.dt * np.clip(direct_visibility, 0.0, 1.0)
    )
    clicks = (rng.random(size) < click_probability).astype(float)

    return SimulationResult(
        model=model,
        time=time,
        measurement=measurement,
        shell=shell,
        bulk=bulk,
        direct_visibility=direct_visibility,
        residual_visibility=residual_visibility,
        coherent_signal=coherent_signal,
        observed_signal=observed,
        clicks=clicks,
        return_flux=return_flux,
        instrument_state=instrument,
    )
