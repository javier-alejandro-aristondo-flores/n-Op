"""the linear-algebra facet, double-precision solves on the reference arrays"""

import numpy as np
from numpy.typing import NDArray


def Solve_Linear_System(matrix: NDArray[np.float64], right_hand_side: NDArray[np.float64]) -> NDArray[np.float64]:
    """the square system solved in double precision"""
    return np.asarray(np.linalg.solve(matrix, right_hand_side), dtype=np.float64)


def Least_Squares_Solution(design: NDArray[np.float64], targets: NDArray[np.float64]) -> NDArray[np.float64]:
    """least-squares coefficients of the design against the targets"""
    coefficients, *_ = np.linalg.lstsq(design, targets, rcond=None)
    return np.asarray(coefficients, dtype=np.float64)
