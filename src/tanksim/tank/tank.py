# coding: utf-8
from .geometry import Geometry


class Tank:
    def __init__(self, geometry: Geometry):
        self.geometry = geometry
        self.level = None
        self.liquid_volume = None
        self.liquid_density = 1000.0
        self.liquid_mass = None

        self.massflow_break = 0.0

    def set_level(self, level: float):
        self.level = level
        self.liquid_volume = self.geometry.volume * level
        self.liquid_mass = self.liquid_volume * self.liquid_density

    def openbreak(self, massflow: float):
        self.massflow_break = massflow

    def update(self, dt):
        self.liquid_mass -= self.massflow_break * dt

        self.liquid_volume = self.liquid_mass / self.liquid_density 
        self.level = self.liquid_volume / self.geometry.volume
        if self.liquid_mass < 0:
            self.liquid_mass = 0.0
            self.liquid_volume = 0.0
            self.level = 0.0
    
    def show(self):
        print(f"+++++++ TANK +++++++")
        print(f"| mliq             = {self.liquid_mass:<3.2f} kg")
        print(f"| Vliq             = {self.liquid_volume:<3.2f} m3")
        print(f"| level            = {self.level:<3.2f} m")
        print(f"| massflow (break) = {self.massflow_break:<3.2f} kg/s")
        print(f"++++++++++++++++++++")
