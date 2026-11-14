# coding: utf-8
from pathlib import Path

from tanksim.tank import Geometry, Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link.link import Link
from tanksim.postprocessing import ReadResults
from tanksim.physics import TankPhysicalProperty, LinkPhysicalProperty
from tanksim.simulation import Simulation

def main():
    top_tank = Tank("TOP_TANK")
    top_tank.set_geometry(Geometry(height=1.0, surface=2.0))
    top_tank.set_level(level=1.0)

    left_tank = Tank("LEFT_TANK")
    left_tank.set_geometry(Geometry(height=2.0, surface=1.0))
    left_tank.set_level(level=0.0)

    rigth_tank = Tank("RIGHT_TANK")
    rigth_tank.set_geometry(Geometry(height=2.0, surface=1.0))
    rigth_tank.set_level(level=0.0)

    bot_tank = Tank("BOT_TANK")
    bot_tank.set_geometry(Geometry(height=1.0, surface=3.0))
    bot_tank.set_level(level=0.0)

    top_left = Link(
        name="TOP_LEFT",
        upstream=Port(top_tank, 0.0),
        downstream=Port(left_tank, 2.0),
        model=Orifice(diameter=50.0e-3),
        align_ports=True,
    )

    top_right = Link(
        name="TOP_RIGHT",
        upstream=Port(top_tank, 0.0),
        downstream=Port(rigth_tank, 2.0),
        model=Orifice(diameter=50.0e-3),
        align_ports=True,
    )

    left_bot = Link(
        name="LEFT_BOT",
        upstream=Port(left_tank, 0.2),
        downstream=Port(bot_tank, 0.8),
        model=Orifice(diameter=80.0e-3),
        align_ports=True,
    )

    rigth_bot = Link(
        name="RIGTH_BOT",
        upstream=Port(rigth_tank, 0.4),
        downstream=Port(bot_tank, 1.0),
        model=Orifice(diameter=80.0e-3),
        align_ports=True,
    )

    atmosphere = Link(
        name="BC_ATM",
        upstream=Port(bot_tank, 0.1),
        downstream=Atmosphere(),
        model=Orifice(diameter=400.0e-3),
    )

    simulation = Simulation(tanks=[top_tank, left_tank, rigth_tank, bot_tank], links=[top_left, top_right, left_bot, rigth_bot, atmosphere])
    simulation.setup()

    # Variables declaration
    simulation.enable_state_recording(interval=1.0)
    t_max = 500.0
    t_print = 0.0
    dt_print = 5.0

    are_top_links_opened = False

    # Ouverture des liens
    left_bot.open()
    rigth_bot.open()

    # Vidange à la fin
    is_drainage_opened = False

    while simulation.time < t_max:
        # Actions
        if simulation.time > 20.0 and are_top_links_opened == False:
            top_left.open()
            top_right.open()
            are_top_links_opened = True

        if simulation.time > 300.0 and is_drainage_opened == False:
            atmosphere.open()
            is_drainage_opened = True

        dt = simulation.step()

    results = ReadResults()
    results.add_time_evolution(top_tank, TankPhysicalProperty.MASS)
    results.add_time_evolution(left_tank, TankPhysicalProperty.MASS)
    results.add_time_evolution(rigth_tank, TankPhysicalProperty.MASS)
    results.add_time_evolution(bot_tank, TankPhysicalProperty.MASS)
    results.add_time_evolution(rigth_bot, LinkPhysicalProperty.MASSFLOW)
    results.add_time_evolution(left_bot, LinkPhysicalProperty.MASSFLOW)

    results.show()

    results.save_pdf()


if __name__ == "__main__":
    main()