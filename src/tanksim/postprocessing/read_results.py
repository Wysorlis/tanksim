# coding: utf-8
import __main__
import h5py
from h5py import Group
import math
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field
from functools import partial
from difflib import get_close_matches
from matplotlib.backends.backend_pdf import PdfPages

from tanksim.physics import PhysicalProperty, PROPERTY_SPECS

@dataclass
class TimeEvolution:
    time: list[float] = field(default_factory=list)
    value: list[float] = field(default_factory=list)

    def append(self, new_time: float, new_value: float):
        self.time.append(new_time)
        self.value.append(new_value)


class ReadResults():
    def __init__(self):
        script_file = getattr(__main__, "__file__", None)
        self.output_results_path = Path(script_file).resolve().with_name("results.h5")

        self.requested_variables = {}

        self._derived_readers = {
            PhysicalProperty.LEVEL: self._read_level,
            PhysicalProperty.VOLUME: self._read_volume,
        }
        
    def add_time_evolution(self, element_name: str, variable: str | PhysicalProperty):
        if not self.output_results_path.is_file():
            raise FileNotFoundError(
                f"\nNo results file at {self.output_results_path!r}.\n"
                "Run the simulation with state recording enabled.\n" \
                "Consider using 'simulation.enable_state_recording(interval: float)'."
            )

        read_func_with_name = partial(self._read_stored_evolution, variable=variable)

        reader = self._derived_readers.get(variable, read_func_with_name)

        with h5py.File(self.output_results_path, "r") as file:
            evolution = reader(file, element_name)

        self.add_requested_variable(element_name, variable, evolution)

    def add_requested_variable(self, name: str, variable: str | PhysicalProperty, requested_evolution: TimeEvolution):
        key_to_store = f"{name}-{variable}"

        if key_to_store in self.requested_variables.keys():
            known_properties = "\n".join(f"- {prop.value}" for prop in PhysicalProperty)

            raise DuplicateRequestError(
                f"Cannot request {variable!r} under the name {name!r}.\n"
                f"That name is already in use.\n"
                f"Know propreties :\n{known_properties}"
            )
        
        self.requested_variables[key_to_store] = requested_evolution

    def _read_stored_evolution(self, file: h5py.File, element_name: str, *, variable: str) -> TimeEvolution:
        key = f"{element_name}/{variable}"
        group = self._get_series_group(file, f"{key}")

        return TimeEvolution(
            time=group["time"][:].tolist(),
            value=group["values"][:].tolist(),
        )

    def save_pdf(self) -> Path:
        if not self.requested_variables:
            raise ValueError("No requested variables to export.")

        path = self.output_results_path.with_suffix(".pdf")

        with PdfPages(path) as pdf:
            for name, evolution in self.requested_variables.items():
                tank_name, variable_name = name.rsplit("-", 1)
                spec = PROPERTY_SPECS.get(variable_name)
                label = spec.label if spec else variable_name
                ylabel = f"{variable_name} [{spec.unit}]" if spec else variable_name

                fig, ax = plt.subplots(figsize=(10, 5))
                try:
                    ax.plot(evolution.time, evolution.value, marker=".")
                    ax.set_title(f"{tank_name} - {label}")
                    ax.set_xlabel("Temps [s]")
                    ax.set_ylabel(ylabel)
                    ax.grid(True)

                    fig.tight_layout()
                    pdf.savefig(fig)
                finally:
                    plt.close(fig)

        return path

    def show(self):
            count = len(self.requested_variables)
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
    
            for ax, (name, evolution) in zip(axes.flat, self.requested_variables.items()):
                tank_name, variable_name = name.split("-")
                specs = PROPERTY_SPECS[PhysicalProperty(variable_name)]

                ax.plot(evolution.time, evolution.value, marker=".")
                ax.set_title(f"{tank_name} - {specs.label}")
                ax.set_xlabel("Temps [s]")
                ax.set_ylabel(f"{variable_name} [{specs.unit}]")
                ax.grid(True)
    
            # Masquer les emplacements inutilisés.
            for ax in list(axes.flat)[count:]:
                ax.set_visible(False)
    
            fig.tight_layout()
            plt.show()

    def _get_series_group(self, file: h5py.File, key: str) -> Group:
        group = file.get(key)

        if isinstance(group, Group) and "time" in group and "values" in group:
            return group
    
        available = self._list_series_paths(file)
        closest_matches = get_close_matches(key, available, n=3)

        message = f"Requested variable {key!r} not found."
        if closest_matches:
            message += f"\nClosest matches: {', '.join(closest_matches)}."
        else:
            message += "\nNo close match found."
        raise KeyRequestError(message)

    def _read_level(self, file: h5py.File, element_name: str) -> TimeEvolution:
        mass = self._get_series_group(file, f"{element_name}/{PhysicalProperty.MASS}")
        density = self._get_series_group(file, f"{element_name}/{PhysicalProperty.DENSITY}")
        surface = file[f"{element_name}/geometry"].attrs["surface"]

        levels = mass["values"][:] / (density["values"][:] * surface)

        return TimeEvolution(
            time=mass["time"][:].tolist(),
            value=levels.tolist(),
        )
    
    def _read_volume(self, file: h5py.File, element_name: str) -> TimeEvolution:
        mass = self._get_series_group(file, f"{element_name}/{PhysicalProperty.MASS}")
        density = self._get_series_group(file, f"{element_name}/{PhysicalProperty.DENSITY}")
        volume = mass["values"][:] / density["values"][:] 

        return TimeEvolution(
            time=mass["time"][:].tolist(),
            value=volume.tolist(),
        )
        
    @staticmethod
    def _list_series_paths(file: h5py.File) -> list[str]:
        paths = []

        for element, element_group in file.items():
            if not isinstance(element_group, Group):
                continue

            for name, series in element_group.items():
                if isinstance(series, Group) and "time" in series and "values" in series:
                    paths.append(f"{element}/{name}")

        return paths

class DuplicateRequestError(KeyError):
    def __str__(self) -> str:
        if len(self.args) == 1:
            return str(f"\n{self.args[0]}")
        return super().__str__()

class KeyRequestError(KeyError):
    def __str__(self) -> str:
        if len(self.args) == 1:
            return str(f"\n{self.args[0]}")
        return super().__str__()
    
    