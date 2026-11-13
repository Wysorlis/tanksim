# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.link.link import Link
from tanksim.boundaries import Atmosphere
from tanksim.postprocessing import ReadResults
from tanksim.physics import TankPhysicalProperty, LinkPhysicalProperty
from tanksim.simulation import Simulation

def main():
    tank_a = Tank("TANK_A")
    tank_a.set_geometry(Geometry(height=1.0, surface=2.5))
    tank_a.set_level(level=1.0)

    tank_b = Tank("TANK_B")
    tank_b.set_geometry(Geometry(height=1.0, surface=2.5))
    tank_b.set_level(level=0.5)
    
    connection = Link(
        name="connection",
        upstream=Port(tank_a, 0.3),
        downstream=Port(tank_b, 0.3),
        model=Orifice(diameter=50.0e-3),
        align_ports=True,
    )

    drainage = Link(
        name="drainage",
        upstream=Port(tank_a, 0.0),
        downstream=Atmosphere(),
        model=Orifice(diameter=200.0e-3),
    )


    simulation = Simulation()
    simulation.add_tank(tank_a)
    simulation.add_tank(tank_b)
    simulation.add_link(connection)
    simulation.add_link(drainage)
    simulation.setup()

    # Variables declaration
    simulation.enable_state_recording(interval=1.0)
    t_max = 300.0
    t_print = 0.0
    dt_print = 5.0

    is_orifice_opened = False
    is_drainage_opened = False

    # record = Record()

    while simulation.time < t_max:
        # Actions
        if simulation.time > 10.0 and is_orifice_opened == False:
            connection.open()
            is_orifice_opened = True

        if simulation.time > 75.0 and is_drainage_opened == False:
            drainage.open()
            is_drainage_opened = True
            
        # Prints        
        if simulation.time >= t_print:
            print("="*50)
            print(f"time = {simulation.time:.2f} s")
            print("="*50)
            tank_a.show()
            tank_b.show()
            print()

            t_print += dt_print

        dt = simulation.step()

    results = ReadResults()
    results.add_time_evolution(tank_a, TankPhysicalProperty.MASS)
    results.add_time_evolution(tank_a, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(tank_b, TankPhysicalProperty.MASS)
    results.add_time_evolution(tank_b, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(connection, LinkPhysicalProperty.MASSFLOW)
    results.add_time_evolution(drainage, LinkPhysicalProperty.MASSFLOW)
    results.show()

    results.save_pdf()

if __name__ == "__main__":
    main()
