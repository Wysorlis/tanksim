
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Geometry:
    height: float
    surface: float
    volume: float = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "volume", self.height * self.surface)