"""The periodic cell, and the two ways of naming where an operator evaluates."""

from dataclasses import dataclass
from typing import Any

type Array = Any


@dataclass(frozen=True, slots=True)
class Domain:
    """A crystal cell as a torus, holding its three lattice vectors as rows in angstrom."""

    lattice: Array


@dataclass(frozen=True, slots=True)
class GridSpec:
    """A uniform grid shape in fractional coordinates."""

    shape: tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class PointSpec:
    """Explicit fractional-coordinate evaluation points, one per row."""

    points: Array


type Discretization = GridSpec | PointSpec
