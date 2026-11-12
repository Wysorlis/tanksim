# coding: utf-8
import __main__
from pathlib import Path

from tanksim.postprocessing import ReadResults
from tanksim.physics import TankPhysicalProperty, LinkPhysicalProperty

def main():
    script_file = getattr(__main__, "__file__", None)
    path =  Path(script_file).resolve().with_name("results.h5")
    
    results = ReadResults(path)
    results.add_time_evolution("TANK_A", TankPhysicalProperty.MASS)
    results.add_time_evolution("TANK_A", TankPhysicalProperty.LEVEL)
    results.add_time_evolution("connection", LinkPhysicalProperty.MASSFLOW)
    results.add_time_evolution("connection", LinkPhysicalProperty.VELOCITY)
    results.add_time_evolution("connection", LinkPhysicalProperty.DENSITY)

    results.show()

    results.save_pdf()

if __name__ == "__main__":
    main()
