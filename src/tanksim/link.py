# coding: utf-8
import numpy as np
from tanksim.tank import Tank, Port
from tanksim.models.orifice import Orifice
from tanksim.boundaries import Boundary


class Link:
    def __init__(self, upstream: Port | Boundary, downstream: Port | Boundary, model: Orifice, align_ports: bool = False,):
        self.upstream = upstream
        self.downstream = downstream
        self.model = model
        self.align_ports = align_ports

        self.massflow = 0.0
        self.is_opened = False

        self._check()

        # if self.align_ports:
        #     self._align_ports()

    def update(self, dt):
        if self.is_opened:
            self.massflow = self.model.update(
                dt=dt,
                upstream=self.upstream,
                downstream=self.downstream,
            )

    def open(self):
        self.is_opened = True

    def close(self):
        self.is_opened = False
        self.massflow = 0.0

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
    # def _align_ports(self):
    #     if not (
    #         isinstance(self.upstream, Port)
    #         and isinstance(self.downstream, Port)
    #     ):
    #         raise ValueError("Port alignment requires two Ports.")

    #     if self.upstream.tank is self.downstream.tank:
    #         raise ValueError("Port alignment requires two different tanks.")

    #     self.downstream.tank.bottom_elevation = (
    #         self.upstream.elevation - self.downstream.height
    #     )