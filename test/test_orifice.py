from math import pi, sqrt

import pytest

from tanksim.boundaries import Atmosphere
from tanksim.constants import GRAVITY
from tanksim.models.orifice import Orifice
from tanksim.tank import Geometry, Port, Tank


def test_orifice_has_no_flow_at_zero_head():
    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.set_level(0.0)
    orifice = Orifice(diameter=0.01)

    massflow = orifice.update(
        dt=0.1,
        upstream=Port(tank=tank, height=0.0),
        downstream=Atmosphere(),
    )

    assert massflow == pytest.approx(0.0)


def test_orifice_matches_torricelli_reference_case():
    # A head of 2 / g metres gives a velocity of 2 m/s.
    # With a section of 0.001 m² and water at 1000 kg/m³,
    # the expected mass flow is 2 kg/s.
    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.liquid_density = 1000.0
    tank.set_level(2.0 / GRAVITY)
    orifice = Orifice(diameter=sqrt(4.0 * 0.001 / pi))

    massflow = orifice.update(
        dt=0.1,
        upstream=Port(tank=tank, height=0.0),
        downstream=Atmosphere(),
    )

    assert massflow == pytest.approx(2.0)
