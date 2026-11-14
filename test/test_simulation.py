import pytest
from math import pi, sqrt

from tanksim.link.link import Link
from tanksim.models.orifice import Orifice
from tanksim.simulation import Simulation
from tanksim.tank import Geometry, Port, Tank
from tanksim.boundaries import Atmosphere
from tanksim.constants import GRAVITY


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

def make_tank(name):
    tank = Tank(name)
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    return tank

def test_rejects_duplicate_names_between_tank_and_link():
    tank = make_tank("SHARED")
    simulation = Simulation(tanks=[tank])

    link = Link(
        name="SHARED",
        upstream=Port(tank, 0.0),
        downstream=Atmosphere(),
        model=Orifice(diameter=0.1),
    )

    with pytest.raises(ValueError, match="Element name 'SHARED' is already in use."):
        simulation.add_link(link)


def test_setup_aligns_ports_from_fixed_elevation():
    tank_a = make_tank("A")
    tank_b = make_tank("B")
    tank_a.bottom_elevation = 10.0

    port_a = Port(tank_a, 0.8)
    port_b = Port(tank_b, 0.3)

    link = Link(
        name="AB",
        upstream=port_a,
        downstream=port_b,
        model=Orifice(diameter=0.1),
        align_ports=True,
    )

    simulation = Simulation(tanks=[tank_a, tank_b], links=[link])
    simulation.setup()

    # Le port A est à 10,8 m ; le fond de B doit donc être à 10,5 m.
    assert tank_a.bottom_elevation == pytest.approx(10.0)
    assert tank_b.bottom_elevation == pytest.approx(10.5)
    assert port_a.elevation == pytest.approx(port_b.elevation)


def test_setup_rejects_incompatible_alignment_cycle():
    a, b, c = [make_tank(name) for name in ("A", "B", "C")]

    links = [
        Link(
            name=name,
            upstream=Port(upstream, 1.0),
            downstream=Port(downstream, 0.0),
            model=Orifice(diameter=0.1),
            align_ports=True,
        )
        for name, upstream, downstream in (
            ("AB", a, b),
            ("BC", b, c),
            ("CA", c, a),
        )
    ]

    simulation = Simulation(tanks=[a, b, c], links=links)

    with pytest.raises(ValueError, match="Incompatible port-alignment cycle"):
        simulation.setup()


def test_outflow_limiter_preserves_flow_when_mass_is_sufficient():
    tank = Tank("SOURCE")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    tank.state.liquid_density = 1000.0

    # Hauteur choisie pour obtenir une vitesse de 2 m/s.
    tank.set_level(2.0 / GRAVITY)

    link = Link(
        name="DRAIN",
        upstream=Port(tank, 0.0),
        downstream=Atmosphere(),
        # Section de 0,001 m² → débit attendu de 2 kg/s.
        model=Orifice(diameter=sqrt(4.0 * 0.001 / pi)),
    )

    simulation = Simulation(tanks=[tank], links=[link])
    simulation.dt = 0.1
    simulation.setup()

    initial_mass = tank.liquid_mass
    link.open()

    simulation.step()

    assert link.state.liquid_velocity == pytest.approx(2.0)
    assert link.massflow == pytest.approx(2.0)

    # Pendant 0,1 s à 2 kg/s, le tank perd 0,2 kg.
    assert tank.liquid_mass == pytest.approx(initial_mass - 0.2)


def test_outflow_limiter_preserves_flow_when_mass_is_sufficient():
    tank = Tank("SOURCE")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    tank.state.liquid_density = 1000.0

    # Hauteur choisie pour obtenir une vitesse de 2 m/s.
    tank.set_level(2.0 / GRAVITY)

    link = Link(
        name="DRAIN",
        upstream=Port(tank, 0.0),
        downstream=Atmosphere(),
        # Section de 0,001 m² → débit attendu de 2 kg/s.
        model=Orifice(diameter=sqrt(4.0 * 0.001 / pi)),
    )

    simulation = Simulation(tanks=[tank], links=[link])
    simulation.dt = 0.1
    simulation.setup()

    initial_mass = tank.liquid_mass
    link.open()

    simulation.step()

    assert link.state.liquid_velocity == pytest.approx(2.0)
    assert link.massflow == pytest.approx(2.0)

    # Pendant 0,1 s à 2 kg/s, le tank perd 0,2 kg.
    assert tank.liquid_mass == pytest.approx(initial_mass - 0.2)