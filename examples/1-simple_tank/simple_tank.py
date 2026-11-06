# coding: utf-8
from tanksim.tank import Geometry, Tank
from tanksim.tank import Breach
from tanksim.record import Record
from tanksim.simulation import Simulation

def main():
    # Element declaration
    elements = []

    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.add_opening()
    tank.set_level(level=0.5)


    simulation = Simulation()
    simulation.append(tank)

    # Variable declaration
    t_max = 100.0
    t_print = 0.0
    dt_print = 5.0

    record = Record()

    while simulation.time < t_max:
        # Actions
        if simulation.time > 10.0:
            tank.openbreak(massflow=20.0)

        # Prints        
        if simulation.time >= t_print:
            print("="*50)
            print(f"time = {simulation.time:.2f} s")
            print("="*50)
            tank.show()
            print()

            record.monitor("m_liq", simulation.time, tank.liquid_mass)
            record.monitor("v_liq", simulation.time, tank.liquid_volume)
            record.monitor("lvl", simulation.time, tank.level)
            record.monitor("qm_break", simulation.time, tank.massflow_break)

            t_print += dt_print


        dt = simulation.step()

    record.show()

if __name__ == "__main__":
    main()
