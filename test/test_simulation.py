import pytest

from tanksim.link.link import Link
from tanksim.models.orifice import Orifice
from tanksim.simulation import Simulation
from tanksim.tank import Geometry, Port, Tank


@pytest.mark.parametrize("reverse", [False, True])
def test_outflows_share_available_mass_without_creating_mass(reverse):
    source = Tank("SOURCE")
    receiver_a = Tank("RECEIVER_A")
    receiver_b = Tank("RECEIVER_B")

    for tank, level in (
        (source, 0.01),
        (receiver_a, 0.0),
        (receiver_b, 0.0),
    ):
        tank.set_geometry(Geometry(height=1.0, surface=1.0))
        tank.set_level(level)

    # SOURCE contient 10 kg.
    # Les sections des deux orifices sont dans un rapport 1:4.
    links = []
    for receiver, diameter in (
        (receiver_a, 1.0),
        (receiver_b, 2.0),
    ):
        upstream, downstream = (receiver, source) if reverse else (source, receiver)

        links.append(
            Link(
                name=f"TRANSFER_{receiver.name}",
                upstream=Port(upstream, 0.0),
                downstream=Port(downstream, 0.0),
                model=Orifice(diameter=diameter),
                align_ports=True,
            )
        )

    simulation = Simulation(
        tanks=[source, receiver_a, receiver_b],
        links=links,
    )
    simulation.dt = 0.1
    simulation.setup()

    for link in links:
        link.open()

    initial_mass = sum(tank.liquid_mass for tank in simulation.tanks)

    simulation.step()

    # Le donneur est vidé, sans masse négative.
    assert source.liquid_mass == pytest.approx(0.0)

    # Même facteur appliqué aux deux sorties : répartition 1:4.
    assert receiver_a.liquid_mass == pytest.approx(2.0)
    assert receiver_b.liquid_mass == pytest.approx(8.0)

    # Conservation globale.
    final_mass = sum(tank.liquid_mass for tank in simulation.tanks)
    assert final_mass == pytest.approx(initial_mass)

    # L'état des liens représente bien les transferts appliqués.
    direction = -1.0 if reverse else 1.0
    assert links[0].massflow * simulation.dt == pytest.approx(direction * 2.0)
    assert links[1].massflow * simulation.dt == pytest.approx(direction * 8.0)