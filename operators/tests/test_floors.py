"""Checks the floor machinery against closed forms."""

import numpy

from operators.data.floors import (
    Apply_Per_Shell_Filter,
    Fit_Per_Shell_Filter,
    Hartree_Potential,
    Ridge_Apply,
    Ridge_Fit,
    Shell_Index_Grid,
    Spectral_Gradient_Magnitude_And_Laplacian,
    COULOMB_CONSTANT,
)
from operators.substrate.fourier import Cartesian_Wavevectors, Reciprocal_Rows
from operators.data.pod import Basis_Decay_Gate, Gram_Pod, Project, Reconstruct, Reconstruction_Error_Curve


def Test_Reciprocal_Rows_Are_Dual_To_The_Lattice() -> None:
    """Asserts lattice rows and reciprocal rows satisfy the two-pi duality on a skewed cell."""
    lattice = numpy.asarray([[3.0, 0.0, 0.0], [0.4, 2.5, 0.0], [0.1, 0.3, 4.0]])
    duality = lattice @ Reciprocal_Rows(lattice).T
    assert numpy.allclose(duality, 2.0 * numpy.pi * numpy.eye(3))


def Test_The_Hartree_Potential_Solves_A_Single_Mode() -> None:
    """Asserts the spectral Poisson solution matches the closed form for one cosine."""
    extent = 16
    length = 5.0
    lattice = numpy.eye(3) * length
    coordinates = numpy.arange(extent) / extent * length
    x_coordinate = coordinates[:, None, None] * numpy.ones((1, extent, extent))
    wavenumber = 2.0 * numpy.pi / length
    density = 0.3 * numpy.cos(wavenumber * x_coordinate)
    expected = 4.0 * numpy.pi * COULOMB_CONSTANT * 0.3 * numpy.cos(wavenumber * x_coordinate) / wavenumber**2
    assert numpy.allclose(Hartree_Potential(density, lattice), expected, atol=1e-9)


def Test_Spectral_Derivatives_Match_Closed_Forms() -> None:
    """Asserts the gradient magnitude and Laplacian of one sine mode."""
    extent = 16
    length = 2.0
    lattice = numpy.eye(3) * length
    coordinates = numpy.arange(extent) / extent * length
    x_coordinate = coordinates[:, None, None] * numpy.ones((1, extent, extent))
    wavenumber = 2.0 * numpy.pi / length
    field = numpy.sin(wavenumber * x_coordinate)
    gradient, laplacian = Spectral_Gradient_Magnitude_And_Laplacian(field, lattice)
    assert numpy.allclose(gradient, numpy.abs(wavenumber * numpy.cos(wavenumber * x_coordinate)), atol=1e-9)
    assert numpy.allclose(laplacian, -(wavenumber**2) * field, atol=1e-9)


def Test_The_Shell_Filter_Recovers_A_Diagonal_Map() -> None:
    """Asserts fitting on one filtered pair recovers the applied gains exactly."""
    generator = numpy.random.default_rng(11)
    field = generator.random((8, 8, 8))
    shells = Shell_Index_Grid(field.shape)
    true_gains = 1.0 / (1.0 + numpy.arange(int(shells.max()) + 1, dtype=numpy.float64))
    target = Apply_Per_Shell_Filter(true_gains, field)
    fitted = Fit_Per_Shell_Filter([field], [target])
    assert numpy.allclose(Apply_Per_Shell_Filter(fitted, field), target, atol=1e-10)


def Test_Gram_Pod_Reconstructs_A_Low_Rank_Block() -> None:
    """Asserts a rank-three block reconstructs exactly and passes the gate."""
    generator = numpy.random.default_rng(5)
    modes = generator.standard_normal((3, 200))
    coefficients = generator.standard_normal((24, 3))
    snapshots = coefficients @ modes + 7.0
    basis = Gram_Pod(snapshots)
    assert basis.singular_values.shape[0] == 3
    rebuilt = Reconstruct(basis, Project(basis, snapshots))
    assert numpy.allclose(rebuilt, snapshots, atol=1e-9)
    curve = Reconstruction_Error_Curve(snapshots)
    assert curve[2] < 1e-9
    passes, rank = Basis_Decay_Gate(snapshots)
    assert passes and rank <= 3


def Test_Ridge_Fits_A_Linear_Law() -> None:
    """Asserts the ridge recovers a noiseless linear relation with intercept."""
    generator = numpy.random.default_rng(3)
    features = generator.standard_normal((500, 2))
    targets = 2.0 * features[:, 0] - 3.0 * features[:, 1] + 1.0
    coefficients = Ridge_Fit(features, targets, regularization=1e-10)
    assert numpy.allclose(coefficients, [2.0, -3.0, 1.0], atol=1e-5)
    assert numpy.allclose(Ridge_Apply(coefficients, features), targets, atol=1e-5)


def Test_Wavevectors_Have_The_Nyquist_Symmetry() -> None:
    """Asserts centered modes give equal and opposite wavevectors off the axis ends."""
    lattice = numpy.eye(3) * 4.0
    wavevectors = Cartesian_Wavevectors(lattice, (8, 8, 8))
    assert numpy.allclose(wavevectors[1, 0, 0], -wavevectors[7, 0, 0])
    assert numpy.allclose(wavevectors[0, 0, 0], 0.0)
