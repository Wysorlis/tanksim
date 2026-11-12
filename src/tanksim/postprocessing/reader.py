# coding: utf-8
from abc import ABC, abstractmethod
import numpy as np
from h5py import File, Group
from functools import partial
from difflib import get_close_matches

from tanksim.physics import PhysicalProperty, TankPhysicalProperty, LinkPhysicalProperty, PROPERTY_SPECS
from tanksim.tank import Tank
from tanksim.link import Link
from tanksim.postprocessing.time_evolution import TimeEvolution

class Reader(ABC):
    def read(self, file: File, element_id: str, property: PhysicalProperty) -> TimeEvolution:
        """Lit l'évolution temporelle d'une propriété.

        Utilise une méthode spécifique si elle est définie dans le dictionnaire,
        sinon lit directement la série stockée dans le fichier HDF5.
        """
        read_func = self._property_readers.get(property, partial(self._read_stored_evolution, property=property))
        evolution = read_func(file, element_id)
        return evolution

    def _read_stored_evolution(self, file: File, element_name: str, *, property: PhysicalProperty) -> TimeEvolution:
        key = f"{element_name}/{property}"
        group = self._get_series_group(file, f"{key}")

        return TimeEvolution(
            time=group["time"][:].tolist(),
            value=group["values"][:].tolist(),
        )
    
    def _get_series_group(self, file: File, key: str) -> Group:
        group = file.get(key)

        if isinstance(group, Group) and "time" in group and "values" in group:
            return group
    
        available = self._list_series_paths(file)
        closest_matches = get_close_matches(key, available, n=3)

        message = f"Requested variable {key!r} not found."
        if closest_matches:
            message += f"\nClosest matches: {', '.join(closest_matches)}."
        else:
            message += "\nNo close match found."
        raise KeyRequestError(message)

            
    @staticmethod
    def _list_series_paths(file: File) -> list[str]:
        """Renvoie la liste des chemins présents dans le fichier .h5."""
        paths = []

        for element, element_group in file.items():
            if not isinstance(element_group, Group):
                continue

            for name, series in element_group.items():
                if isinstance(series, Group) and "time" in series and "values" in series:
                    paths.append(f"{element}/{name}")

        return paths



class KeyRequestError(KeyError):
    def __str__(self) -> str:
        if len(self.args) == 1:
            return str(f"\n{self.args[0]}")
        return super().__str__()


class TankReader(Reader):
    def __init__(self):
        super().__init__()

        self._property_readers = {
            TankPhysicalProperty.LEVEL: self._read_level,
            TankPhysicalProperty.VOLUME: self._read_volume,
        }

    def _read_level(self, file: File, element_name: str) -> TimeEvolution:
        mass = self._get_series_group(file, f"{element_name}/{TankPhysicalProperty.MASS}")
        density = self._get_series_group(file, f"{element_name}/{TankPhysicalProperty.DENSITY}")
        surface = file[f"{element_name}/geometry"].attrs["surface"]

        levels = mass["values"][:] / (density["values"][:] * surface)

        return TimeEvolution(
            time=mass["time"][:].tolist(),
            value=levels.tolist(),
        )
    
    def _read_volume(self, file: File, element_name: str) -> TimeEvolution:
        mass = self._get_series_group(file, f"{element_name}/{TankPhysicalProperty.MASS}")
        density = self._get_series_group(file, f"{element_name}/{TankPhysicalProperty.DENSITY}")
        volume = mass["values"][:] / density["values"][:] 

        return TimeEvolution(
            time=mass["time"][:].tolist(),
            value=volume.tolist(),
        )

class LinkReader(Reader):
    def __init__(self):
        super().__init__()

        self._property_readers = {
            LinkPhysicalProperty.MASSFLOW: self._read_massflow,
            # LinkPhysicalProperty.VOLUME: self._read_volume,
        }

    def _read_massflow(self, file: File, element_name: str) -> TimeEvolution:
        diameter = file[f"{element_name}/geometry"].attrs["diameter"]
        surface = np.pi * diameter**2.0 / 4.0
        
        velocity = self._get_series_group(file, f"{element_name}/{LinkPhysicalProperty.VELOCITY}")
        density = self._get_series_group(file, f"{element_name}/{LinkPhysicalProperty.DENSITY}")        

        massflow = density["values"][:] * surface * velocity["values"][:]

        return TimeEvolution(
            time=velocity["time"][:].tolist(),
            value=massflow.tolist(),
        )
        

ELEMENT_TO_READER = {
    Tank: TankReader,
    Link: LinkReader,
}

