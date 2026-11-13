import pytest

from tanksim.boundaries import Atmosphere
from tanksim.link.link import Link
from tanksim.models.orifice import Orifice
from tanksim.simulation import Simulation
from tanksim.tank import Geometry, Port, Tank


def test_closed_tank_preserves_mass_and_level():
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=1.0, surface=2.5))
    tank.set_level(0.5)
    initial_mass = tank.liquid_mass
    initial_volume = tank.liquid_volume
    initial_level = tank.level

    for _ in range(10):
        tank.update(dt=0.1, net_massflow=0.0)

    assert tank.liquid_mass == pytest.approx(initial_mass)
    assert tank.liquid_volume == pytest.approx(initial_volume)
    assert tank.level == pytest.approx(initial_level)


def test_mass_loss_matches_total_outflow_through_two_orifices():
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=1.0, surface=2.5))
    tank.set_level(0.5)
    connections = [
        Link(
            name=f"connection_{diameter}",
            upstream=Port(tank=tank, height=0.0),
            downstream=Atmosphere(),
            model=Orifice(diameter=diameter),
        )
        for diameter in (0.01, 0.02)
    ]
    for connection in connections:
        connection.open()

    initial_mass = tank.liquid_mass
    dt = 0.1
    simulation = Simulation(tanks=[tank], links=connections)
    simulation.dt = dt
    simulation.setup()

    simulation.step()

    discharged_mass = sum(connection.massflow for connection in connections) * dt
    assert discharged_mass > 0.0
    assert initial_mass - tank.liquid_mass == pytest.approx(discharged_mass)
    assert tank.liquid_mass == pytest.approx(tank.liquid_volume * tank.liquid_density)
