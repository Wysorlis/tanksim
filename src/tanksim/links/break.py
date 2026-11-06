# coding: utf-8
import numpy as np


class Break:
    def __init__(self, diameter: float):
        self._massflow = 0.0
        self._velocity = 0.0

        self.diameter = diameter
        self.absolute_section = np.pi * diameter**2.0 / 4.0

        self.frac = 0.0
        self.break_section = self.frac * self.absolute_section


    def openbreak(self, frac: float):
        self.break_section = self.frac * self.absolute_section

    def update(self, dt, rho, delta_pressure_above):
        self._velocity += - 9.81 * dt

    @property
    def massflow(self) -> float:
        return self._massflow
