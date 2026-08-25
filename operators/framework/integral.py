"""Direct evaluation of the kernel integral by summation over source points."""

from __future__ import annotations

from typing import Callable

from operators.framework.domain import Array, Discretization
from operators.framework.representation import Representation


def Dense_Reference_Integral(
    kernel_function: Callable[[Array, Array], Array],
    input_function: Representation,
    output_discretization: Discretization,
) -> Array:
    """Sums kernel values against the input's quadrature weights at every output point."""
    raise NotImplementedError
