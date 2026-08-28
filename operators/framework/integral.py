"""direct evaluation of the kernel integral by summation over source points"""

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from operators.framework.domain import Discretization, GridSpec
from operators.framework.representation import (
    Coefficients,
    GridFunction,
    PointSet,
    Representation,
    UniformGridQuadrature,
)


def Fractional_Grid_Coordinates(shape: tuple[int, ...]) -> NDArray[np.float64]:
    """fractional coordinates of a uniform grid, in value-flattening order"""
    axes = [np.arange(extent, dtype=np.float64) / extent for extent in shape]
    # ij indexing is the order the field values flatten in
    grids = np.meshgrid(*axes, indexing="ij")
    return np.stack([grid.reshape(-1) for grid in grids], axis=1)


def Quadrature_Weights(representation: Representation) -> NDArray[np.float64]:
    """the integration weight carried by every sample"""
    if isinstance(representation, GridFunction):
        quadrature = representation.quadrature
        values = np.asarray(representation.values)
        # one weight per grid point, the channels share it
        weight = quadrature.cell_volume / quadrature.point_count
        return np.full(values.size // int(values.shape[0]), weight, dtype=np.float64)
    if isinstance(representation, PointSet):
        count = int(np.asarray(representation.positions).shape[0])
        if isinstance(representation.quadrature, UniformGridQuadrature):
            weight = representation.quadrature.cell_volume / representation.quadrature.point_count
            return np.full(count, weight, dtype=np.float64)
        return np.ones(count, dtype=np.float64)
    if isinstance(representation, Coefficients):
        return np.ones(int(np.asarray(representation.vector).shape[0]), dtype=np.float64)
    raise TypeError(f"no quadrature rule for {type(representation).__name__}")


def Source_Points_And_Values(input_function: Representation) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """sample points and per-point channel values"""
    if isinstance(input_function, GridFunction):
        stacked_values = np.asarray(input_function.values)
        points = Fractional_Grid_Coordinates(stacked_values.shape[1:])
        return points, stacked_values.reshape(stacked_values.shape[0], -1).T
    if isinstance(input_function, PointSet):
        if input_function.values is None:
            raise ValueError("a point set needs values to be integrated")
        return np.asarray(input_function.positions), np.asarray(input_function.values)
    if isinstance(input_function, Coefficients):
        vector = np.asarray(input_function.vector, dtype=np.float64)
        # a finite index set carries its own index as its coordinate
        points = np.arange(vector.shape[0], dtype=np.float64).reshape(-1, 1)
        return points, vector.reshape(-1, 1)
    raise TypeError(f"no sampling rule for {type(input_function).__name__}")


def Output_Points(output_discretization: Discretization) -> NDArray[np.float64]:
    """the evaluation points a discretization requests"""
    if isinstance(output_discretization, GridSpec):
        return Fractional_Grid_Coordinates(output_discretization.shape)
    return np.asarray(output_discretization.points, dtype=np.float64)


def Dense_Reference_Integral(
    kernel_function: Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]],
    input_function: Representation,
    output_discretization: Discretization,
) -> NDArray[np.float64]:
    """kernel values summed against the input's quadrature weights at every output point"""
    sources, values = Source_Points_And_Values(input_function)
    weights = Quadrature_Weights(input_function)
    targets = Output_Points(output_discretization)
    kernel_values = np.asarray(kernel_function(targets, sources), dtype=np.float64)
    weighted = np.asarray(values, dtype=np.float64) * weights[:, None]
    if kernel_values.ndim == 2:
        # a scalar kernel treats every channel alike
        integrated = np.einsum("mn,nc->mc", kernel_values, weighted)
    elif kernel_values.ndim == 4:
        # a four-axis kernel mixes channels while it integrates
        integrated = np.einsum("mnoc,nc->mo", kernel_values, weighted)
    else:
        raise ValueError(f"kernel values must have two or four axes, not {kernel_values.ndim}")
    if isinstance(output_discretization, GridSpec):
        return integrated.T.reshape(integrated.shape[1], *output_discretization.shape)
    return integrated
