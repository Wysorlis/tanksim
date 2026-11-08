# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link import Link
from tanksim.record import Record
from tanksim.simulation import Simulation

def main():
    tank = Tank(Geometry(height=1.0, surface=2.5))
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
    t_max = 300.0
    t_print = 0.0
    dt_print = 5.0

    is_orifice_opened = False

    record = Record()

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

            record.monitor("m_liq", simulation.time, tank.liquid_mass)
            # record.monitor("v_liq", simulation.time, tank.liquid_volume)
            record.monitor("lvl", simulation.time, tank.level)

            t_print += dt_print

        dt = simulation.step()

    record.save_pdf(Path(__file__).with_name("results.pdf"))
    record.show()

if __name__ == "__main__":
    main()
