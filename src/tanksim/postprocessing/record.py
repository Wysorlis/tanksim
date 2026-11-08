# coding: utf-8
from __future__ import annotations
import __main__

import math
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tanksim.simulation import Simulation

import h5py
from h5py import Group

@dataclass
class TimeRecord:
    time: list[float] = field(default_factory=list)
    value: list[float] = field(default_factory=list)

    def append(self, new_time: float, new_value: float):
        self.time.append(new_time)
        self.value.append(new_value)

class Record:
    def __init__(self):
        script_file = getattr(__main__, "__file__", None)

        self.output_folder_path = Path(script_file).resolve().parent
        self.output_results_path = self.output_folder_path / "results.h5"

        self.stored_variables = {}

        self.next_record_time = 0.0
        self.dt_record_time = 5.0

    def monitor(self, name: str, time: float, value: float):
        if name not in self.stored_variables:
            self.stored_variables[name] = TimeRecord()

        self.stored_variables[name].append(new_time=time, new_value=value)

    def initialise_dataset_time_series(self, group: Group):
        times = group.create_dataset(
            "time",
            shape=(0,),
            maxshape=(None,),
            dtype="f8",
            compression="gzip",
            compression_opts=4,
        )

        values = group.create_dataset(
            "values",
            shape=(0,),
            maxshape=(None,),
            dtype="f8",
            compression="gzip",
            compression_opts=4,
        )
        return times, values

    
    def save_state(self, simulation: Simulation):
        if simulation.time < self.next_record_time:
            return

        with h5py.File(self.output_results_path, "a") as file:
            for tank in simulation.tanks:
                level = file.require_group(f"{tank.name}/level")

                if "time" not in level:
                    times, values = self.initialise_dataset_time_series(level)

                times = level["time"]
                values = level["values"]

                index = len(times)
                times.resize(index + 1, axis=0)
                values.resize(index + 1, axis=0)

                times[index] = simulation.time
                values[index] = tank.level

        self.next_record_time += self.dt_record_time

    def show(self):
        count = len(self.stored_variables)
        if count == 0:
            return

        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        fig, axes = plt.subplots(
            rows,
            cols,
            squeeze=False,
            figsize=(6 * cols, 4 * rows),
        )

        for ax, (name, record) in zip(
            axes.flat, self.stored_variables.items()
        ):
            ax.plot(record.time, record.value, marker=".")
            ax.set_title(name)
            ax.set_xlabel("Temps")
            ax.set_ylabel(name)
            ax.grid(True)

        # Masquer les emplacements inutilisés.
        for ax in list(axes.flat)[count:]:
            ax.set_visible(False)

        fig.tight_layout()
        plt.show()

    def save_pdf(self, filename: str | Path = "results.pdf") -> Path:
        if not self.stored_variables:
            raise ValueError("No recorded variables to export.")

        path = Path(filename).resolve()

        with PdfPages(path) as pdf:
            for name, record in self.stored_variables.items():
                fig, ax = plt.subplots(figsize=(10, 5))

                try:
                    ax.plot(record.time, record.value)
                    ax.set_title(name)
                    ax.set_xlabel("Temps (s)")
                    ax.set_ylabel(name)
                    ax.grid(True)

                    fig.tight_layout()
                    pdf.savefig(fig)
                finally:
                    plt.close(fig)

        return path