"""the linear-algebra facet, double-precision solves on the reference arrays"""

from typing import Any

import numpy as np
from numpy.typing import NDArray


def Solve_Linear_System(matrix: NDArray[np.float64], right_hand_side: NDArray[np.float64]) -> NDArray[np.float64]:
    """the square system solved in double precision"""
    return np.asarray(np.linalg.solve(matrix, right_hand_side), dtype=np.float64)


def Least_Squares_Solution(design: NDArray[np.float64], targets: NDArray[np.float64]) -> NDArray[np.float64]:
    """least-squares coefficients of the design against the targets"""
    coefficients, *_ = np.linalg.lstsq(design, targets, rcond=None)
    return np.asarray(coefficients, dtype=np.float64)


def Largest_Singular_Values_Of_Stack(stack: NDArray[Any]) -> NDArray[np.float64]:
    """the largest singular value of every matrix in a batched stack"""
    singular_values = np.linalg.svd(stack, compute_uv=False)
    return np.asarray(singular_values[..., 0], dtype=np.float64)


def Singular_Values_Clipped(stack: NDArray[Any], ceiling: float) -> NDArray[Any]:
    """every matrix in the stack rebuilt from its singular values, none past the ceiling"""
    left, singular_values, right = np.linalg.svd(stack, full_matrices=False)
    clipped = np.minimum(singular_values, ceiling)
    # broadcasting the clipped values down the last axis scales each right-singular row before the product
    rescaled_right = clipped[..., :, None] * right
    return np.asarray(left @ rescaled_right, dtype=stack.dtype)
