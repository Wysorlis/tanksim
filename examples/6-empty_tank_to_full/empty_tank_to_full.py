# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import PressureBoundary
from tanksim.link.link import Link
from tanksim.postprocessing import ReadResults
from tanksim.physics import TankPhysicalProperty, LinkPhysicalProperty
from tanksim.simulation import Simulation


def main():
    tank = Tank("TANK")
    tank.set_geometry(Geometry(height=3.0, surface=1.0))
    tank.set_level(level=3.0)

    one_third_tank = Tank("1/3_TANK")
    one_third_tank.set_geometry(Geometry(height=1.0, surface=1.0))
    one_third_tank.set_level(level=0.0)
    
    connection = Link(
        name="connection",
        upstream=Port(tank, 0.0),
        downstream=Port(one_third_tank, 0.0),
        model=Orifice(diameter=100.0e-3),
    )

    simulation = Simulation(tanks=[tank, one_third_tank], links=[connection])
    simulation.setup()

    # Variables declaration
    simulation.enable_state_recording(interval=5.0)
    t_max = 300.0

    is_orifice_opened = False

    while simulation.time < t_max:
        # Actions
        if simulation.time > 50.0 and is_orifice_opened == False:
            connection.open()
            is_orifice_opened = True

        dt = simulation.step()

    results = ReadResults()
    results.add_time_evolution(tank, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(one_third_tank, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(one_third_tank, TankPhysicalProperty.OVERFLOW_MASS)
    results.add_time_evolution(connection, LinkPhysicalProperty.MASSFLOW)
    results.show()

    results.save_pdf()
    cwd = Path.cwd()
    folder = cwd / "examples/1-tank_drainage_to_atmosphere/report.csv"
    results.generate_report(folder)

if __name__ == "__main__":
    main()
