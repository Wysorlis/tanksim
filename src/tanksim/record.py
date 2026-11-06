# coding: utf-8
import math
import matplotlib.pyplot as plt
from dataclasses import dataclass, field


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
            ax.plot(record.time, record.value)
            ax.set_title(name)
            ax.set_xlabel("Temps")
            ax.set_ylabel(name)
            ax.grid(True)

        # Masquer les emplacements inutilisés.
        for ax in list(axes.flat)[count:]:
            ax.set_visible(False)

        fig.tight_layout()
        plt.show()