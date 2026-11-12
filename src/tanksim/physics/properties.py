# coding: utf-8
from dataclasses import dataclass
from enum import StrEnum
from tanksim.tank import Tank
from tanksim.link import Link

class PhysicalProperty(StrEnum):
    pass

class TankPhysicalProperty(PhysicalProperty):
    """Propriétés accessibles sur un tank"""
    MASS = "liquid_mass"
    DENSITY = "liquid_density"
    VOLUME = "liquid_volume"
    LEVEL = "level"

class LinkPhysicalProperty(PhysicalProperty):
    """Propriétés accessibles sur un link"""
    MASSFLOW = "massflow"


CLASS_TO_PROPERTY = {
    Tank: TankPhysicalProperty,
    Link: LinkPhysicalProperty,
}

@dataclass(frozen=True)
class PropertySpec:
    unit: str
    label: str

PROPERTY_SPECS = {
    TankPhysicalProperty.DENSITY: PropertySpec("kg/m³", "Liquid density"),
    TankPhysicalProperty.MASS: PropertySpec("kg", "Liquid mass"),
    TankPhysicalProperty.VOLUME: PropertySpec("m³", "Liquid volume"),
    TankPhysicalProperty.LEVEL: PropertySpec("m", "Liquid level"),
    LinkPhysicalProperty.MASSFLOW: PropertySpec("kg/s", "Massflow rate"),
}