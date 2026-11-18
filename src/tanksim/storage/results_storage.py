# coding: utf-8
from __future__ import annotations
import __main__

from math import isfinite
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
        self._buffer = []

        self.batch_size = 1

        self.next_record_time = 0.0
        self.dt_record_time = 5.0

    def enable(self, interval: float, start_time: float):
        if not isfinite(interval) or interval <= 0:
            raise ValueError("Recording interval must be finite and positive.")

        self.dt_record_time = interval
        self.next_record_time = start_time
        self._is_recording = True

    def set_batch_size(self, batch_size: int | None):
        if batch_size is not None:
            if type(batch_size) is not int or batch_size < 1:
                raise ValueError("Batch size must be None or an integer >= 1.")

        self.batch_size = batch_size

    def save_state(self, simulation: Simulation):
        tolerance = 1e-12 * max(1.0, abs(simulation.time))

        if not self._is_recording or simulation.time + tolerance < self.next_record_time:
            return
        
        if self._first_write:
            with h5py.File(self.output_results_path, "w") as file:
                self._initialise_tanks(simulation, file)
                self._initialise_links(simulation, file)
                self._initialise_devices(simulation, file)
            self._first_write = False

        self._buffer.append((
            simulation.time,
            self._capture_state(simulation),
        ))

        if self.batch_size is not None and len(self._buffer) >= self.batch_size:
            self.flush()

        # Sauter les échéances dépassées, sans inventer d'échantillons.
        while self.next_record_time <= simulation.time + tolerance:
            self.next_record_time += self.dt_record_time

    def flush(self):
        if not self._buffer:
            return

        paths = self._buffer[0][1].keys()

        if any(values.keys() != paths for _, values in self._buffer):
            raise ValueError("Recorded variables changed during the batch.")

        times = [time for time, _ in self._buffer]

        columns = {
            path: [values[path] for _, values in self._buffer]
            for path in paths
        }

        with h5py.File(self.output_results_path, "a") as file:
            for path, values in columns.items():
                self._append_samples(file[path], times, values)

        self._buffer.clear()
        
    def finish(self):
        self.flush()
        self._is_recording = False

    @property
    def has_started(self) -> bool:
        return not self._first_write

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

    def _initialise_links(self, simulation: Simulation, file: File):
         for link in simulation.links:
            type_group = file.create_group(f"{link.name}/type")
            type_group.attrs["class_name"] = type(link).__name__

            geometry_group = file.create_group(f"{link.name}/geometry")
            geometry_group.attrs["section"] = link.model.section

            for field in fields(link.state):
                group = file.create_group(f"{link.name}/{field.name}")
                self._initialise_dataset_time_series(group)

    def _initialise_devices(self, simulation: Simulation, file: File):
        for device in simulation.devices:
            type_group = file.create_group(f"{device.name}/type")
            type_group.attrs["class_name"] = type(device).__name__

            for field in fields(device.state):
                group = file.create_group(f"{device.name}/{field.name}")
                self._initialise_dataset_time_series(group)

    def _append_samples(self, group: Group, times: list[float], values: list[float]):
        time_dataset = group["time"]
        value_dataset = group["values"]

        start = len(time_dataset)
        stop = start + len(times)

        time_dataset.resize((stop,))
        value_dataset.resize((stop,))

        time_dataset[start:stop] = times
        value_dataset[start:stop] = values

    def _capture_state(self, simulation: Simulation) -> dict[str, float]:
        values = {}

        elements = simulation.tanks + simulation.links + simulation.devices

        for element in elements:
            for field in fields(element.state):
                key = f"{element.name}/{field.name}"
                values[key] = float(getattr(element.state, field.name))

        return values
