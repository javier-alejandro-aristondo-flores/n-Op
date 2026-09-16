"""the ladder's first stability rung: a post-step Lipschitz clip on the shared layer's own factors"""

from typing import Any

import numpy as np
import pytest

from operators.compositions.contraction import (
    ContractionBudget,
    ContractionProjection,
    GELU_LIPSCHITZ_SLOPE,
    Nominal_Lipschitz,
    STEM_NAMES,
)
from operators.compositions.fixed_point import Single_Layer_Parameter_Values
from operators.encoders import PointwiseLift
from operators.framework import Layer
from operators.kernels import SpectralKernel
from operators.substrate import NumpyEngine, ParameterSet
from operators.training.loop import Fresh_Progress, TrainingBatch, Train
from operators.training.sampling import BatchSource


def Scaled(part: Any, scale: float) -> Any:
    """the part with every stored parameter multiplied by a scale, returned for chaining"""
    for name in part.parameter_values:
        part.parameter_values[name] *= scale
    return part


def Separable_Layer(seed: int, channels: int = 3, scale: float = 0.05) -> Layer[Any]:
    """a kernel-plus-local-linear layer built with the flagship's own separable mixing, scaled small"""
    kernel = SpectralKernel(
        kept_modes=(1, 1, 1), output_channels=channels, input_channels=channels, seed=seed, mode_mixing="separable"
    )
    kernel.Hermitian_Symmetrize()
    kernel = Scaled(kernel, scale)
    local_linear = Scaled(PointwiseLift(hidden_channels=channels, input_channels=channels, seed=seed + 1), scale)
    return Layer(kernel=kernel, local_linear=local_linear)


class EmptyBatches(BatchSource):
    """a batch source carrying no data at all, for a loss that reads nothing but the parameters"""


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        return TrainingBatch({})


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        return (("only_unit", TrainingBatch({})),)


    def Inspect(self) -> dict[str, Any]:
        return {}


def Growth_Loss(parameter_names: tuple[str, ...]) -> Any:
    """the negative sum of squares over the named parameters, whose gradient grows every one of them every step"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        total = 0.0
        for name in parameter_names:
            total = total - (lifted[name] * lifted[name]).sum()
        return total

    return Loss


def Test_The_Budget_Splits_Its_Target_Between_The_Local_Share_And_The_Modes() -> None:
    """the local bound plus every factor's own bound, summed back up, returns exactly the undivided target"""
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    local_bound = budget.Local_Bound()
    mode_bound = budget.Mode_Bound(3)
    assert abs(local_bound - 0.2 * 0.9 / GELU_LIPSCHITZ_SLOPE) < 1e-12
    assert abs(mode_bound - 0.8 * 0.9 / (GELU_LIPSCHITZ_SLOPE * 3)) < 1e-12
    assert abs(GELU_LIPSCHITZ_SLOPE * (local_bound + 3 * mode_bound) - budget.target_lipschitz) < 1e-10


def Test_The_Mode_Bound_Refuses_A_Zero_Factor_Count() -> None:
    """a separable kernel always carries at least one factor, so a zero count is not a budget to divide"""
    with pytest.raises(ValueError):
        ContractionBudget().Mode_Bound(0)


def Test_Nominal_Lipschitz_Matches_A_Direct_Svd_Of_The_Same_Arrays() -> None:
    """the free function's own number against a plain numpy computation over the same parameter dict"""
    layer = Separable_Layer(seed=1, channels=3, scale=1.0)
    parameters = Single_Layer_Parameter_Values(layer)
    expected = GELU_LIPSCHITZ_SLOPE * (
        float(np.linalg.svd(parameters["local_linear.lift_weights"], compute_uv=False)[0])
        + sum(
            float(
                np.max(
                    np.linalg.svd(
                        parameters[f"kernel.{stem}_real"] + 1j * parameters[f"kernel.{stem}_imaginary"],
                        compute_uv=False,
                    )[..., 0]
                )
            )
            for stem in STEM_NAMES
        )
    )
    assert abs(Nominal_Lipschitz(parameters) - expected) < 1e-8


def Test_An_In_Budget_Layer_Is_Left_Untouched_By_The_Projection() -> None:
    """a layer already under budget round-trips through the exact clip to floating-point precision"""
    layer = Separable_Layer(seed=2, channels=2, scale=0.01)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    projection = ContractionProjection(layer, budget)
    before = {name: value.copy() for name, value in Single_Layer_Parameter_Values(layer).items()}
    parameters = ParameterSet(values={name: value.copy() for name, value in before.items()})
    progress = Fresh_Progress(parameters, np.random.default_rng(0))
    assert Nominal_Lipschitz(before) < budget.target_lipschitz
    projection.After_Step(progress)
    for name, value in before.items():
        assert np.allclose(progress.parameters.values[name], value, atol=1e-9), name


def Test_A_Fifty_Times_Scaled_Layer_Is_Brought_Under_The_Target_Lipschitz() -> None:
    """a layer scaled far past the budget still clips into it in one post-step application"""
    layer = Separable_Layer(seed=3, channels=2, scale=50.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    projection = ContractionProjection(layer, budget)
    parameters = ParameterSet(values={name: value.copy() for name, value in Single_Layer_Parameter_Values(layer).items()})
    assert Nominal_Lipschitz(parameters.values) > budget.target_lipschitz
    progress = Fresh_Progress(parameters, np.random.default_rng(0))
    projection.After_Step(progress)
    assert Nominal_Lipschitz(progress.parameters.values) <= budget.target_lipschitz + 1e-8
    assert projection.last_clipped_fraction is not None and projection.last_clipped_fraction > 0.0


def Test_The_Projection_Is_Idempotent() -> None:
    """a second application right after the first changes nothing more, the map already inside its own budget"""
    layer = Separable_Layer(seed=4, channels=2, scale=50.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    projection = ContractionProjection(layer, budget)
    parameters = ParameterSet(values={name: value.copy() for name, value in Single_Layer_Parameter_Values(layer).items()})
    progress = Fresh_Progress(parameters, np.random.default_rng(0))
    projection.After_Step(progress)
    once = {name: value.copy() for name, value in progress.parameters.values.items()}
    projection.After_Step(progress)
    for name, value in once.items():
        assert np.allclose(progress.parameters.values[name], value, atol=1e-9), name


def Test_The_Projection_Refuses_A_Metric_Aware_Kernel() -> None:
    """a metric-aware kernel's gain is unbounded, so the projection must not pretend to bound it"""
    kernel = SpectralKernel(
        kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=5, mode_mixing="separable", metric_aware=True
    )
    local_linear = PointwiseLift(hidden_channels=2, input_channels=2, seed=6)
    layer = Layer(kernel=kernel, local_linear=local_linear)
    with pytest.raises(ValueError):
        ContractionProjection(layer, ContractionBudget())


def Test_The_Projection_Refuses_Full_Mode_Mixing() -> None:
    """the per-factor bound is stated for the separable form alone, and a dense mode tensor is not that form"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=2, input_channels=2, seed=7, mode_mixing="full")
    local_linear = PointwiseLift(hidden_channels=2, input_channels=2, seed=8)
    layer = Layer(kernel=kernel, local_linear=local_linear)
    with pytest.raises(ValueError):
        ContractionProjection(layer, ContractionBudget())


def Test_Flat_Name_Prefix_Handling() -> None:
    """a composition-scoped prefix reaches the projection to the same effect, and untouched names are left alone"""
    layer = Separable_Layer(seed=9, channels=2, scale=50.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    prefix = "shared_layer."
    projection = ContractionProjection(layer, budget, prefix=prefix)
    bare_values = Single_Layer_Parameter_Values(layer)
    prefixed_values = {f"{prefix}{name}": value.copy() for name, value in bare_values.items()}
    unrelated_name = "projection.head_weights"
    prefixed_values[unrelated_name] = np.ones((3, 3))
    parameters = ParameterSet(values=prefixed_values)
    progress = Fresh_Progress(parameters, np.random.default_rng(0))
    projection.After_Step(progress)
    assert Nominal_Lipschitz(progress.parameters.values, prefix=prefix) <= budget.target_lipschitz + 1e-8
    assert np.array_equal(progress.parameters.values[unrelated_name], np.ones((3, 3)))


def Test_The_Projected_Map_Stays_Contractive_While_The_Unprojected_One_Leaves_The_Ball() -> None:
    """thirty adam steps of a loss that only ever grows the weights: the hooked run stays bounded, the bare one does not"""
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    layer_projected = Separable_Layer(seed=101, channels=3, scale=0.05)
    layer_unprojected = Separable_Layer(seed=101, channels=3, scale=0.05)
    parameters_projected = ParameterSet(
        values={name: value.copy() for name, value in Single_Layer_Parameter_Values(layer_projected).items()}
    )
    parameters_unprojected = ParameterSet(
        values={name: value.copy() for name, value in Single_Layer_Parameter_Values(layer_unprojected).items()}
    )
    growth_loss = Growth_Loss(tuple(parameters_projected.values))
    hook = ContractionProjection(layer_projected, budget)

    result_projected = Train(
        NumpyEngine(), parameters_projected, growth_loss, EmptyBatches(), step_count=30, learning_rate=0.1,
        validation_interval=30, hook=hook,
    )
    result_unprojected = Train(
        NumpyEngine(), parameters_unprojected, growth_loss, EmptyBatches(), step_count=30, learning_rate=0.1,
        validation_interval=30,
    )
    assert Nominal_Lipschitz(result_projected.parameters.values) <= budget.target_lipschitz + 1e-8
    assert Nominal_Lipschitz(result_unprojected.parameters.values) > budget.target_lipschitz
