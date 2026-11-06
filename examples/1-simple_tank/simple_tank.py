# coding: utf-8
from tanksim.tank import Geometry, Tank
from tanksim.record import Record

def main():
    # Element declaration
    elements = []

    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.set_level(level=0.5)

    elements.append(tank)

    # Variable declaration
    time = 0.0
    t_max = 100.0
    dt = 0.1

    t_print = 0.0
    dt_print = 5.0

    record = Record()

    while time < t_max:
        # Actions
        if time > 10.0:
            tank.openbreak(massflow=20.0)

        # Prints        
        if time >= t_print:
            print("="*50)
            print(f"time = {time:.2f} s")
            print("="*50)
            tank.show()
            print()

            record.monitor("m_liq", time, tank.liquid_mass)
            record.monitor("v_liq", time, tank.liquid_volume)
            record.monitor("lvl", time, tank.level)
            record.monitor("qm_break", time, tank.massflow_break)

            t_print += dt_print

        # Time management
        time += dt

        # Elements management
        for elem in elements:
            elem.update(dt)

    record.show()

if __name__ == "__main__":
    main()
