"""Checks the dense reference integral against closed forms."""

import numpy

from operators.framework import (
    Coefficients,
    CountingQuadrature,
    Domain,
    GridFunction,
    GridSpec,
    PointSet,
    PointSpec,
    UniformGridQuadrature,
)
from operators.framework.domain import Array
from operators.framework.integral import Dense_Reference_Integral, Quadrature_Weights

CUBE = Domain(lattice=numpy.eye(3) * 2.0)


def Constant_Kernel(targets: Array, sources: Array) -> Array:
    """Returns one for every target and source pair."""
    return numpy.ones((numpy.asarray(targets).shape[0], numpy.asarray(sources).shape[0]))


def Test_A_Constant_Kernel_Integrates_The_Field() -> None:
    """Asserts the constant kernel returns the field integral at every output point."""
    values = numpy.arange(16.0).reshape(1, 4, 2, 2)
    field = GridFunction(
        values=values,
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=16),
    )
    result = Dense_Reference_Integral(Constant_Kernel, field, GridSpec((2, 2, 2)))
    expected = float(values.mean()) * 8.0
    assert result.shape == (1, 2, 2, 2)
    assert numpy.allclose(result, expected)


def Test_A_Dot_Kernel_Sums_Points_Analytically() -> None:
    """Asserts a coordinate-dot kernel over counted points matches the closed form."""
    positions = numpy.asarray([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    point_values = numpy.asarray([[3.0], [5.0]])
    cloud = PointSet(positions=positions, domain=CUBE, values=point_values, quadrature=CountingQuadrature())

    def Dot_Kernel(targets: Array, sources: Array) -> Array:
        """Returns the coordinate dot product of every pair."""
        return numpy.asarray(targets) @ numpy.asarray(sources).T

    result = Dense_Reference_Integral(Dot_Kernel, cloud, PointSpec(numpy.asarray([[1.0, 1.0, 0.0]])))
    assert numpy.allclose(result, [[1.0 * 3.0 + 2.0 * 5.0]])


def Test_A_Channel_Mixing_Kernel_Uses_The_Four_Axis_Path() -> None:
    """Asserts a swap-channel kernel routes values across channels."""
    positions = numpy.asarray([[0.0, 0.0, 0.0]])
    cloud = PointSet(positions=positions, domain=CUBE, values=numpy.asarray([[2.0, 7.0]]))

    def Swap_Kernel(targets: Array, sources: Array) -> Array:
        """Returns the channel-swap matrix for every pair."""
        pairs = (numpy.asarray(targets).shape[0], numpy.asarray(sources).shape[0])
        return numpy.broadcast_to(numpy.asarray([[0.0, 1.0], [1.0, 0.0]]), (*pairs, 2, 2))

    result = Dense_Reference_Integral(Swap_Kernel, cloud, PointSpec(numpy.zeros((1, 3))))
    assert numpy.allclose(result, [[7.0, 2.0]])


def Test_Coefficients_Integrate_As_A_Weighted_Sum() -> None:
    """Asserts an index-selecting kernel reads coefficients like a matrix product."""
    coefficients = Coefficients(vector=numpy.asarray([2.0, 4.0, 8.0]), domain=CUBE)

    def Selector_Kernel(targets: Array, sources: Array) -> Array:
        """Returns one only where the source index matches the target row."""
        return (numpy.asarray(targets) == numpy.asarray(sources).T).astype(numpy.float64)

    result = Dense_Reference_Integral(Selector_Kernel, coefficients, PointSpec(numpy.asarray([[1.0], [2.0]])))
    assert numpy.allclose(result, [[4.0], [8.0]])


def Test_Quadrature_Weights_Read_The_Measure() -> None:
    """Asserts grid weights are the cell volume per point and counting weights are one."""
    field = GridFunction(
        values=numpy.zeros((1, 2, 2, 2)),
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=8),
    )
    assert numpy.allclose(Quadrature_Weights(field), 1.0)
    cloud = PointSet(positions=numpy.zeros((3, 3)), domain=CUBE, values=numpy.zeros((3, 1)))
    assert numpy.allclose(Quadrature_Weights(cloud), 1.0)
