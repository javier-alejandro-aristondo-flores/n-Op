"""the U-shaped composition: descent, the bottom, ascent through skip connections, and its output scale"""

from collections.abc import Callable
from typing import Any, Literal

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import MultiScale
from operators.compositions.multi_scale import Downsampled_By_Two, Layer_Applied, Sliced_Lifted, Upsampled_By_Two
from operators.encoders import PointwiseLift
from operators.framework import Domain, GridFunction, Layer, UniformGridQuadrature
from operators.kernels import SpectralKernel
from operators.substrate import Concatenate_Channels, NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine

CUBE = Domain(lattice=np.eye(3) * 2.0)


def Small_Field(channels: int, shape: tuple[int, int, int], seed: int) -> GridFunction:
    """a random field on the given grid, carrying the cube quadrature at that grid's own point count"""
    generator = np.random.default_rng(seed)
    labels = tuple(f"channel_{channel}" for channel in range(channels))
    point_count = shape[0] * shape[1] * shape[2]
    quadrature = UniformGridQuadrature(cell_volume=8.0, point_count=point_count)
    return GridFunction(generator.random((channels, *shape)), labels, CUBE, quadrature)


def Band_Limited_Field(
    channels: int, shape: tuple[int, int, int], highest_mode: int, seed: int
) -> NDArray[np.float64]:
    """a real field built from only the low modes a coarser scale still resolves exactly"""
    generator = np.random.default_rng(seed)
    grids = np.meshgrid(*[np.arange(extent) for extent in shape], indexing="ij")
    field = np.zeros((channels, *shape), dtype=np.float64)
    for channel in range(channels):
        for first_mode in range(-highest_mode, highest_mode + 1):
            for second_mode in range(-highest_mode, highest_mode + 1):
                for third_mode in range(-highest_mode, highest_mode + 1):
                    phase = 2.0 * np.pi * (
                        first_mode * grids[0] / shape[0]
                        + second_mode * grids[1] / shape[1]
                        + third_mode * grids[2] / shape[2]
                    )
                    field[channel] += generator.normal(0.0, 1.0) * np.cos(phase)
    return field


def Small_Layer(
    input_channels: int,
    output_channels: int,
    seed: int,
    activation: Literal["pointwise", "alias_free"] = "pointwise",
    residual: bool = False,
) -> Layer[GridFunction]:
    """a fresh spectral kernel paired with a pointwise local map, both built at the same output width"""
    kernel = SpectralKernel(
        kept_modes=(1, 1, 1), output_channels=output_channels, input_channels=input_channels, seed=seed
    )
    kernel.Hermitian_Symmetrize()
    local_linear = PointwiseLift(hidden_channels=output_channels, input_channels=input_channels, seed=seed + 1)
    return Layer(kernel=kernel, local_linear=local_linear, activation=activation, residual=residual)


def Test_Every_Scale_Halves_Exactly_And_The_Output_Leaves_At_Its_Designated_Shape() -> None:
    """the descending path visits every halved shape in turn, and ascent stops at the scale asked for"""
    descending = (Small_Layer(2, 3, seed=1), Small_Layer(3, 4, seed=3))
    bottom = Small_Layer(4, 5, seed=5)
    ascending = (Small_Layer(5 + 4, 6, seed=7),)
    composition = MultiScale(descending, bottom, ascending, output_scale=1)
    field = Small_Field(2, (16, 16, 16), seed=9)
    produced = composition.Apply(field)
    assert composition.last_scale_shapes == {
        "descending_0": (16, 16, 16),
        "descending_1": (8, 8, 8),
        "bottom": (4, 4, 4),
        "ascending_0": (8, 8, 8),
    }
    assert np.asarray(produced.values).shape == (6, 8, 8, 8)


def Test_A_Shape_That_Will_Not_Halve_Raises() -> None:
    """a grid extent that cannot split in two is refused rather than rounded away"""
    descending = (Small_Layer(2, 3, seed=1),)
    bottom = Small_Layer(3, 4, seed=3)
    composition = MultiScale(descending, bottom, (), output_scale=1)
    field = Small_Field(2, (15, 15, 15), seed=9)
    with pytest.raises(ValueError):
        composition.Apply(field)


def Test_Downsampling_Then_Upsampling_Recovers_A_Band_Limited_Field_Exactly() -> None:
    """the operator-gate claim the whole entry rests on: sinc resampling on a periodic cell is exact"""
    field = Band_Limited_Field(channels=2, shape=(16, 16, 16), highest_mode=1, seed=11)
    descended_twice = Downsampled_By_Two(Downsampled_By_Two(field))
    round_tripped = Upsampled_By_Two(Upsampled_By_Two(descended_twice))
    assert float(np.abs(round_tripped - field).max()) < 1e-9


def Test_The_Skip_Connection_Carries_Information() -> None:
    """the ascending layer's output moves when the same-scale descending contribution is zeroed instead"""
    descending = (Small_Layer(2, 3, seed=51),)
    bottom = Small_Layer(3, 4, seed=53)
    ascending = (Small_Layer(4 + 3, 5, seed=55),)
    composition = MultiScale(descending, bottom, ascending, output_scale=0)
    values = np.asarray(Small_Field(2, (8, 8, 8), seed=57).values, dtype=np.float64)
    lifted = composition.Parameter_Values()
    by_scale = dict(composition.Scale_Outputs(lifted, values))
    baseline_output = np.asarray(by_scale["ascending_0"], dtype=np.float64)
    skip_value = by_scale["descending_0"]
    bottom_value = by_scale["bottom"]

    ablated_joined = Concatenate_Channels([Upsampled_By_Two(bottom_value), np.zeros_like(skip_value)])
    ablated_output = Layer_Applied(
        composition.ascending_layers[0], Sliced_Lifted(lifted, "ascending_0."), ablated_joined
    )
    assert not np.allclose(baseline_output, np.asarray(ablated_output, dtype=np.float64))


def Test_Forward_And_Apply_Agree() -> None:
    """the numpy wrapper reaches the same numbers as a direct call into the lifted forward"""
    descending = (Small_Layer(2, 3, seed=41),)
    bottom = Small_Layer(3, 4, seed=43)
    ascending = (Small_Layer(4 + 3, 5, seed=45),)
    composition = MultiScale(descending, bottom, ascending, output_scale=0)
    field = Small_Field(2, (8, 8, 8), seed=47)
    values = np.asarray(field.values, dtype=np.float64)
    through_forward = composition.Forward(composition.Parameter_Values(), values)
    through_apply = composition.Apply(field).values
    assert np.allclose(np.asarray(through_forward, dtype=np.float64), np.asarray(through_apply, dtype=np.float64))


def Multi_Scale_Loss(composition: MultiScale, field_values: Any, target: Any) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the composition's output and a fixed target, as an engine can drive it"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = composition.Forward(lifted, field_values) - target
        return (difference * difference).sum()

    return Loss


def Agreeing_Gradients(
    parameters: ParameterSet,
    lifted_loss: Callable[[dict[str, Any]], Any],
    reference_loss: Callable[[dict[str, Any]], Any],
) -> dict[str, NDArray[np.float64]]:
    """the differentiable engine's gradients, checked against the finite-difference oracle and handed back"""
    value, gradients = TorchEngine().Value_And_Gradients(parameters, lifted_loss)
    reference = NumpyEngine()
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-10
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(reference_gradients)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-5, atol=1e-6), name
    return gradients


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradients_Reach_Every_Layers_Kernel_And_Local_Linear_Weights() -> None:
    """a tape severed at a resample, a concatenation, or the bottom would leave part of the U untrained"""
    descending = (Small_Layer(2, 2, seed=31),)
    bottom = Small_Layer(2, 2, seed=33)
    ascending = (Small_Layer(2 + 2, 2, seed=35),)
    composition = MultiScale(descending, bottom, ascending, output_scale=0)
    field = Small_Field(2, (8, 8, 8), seed=37)
    field_values = np.asarray(field.values, dtype=np.float64)
    target = np.random.default_rng(39).random((2, 8, 8, 8))
    parameters = ParameterSet(values={name: value.copy() for name, value in composition.Parameter_Values().items()})

    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Multi_Scale_Loss(composition, engine.Lift_Constant(field_values), engine.Lift_Constant(target)),
        Multi_Scale_Loss(composition, field_values, target),
    )
    assert set(gradients) == set(composition.Parameter_Values())
    for name, gradient in gradients.items():
        # a tape severed anywhere between a weight and the loss shows up here as an exactly zero gradient
        assert float(np.abs(gradient).max()) > 1e-6, name


def Test_The_Alias_Free_Activation_Raises_Where_The_Explicit_Stack_Does() -> None:
    """the fused kernel is the convolutional entry's own build, not a topology default"""
    descending = (Small_Layer(2, 2, seed=61, activation="alias_free"),)
    bottom = Small_Layer(2, 2, seed=63)
    composition = MultiScale(descending, bottom, (), output_scale=1)
    field = Small_Field(2, (8, 8, 8), seed=65)
    with pytest.raises(NotImplementedError, match="the alias-free activation is the convolutional entry's own build"):
        composition.Apply(field)
