# coding: utf-8
import math
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages


@dataclass
class TimeRecord:
    time: list[float] = field(default_factory=list)
    value: list[float] = field(default_factory=list)

    def append(self, new_time: float, new_value: float):
        self.time.append(new_time)
        self.value.append(new_value)

class Record:
    def __init__(self):
        self.stored_variables = {}

    def monitor(self, name: str, time: float, value: float):
        if name not in self.stored_variables:
            self.stored_variables[name] = TimeRecord()

        self.stored_variables[name].append(new_time=time, new_value=value)

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