# coding: utf-8
import numpy as np
from typing import override

from tanksim.tank import Port
from tanksim.boundaries import Boundary


from tanksim.models import FlowModel
from tanksim.constants import GRAVITY

from tanksim.link.link_state import LinkState


class Orifice(FlowModel):
    def __init__(self, diameter: float):
        self.diameter = diameter

    @override
    def compute(self, dt, upstream: Port | Boundary, downstream: Port | Boundary) -> LinkState:
        # Au moins une extrémité est un Port, vérifié par Link.
        reference_port = upstream if isinstance(upstream, Port) else downstream
        liquid_density = reference_port.tank.liquid_density
        
        # Les deux extrémités exposent une pression
        delta_pressure = upstream.pressure - downstream.pressure

        if isinstance(upstream, Port) and isinstance(downstream, Port):
            delta_z = downstream.elevation - upstream.elevation
        else:
            # La pression extérieure s'applique au port connecté.
            delta_z = 0.0

        driving_velocity_squared = 2.0 * delta_pressure / liquid_density - 2.0 * GRAVITY * delta_z

        # Empêcher un départ de liquide depuis un port dénoyé.
        donor = upstream if driving_velocity_squared >= 0.0 else downstream
        if isinstance(donor, Port) and not donor.is_submerged:
            driving_velocity_squared = 0.0

        liquid_velocity = np.sign(driving_velocity_squared) * np.sqrt(abs(driving_velocity_squared))

        return LinkState(
            liquid_velocity=liquid_velocity,
            liquid_density=liquid_density,
        )
    
    @property
    @override
    def section(self) -> float:
        return np.pi * self.diameter**2 / 4


if __name__ == "__main__":
    sign = np.sign(2 - 1)
    print(sign)
    sign = np.sign(1 - 2)
    print(sign)
    sign = np.sign(0)
    print(sign)

