import pytest

from tanksim.tank import Geometry


def test_volume_is_computed_from_dimensions():
    geometry = Geometry(height=2.0, surface=2.5)

    assert geometry.volume == pytest.approx(5.0)
