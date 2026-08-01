"""Residual keys, observable references, and the category vocabulary.

Auditor 3 found `ObservableRef` -- the key type of two of the three public exports --
defined nowhere, independently reported by two auditors who never spoke. `AxisLabel` was
never enumerated, and `ResidualKey` carried no field for the axis point it is required to
distinguish. This module gives all three a concrete form.

The emission discipline the corpus fixes and this module enforces:

    every independent component is its own scalar with its own content-addressed key,
    and the oracle never preaggregates.

So a residual map is `dict[ResidualKey, float]` and nothing here sums, weights, normalises
or thresholds. Aggregation belongs to the consumer.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Axes. An axis coordinate is (label, value); a key's axes are an ordered tuple.
# The label set is open at the type level and closed per compiled kernel -- the
# kernel's static schema enumerates exactly the labels it emits.
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class Axis:
    """One axis coordinate of a residual contribution."""

    label: str
    value: Any

    def __str__(self) -> str:  # stable, and what the content address hashes
        return f"{self.label}={self.value!r}"


def axes(**kwargs: Any) -> tuple[Axis, ...]:
    """`axes(ion=3, cartesian='x')` -> a canonical, sorted axis tuple.

    Sorted by label so that two callers writing the same axes in different orders
    produce the same key. Without this, key identity depends on keyword order.
    """
    return tuple(sorted((Axis(k, v) for k, v in kwargs.items())))


# ---------------------------------------------------------------------------
# The 19 residual categories. Closed enum, named never by ordinal.
# ---------------------------------------------------------------------------

class CategoryTag(Enum):
    """The 19 residual categories: 9 equation-of-motion, 3 structural, 5 algebraic,
    2 constraint-violation. Named, never ordinal -- the corpus is explicit that the
    ordinal carries no meaning."""

    EOM_DENSITY_MATRIX = "EOM/gamma-hat"
    EOM_VECTOR_POTENTIAL = "EOM/A"
    EOM_ION_POSITIONS = "EOM/R"
    EOM_ION_MOMENTA = "EOM/P"
    EOM_CELL = "EOM/h"
    EOM_CELL_MOMENTUM = "EOM/Pi-h"
    EOM_SPECIES = "EOM/Z"
    EOM_DEFECT_POPULATION = "EOM/DefectPopulation"
    EOM_CONTINUUM = "EOM/Continuum"

    DEGENERACY = "Degeneracy"
    CONSERVATION = "Conservation"
    POSITIVITY = "Positivity"

    ALGEBRAIC_KRAMERS_KRONIG = "Algebraic/Kramers-Kronig"
    ALGEBRAIC_SUM_RULES = "Algebraic/SumRules"
    ALGEBRAIC_BALANCE_LAWS = "Algebraic/BalanceLaws"
    ALGEBRAIC_SYMMETRIES = "Algebraic/Symmetries"
    ALGEBRAIC_METHOD_EQUIVALENCE = "Algebraic/MethodEquivalence"

    STATIC_SNAPSHOT = "Static/Snapshot"
    STATIC_THERMODYNAMIC = "Static/Thermodynamic"


assert len(CategoryTag) == 19, "the category vocabulary is closed at 19"


# ---------------------------------------------------------------------------
# Producers and keys
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class Producer:
    """What emitted a contribution: a named registry formula, or a named method.

    `name` is the registry row's `Name` cell where one exists -- `elastic-stability-criteria`,
    `bulk-modulus` -- so a key traces back to a numbered, cited row.
    """

    kind: str  # "formula" | "method" | "invariant"
    name: str

    def __post_init__(self) -> None:
        if self.kind not in ("formula", "method", "invariant"):
            raise ValueError(f"unknown producer kind: {self.kind!r}")


@dataclass(frozen=True, order=True)
class ResidualKey:
    """The atomic unit: the smallest scalar the consumer can weight independently.

    Content-addressed. Two evaluations with identical inputs produce the identical key,
    and the address is stable across recompiles so a consumer's weight map survives them.
    """

    producer: Producer
    axis_tuple: tuple[Axis, ...] = ()

    def canonical(self) -> str:
        inner = ",".join(str(a) for a in self.axis_tuple)
        return f"{self.producer.kind}:{self.producer.name}({inner})"

    @property
    def address(self) -> str:
        """Content address. Truncated blake2b of the canonical string."""
        return hashlib.blake2b(self.canonical().encode("utf-8"), digest_size=16).hexdigest()

    def __str__(self) -> str:
        return self.canonical()


@dataclass(frozen=True, order=True)
class ObservableRef:
    """A named physical quantity the kernel can return a *value* for.

    Distinct from `ResidualKey`: a residual is a disagreement, an observable is a value.
    Two of the three public exports key on this type and no page defines it -- found
    independently by two auditors.
    """

    name: str
    axis_tuple: tuple[Axis, ...] = ()

    def canonical(self) -> str:
        inner = ",".join(str(a) for a in self.axis_tuple)
        return f"observable:{self.name}({inner})"

    @property
    def address(self) -> str:
        return hashlib.blake2b(self.canonical().encode("utf-8"), digest_size=16).hexdigest()

    def __str__(self) -> str:
        return self.canonical()


@dataclass(frozen=True)
class ContributionFacets:
    """Queryable provenance attached to a key. Never part of key identity, and never
    the basis for a weight -- the corpus is explicit that facets answer "which residuals
    belong to the transport bundle?" and never "what is the weight of residual r?"."""

    category: CategoryTag
    bundle: str | None = None
    dressing: str = "bare"


@dataclass
class ResidualMap:
    """What `Validate` returns: raw keyed scalars, plus the facets sidecar.

    Deliberately not a plain dict subclass -- the sidecar travels with it, and there is
    no `.total()`, no `.sum()`, no `.score()`. Adding one would violate
    *evidence, never verdicts*.
    """

    values: dict[ResidualKey, float] = field(default_factory=dict)
    facets: dict[ResidualKey, ContributionFacets] = field(default_factory=dict)

    def emit(self, key: ResidualKey, value: float, facets: ContributionFacets) -> None:
        if key in self.values:
            raise ValueError(f"duplicate residual key: {key}")
        self.values[key] = float(value)
        self.facets[key] = facets

    def __contains__(self, key: ResidualKey) -> bool:
        return key in self.values

    def __len__(self) -> int:
        return len(self.values)

    def by_category(self, category: CategoryTag) -> dict[ResidualKey, float]:
        """A *query*, not an aggregation -- returns the raw scalars, unreduced."""
        return {k: v for k, v in self.values.items() if self.facets[k].category is category}
