# coding: utf-8
from dataclasses import dataclass, field
from abc import ABC

from tanksim.constants import STANDARD_ATMOSPHERIC_PRESSURE


class Boundary(ABC):
    pass

@dataclass
class PressureBoundary(Boundary):
    pressure: float

@dataclass
class Atmosphere(PressureBoundary):
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE