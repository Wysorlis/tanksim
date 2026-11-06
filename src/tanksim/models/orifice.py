# coding: utf-8
import numpy as np

GRAVITY = 9.81

class Orifice:
    def __init__(self, diameter: float):
        self._massflow = 0.0
        self._velocity = 0.0

        self.diameter = diameter
        self.section = np.pi * diameter**2.0 / 4.0

        # self.frac = 0.0
        # self.eff_section = self.frac * self.section


    # def openbreak(self, frac: float):
    #     self.eff_section = self.frac * self.section

    def update(self, dt, level, density) -> float:
        # self._velocity += - 9.81 * dt
        self._velocity = np.sqrt(2.0 * GRAVITY * level)
        self._massflow = density * self.section * self._velocity
        return self._massflow

    @property
    def massflow(self) -> float:
        return self._massflow
