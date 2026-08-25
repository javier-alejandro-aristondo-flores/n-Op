"""The periodic cell, and the two ways of saying "evaluate here".

``Array`` is an opaque alias: the array/autodiff substrate is dictated in the implementation
documents, and nothing in the framework's signatures may assume one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# The tensor type of the (not yet chosen) backend. Signatures use it; no framework code may
# call methods on it until the backend lands.
Array = Any


@dataclass(frozen=True)
class Domain:
    """The crystal's repeating cell: a torus with a lattice.

    ``lattice`` holds the three cell vectors as rows, in ångström. Everything metric flows
    from it: reciprocal vectors (spectral kernels need physical wavevectors in non-orthogonal
    cells), cell volume (the uniform-grid quadrature weight is volume / point count), and
    cell heights (periodic image enumeration must use heights, never the minimum-image
    shortcut — the alloy cell is strongly skewed and the shortcut is wrong there).
    """

    lattice: Array  # shape (3, 3), rows are cell vectors, ångström


@dataclass(frozen=True)
class GridSpec:
    """Evaluate on a uniform grid of this shape, in fractional coordinates."""

    shape: tuple[int, int, int]


@dataclass(frozen=True)
class PointSpec:
    """Evaluate at these fractional-coordinate points (shape (n, 3))."""

    points: Array


# Where an operator is asked to produce its output. Grid or points — a probe lattice is a
# GridSpec used internally by an operator, not a third kind.
Discretization = GridSpec | PointSpec
