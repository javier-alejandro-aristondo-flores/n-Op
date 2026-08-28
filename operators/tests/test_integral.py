"""the dense reference integral against closed forms"""

import numpy as np

from numpy.typing import NDArray

from operators.framework import (
    Coefficients,
    CountingQuadrature,
    Dense_Reference_Integral,
    Domain,
    GridFunction,
    GridSpec,
    PointSet,
    PointSpec,
    Quadrature_Weights,
    UniformGridQuadrature,
)

CUBE = Domain(lattice=np.eye(3) * 2.0)


def Constant_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
    """one, for every target and source pair"""
    return np.ones((np.asarray(targets).shape[0], np.asarray(sources).shape[0]))


def Test_A_Constant_Kernel_Integrates_The_Field() -> None:
    """a constant kernel returns the field's integral at every output point"""
    values = np.arange(16.0).reshape(1, 4, 2, 2)
    field = GridFunction(
        values=values,
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=16),
    )
    result = Dense_Reference_Integral(Constant_Kernel, field, GridSpec((2, 2, 2)))
    expected = float(values.mean()) * 8.0
    assert result.shape == (1, 2, 2, 2)
    assert np.allclose(result, expected)


def Test_A_Dot_Kernel_Sums_Points_Analytically() -> None:
    """a coordinate-dot kernel over counted points, against the closed form"""
    positions = np.asarray([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    point_values = np.asarray([[3.0], [5.0]])
    cloud = PointSet(positions=positions, domain=CUBE, values=point_values, quadrature=CountingQuadrature())

    def Dot_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        """the coordinate dot product of every pair"""
        return np.asarray(targets) @ np.asarray(sources).T

    result = Dense_Reference_Integral(Dot_Kernel, cloud, PointSpec(np.asarray([[1.0, 1.0, 0.0]])))
    assert np.allclose(result, [[1.0 * 3.0 + 2.0 * 5.0]])


def Test_A_Channel_Mixing_Kernel_Uses_The_Four_Axis_Path() -> None:
    """a swap-channel kernel routes values across channels"""
    positions = np.asarray([[0.0, 0.0, 0.0]])
    cloud = PointSet(positions=positions, domain=CUBE, values=np.asarray([[2.0, 7.0]]))

    def Swap_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        """the channel-swap matrix, for every pair"""
        pairs = (np.asarray(targets).shape[0], np.asarray(sources).shape[0])
        return np.broadcast_to(np.asarray([[0.0, 1.0], [1.0, 0.0]]), (*pairs, 2, 2))

    result = Dense_Reference_Integral(Swap_Kernel, cloud, PointSpec(np.zeros((1, 3))))
    assert np.allclose(result, [[7.0, 2.0]])


def Test_Coefficients_Integrate_As_A_Weighted_Sum() -> None:
    """an index-selecting kernel reads coefficients like a matrix product"""
    coefficients = Coefficients(vector=np.asarray([2.0, 4.0, 8.0]), domain=CUBE)

    def Selector_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        """one only where the source index matches the target row"""
        return (np.asarray(targets) == np.asarray(sources).T).astype(np.float64)

    result = Dense_Reference_Integral(Selector_Kernel, coefficients, PointSpec(np.asarray([[1.0], [2.0]])))
    assert np.allclose(result, [[4.0], [8.0]])


def Test_Quadrature_Weights_Read_The_Measure() -> None:
    """grid weights are cell volume per point, counting weights are one"""
    field = GridFunction(
        values=np.zeros((1, 2, 2, 2)),
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=8),
    )
    assert np.allclose(Quadrature_Weights(field), 1.0)
    cloud = PointSet(positions=np.zeros((3, 3)), domain=CUBE, values=np.zeros((3, 1)))
    assert np.allclose(Quadrature_Weights(cloud), 1.0)
