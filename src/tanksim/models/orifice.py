# coding: utf-8
import numpy as np
from tanksim.tank import Port
from tanksim.boundaries import Boundary
from tanksim.constants import GRAVITY


class Orifice:
    def __init__(self, diameter: float):
        self._massflow = 0.0
        self._velocity = 0.0

        self.diameter = diameter
        self.section = np.pi * diameter**2.0 / 4.0

    def update(self, dt, upstream: Port | Boundary, downstream: Port | Boundary) -> float:
        # Au moins une extrémité est un Port, vérifié par Link.
        reference_port = upstream if isinstance(upstream, Port) else downstream
        density = reference_port.tank.liquid_density
        
        # Les deux extrémités exposent une pression
        delta_pressure = upstream.pressure - downstream.pressure

        if isinstance(upstream, Port) and isinstance(downstream, Port):
            delta_z = downstream.elevation - upstream.elevation
        else:
            # La pression extérieure s'applique au port connecté.
            delta_z = 0.0

        driving_velocity_squared = 2.0 * delta_pressure / density - 2.0 * GRAVITY * delta_z

        # Empêcher un départ de liquide depuis un port dénoyé.
        donor = upstream if driving_velocity_squared >= 0.0 else downstream
        if isinstance(donor, Port) and not donor.is_submerged:
            driving_velocity_squared = 0.0

        self._velocity = np.sign(driving_velocity_squared) * np.sqrt(abs(driving_velocity_squared))

        self._massflow = density * self.section * self._velocity
        return self._massflow

    @property
    def massflow(self) -> float:
        return self._massflow

if __name__ == "__main__":
    sign = np.sign(2 - 1)
    print(sign)
    sign = np.sign(1 - 2)
    print(sign)
    sign = np.sign(0)
    print(sign)

