
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Geometry:
    height: float
    surface: float
    volume: float = field(init=False)

    def __post_init__(self):
        if self.height <= 0.0:
            raise ValueError(f"Tank height should be > 0.")

        if self.surface <= 0.0:
            raise ValueError(f"Tank surface should be > 0.")
        
        object.__setattr__(self, "volume", self.height * self.surface)