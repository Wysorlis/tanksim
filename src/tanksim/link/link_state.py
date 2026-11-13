# coding: utf-8
from dataclasses import dataclass


@dataclass
class LinkState:
    liquid_velocity: float = 0.0  # m/s
    liquid_density : float = 1000.0  # kg/m³