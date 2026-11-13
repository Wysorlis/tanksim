# coding: utf-8

from abc import ABC, abstractmethod

from tanksim.boundaries import Boundary
from tanksim.tank import Port

from tanksim.link.link_state import LinkState

class FlowModel(ABC):
    @abstractmethod
    def compute(self, dt: float, upstream: Port | Boundary, downstream: Port | Boundary) -> LinkState:
        pass

    @property
    @abstractmethod
    def section(self) -> float:
        pass
