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

    def enable(self, interval: float):
        if interval <= 0:
            raise ValueError("Recording interval must be positive.")

        self.dt_record_time = interval
        self._is_recording = True
        
    def save_state(self, simulation: Simulation):
        if not self._is_recording or simulation.time < self.next_record_time:
            return
        
        mode = "w" if self._first_write else "a"

        with h5py.File(self.output_results_path, mode) as file:
            if self._first_write:
                self._initialise_tanks(simulation, file)
                self._initialise_links(simulation, file)

            self._append_tank_state(simulation, file)
            self._append_link_state(simulation, file)

        self._first_write = False
        self.next_record_time += self.dt_record_time

    def _initialise_dataset_time_series(self, group: Group):
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
    
    def _initialise_tanks(self, simulation: Simulation, file: File):
        for tank in simulation.tanks:
            type_group = file.create_group(f"{tank.name}/type")
            type_group.attrs["class_name"] = type(tank).__name__

            if tank.geometry is not None:
                geometry_group = file.create_group(f"{tank.name}/geometry")

                for field in fields(tank.geometry):
                    geometry_group.attrs[field.name] = getattr(tank.geometry, field.name)

            for field in fields(tank.state):
                group = file.create_group(f"{tank.name}/{field.name}")
                self._initialise_dataset_time_series(group)

    def _append_tank_state(self, simulation: Simulation, file: File):
        for tank in simulation.tanks:
            for field in fields(tank.state):
                group = file[f"{tank.name}/{field.name}"]
                value = getattr(tank.state, field.name)

                self._append_sample(group, simulation.time, value)

    def _initialise_links(self, simulation: Simulation, file: File):
         for link in simulation.links:
            type_group = file.create_group(f"{link.name}/type")
            type_group.attrs["class_name"] = type(link).__name__

            geometry_group = file.create_group(f"{link.name}/geometry")
            geometry_group.attrs["section"] = link.model.section

            for field in fields(link.state):
                group = file.create_group(f"{link.name}/{field.name}")
                self._initialise_dataset_time_series(group)

    def _append_link_state(self, simulation: Simulation, file: File):
        for link in simulation.links:
            for field in fields(link.state):
                group = file[f"{link.name}/{field.name}"]
                value = getattr(link.state, field.name)

                self._append_sample(group, simulation.time, value)

    def _append_sample(self, group: Group, time: float, value: float) -> None:
        times = group["time"]
        values = group["values"]

        index = len(times)
        times.resize(index + 1, axis=0)
        values.resize(index + 1, axis=0)

        times[index] = time
        values[index] = value
