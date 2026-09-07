"""the floor machinery against closed forms"""

import numpy as np
import pytest

from operators.data import (
    Apply_Standardized_Ridge,
    Basis_Decay_Gate,
    Fit_Per_Shell_Filter,
    Fit_Standardized_Ridge,
    Gram_Pod,
    Nearest_Training_Run,
    Hartree_Potential,
    Project,
    Reconstruct,
    Reconstruction_Error_Curve,
)
from operators.metrics import Relative_L2
from operators.tasks import Card_Named
from operators.training import Parameter_Field_Examples
from operators.data.floors import (
    Apply_Per_Shell_Filter,
    COULOMB_CONSTANT,
    Ridge_Apply,
    Ridge_Fit,
    Shell_Index_Grid,
    Spectral_Gradient_Magnitude_And_Laplacian,
)
from operators.substrate import Cartesian_Wavevectors, Reciprocal_Rows


def Test_Reciprocal_Rows_Are_Dual_To_The_Lattice() -> None:
    """lattice rows against reciprocal rows, on a skewed cell"""
    lattice = np.asarray([[3.0, 0.0, 0.0], [0.4, 2.5, 0.0], [0.1, 0.3, 4.0]])
    duality = lattice @ Reciprocal_Rows(lattice).T
    assert np.allclose(duality, 2.0 * np.pi * np.eye(3))


def Test_The_Hartree_Potential_Solves_A_Single_Mode() -> None:
    """the spectral Poisson solution against the closed form for one cosine"""
    extent = 16
    length = 5.0
    lattice = np.eye(3) * length
    coordinates = np.arange(extent) / extent * length
    x_coordinate = coordinates[:, None, None] * np.ones((1, extent, extent))
    wavenumber = 2.0 * np.pi / length
    density = 0.3 * np.cos(wavenumber * x_coordinate)
    expected = 4.0 * np.pi * COULOMB_CONSTANT * 0.3 * np.cos(wavenumber * x_coordinate) / wavenumber**2
    assert np.allclose(Hartree_Potential(density, lattice), expected, atol=1e-9)


def Test_Spectral_Derivatives_Match_Closed_Forms() -> None:
    """the gradient magnitude and Laplacian of one sine mode"""
    extent = 16
    length = 2.0
    lattice = np.eye(3) * length
    coordinates = np.arange(extent) / extent * length
    x_coordinate = coordinates[:, None, None] * np.ones((1, extent, extent))
    wavenumber = 2.0 * np.pi / length
    field = np.sin(wavenumber * x_coordinate)
    gradient, laplacian = Spectral_Gradient_Magnitude_And_Laplacian(field, lattice)
    assert np.allclose(gradient, np.abs(wavenumber * np.cos(wavenumber * x_coordinate)), atol=1e-9)
    assert np.allclose(laplacian, -(wavenumber**2) * field, atol=1e-9)


def Test_The_Shell_Filter_Recovers_A_Diagonal_Map() -> None:
    """fitting on one filtered pair recovers the applied gains exactly"""
    generator = np.random.default_rng(11)
    field = generator.random((8, 8, 8))
    shells = Shell_Index_Grid(field.shape)
    true_gains = 1.0 / (1.0 + np.arange(int(shells.max()) + 1, dtype=np.float64))
    target = Apply_Per_Shell_Filter(true_gains, field)
    fitted = Fit_Per_Shell_Filter([field], [target])
    assert np.allclose(Apply_Per_Shell_Filter(fitted, field), target, atol=1e-10)


def Test_Gram_Pod_Reconstructs_A_Low_Rank_Block() -> None:
    """a rank-three block reconstructs exactly, and passes the gate"""
    generator = np.random.default_rng(5)
    modes = generator.standard_normal((3, 200))
    coefficients = generator.standard_normal((24, 3))
    snapshots = coefficients @ modes + 7.0
    basis = Gram_Pod(snapshots)
    assert basis.singular_values.shape[0] == 3
    rebuilt = Reconstruct(basis, Project(basis, snapshots))
    assert np.allclose(rebuilt, snapshots, atol=1e-9)
    curve = Reconstruction_Error_Curve(snapshots)
    assert curve[2] < 1e-9
    passes, rank = Basis_Decay_Gate(snapshots)
    assert passes and rank <= 3


def Test_Ridge_Fits_A_Linear_Law() -> None:
    """the ridge recovers a noiseless linear relation with intercept"""
    generator = np.random.default_rng(3)
    features = generator.standard_normal((500, 2))
    targets = 2.0 * features[:, 0] - 3.0 * features[:, 1] + 1.0
    coefficients = Ridge_Fit(features, targets, regularization=1e-10)
    assert np.allclose(coefficients, [2.0, -3.0, 1.0], atol=1e-5)
    assert np.allclose(Ridge_Apply(coefficients, features), targets, atol=1e-5)


def Test_Wavevectors_Have_The_Nyquist_Symmetry() -> None:
    """centered modes give equal and opposite wavevectors off the axis ends"""
    lattice = np.eye(3) * 4.0
    wavevectors = Cartesian_Wavevectors(lattice, (8, 8, 8))
    assert np.allclose(wavevectors[1, 0, 0], -wavevectors[7, 0, 0])
    assert np.allclose(wavevectors[0, 0, 0], 0.0)


def Test_The_Standardized_Ridge_Is_Blind_To_Parameter_Units() -> None:
    """the same law is recovered whether a parameter is measured in ones or in millionths"""
    generator = np.random.default_rng(21)
    parameters = generator.standard_normal((300, 3))
    targets = 2.0 * parameters[:, 0] - 3.0 * parameters[:, 1] + 0.5 * parameters[:, 2] + 1.0
    rescaled = parameters * np.asarray([1.0, 1e-6, 1e3])
    plain = Apply_Standardized_Ridge(Fit_Standardized_Ridge(parameters, targets), parameters)
    stretched = Apply_Standardized_Ridge(Fit_Standardized_Ridge(rescaled, targets), rescaled)
    assert np.allclose(plain, targets, atol=1e-6)
    assert np.allclose(stretched, targets, atol=1e-6)


def Test_The_Standardized_Ridge_Carries_Several_Targets_At_Once() -> None:
    """one fit maps parameters onto every basis coefficient, as the floor needs"""
    generator = np.random.default_rng(22)
    parameters = generator.standard_normal((200, 4))
    weights = generator.standard_normal((4, 7))
    targets = parameters @ weights
    fitted = Fit_Standardized_Ridge(parameters, targets)
    assert fitted.coefficients.shape == (5, 7)
    assert np.allclose(Apply_Standardized_Ridge(fitted, parameters), targets, atol=1e-5)


def Test_A_Constant_Parameter_Does_Not_Divide_The_Fit_By_Zero() -> None:
    """a parameter the sweep never varied has no spread, and must not break the standardization"""
    generator = np.random.default_rng(23)
    varying = generator.standard_normal((80, 1))
    parameters = np.concatenate([varying, np.zeros((80, 1))], axis=1)
    targets = 3.0 * varying[:, 0]
    fitted = Fit_Standardized_Ridge(parameters, targets)
    assert float(fitted.parameter_spreads[1]) == 1.0
    assert np.allclose(Apply_Standardized_Ridge(fitted, parameters), targets, atol=1e-6)


def Test_The_Nearest_Training_Run_Is_The_Closest_In_Parameter_Space() -> None:
    """the memorization floor copies from the run a query actually sits next to"""
    train_parameters = np.asarray([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    queries = np.asarray([[0.1, 0.1], [0.9, 0.2], [0.2, 0.9], [0.8, 0.8]])
    assert np.array_equal(Nearest_Training_Run(train_parameters, queries), [0, 1, 2, 3])
    # a query sitting exactly on a training run picks that run
    assert np.array_equal(Nearest_Training_Run(train_parameters, train_parameters), [0, 1, 2, 3])


def Same_Shape_Strain_Block(role: str, functional: str) -> tuple[np.ndarray, np.ndarray]:
    """the strain runs of one functional that share the campaign's most common grid"""
    parameters: list[np.ndarray] = []
    fields: list[np.ndarray] = []
    for example in Parameter_Field_Examples(Card_Named("strain_to_charge"), role):
        values = np.asarray(example.target_function.values, dtype=np.float64)
        if values.shape[1:] != (40, 40, 40) or example.covariate_values["functional"] != functional:
            continue
        parameters.append(np.asarray(example.parameters.vector, dtype=np.float64))
        fields.append(values.reshape(-1))
    return np.asarray(parameters), np.asarray(fields)


@pytest.mark.pool
def Test_The_Parameter_Floors_Land_Where_They_Were_Measured() -> None:
    """the two floors this member must beat, pinned against the store they were measured on"""
    train_parameters, train_fields = Same_Shape_Strain_Block("train", "cheap")
    test_parameters, test_fields = Same_Shape_Strain_Block("test", "cheap")
    assert train_fields.shape == (608, 64000)
    assert test_fields.shape == (88, 64000)

    basis = Gram_Pod(train_fields, rank=32)
    fitted = Fit_Standardized_Ridge(train_parameters, Project(basis, train_fields))
    rebuilt = Reconstruct(basis, Apply_Standardized_Ridge(fitted, test_parameters))
    ridge_errors = np.asarray(
        [Relative_L2(rebuilt[run], test_fields[run]) for run in range(test_fields.shape[0])]
    )
    nearest = Nearest_Training_Run(train_parameters, test_parameters)
    copy_errors = np.asarray(
        [Relative_L2(train_fields[nearest[run]], test_fields[run]) for run in range(test_fields.shape[0])]
    )
    projected = Reconstruct(basis, Project(basis, test_fields))
    ceiling_errors = np.asarray(
        [Relative_L2(projected[run], test_fields[run]) for run in range(test_fields.shape[0])]
    )

    ridge_median = float(np.median(ridge_errors))
    copy_median = float(np.median(copy_errors))
    assert 0.0020 < ridge_median < 0.0032
    assert 0.011 < copy_median < 0.018
    # the ridge floor is the binding one here, contrary to the suite's expectation of the copy
    assert ridge_median < copy_median
    # rank 32 reconstructs these fields to near nothing, so the error is all in the parameter map
    assert float(np.median(ceiling_errors)) < 1e-4
