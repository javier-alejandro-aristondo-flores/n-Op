"""The dense reference integral — the correctness oracle, never the production path.

This is the definition, evaluated literally: loop over the sources y of ``v``, evaluate the
kernel, weigh by the quadrature, sum. O(sources × targets), unusable at size, and exactly
what every fused Kernel implementation must reproduce on small problems (8³ grids, a few
atoms) before any full-size run. This is the project's calibrate-the-instruments rule
applied to code: a fast kernel that has never been checked against the definition is not an
implementation of the definition.
"""

from __future__ import annotations

from typing import Callable

from operators.framework.domain import Array, Discretization
from operators.framework.representation import Representation


def dense_reference_integral(
    kernel_function: Callable[[Array, Array], Array],
    v: Representation,
    out: Discretization,
) -> Array:
    """∫ κ(x, y) · v(y) · dν(y), by direct summation with the representation's quadrature.

    ``kernel_function`` maps (targets x, sources y) to κ values; the quadrature weights come
    from ``v``. Returns the raw output values at ``out``.
    """
    raise NotImplementedError("implementation phase")
