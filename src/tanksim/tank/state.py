# coding: utf-8
from dataclasses import dataclass


@dataclass
class TankState:
    liquid_mass: float = 0.0  # kg
    liquid_density: float = 1000.0  # kg
