# coding: utf-8
import pytest
import numpy as np

from tanksim.tank import Tank, Geometry, Port
from tanksim.models import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link.link import Link    
from tanksim.constants import GRAVITY


def test_closed_link_after_open_has_zero_velocity():
    tank = Tank("TANK_TEST")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    tank.set_level(level=1.0)

    tank_port = Port(tank, 0.0)
    boundary = Atmosphere()

    connection = Link(
        name="connection",
        upstream=tank_port,
        downstream=boundary,
        model=Orifice(diameter=100.0e-3),
    )

    connection.open()
    connection.update(dt=0.3)

    expected_velocity = np.sqrt(2.0 * GRAVITY * (tank.level - tank_port.height))
    
    assert connection.state.liquid_velocity == pytest.approx(expected_velocity)

    connection.close()

    # La fermeture annule immédiatement l'écoulement.
    assert connection.state.liquid_velocity == pytest.approx(0.0)
    assert connection.massflow == pytest.approx(0.0)

    # Il reste nul lors du calcul suivant.
    connection.update(dt=0.3)

    assert connection.state.liquid_velocity == pytest.approx(0.0)
    assert connection.massflow == pytest.approx(0.0)