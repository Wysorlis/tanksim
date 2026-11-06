from math import pi, sqrt

import pytest

from tanksim.models.orifice import Orifice


def test_orifice_has_no_flow_at_zero_head():
    orifice = Orifice(diameter=0.01)

    massflow = orifice.update(dt=0.1, level=0.0, density=1000.0)

    assert massflow == pytest.approx(0.0)


def test_orifice_matches_torricelli_reference_case():
    # A head of 2 / g metres gives a velocity of 2 m/s.
    # With a section of 0.001 m² and water at 1000 kg/m³,
    # the expected mass flow is 2 kg/s.
    orifice = Orifice(diameter=sqrt(4.0 * 0.001 / pi))

    massflow = orifice.update(dt=0.1, level=2.0 / 9.81, density=1000.0)

    assert massflow == pytest.approx(2.0)
