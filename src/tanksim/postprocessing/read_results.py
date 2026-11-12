# coding: utf-8
import __main__
import h5py
import math
import matplotlib.pyplot as plt
from pathlib import Path
from functools import partial

from matplotlib.backends.backend_pdf import PdfPages

from tanksim.physics import TankPhysicalProperty, PhysicalProperty, PROPERTY_SPECS
from tanksim.tank import Tank
from tanksim.link import Link
from tanksim.postprocessing.reader import ELEMENT_TO_READER, Reader
from tanksim.postprocessing.time_evolution import TimeEvolution

type Element = Tank | Link

def _get_element_name(element: str | Element) -> str:
    if isinstance(element, str):
        return element

    if isinstance(element, (Tank, Link)):
        return element.name

    raise TypeError(f"Unsupported type: {type(element).__name__}")

StrToClass = {
    "Tank": Tank,
    "Link": Link,
}

def _get_element_reader(path: Path, element: str | Element) -> Reader:
    if isinstance(element, str):
        with h5py.File(path, "r") as file:
            if element not in file:
                raise KeyError(f"Requested element name {element!r} not found.")
            
            class_name = file[f"{element}/type"].attrs["class_name"]

        element_type = StrToClass.get(class_name)

        if element_type is None:
            raise TypeError(f"Unsupported stored class: {class_name!r}")
    else:
        element_type = type(element)

    reader_class = ELEMENT_TO_READER.get(element_type)

    if reader_class is None:
        raise TypeError(f"Unsupported type: {type(element_type).__name__}")

    return reader_class()


class ReadResults():
    def __init__(self, path: Path=None):
        script_file = getattr(__main__, "__file__", None)
        self.output_results_path = Path(script_file).resolve().with_name("results.h5") if path is None else path

        self.requested_variables = {}

    def add_time_evolution(self, element, variable: str | PhysicalProperty):
            if not self.output_results_path.is_file():
                raise FileNotFoundError(
                    f"\nNo results file at {self.output_results_path!r}.\n"
                    "Run the simulation with state recording enabled.\n" \
                    "Consider using 'simulation.enable_state_recording(interval: float)'."
                )
            
            element_name = _get_element_name(element)

            reader = _get_element_reader(self.output_results_path, element)

            with h5py.File(self.output_results_path, "r") as file:
                evolution = reader.read(file, element_name, variable)

            self.add_requested_variable(element_name, variable, evolution)

    def add_requested_variable(self, name: str, variable: str | PhysicalProperty, requested_evolution: TimeEvolution):
        key_to_store = f"{name}-{variable}"

        if key_to_store in self.requested_variables.keys():
            known_properties = "\n".join(f"- {prop.value}" for prop in TankPhysicalProperty)

            raise DuplicateRequestError(
                f"Cannot request {variable!r} under the name {name!r}.\n"
                f"That name is already in use.\n"
                f"Know propreties :\n{known_properties}"
            )
        
        self.requested_variables[key_to_store] = requested_evolution


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
                element_name, variable_name = name.split("-")
                # element_name = element_name[:8]
                specs = PROPERTY_SPECS[variable_name]

                ax.plot(evolution.time, evolution.value, marker=".")
                ax.set_title(f"{element_name} - {specs.label}")
                ax.set_xlabel("Temps [s]")
                ax.set_ylabel(f"{variable_name} [{specs.unit}]")
                ax.grid(True)
    
            # Masquer les emplacements inutilisés.
            for ax in list(axes.flat)[count:]:
                ax.set_visible(False)
    
            fig.tight_layout()
            plt.show()


class DuplicateRequestError(KeyError):
    def __str__(self) -> str:
        if len(self.args) == 1:
            return str(f"\n{self.args[0]}")
        return super().__str__()
    