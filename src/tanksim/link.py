# coding: utf-8
import numpy as np
from tanksim.tank import Tank, Port
from tanksim.models.orifice import Orifice


class Link:
    def __init__(self, upstream: Port, dowstream: Port, model: Orifice):
        pass