# coding: utf-8
from tanksim.tank import Geometry, Tank
from tanksim.models.orifice import Orifice
from tanksim.record import Record
from tanksim.simulation import Simulation

def main():
    # Element declaration
    elements = []

    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.set_level(level=0.5)

    is_orifice_opened = False

    simulation = Simulation()
    simulation.append(tank)

    # Variables declaration
    t_max = 100.0
    t_print = 0.0
    dt_print = 5.0

    record = Record()

    while simulation.time < t_max:
        # Actions
        if simulation.time > 10.0 and is_orifice_opened == False:
            tank.add_orifice(diameter=100.0e-3)
            is_orifice_opened = True

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
            for i, ori in enumerate(tank.orifices):
                record.monitor(f"qm_break{i}", simulation.time, ori.massflow)

            t_print += dt_print

        dt = simulation.step()

    record.show()

if __name__ == "__main__":
    main()
