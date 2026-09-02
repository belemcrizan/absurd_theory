"""Configuration for the WIOS and instrumental-null simulators."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SimulationConfig:
    """Dimensionless v0.1 parameters.

    The model intentionally uses normalized units. No value is fitted to evidence
    for a new particle or an extra dimension.
    """

    duration: float = 80.0
    dt: float = 0.01
    wave_frequency: float = 1.7
    wave_amplitude: float = 0.32

    shell_barrier: float = 5.0
    wave_shell_drive: float = 0.46
    measurement_backaction: float = 5.8
    shell_relaxation: float = 1.5
    shell_noise: float = 0.13

    direct_suppression: float = 5.5
    residual_suppression: float = 0.15

    bulk_entry_rate: float = 1.0
    bulk_return_rate: float = 0.18
    bulk_threshold: float = 0.62
    bulk_temperature: float = 0.07
    bulk_attenuation: float = 0.2
    echo_strength: float = 0.18

    click_rate: float = 7.0
    white_noise: float = 0.16
    colored_noise: float = 0.13
    colored_rho: float = 0.985
    glitch_rate: float = 0.035
    glitch_scale: float = 0.75

    pulse_start: float = 10.0
    pulse_interval: float = 10.0
    pulse_duration: float = 0.55
    pulse_strength: float = 1.0

    instrument_recovery: float = 1.8
    instrument_artifact: float = 0.75

    def validate(self) -> None:
        if self.duration <= 0 or self.dt <= 0:
            raise ValueError("duration and dt must be positive")
        if self.dt >= self.duration:
            raise ValueError("dt must be smaller than duration")
        if not 0 <= self.colored_rho < 1:
            raise ValueError("colored_rho must be in [0, 1)")
        if self.bulk_temperature <= 0:
            raise ValueError("bulk_temperature must be positive")
        if self.pulse_interval <= 0 or self.pulse_duration < 0:
            raise ValueError("invalid measurement-pulse schedule")

    @classmethod
    def from_json(cls, path: str | Path) -> SimulationConfig:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        config = cls(**payload)
        config.validate()
        return config

    def to_dict(self) -> dict[str, float]:
        return asdict(self)
