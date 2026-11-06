# coding: utf-8
from .geometry import Geometry
from tanksim.models.orifice import Orifice 


class Tank:
    def __init__(self, geometry: Geometry):
        self.geometry = geometry
        self.level = None
        self.liquid_volume = None
        self.liquid_density = 1000.0
        self.liquid_mass = None

        self.orifices: list[Orifice] = []

    def set_level(self, level: float):
        self.level = level
        self.liquid_volume = self.geometry.volume * level
        self.liquid_mass = self.liquid_volume * self.liquid_density

    def add_orifice(self, diameter: float):
        self.orifices.append(Orifice(diameter=diameter))

    def update(self, dt):
        for orifice in self.orifices:
            massflow_orifice = orifice.update(dt, self.level, self.liquid_density)
            
            self.liquid_mass -= massflow_orifice * dt

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
        for i, ori in enumerate(self.orifices):
            print(f"| massflow (break n°{i}) = {ori.massflow:<3.2f} kg/s")
        print(f"++++++++++++++++++++")
