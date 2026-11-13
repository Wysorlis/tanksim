# coding: utf-8
import numpy as np
from math import isclose
from pathlib import Path

from tanksim.tank import Tank, Port
from tanksim.link.link import Link
from tanksim.storage.results_storage import ResultsStorage

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

        self.results_storage = ResultsStorage()

    def add_tank(self, tank: Tank):
        self._check_element_name(tank.name)
        self.tanks.append(tank)

    def add_link(self, link: Link):
        self._check_element_name(link.name)
        self.links.append(link)

    def _check_element_name(self, name: str):
        if any(element.name == name for element in self.tanks + self.links):
            raise ValueError(f"Element name {name!r} is already in use.")
    
    def step(self):
        # 1. Calculer les écoulements proposés par les modèles.
        for link in self.links:
            link.update(self.dt)

        # 2. Limiter les prélèvements aux masses disponibles.
        net_massflows = self._limit_outflows()

        # 3. Construire les débits corrigés.
        net_massflows = self._compute_net_massflows()

        # 4. Mettre à jour les tanks.
        for tank in self.tanks:
            tank.update(
                dt=self.dt,
                net_massflow=net_massflows[tank]
            )

        # 5. Avancer le temps
        self.time += self.dt

        # 6. Enregistrer les résultats
        self.results_storage.save_state(self)

        return self.dt

    def _limit_outflows(self):
        requested_mass = {tank: 0.0 for tank in self.tanks}

        # Masse totale demandée à chaque tank, toutes sorties confondues.
        for link in self.links:
            massflow = link.massflow
            donor = link.upstream if massflow >= 0.0 else link.downstream

            if isinstance(donor, Port):
                requested_mass[donor.tank] += abs(massflow) * self.dt

        factors = {
            tank: min(1.0, tank.liquid_mass / requested)
            if requested > 0.0 else 1.0
            for tank, requested in requested_mass.items()
        }

        # Même facteur pour toutes les sorties d'un tank.
        for link in self.links:
            massflow = link.massflow
            donor = link.upstream if massflow >= 0.0 else link.downstream

            if isinstance(donor, Port):
                link.state.liquid_velocity *= factors[donor.tank]

    def _compute_net_massflows(self) -> dict[Tank, float]:
        net_massflows = {tank: 0.0 for tank in self.tanks}

        for link in self.links:
            massflow = link.massflow  # Débit après limitation.

            if isinstance(link.upstream, Port):
                net_massflows[link.upstream.tank] -= massflow

            if isinstance(link.downstream, Port):
                net_massflows[link.downstream.tank] += massflow

        return net_massflows

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

    def enable_state_recording(self, interval: float):
        self.results_storage.enable(interval)
