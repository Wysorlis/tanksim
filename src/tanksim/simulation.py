# coding: utf-8
import numpy as np
from math import isclose
from pathlib import Path

from tanksim.tank import Tank, Port
from tanksim.link import Link
from tanksim.postprocessing.record import Record

class Simulation:
    def __init__(self, tanks: list[Tank]=None, links: list[Link]=None):
        self.time = 0.0
        self.dt = 0.1
        self.tanks = []
        self.links = []

        if tanks is not None:
            for tank in tanks:
                self.add_tank(tank)

        if links is not None:
            for link in links:
                self.add_link(link)

        self.record = Record()

    def add_tank(self, tank: Tank):
        self.tanks.append(tank)

    def add_link(self, link: Link):
        self.links.append(link)

    def step(self):
        net_massflows = {tank: 0.0 for tank in self.tanks}

        # Calculer les débits et accumuler les bilans
        for link in self.links:
            link.update(self.dt)
            massflow = link.massflow

            if isinstance(link.upstream, Port):
                net_massflows[link.upstream.tank] -= massflow

            if isinstance(link.downstream, Port):
                net_massflows[link.downstream.tank] += massflow

        # Appliquer les bilans à tous les tanks
        for tank in self.tanks:
            tank.update(
                dt=self.dt,
                net_massflow=net_massflows[tank]
            )

        # Updating time
        self.time += self.dt

        # Saving results
        self.record.save_state(self)

        return self.dt
    
    def setup(self, tolerance: float = 1e-9):
        graph = {tank: [] for tank in self.tanks}

        # Construire les contraintes :
        # altitude_b = altitude_a + hauteur_port_a - hauteur_port_b
        for index, link in enumerate(self.links):
            if not link.align_ports:
                continue

            if not (
                isinstance(link.upstream, Port)
                and isinstance(link.downstream, Port)
            ):
                raise ValueError(f"Link {index}: alignment requires two Ports.")

            a = link.upstream.tank
            b = link.downstream.tank

            if a not in graph or b not in graph:
                raise ValueError(f"Link {index}: tank missing from Simulation.")

            offset = link.upstream.height - link.downstream.height
            graph[a].append((b, offset))
            graph[b].append((a, -offset))

        relative = {}
        resolved = {}

        for root in self.tanks:
            if root in relative:
                continue

            relative[root] = 0.0
            pending = [root]
            component = []

            # Propager les positions relatives et vérifier les boucles.
            while pending:
                tank = pending.pop()
                component.append(tank)

                for neighbor, offset in graph[tank]:
                    expected = relative[tank] + offset

                    if neighbor not in relative:
                        relative[neighbor] = expected
                        pending.append(neighbor)
                    elif not isclose(
                        relative[neighbor], expected,
                        rel_tol=0.0, abs_tol=tolerance,
                    ):
                        raise ValueError("Incompatible port-alignment cycle.")

            # Positionner le groupe à partir d'une altitude imposée.
            # Sans altitude imposée, son premier réservoir sert de référence à 0 m.
            anchors = [
                tank for tank in component
                if tank.bottom_elevation is not None
            ]
            shift = (
                anchors[0].bottom_elevation - relative[anchors[0]]
                if anchors else 0.0
            )

            for tank in component:
                expected = shift + relative[tank]
                fixed = tank.bottom_elevation

                if fixed is not None and not isclose(
                    fixed, expected, rel_tol=0.0, abs_tol=tolerance,
                ):
                    index = self.tanks.index(tank)
                    raise ValueError(
                        f"Tank {index}: bottom elevation {fixed:g} m "
                        f"conflicts with required elevation {expected:g} m."
                    )

                resolved[tank] = fixed if fixed is not None else expected

        # Appliquer les positions uniquement si tout le réseau est compatible.
        for tank, elevation in resolved.items():
            tank.bottom_elevation = elevation