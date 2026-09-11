"""the real transform facet, and the spectral kernel's gradients through it"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from operators.framework import Dense_Reference_Integral, Domain, GridFunction, GridSpec, UniformGridQuadrature
from operators.kernels import ModeMixing, SpectralKernel
from operators.substrate import (
    Engine,
    Fourier_Transform_3d,
    Half_Spectrum_Extent,
    Inverse_Real_Fourier_Transform_3d,
    NumpyEngine,
    ParameterSet,
    Real_Fourier_Transform_3d,
    Split_Batch_From_Grid,
    Torch_Is_Available,
    TorchEngine,
)

CUBE = Domain(lattice=np.eye(3) * 2.0)

MIXINGS: tuple[ModeMixing, ModeMixing] = ("full", "separable")

ENGINE_CASES = [
    pytest.param(NumpyEngine(), id="numpy_reference"),
    pytest.param(
        TorchEngine(),
        id="torch",
        marks=pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet"),
    ),
]


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_The_Real_Transform_Round_Trips_On_Every_Engine(engine: Engine) -> None:
    """the half spectrum carries a real field back unchanged, on an odd last axis and on an even one"""
    generator = np.random.default_rng(31)
    for grid in ((4, 5, 6), (3, 4, 7)):
        field = generator.random((2, *grid))
        spectrum = Real_Fourier_Transform_3d(engine.Lift_Constant(field), engine.working_precision)
        assert tuple(spectrum.shape) == (2, grid[0], grid[1], Half_Spectrum_Extent(grid[2]))
        returned = np.asarray(Inverse_Real_Fourier_Transform_3d(spectrum, grid, engine.working_precision))
        assert np.allclose(returned, field, atol=1e-12)


def Test_The_Real_Transform_Holds_Only_What_A_Real_Field_Needs() -> None:
    """the half spectrum agrees entry for entry with the whole one, and costs five eighths of it here"""
    generator = np.random.default_rng(32)
    field = generator.random((3, 6, 6, 8))
    half = np.asarray(Real_Fourier_Transform_3d(field))
    whole = np.asarray(Fourier_Transform_3d(field))
    assert half.shape == (3, 6, 6, 5) and whole.shape == (3, 6, 6, 8)
    assert np.allclose(half, whole[..., :5], atol=1e-12)
    # a little over half, because the zero mode and the Nyquist mode are each their own conjugate
    assert half.nbytes / whole.nbytes == 5 / 8


@pytest.mark.parametrize("engine", ENGINE_CASES)
def Test_The_Transform_Never_Widens_What_An_Engine_Narrowed(engine: Engine) -> None:
    """a declared width governs, except that an array which arrived narrow is never promoted back"""
    generator = np.random.default_rng(33)
    wide = engine.Lift_Constant(generator.random((1, 4, 4, 4)))
    assert Real_Fourier_Transform_3d(wide, "double").dtype == Real_Fourier_Transform_3d(wide).dtype
    narrowed = Real_Fourier_Transform_3d(wide, "single")
    assert "complex64" in str(narrowed.dtype)
    assert "complex128" in str(Real_Fourier_Transform_3d(wide, "double").dtype)
    # the hazard this rule exists for: a narrowed engine's array meeting a double declaration, promoted back
    assert "complex64" in str(Real_Fourier_Transform_3d(narrowed.real, "double").dtype)


def Test_The_Transform_Names_Its_Grid_Axes_Apart_From_Its_Channels() -> None:
    """three loose axes are not a field, and any number of leading axes is carried through untouched"""
    generator = np.random.default_rng(34)
    with pytest.raises(ValueError):
        Real_Fourier_Transform_3d(generator.random((4, 4, 4)))
    batched = generator.random((3, 2, 4, 4, 4))
    leading, grid = Split_Batch_From_Grid(batched)
    assert leading == (3, 2) and grid == (4, 4, 4)
    assert np.asarray(Real_Fourier_Transform_3d(batched)).shape == (3, 2, 4, 4, 3)


def Test_The_Kept_Modes_Run_Minus_Kept_To_Plus_Kept() -> None:
    """the gathered block is the signed centered modes, rebuilt where a real field never stored them"""
    generator = np.random.default_rng(35)
    grid = (5, 6, 7)
    field = generator.random((2, *grid))
    kernel = SpectralKernel(kept_modes=(2, 2, 3), output_channels=1, input_channels=2)
    gathered = np.asarray(kernel.Gathered_Modes(Real_Fourier_Transform_3d(field), grid))
    assert gathered.shape == (2, 5, 5, 7)
    whole = np.fft.fftn(field, axes=(1, 2, 3))
    for first_mode in range(-2, 3):
        for second_mode in range(-2, 3):
            for third_mode in range(-3, 4):
                stored = whole[:, first_mode % 5, second_mode % 6, third_mode % 7]
                block = gathered[:, first_mode + 2, second_mode + 2, third_mode + 3]
                assert np.allclose(block, stored, atol=1e-12), (first_mode, second_mode, third_mode)


def Test_The_Kernel_Refuses_A_Grid_Too_Coarse_For_Its_Modes() -> None:
    """a mode whose negative lands on its own positive is a silent alias, so it is refused instead"""
    kernel = SpectralKernel(kept_modes=(3, 1, 1), output_channels=1, input_channels=1)
    with pytest.raises(ValueError):
        kernel.Forward(kernel.parameter_values, np.zeros((1, 6, 6, 6)), (6, 6, 6))


def Squared_Error_Loss(
    kernel: SpectralKernel, field: Any, target: Any, output_shape: tuple[int, int, int]
) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the kernel's output and a fixed target, as a forward an engine can drive"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = kernel.Forward(lifted, field, output_shape) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
@pytest.mark.parametrize("mode_mixing", MIXINGS)
def Test_The_Spectral_Kernel_Sends_Gradients_To_Its_Mode_Weights(mode_mixing: ModeMixing) -> None:
    """a gradient reaches every stored mode weight through the transform, and it is the reference's own number"""
    kernel = SpectralKernel((1, 1, 1), output_channels=2, input_channels=2, seed=11, mode_mixing=mode_mixing)
    generator = np.random.default_rng(12)
    field = generator.random((2, 4, 4, 4))
    target = generator.random((2, 4, 4, 4))
    parameters = ParameterSet(values={name: value.copy() for name, value in kernel.parameter_values.items()})

    engine = TorchEngine()
    lifted_loss = Squared_Error_Loss(kernel, engine.Lift_Constant(field), engine.Lift_Constant(target), (4, 4, 4))
    value, gradients = engine.Value_And_Gradients(parameters, lifted_loss)

    reference = NumpyEngine()
    reference_loss = Squared_Error_Loss(kernel, field, target, (4, 4, 4))
    reference_value = reference.Evaluate(parameters, reference_loss)
    reference_gradients = reference.Gradients(parameters, reference_loss)

    assert set(gradients) == set(kernel.parameter_values)
    assert abs(value - reference_value) < 1e-10
    for name, gradient in gradients.items():
        # a tape severed anywhere between the weight and the loss shows up here as an exactly zero gradient
        assert float(np.abs(gradient).max()) > 1e-6, name
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-5, atol=1e-6), name


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
@pytest.mark.parametrize("mode_mixing", MIXINGS)
def Test_The_Kernel_Answers_The_Same_On_Either_Engine(mode_mixing: ModeMixing) -> None:
    """the foreign engine is a way of differentiating the kernel, not a different kernel"""
    kernel = SpectralKernel((1, 1, 1), output_channels=2, input_channels=3, seed=13, mode_mixing=mode_mixing)
    generator = np.random.default_rng(14)
    field = generator.random((3, 6, 6, 6))
    engine = TorchEngine()
    lifted = engine.Lift(kernel.parameter_values, requires_gradient=False)
    through_torch = np.asarray(kernel.Forward(lifted, engine.Lift_Constant(field), (8, 8, 8)))
    directly = np.asarray(kernel.Forward(kernel.parameter_values, field, (8, 8, 8)))
    assert np.allclose(through_torch, directly, atol=1e-12)


def Random_Field(channels: int, grid: tuple[int, int, int], cell_volume: float, seed: int) -> GridFunction:
    """a random multi-channel field on the cube, carrying the quadrature the oracle integrates against"""
    generator = np.random.default_rng(seed)
    labels = tuple(f"channel_{channel}" for channel in range(channels))
    return GridFunction(
        values=generator.random((channels, *grid)),
        channel_labels=labels,
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=cell_volume, point_count=int(np.prod(grid))),
    )


def Test_The_Separable_Spectral_Kernel_Matches_The_Dense_Oracle() -> None:
    """the factorized weight is a kernel too, and the closed-form summation says which one"""
    kernel = SpectralKernel((1, 1, 1), output_channels=2, input_channels=2, seed=15, mode_mixing="separable")
    kernel.Hermitian_Symmetrize()
    cell_volume = 2.0
    field = Random_Field(2, (6, 6, 6), cell_volume, seed=16)
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume), field, GridSpec((6, 6, 6)))
    produced = kernel.Integrate(field, GridSpec((6, 6, 6)))
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-10)


def Test_The_Separable_Spectral_Kernel_Transfers_Discretization() -> None:
    """the same factorized weights evaluate exactly on a finer output grid"""
    kernel = SpectralKernel((1, 1, 1), output_channels=1, input_channels=1, seed=17, mode_mixing="separable")
    kernel.Hermitian_Symmetrize()
    cell_volume = 8.0
    field = Random_Field(1, (6, 6, 6), cell_volume, seed=18)
    reference = Dense_Reference_Integral(kernel.Dense_Kernel_Function(cell_volume), field, GridSpec((8, 8, 8)))
    produced = kernel.Integrate(field, GridSpec((8, 8, 8)))
    assert np.asarray(produced.values).shape == (1, 8, 8, 8)
    assert np.allclose(np.asarray(produced.values), reference, atol=1e-10)


def Test_The_Separable_Form_Stores_Far_Fewer_Weights_Than_The_Full_One() -> None:
    """the counted weights match the priced ones, and the price is what makes a full Nyquist budget affordable"""
    for mode_mixing in MIXINGS:
        kernel = SpectralKernel((3, 4, 5), output_channels=5, input_channels=4, mode_mixing=mode_mixing)
        assert kernel.Parameter_Count() == SpectralKernel.Parameter_Count_For((3, 4, 5), 5, 4, mode_mixing)
    # the full coarse Nyquist of a forty-cubed grid at sixty-four channels, which is the flagship's own budget
    full = SpectralKernel.Parameter_Count_For((20, 20, 20), 64, 64, "full")
    separable = SpectralKernel.Parameter_Count_For((20, 20, 20), 64, 64, "separable")
    assert (full, separable) == (564_600_832, 1_007_616)
    assert full > 500 * separable


def Test_The_Separable_Kernel_Publishes_Every_Axis_As_Magnitude_And_Phase() -> None:
    """each axis factor is one complex weight, and each is reachable as the pair it is stored as"""
    kernel = SpectralKernel((2, 1, 1), output_channels=2, input_channels=3, seed=19, mode_mixing="separable")
    inspected = kernel.Inspect()
    for axis_name, extent in zip(("first_axis", "second_axis", "third_axis"), (5, 3, 3)):
        magnitudes = np.asarray(inspected[f"{axis_name}_mode_magnitudes"], dtype=np.float64)
        phases = np.asarray(inspected[f"{axis_name}_mode_phases"], dtype=np.float64)
        real_part = np.asarray(inspected[f"{axis_name}_mode_weights_real"], dtype=np.float64)
        imaginary_part = np.asarray(inspected[f"{axis_name}_mode_weights_imaginary"], dtype=np.float64)
        assert magnitudes.shape == (extent, 2, 3)
        assert np.allclose(magnitudes * np.cos(phases), real_part)
        assert np.allclose(magnitudes * np.sin(phases), imaginary_part)


def Test_The_Assembled_Weights_Are_What_The_Factors_Add_Up_To() -> None:
    """the factorized form is the whole mode tensor, flat along the two axes each factor does not know"""
    kernel = SpectralKernel((1, 2, 1), output_channels=2, input_channels=2, seed=20, mode_mixing="separable")
    assembled = kernel.Assembled_Mode_Weights()
    assert assembled.shape == (3, 5, 3, 2, 2)
    first = kernel.Complex_Weight(kernel.parameter_values, "first_axis_mode_weights")
    second = kernel.Complex_Weight(kernel.parameter_values, "second_axis_mode_weights")
    third = kernel.Complex_Weight(kernel.parameter_values, "third_axis_mode_weights")
    for first_mode in range(3):
        for second_mode in range(5):
            for third_mode in range(3):
                added = first[first_mode] + second[second_mode] + third[third_mode]
                assert np.allclose(assembled[first_mode, second_mode, third_mode], added)
