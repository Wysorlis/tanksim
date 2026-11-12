# coding: utf-8
from __future__ import annotations
import __main__

from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tanksim.simulation import Simulation

import h5py
from h5py import Group, File

from dataclasses import fields

def _get_link_name(link) -> str:
    # return f"link_{type(link.upstream)}_to_{type(link.downstream)}_with_{type(link.model)}_{link.model.diameter}"
    return link.name

class ResultsStorage:
    def __init__(self):
        script_file = getattr(__main__, "__file__", None)

        self.output_folder_path = Path(script_file).resolve().parent
        self.output_results_path = self.output_folder_path / "results.h5"

        self._first_write = True
        self._is_recording = False

        self.stored_variables = {}

        self.next_record_time = 0.0
        self.dt_record_time = 5.0

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
        if not self._is_recording or simulation.time < self.next_record_time:
            return
        
        mode = "w" if self._first_write else "a"

        with h5py.File(self.output_results_path, mode) as file:
            self._save_tank_state(simulation, file)
            self._save_link_state(simulation, file)

        self._first_write = False
        self.next_record_time += self.dt_record_time

    def _save_tank_state(self, simulation: Simulation, file: File):
        for tank in simulation.tanks:
            if self._first_write and tank.geometry is not None:
                geometry_group = file.require_group(f"{tank.name}/geometry")

                for field in fields(tank.geometry):
                    geometry_group.attrs[field.name] = getattr(tank.geometry, field.name)

            for field in fields(tank.state):
                group = file.require_group(f"{tank.name}/{field.name}")

                value = getattr(tank.state, field.name)

                self._append_sample(group, simulation.time, value)

    def _save_link_state(self, simulation: Simulation, file: File):
        for link in simulation.links:
            link_name = _get_link_name(link)
            group = file.require_group(f"{link_name}/massflow")
            value = link.massflow
            self._append_sample(group, simulation.time, value)

            # [TODO: Si on veut généraliser et qu'on veut mettre plusieurs grandeurs (STATE) pour le link]
            # for field in fields(link.state):
            #     group = file.require_group(f"{link.name}/{field.name}")

            #     value = getattr(link.state, field.name)

            #     self._append_sample(group, simulation.time, value)

    def _append_sample(self, group: Group, time: float, value: float) -> None:
        if "time" not in group:
            self.initialise_dataset_time_series(group)

        times = group["time"]
        values = group["values"]

        index = len(times)
        times.resize(index + 1, axis=0)
        values.resize(index + 1, axis=0)

        times[index] = time
        values[index] = value

    def enable(self, interval: float):
        if interval <= 0:
            raise ValueError("Recording interval must be positive.")

        self.dt_record_time = interval
        self._is_recording = True
