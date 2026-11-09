# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link import Link
from tanksim.postprocessing import ReadResults, PhysicalProperty
from tanksim.simulation import Simulation

def main():
    tank = Tank("TANK_A")
    tank.set_geometry(Geometry(height=1.0, surface=2.5))
    tank.set_level(level=0.8)
    
    connection = Link(
        upstream=Port(tank, 0.0),
        downstream=Atmosphere(),
        model=Orifice(diameter=100.0e-3),
    )

    simulation = Simulation()
    simulation.add_tank(tank)

    simulation.add_link(connection)

    simulation.setup()

    # Variables declaration
    simulation.enable_state_recording(interval=5.0)
    t_max = 300.0
    t_print = 0.0
    dt_print = 5.0

    is_orifice_opened = False

    while simulation.time < t_max:
        # Actions
        if simulation.time > 10.0 and is_orifice_opened == False:
            connection.open()
            is_orifice_opened = True

        # Prints        
        if simulation.time >= t_print:
            print("="*50)
            print(f"time = {simulation.time:.2f} s")
            print("="*50)
            tank.show()
            print()

            t_print += dt_print

        dt = simulation.step()

    results = ReadResults()
    results.add_time_evolution(tank.name, PhysicalProperty.MASS)
    results.add_time_evolution(tank.name, PhysicalProperty.DENSITY)
    results.add_time_evolution(tank.name, PhysicalProperty.LEVEL)
    results.add_time_evolution(tank.name, PhysicalProperty.VOLUME)
    results.show()

    results.save_pdf()

if __name__ == "__main__":
    main()
