# coding: utf-8
import numpy as np
from tanksim.tank import Tank

class Simulation:
    def __init__(self):
        self.time = 0.0
        self.dt = 0.1
        self._elements = []

    def append(self, element: Tank):
        self._elements.append(element)

    def step(self):
        for elem in self._elements:
            elem.update(self.dt)

        self.time += self.dt
        return self.time