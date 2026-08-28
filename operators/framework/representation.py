"""typed function objects, each carrying the quadrature it is integrated against"""

from dataclasses import dataclass, field

from operators.framework.domain import Array, Domain


@dataclass(frozen=True, slots=True)
class UniformGridQuadrature:
    """the cell volume split evenly over the grid points"""

    cell_volume: float
    point_count: int


@dataclass(frozen=True, slots=True)
class CountingQuadrature:
    """unit weight on every point"""


type Quadrature = UniformGridQuadrature | CountingQuadrature


class Representation:
    """base of the typed function objects"""

    __slots__ = ()

    # only the domain is declared here, each form narrows its own quadrature
    domain: Domain


@dataclass(frozen=True, slots=True)
class GridFunction(Representation):
    """field values on a uniform grid, one named channel per quantity"""

    values: Array
    channel_labels: tuple[str, ...]
    domain: Domain
    quadrature: UniformGridQuadrature


@dataclass(frozen=True, slots=True)
class PointSet(Representation):
    """points in the cell with optional values, species and message-passing roles"""

    positions: Array
    domain: Domain
    values: Array | None = None
    species: Array | None = None
    roles: Array | None = None
    quadrature: Quadrature = field(default_factory=CountingQuadrature)


@dataclass(frozen=True, slots=True)
class Coefficients(Representation):
    """a finite vector over an index set"""

    vector: Array
    domain: Domain
    quadrature: CountingQuadrature = field(default_factory=CountingQuadrature)
