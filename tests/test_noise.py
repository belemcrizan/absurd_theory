import numpy as np
import pytest

from absurd_theory.noise import colored_background, load_empirical_noise


def test_empirical_csv_loader(tmp_path):
    path = tmp_path / "noise.csv"
    path.write_text("time,strain\n0,1\n1,2\n2,4\n", encoding="utf-8")
    noise = load_empirical_noise(path, "strain")
    assert np.isclose(noise.mean(), 0)
    assert np.isclose(noise.std(), 1)


def test_constant_noise_is_rejected(tmp_path):
    path = tmp_path / "noise.csv"
    path.write_text("value\n2\n2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_empirical_noise(path)


def test_colored_noise_is_reproducible():
    left = colored_background(100, np.random.default_rng(7), 0.9, 0.1, 0.2)
    right = colored_background(100, np.random.default_rng(7), 0.9, 0.1, 0.2)
    assert np.array_equal(left, right)
