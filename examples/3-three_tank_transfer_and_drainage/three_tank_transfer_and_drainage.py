# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link import Link
from tanksim.postprocessing import ReadResults
from tanksim.physics import TankPhysicalProperty, LinkPhysicalProperty
from tanksim.simulation import Simulation

def main():
    tank_a = Tank("TANK_A")
    tank_a.set_geometry(Geometry(height=1.0, surface=2.5))
    tank_a.set_level(level=0.2)

    tank_b = Tank("TANK_B")
    tank_b.set_geometry(Geometry(height=1.0, surface=2.5))
    tank_b.set_level(level=0.8)

    tank_c = Tank("TANK_C")
    tank_c.set_geometry(Geometry(height=2.0, surface=3))
    tank_c.set_level(level=0.75)
    
    connection = Link(
        name="connection",
        upstream=Port(tank_a, 0.2),
        downstream=Port(tank_b, 0.0),
        model=Orifice(diameter=100.0e-3),
        align_ports=True,
    )

    connection2 = Link(
        name="connection2",
        upstream=Port(tank_b, 0.0),
        downstream=Port(tank_c, 2.0),
        model=Orifice(diameter=100.0e-3),
        align_ports=True,
    )

    connection3 = Link(
        name="connection3",
        upstream=Port(tank_c, 0.0),
        downstream=Atmosphere(),
        model=Orifice(diameter=400.0e-3),
    )

    simulation = Simulation()
    simulation.add_tank(tank_a)
    simulation.add_tank(tank_b)
    simulation.add_tank(tank_c)
    simulation.add_link(connection)
    simulation.add_link(connection2)
    simulation.add_link(connection3)
    simulation.setup()

    # Variables declaration
    simulation.enable_state_recording(interval=5.0)
    t_max = 300.0
    t_print = 0.0
    dt_print = 5.0

    is_orifice_opened = False
    is_orifice_opened2 = False
    is_orifice_opened3 = False

    while simulation.time < t_max:
        # Actions
        if simulation.time > 10.0 and is_orifice_opened == False:
            connection.open()
            is_orifice_opened = True

        if simulation.time > 50.0 and is_orifice_opened2 == False:
            connection2.open()
            is_orifice_opened2 = True

        if simulation.time > 100.0 and is_orifice_opened3 == False:
            connection3.open()
            is_orifice_opened3 = True

        # Prints        
        if simulation.time >= t_print:
            print("="*50)
            print(f"time = {simulation.time:.2f} s")
            print("="*50)
            tank_a.show()
            tank_b.show()
            tank_c.show()
            print()

            t_print += dt_print

        dt = simulation.step()

    results = ReadResults()
    results.add_time_evolution(tank_a, TankPhysicalProperty.MASS)
    results.add_time_evolution(tank_a, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(tank_b, TankPhysicalProperty.MASS)
    results.add_time_evolution(tank_b, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(tank_c, TankPhysicalProperty.MASS)
    results.add_time_evolution(tank_c, TankPhysicalProperty.LEVEL)
    results.add_time_evolution(connection, LinkPhysicalProperty.MASSFLOW)
    results.add_time_evolution(connection2, LinkPhysicalProperty.MASSFLOW)
    results.add_time_evolution(connection3 ,LinkPhysicalProperty.MASSFLOW)
    results.show()

    results.save_pdf()

if __name__ == "__main__":
    main()
