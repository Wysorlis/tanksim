# coding: utf-8
from abc import ABC
from dataclasses import dataclass
from math import isfinite

from tanksim.tank import Tank


@dataclass
class SourceState:
    liquid_massflow: float = 0.0  # kg/s


class Device(ABC):
    pass


class Source(Device):
    def __init__(self, name: str, tank: Tank, massflow: float):
        self._name = name
        self.tank = tank

        self.state = SourceState()
        
        self.is_enabled = False
        self.massflow = massflow

    def enable(self):
        self.is_enabled = True
        self.state.liquid_massflow = self._massflow
    
    def disable(self):
        self.is_enabled = False
        self.state.liquid_massflow = 0.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def massflow(self) -> float:
        return self.state.liquid_massflow

    @massflow.setter
    def massflow(self, value: float):
        if not isfinite(value) or value < 0.0:
            raise ValueError("Source mass flow must be finite and non-negative.")

        self._massflow = value
        self.state.liquid_massflow = value if self.is_enabled else 0.0

