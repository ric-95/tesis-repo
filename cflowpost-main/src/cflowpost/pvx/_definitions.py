from dataclasses import dataclass, asdict
from typing import List
from abc import ABC

Point = List[float]


@dataclass
class Definition(ABC):

    def to_dict(self):
        return asdict(self)


@dataclass
class Plane:
    """Class used to define a plane.

    The origin, point1 and point2"""
    origin: Point
    point1: Point
    point2: Point
    x_res: int
    y_res: int
    timestep: float
    variables: List[str]
    output: str


@dataclass
class Line:
    point1: Point
    point2: Point
    resolution: int
    timestep: float
    variables: List[str]
    output: str


@dataclass
class Streamlines(Definition):
    pass

