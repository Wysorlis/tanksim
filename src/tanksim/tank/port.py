# coding: utf-8
from tanksim.tank import Tank, Geometry
from tanksim.constants import GRAVITY


class Port:
    def __init__(self, tank: Tank, height: float):
        self.tank = tank
        self.height = height

        self._check()

    def _check(self):
        if self.height < 0.0:
            raise ValueError("The height of the 'Port' should be positive.")

        if self.height > self.tank.geometry.height:
             raise ValueError(f"""The height of the 'Port' should be between the bottom of the top of the tank.
            Tank height -> [0.0, {self.tank.geometry.height:.1f}]""")

    @property
    def pressure(self) -> float:
        depth = max(self.tank.level - self.height, 0.0)

        return (
            self.tank.surface_pressure
            + self.tank.liquid_density * GRAVITY * depth
        )

    @property
    def elevation(self) -> float:
        return self.tank.bottom_elevation + self.height

    @property
    def is_submerged(self) -> bool:
        return self.tank.level > self.height

if __name__ == "__main__":
    tank = Tank(Geometry(height=1.0, surface=2.5))
    tank.set_level(level=0.5)

    # Port(tank, -1.0)
    # Port(tank, 0.0)
    # Port(tank, 1.0)
    # Port(tank, 2.0)