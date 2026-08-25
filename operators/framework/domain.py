"""The periodic cell, and the two ways of naming where an operator evaluates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

Array = Any


@dataclass(frozen=True)
class Domain:
    """A crystal cell as a torus, holding its three lattice vectors as rows in angstrom."""

    lattice: Array


@dataclass(frozen=True)
class GridSpec:
    """A uniform grid shape in fractional coordinates."""

    shape: tuple[int, int, int]


@dataclass(frozen=True)
class PointSpec:
    """Explicit fractional-coordinate evaluation points, one per row."""

    points: Array


Discretization = GridSpec | PointSpec
