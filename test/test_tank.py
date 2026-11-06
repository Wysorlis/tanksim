import pytest

from tanksim.tank import Geometry, Tank


def test_closed_tank_preserves_mass_and_level():
    tank = Tank(Geometry(height=2.0, surface=2.5))
    tank.set_level(0.5)
    initial_mass = tank.liquid_mass
    initial_volume = tank.liquid_volume
    initial_level = tank.level

    for _ in range(10):
        tank.update(dt=0.1)

    assert tank.liquid_mass == pytest.approx(initial_mass)
    assert tank.liquid_volume == pytest.approx(initial_volume)
    assert tank.level == pytest.approx(initial_level)


def test_mass_loss_matches_total_outflow_through_two_orifices():
    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.set_level(0.5)
    tank.add_orifice(diameter=0.01)
    tank.add_orifice(diameter=0.02)
    initial_mass = tank.liquid_mass
    dt = 0.1

    tank.update(dt)

    discharged_mass = sum(orifice.massflow for orifice in tank.orifices) * dt
    assert discharged_mass > 0.0
    assert initial_mass - tank.liquid_mass == pytest.approx(discharged_mass)
    assert tank.liquid_mass == pytest.approx(tank.liquid_volume * tank.liquid_density)
