import pytest

from tanksim.boundaries import Atmosphere
from tanksim.link import Link
from tanksim.models import Orifice
from tanksim.physics import (
    TankPhysicalProperty as TP,
    LinkPhysicalProperty as LP,
)
from tanksim.postprocessing import ReadResults
from tanksim.simulation import Simulation
from tanksim.tank import Geometry, Port, Tank


def test_recorded_states_can_be_read_back(tmp_path):
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=1.0, surface=2.0))
    tank.state.liquid_density = 850.0
    tank.set_level(0.5)

    link = Link(
        name="DRAIN",
        upstream=Port(tank, 0.0),
        downstream=Atmosphere(),
        model=Orifice(diameter=0.1),
    )

    simulation = Simulation(tanks=[tank], links=[link])
    simulation.setup()

    path = tmp_path / "results.h5"
    simulation.results_storage.output_results_path = path
    simulation.enable_state_recording(interval=simulation.dt)

    times = []
    expected = []

    link.open()

    for index in range(3):
        if index == 2:
            link.close()

        simulation.step()

        # Conserver les valeurs attendues à chaque instant.
        times.append(simulation.time)
        expected.append({
            ("TANK", TP.MASS): tank.liquid_mass,
            ("TANK", TP.DENSITY): tank.liquid_density,
            ("TANK", TP.VOLUME): tank.liquid_volume,
            ("TANK", TP.LEVEL): tank.level,
            ("DRAIN", LP.VELOCITY): link.state.liquid_velocity,
            ("DRAIN", LP.DENSITY): link.state.liquid_density,
            ("DRAIN", LP.MASSFLOW): link.massflow,
        })

    # Relire uniquement à partir des noms enregistrés.
    results = ReadResults(path)

    for name, property in expected[0]:
        results.add_time_evolution(name, property)
        evolution = results.requested_variables[(name, property)]

        assert evolution.time == pytest.approx(times)
        assert evolution.value == pytest.approx([
            sample[(name, property)] for sample in expected
        ])

    flow = results.requested_variables[("DRAIN", LP.MASSFLOW)]
    assert flow.value[0] > 0.0
    assert flow.value[-1] == pytest.approx(0.0)