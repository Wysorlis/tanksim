# coding: utf-8
from dataclasses import dataclass
from enum import StrEnum

class PhysicalProperty(StrEnum):
    """Propriétés accessibles sur un tank"""
    MASS = "liquid_mass"
    DENSITY = "liquid_density"
    VOLUME = "volume"
    LEVEL = "level"


@dataclass(frozen=True)
class PropertySpec:
    unit: str
    label: str

PROPERTY_SPECS = {
    PhysicalProperty.DENSITY: PropertySpec("kg/m³", "Liquid density"),
    PhysicalProperty.MASS: PropertySpec("kg", "Liquid mass"),
    PhysicalProperty.VOLUME: PropertySpec("m³", "Liquid volume"),
    PhysicalProperty.LEVEL: PropertySpec("m", "Liquid level"),
}