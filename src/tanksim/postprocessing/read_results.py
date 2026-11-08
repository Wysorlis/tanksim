# coding: utf-8
import __main__
import h5py
from pathlib import Path

class ReadResults():
    def __init__(self):
        script_file = getattr(__main__, "__file__", None)
        self.output_results_path = Path(script_file).resolve().with_name("results.h5")

    def read(self, tank_name: str, variable: str):
        with h5py.File(self.output_results_path, "r") as file:
            print(list(file.keys()))  # Noms des réservoirs enregistrés

            level = file[f"{tank_name}/{variable}"]  # Remplace tank_1 par le nom voulu
            times = level["time"][:]
            levels = level["values"][:]

        return times, levels