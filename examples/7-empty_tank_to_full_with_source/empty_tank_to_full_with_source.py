# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.devices import Source 
from tanksim.link.link import Link
from tanksim.postprocessing import ReadResults
from tanksim.physics import TankPhysicalProperty, SourcePhysicalProperty
from tanksim.simulation import Simulation


def main():
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))
    tank.set_level(level=0.0)
    
    source = Source(
        name="FEED",
        tank=tank,
        massflow=10.0,
    )

    simulation = Simulation(tanks=[tank], devices=[source])
    simulation.setup()

    # Variables declaration
    simulation.enable_state_recording(interval=1.0)
    t_max = 300.0

    source_flag = 0

    while simulation.time < t_max:
        # Actions
        if simulation.time > 50.0 and source_flag == 0:
            source.enable()
            source_flag = 1

        if simulation.time > 60.0 and source_flag == 1:
            source.disable()
            source_flag = 2

        if simulation.time > 100.0 and source_flag == 2:
            source.enable()
            source_flag = 3

        if simulation.time > 150.0 and source_flag == 3:
            source.massflow = 20.0
            source_flag = 4

        dt = simulation.step()

    results = ReadResults()
    results.add_time_evolution(tank, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(tank, TankPhysicalProperty.MASS)
    results.add_time_evolution(source, SourcePhysicalProperty.MASSFLOW)
    results.show()

    results.save_pdf()
    cwd = Path.cwd()
    folder = cwd / "examples/1-tank_drainage_to_atmosphere/report.csv"
    results.generate_report(folder)

if __name__ == "__main__":
    main()
