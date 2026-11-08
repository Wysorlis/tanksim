# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link import Link
from tanksim.postprocessing.record import Record
from tanksim.simulation import Simulation

def main():
    tank_a = Tank("TANK_A")
    tank_a.add_geometry(Geometry(height=1.0, surface=2.5))
    tank_a.set_level(level=0.2)

    tank_b = Tank("TANK_B")
    tank_b.add_geometry(Geometry(height=1.0, surface=2.5))
    tank_b.set_level(level=0.8)

    tank_c = Tank("TANK_C")
    tank_c.add_geometry(Geometry(height=2.0, surface=3))
    tank_c.set_level(level=0.75)
    
    connection = Link(
        upstream=Port(tank_a, 0.2),
        downstream=Port(tank_b, 0.0),
        model=Orifice(diameter=100.0e-3),
        align_ports=True,
    )

    connection2 = Link(
        upstream=Port(tank_b, 0.0),
        downstream=Port(tank_c, 2.0),
        model=Orifice(diameter=100.0e-3),
        align_ports=True,
    )

    connection3 = Link(
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
    t_max = 300.0
    t_print = 0.0
    dt_print = 5.0

    is_orifice_opened = False
    is_orifice_opened2 = False
    is_orifice_opened3 = False

    record = Record()

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

            record.monitor("m_liq", simulation.time, tank_a.liquid_mass)
            record.monitor("lvl", simulation.time, tank_a.level)

            record.monitor("m_liq2", simulation.time, tank_b.liquid_mass)
            record.monitor("lvl2", simulation.time, tank_b.level)

            record.monitor("m_liq3", simulation.time, tank_c.liquid_mass)
            record.monitor("lvl3", simulation.time, tank_c.level)

            t_print += dt_print

        dt = simulation.step()

    record.save_pdf(Path(__file__).with_name("results.pdf"))
    record.show()

if __name__ == "__main__":
    main()
