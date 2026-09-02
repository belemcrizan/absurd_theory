import json

import pytest

from absurd_theory.config import SimulationConfig


def test_round_trip_config(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(SimulationConfig().to_dict()), encoding="utf-8")
    loaded = SimulationConfig.from_json(path)
    assert loaded == SimulationConfig()


def test_invalid_config_is_rejected():
    with pytest.raises(ValueError):
        SimulationConfig(dt=-1).validate()
