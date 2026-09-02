"""Absurd Theory: a falsifiable WIOS toy-model simulator."""

from .config import SimulationConfig
from .simulation import SimulationResult, simulate

__all__ = ["SimulationConfig", "SimulationResult", "simulate"]
__version__ = "0.1.0"
