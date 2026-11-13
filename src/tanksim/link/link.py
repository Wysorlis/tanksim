# coding: utf-8
from tanksim.link.link_state import LinkState
from tanksim.tank import Port
from tanksim.models.model import FlowModel
from tanksim.boundaries import Boundary


class Link:
    def __init__(self, name: str, upstream: Port | Boundary, downstream: Port | Boundary, model: FlowModel, align_ports: bool = False):
        self._name = name
        self.upstream = upstream
        self.downstream = downstream
        self.model = model
        self.align_ports = align_ports

        self.state = LinkState()

        self.is_opened = False

        self._check()

    def update(self, dt):
        if self.is_opened:
            self.state = self.model.compute(
                dt=dt,
                upstream=self.upstream,
                downstream=self.downstream,
            )
        else:
            self.state.liquid_velocity = 0.0

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def massflow(self) -> float:
        return self.state.liquid_density * self.model.section * self.state.liquid_velocity

    def open(self):
        self.is_opened = True

    def close(self):
        self.is_opened = False
        self.state.liquid_velocity = 0.0

    def _check(self):
        if isinstance(self.upstream, Boundary) and isinstance(self.downstream, Boundary):
            raise ValueError(
                f"Can't link two boundaries: "
                f"{type(self.upstream).__name__!r} and "
                f"{type(self.downstream).__name__!r}.\n"
                "Allowed connections are:\n"
                "- Port / Port\n"
                "- Port / Boundary\n"
                "- Boundary / Port"
            )
        