# coding: utf-8
from __future__ import annotations

from typing import TYPE_CHECKING

from tanksim.tank.geometry import Geometry
from tanksim.tank.state import TankState
from tanksim.constants import STANDARD_ATMOSPHERIC_PRESSURE


class Tank:
    def __init__(self, name: str):
        self._name = name
        self.geometry = None

        self.state = TankState()

        self.surface_pressure: float = STANDARD_ATMOSPHERIC_PRESSURE
        self.bottom_elevation: float | None = None

    def set_geometry(self, geometry: Geometry):
        self.geometry = geometry

    def set_level(self, level: float):
        if self.geometry is None:
            raise ValueError("Geometry must be set before asigning level to a tank. Consider using tank.add_geometry().")

        if level < 0.0 or level > self.geometry.height:
            raise ValueError(f"Level must be set between 0 and the height of the tank. {self.name!r}: [{0.0}, {self.geometry.height}].\n"
                             f"But requested value is {level}.")
        
        self.state.liquid_mass = level * self.geometry.surface * self.liquid_density

    def update(self, dt, net_massflow):
        new_mass = max(0.0, self.state.liquid_mass + net_massflow * dt)

        maximum_mass = self.liquid_density * self.geometry.volume
        overflow_mass = max(0.0, new_mass - maximum_mass)

        self.state.liquid_mass = new_mass - overflow_mass
        self.state.overflow_liquid_mass += overflow_mass

    def show(self):
        print(f"+++++++ {self.name} +++++++")
        print(f"| mliq             = {self.liquid_mass:<3.2f} kg")
        print(f"| Vliq             = {self.liquid_volume:<3.2f} m3")
        print(f"| level            = {self.level:<3.2f} m")
        print(f"++++++++++++++++++++")

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def liquid_mass(self) -> float:
        return self.state.liquid_mass
    
    @property
    def liquid_volume(self) -> float:
        return self.liquid_mass / self.liquid_density

    @property
    def level(self) -> float:
        if self.geometry is None:
            raise ValueError("Set the tank geometry before reading its level.")
        return self.liquid_volume / self.geometry.surface

    @property
    def liquid_density(self) -> float:
        return self.state.liquid_density
