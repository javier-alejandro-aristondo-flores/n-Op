"""Typed function objects, each carrying the quadrature it is integrated against."""

from dataclasses import dataclass, field

from operators.framework.domain import Array, Domain


@dataclass(frozen=True, slots=True)
class UniformGridQuadrature:
    """Weights every grid point by the cell volume divided by the point count."""

    cell_volume: float
    point_count: int


@dataclass(frozen=True, slots=True)
class CountingQuadrature:
    """Weights every point by one."""


type Quadrature = UniformGridQuadrature | CountingQuadrature


class Representation:
    """Base of the typed function objects; every form carries a domain and a quadrature."""

    __slots__ = ()

    domain: Domain


@dataclass(frozen=True, slots=True)
class GridFunction(Representation):
    """Field values on a uniform grid, one named channel per physical quantity."""

    values: Array
    channel_labels: tuple[str, ...]
    domain: Domain
    quadrature: UniformGridQuadrature


@dataclass(frozen=True, slots=True)
class PointSet(Representation):
    """Points in the cell with optional values, species, and message-passing roles."""

    positions: Array
    domain: Domain
    values: Array | None = None
    species: Array | None = None
    roles: Array | None = None
    quadrature: Quadrature = field(default_factory=CountingQuadrature)


@dataclass(frozen=True, slots=True)
class Coefficients(Representation):
    """A finite vector over an index set."""

    vector: Array
    domain: Domain
    quadrature: CountingQuadrature = field(default_factory=CountingQuadrature)
