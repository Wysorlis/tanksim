# coding: utf-8
from __future__ import annotations

from typing import TYPE_CHECKING

from tanksim.tank.geometry import Geometry
from tanksim.tank.state import TankState
from tanksim.constants import STANDARD_ATMOSPHERIC_PRESSURE

if TYPE_CHECKING:
    from tanksim.models.orifice import Orifice


class Tank:
    def __init__(self, name: str):
        self.name = name
        self.geometry = None

        self.state = TankState()

        self.surface_pressure: float = STANDARD_ATMOSPHERIC_PRESSURE
        self.bottom_elevation: float | None = None

        self.orifices: list[Orifice] = []

    def set_geometry(self, geometry: Geometry):
        self.geometry = geometry

    def set_level(self, level: float):
        if self.geometry is None:
            raise ValueError("Geometry must be set before asigning level to a tank. Consider using tank.add_geometry().")
        
        self.state.liquid_mass = level * self.geometry.surface * self.liquid_density

    def update(self, dt, net_massflow):
        self.state.liquid_mass = max(0.0, self.state.liquid_mass + net_massflow * dt)

    def show(self):
        print(f"+++++++ TANK +++++++")
        print(f"| mliq             = {self.liquid_mass:<3.2f} kg")
        print(f"| Vliq             = {self.liquid_volume:<3.2f} m3")
        print(f"| level            = {self.level:<3.2f} m")
        for i, ori in enumerate(self.orifices):
            print(f"| massflow (break n°{i}) = {ori.massflow:<3.2f} kg/s")
        print(f"++++++++++++++++++++")

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
