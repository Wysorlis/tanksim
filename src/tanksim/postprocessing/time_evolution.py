# coding: utf-8
from dataclasses import dataclass, field

@dataclass
class TimeEvolution:
    time: list[float] = field(default_factory=list)
    value: list[float] = field(default_factory=list)

    def append(self, new_time: float, new_value: float):
        self.time.append(new_time)
        self.value.append(new_value)