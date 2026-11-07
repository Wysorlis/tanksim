# coding: utf-8
from __future__ import annotations

from typing import TYPE_CHECKING

from tanksim.tank.geometry import Geometry
from tanksim.constants import STANDARD_ATMOSPHERIC_PRESSURE

if TYPE_CHECKING:
    from tanksim.models.orifice import Orifice


class Tank:
    def __init__(self, geometry: Geometry):
        self.geometry = geometry
        self.level = None
        self.liquid_volume = None
        self.liquid_density = 1000.0
        self.liquid_mass = None
        self.surface_pressure: float = STANDARD_ATMOSPHERIC_PRESSURE
        self.bottom_elevation: float | None = None

        self.orifices: list[Orifice] = []

    def set_level(self, level: float):
        self.level = level
        self.liquid_volume = self.geometry.surface * level
        self.liquid_mass = self.liquid_volume * self.liquid_density

    # def add_orifice(self, diameter: float):
    #     self.orifices.append(Orifice(diameter=diameter))

    def update(self, dt, net_massflow):
        self.liquid_mass += net_massflow * dt

        self.liquid_volume = self.liquid_mass / self.liquid_density 
        self.level = self.liquid_volume / self.geometry.surface
        if self.liquid_mass < 0:
            self.liquid_mass = 0.0
            self.liquid_volume = 0.0
            self.level = 0.0
    
    def show(self):
        print(f"+++++++ TANK +++++++")
        print(f"| mliq             = {self.liquid_mass:<3.2f} kg")
        print(f"| Vliq             = {self.liquid_volume:<3.2f} m3")
        print(f"| level            = {self.level:<3.2f} m")
        for i, ori in enumerate(self.orifices):
            print(f"| massflow (break n°{i}) = {ori.massflow:<3.2f} kg/s")
        print(f"++++++++++++++++++++")
