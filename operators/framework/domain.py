"""the periodic cell and the two ways of naming where an operator evaluates"""

from dataclasses import dataclass

from operators.substrate import ArrayLike

type Array = ArrayLike


@dataclass(frozen=True, slots=True)
class Domain:
    """a crystal cell as a torus, lattice vectors as rows in angstrom"""

    lattice: Array


@dataclass(frozen=True, slots=True)
class GridSpec:
    """a uniform grid shape in fractional coordinates"""

    shape: tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class PointSpec:
    """explicit fractional-coordinate evaluation points, one per row"""

    points: Array


type Discretization = GridSpec | PointSpec
