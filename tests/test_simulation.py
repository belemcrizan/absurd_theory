import numpy as np
import pytest

from absurd_theory.analysis import lock_in_amplitude, summarize
from absurd_theory.config import SimulationConfig
from absurd_theory.simulation import measurement_schedule, simulate


@pytest.fixture
def fast_config():
    return SimulationConfig(duration=20, dt=0.02, pulse_start=4, pulse_interval=5)


def test_measurement_schedule_has_pulses(fast_config):
    time = np.arange(int(fast_config.duration / fast_config.dt)) * fast_config.dt
    schedule = measurement_schedule(time, fast_config)
    assert schedule.max() == fast_config.pulse_strength
    assert 0 < schedule.mean() < schedule.max()


@pytest.mark.parametrize("model", ["wios", "instrumental_null"])
def test_simulation_is_bounded_and_reproducible(fast_config, model):
    left = simulate(fast_config, seed=9, model=model)
    right = simulate(fast_config, seed=9, model=model)
    assert np.array_equal(left.observed_signal, right.observed_signal)
    assert np.all((0 <= left.shell) & (left.shell <= 1))
    assert np.all((0 <= left.bulk) & (left.bulk <= 1))
    assert np.all((0 <= left.direct_visibility) & (left.direct_visibility <= 1))


def test_measurement_backaction_raises_shell(fast_config):
    result = simulate(fast_config, seed=2, model="wios")
    during = result.measurement > 0
    before = (result.time > 1) & (result.time < fast_config.pulse_start)
    assert result.shell[during].mean() > result.shell[before].mean()


def test_wios_can_hide_direct_channel_while_retaining_wave(fast_config):
    result = simulate(fast_config, seed=12, model="wios")
    assert result.direct_visibility.mean() < result.residual_visibility.mean()
    assert lock_in_amplitude(
        result.coherent_signal, result.time, fast_config.wave_frequency
    ) > 0.01
    metrics = summarize(result, fast_config)
    assert np.isfinite(metrics.direct_to_residual_ratio)


def test_unknown_model_is_rejected(fast_config):
    with pytest.raises(ValueError):
        simulate(fast_config, model="magic")
