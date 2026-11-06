import pytest

from tanksim.tank import Geometry, Port, Tank


@pytest.mark.parametrize("height", [0.0, 0.75, 2.0])
def test_port_accepts_heights_inside_tank(height):
    tank = Tank(Geometry(height=2.0, surface=2.5))

    port = Port(tank=tank, height=height)

    assert port.tank is tank
    assert port.height == pytest.approx(height)


@pytest.mark.parametrize("height", [-0.1, 2.1])
def test_port_rejects_heights_outside_tank(height):
    tank = Tank(Geometry(height=2.0, surface=2.5))

    with pytest.raises(ValueError):
        Port(tank=tank, height=height)
