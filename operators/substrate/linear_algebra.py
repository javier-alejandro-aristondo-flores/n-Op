"""The linear-algebra facet: double-precision solves on the reference arrays."""

import numpy
from numpy.typing import NDArray


def Solve_Linear_System(matrix: NDArray[numpy.float64], right_hand_side: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Solves the square linear system in double precision."""
    return numpy.asarray(numpy.linalg.solve(matrix, right_hand_side), dtype=numpy.float64)


def Least_Squares_Solution(design: NDArray[numpy.float64], targets: NDArray[numpy.float64]) -> NDArray[numpy.float64]:
    """Returns the least-squares coefficients of the design against the targets."""
    coefficients, *_ = numpy.linalg.lstsq(design, targets, rcond=None)
    return numpy.asarray(coefficients, dtype=numpy.float64)
