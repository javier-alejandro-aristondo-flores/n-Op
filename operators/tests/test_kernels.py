"""every shared kernel against the dense reference integral"""

import numpy as np
from numpy.typing import NDArray

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
from operators.framework.integral import Dense_Reference_Integral
from operators.kernels.low_rank import DenseKernel, LowRankKernel, Point_Spec_Over_Indices
from operators.kernels.spectral import SpectralKernel

CUBE = Domain(lattice=np.eye(3) * 2.0)


def Test_The_Dense_Kernel_Matches_The_Oracle() -> None:
    """the dense index kernel equals the reference summation"""
    kernel = DenseKernel(output_count=3, input_count=4, seed=1)
    weights = kernel.parameter_values["weights"]
    coefficients = Coefficients(vector=np.asarray([0.5, -1.0, 2.0, 0.25]), domain=CUBE)

    def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        target_indices = np.asarray(targets[:, 0], dtype=np.int64)
        source_indices = np.asarray(sources[:, 0], dtype=np.int64)
        return weights[np.ix_(target_indices, source_indices)]

    reference = Dense_Reference_Integral(Pair_Kernel, coefficients, Point_Spec_Over_Indices(3))
    produced = kernel.Integrate(coefficients, Point_Spec_Over_Indices(3))
    assert np.allclose(np.asarray(produced.vector), reference[:, 0], atol=1e-12)
    assert "weights" in kernel.Inspect()


def Fourier_Feature_Map(points: NDArray[np.float64]) -> NDArray[np.float64]:
    """a constant plus one wave per axis"""
    waves = np.cos(2.0 * np.pi * points)
    return np.concatenate([np.ones((points.shape[0], 1)), waves], axis=1)


def Test_The_Low_Rank_Kernel_Matches_The_Oracle_On_Points_And_Grids() -> None:
    """the feature-product kernel equals the reference, on grids and on points"""
    kernel = LowRankKernel(Fourier_Feature_Map, feature_count=4, seed=2)
    core = kernel.parameter_values["core"]

    def Pair_Kernel(targets: NDArray[np.float64], sources: NDArray[np.float64]) -> NDArray[np.float64]:
        return Fourier_Feature_Map(targets) @ core @ Fourier_Feature_Map(sources).T

    generator = np.random.default_rng(3)
    cloud = PointSet(
        positions=generator.random((7, 3)),
        domain=CUBE,
        values=generator.random((7, 1)),
        quadrature=CountingQuadrature(),
    )
    query = PointSpec(generator.random((5, 3)))
    reference = Dense_Reference_Integral(Pair_Kernel, cloud, query)
    produced = kernel.Integrate(cloud, query)
    assert np.allclose(np.asarray(produced.vector), reference.reshape(-1), atol=1e-12)

    field = GridFunction(
        values=generator.random((1, 4, 4, 4)),
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    reference = Dense_Reference_Integral(Pair_Kernel, field, query)
    produced = kernel.Integrate(field, query)
    assert np.allclose(np.asarray(produced.vector), reference.reshape(-1), atol=1e-12)


def Test_The_Spectral_Kernel_Matches_The_Dense_Oracle() -> None:
    """the fused spectral path equals the closed-form pair kernel summation"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=4)
    kernel.Hermitian_Symmetrize()
    generator = np.random.default_rng(5)
    cell_volume = 2.0
    field = GridFunction(
        values=generator.random((2, 6, 6, 6)),
        channel_labels=("first_channel", "second_channel"),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=216),
    )
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume), field, GridSpec((6, 6, 6)))
    produced = kernel.Integrate(field, GridSpec((6, 6, 6)))
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-10)


def Test_The_Spectral_Kernel_Transfers_Discretization() -> None:
    """the same weights evaluate exactly on a finer output grid"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=1, input_channels=1, seed=6)
    kernel.Hermitian_Symmetrize()
    generator = np.random.default_rng(7)
    cell_volume = 8.0
    field = GridFunction(
        values=generator.random((1, 6, 6, 6)),
        channel_labels=("charge_density",),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=216),
    )
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume), field, GridSpec((8, 8, 8)))
    produced = kernel.Integrate(field, GridSpec((8, 8, 8)))
    assert np.asarray(produced.values).shape == (1, 8, 8, 8)
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-10)
    inspected = kernel.Inspect()
    assert inspected["mode_magnitudes"].shape == (3, 3, 3, 1, 1)
