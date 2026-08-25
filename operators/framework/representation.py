"""Typed function objects, each carrying its quadrature.

The quadrature is the measure of the kernel integral made explicit as data: it says how a sum
over this representation's points approximates an integral. Making it data (rather than an
assumption inside each kernel) is what lets one compact-support kernel serve both the
convolutional operator (uniform grid measure) and DeepDFT (counting measure over atoms), and
it is read in four independent places: zero-mean projections, electron-count renormalization,
low-rank inner products, and codomain-attention scores.

Three representations cover every operator in the suite:

    GridFunction   values on a uniform grid over the cell, with labeled channels
    PointSet       positions with optional per-point values, species, and roles
    Coefficients   a finite vector — sensor readings, basis coefficients, parameters

``PointSet`` deliberately serves both "the atomic structure as input" (positions + species,
no values) and "features carried on points" (values present) — DeepDFT's receive-only probe
points forced the merge, via the ``roles`` field.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from operators.framework.domain import Array, Domain


@dataclass(frozen=True)
class UniformGridQuadrature:
    """Uniform grid over the cell: every point weighs cell_volume / point_count.

    This is the ÷V_cell convention of the data pipeline, carried into the math.
    """

    cell_volume: float
    point_count: int


@dataclass(frozen=True)
class CountingQuadrature:
    """A plain sum: the measure is counting. Atoms, sensors, and index sets all use it."""


Quadrature = UniformGridQuadrature | CountingQuadrature


class Representation(ABC):
    """Base of the three typed function objects. Carries the domain and the quadrature.

    Deliberately behavior-free: kernels dispatch on the concrete type; the base exists so
    signatures can say "any function object" and so every instance answers for its measure.
    """

    domain: Domain
    quadrature: Quadrature


@dataclass(frozen=True)
class GridFunction(Representation):
    """A field: values on a uniform grid, channels labeled by what they physically are.

    ``channel_labels`` names each channel ("charge_density", "magnetization",
    "electron_localization_up", ...) — the multiple-input and codomain-attention operators
    need to know which field is which, and the spin-block law makes channel sets vary
    across the corpus.
    """

    values: Array  # shape (channels, n1, n2, n3)
    channel_labels: tuple[str, ...]
    domain: Domain
    quadrature: UniformGridQuadrature


@dataclass(frozen=True)
class PointSet(Representation):
    """Points in the cell, with whatever rides on them.

    As input structure: positions + species, values absent. As carried features: values
    present. ``roles`` marks asymmetries in message passing — DeepDFT's probe points are
    part of the graph but only receive.
    """

    positions: Array  # shape (n, 3), fractional coordinates
    domain: Domain
    values: Array | None = None  # shape (n, channels) when present
    species: Array | None = None  # per-point species identity, when the points are atoms
    roles: Array | None = None  # e.g. receive-only flags; None means all points are equal
    quadrature: Quadrature = field(default_factory=CountingQuadrature)


@dataclass(frozen=True)
class Coefficients(Representation):
    """A finite vector: parameters, sensor readings, or coefficients in a basis.

    The finite index set integrates by counting — a dense layer on coefficients is a kernel
    integral against the counting measure, which is why the branch–trunk family needs no
    special case.
    """

    vector: Array  # shape (k,)
    domain: Domain
    quadrature: CountingQuadrature = field(default_factory=CountingQuadrature)
