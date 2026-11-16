import pytest

from tanksim.devices import Source
from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.devices import Source 
from tanksim.link.link import Link
from tanksim.postprocessing import ReadResults
from tanksim.physics import  SourcePhysicalProperty
from tanksim.simulation import Simulation


def test_source_properly_read(tmp_path):
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    tank.set_level(level=0.0)
    
    source = Source(
        name="FEED",
        tank=tank,
        massflow=10.0,
    )

    simulation = Simulation(tanks=[tank], devices=[source])

    results_path = tmp_path  / "results.h5"
    simulation.results_storage.output_results_path = results_path
    simulation.enable_state_recording(interval=0.1)
    simulation.setup()

    source.enable()
    simulation.step()

    source.disable()
    simulation.step()

    source.enable()
    simulation.step()

    source.massflow = 20.0
    simulation.step()

    results = ReadResults(results_path)
    results.add_time_evolution(source, SourcePhysicalProperty.MASSFLOW)

    time_from_hdf5 = results.requested_variables[(source.name, SourcePhysicalProperty.MASSFLOW)].time
    values_from_hdf5 = results.requested_variables[(source.name, SourcePhysicalProperty.MASSFLOW)].value

    assert time_from_hdf5   == pytest.approx([0.0, 0.1, 0.2 , 0.3, 0.4])
    assert values_from_hdf5 == pytest.approx([10.0, 10.0, 0.0, 10.0, 20.0])


def test_source_properly_read_from_str(tmp_path):
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    tank.set_level(level=0.0)
    
    source = Source(
        name="FEED",
        tank=tank,
        massflow=10.0,
    )

    simulation = Simulation(tanks=[tank], devices=[source])

    results_path = tmp_path  / "results.h5"
    simulation.results_storage.output_results_path = results_path
    simulation.enable_state_recording(interval=0.1)
    simulation.setup()

    source.enable()
    simulation.step()

    source.disable()
    simulation.step()

    source.enable()
    simulation.step()

    source.massflow = 20.0
    simulation.step()

    results = ReadResults(results_path)
    results.add_time_evolution("FEED", SourcePhysicalProperty.MASSFLOW)

    time_from_hdf5 = results.requested_variables[(source.name, SourcePhysicalProperty.MASSFLOW)].time
    values_from_hdf5 = results.requested_variables[(source.name, SourcePhysicalProperty.MASSFLOW)].value

    assert time_from_hdf5   == pytest.approx([0.0, 0.1, 0.2 , 0.3, 0.4])
    assert values_from_hdf5 == pytest.approx([10.0, 10.0, 0.0, 10.0, 20.0])

# if __name__ == "__main__":
#      test_source_properly_read()