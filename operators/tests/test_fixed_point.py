"""the weight-tied and fixed-point rungs of the deep-equilibrium ladder"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import FixedPoint, WeightTied
from operators.compositions.fixed_point import Anderson_Mixing_Weights, Sliced_Lifted
from operators.encoders import PointwiseLift
from operators.framework import Domain, GridFunction, Layer, UniformGridQuadrature
from operators.kernels import SpectralKernel
from operators.substrate import Detached, NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine

CUBE = Domain(lattice=np.eye(3) * 2.0)
GRID_QUADRATURE = UniformGridQuadrature(cell_volume=8.0, point_count=8 * 8 * 8)


def Small_Field(channels: int, seed: int) -> GridFunction:
    """a random eight-cubed field, scaled small, with the cube quadrature"""
    generator = np.random.default_rng(seed)
    labels = tuple(f"channel_{channel}" for channel in range(channels))
    return GridFunction(generator.random((channels, 8, 8, 8)) * 0.1, labels, CUBE, GRID_QUADRATURE)


def Scaled(part: Any, scale: float) -> Any:
    """the part with every stored parameter multiplied by a scale, returned for chaining"""
    for name in part.parameter_values:
        part.parameter_values[name] *= scale
    return part


def Contractive_Layer(seed: int, channels: int = 2) -> Layer[GridFunction]:
    """a kernel-plus-local-linear layer scaled small enough that repeated application is a contraction"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=channels, input_channels=channels, seed=seed)
    kernel.Hermitian_Symmetrize()
    kernel = Scaled(kernel, 0.05)
    local_linear = Scaled(PointwiseLift(hidden_channels=channels, input_channels=channels, seed=seed + 1), 0.05)
    return Layer(kernel=kernel, local_linear=local_linear)


def Divergent_Layer(seed: int, channels: int = 2) -> Layer[GridFunction]:
    """a kernel-plus-local-linear layer scaled far past the point where repeated application converges"""
    kernel = SpectralKernel(kept_modes=(1, 1, 1), output_channels=channels, input_channels=channels, seed=seed)
    kernel.Hermitian_Symmetrize()
    kernel = Scaled(kernel, 50.0)
    local_linear = Scaled(PointwiseLift(hidden_channels=channels, input_channels=channels, seed=seed + 1), 50.0)
    return Layer(kernel=kernel, local_linear=local_linear)


def Test_Weight_Tied_Applies_The_Shared_Layer_Its_Depth_Many_Times() -> None:
    """the depth many applications each land in inspect, in order, under the shared layer's own names"""
    layer = Contractive_Layer(seed=1)
    stack = WeightTied(layer, depth=5)
    field = Small_Field(2, seed=2)
    produced = stack.Apply(field)
    assert np.asarray(produced.values).shape == (2, 8, 8, 8)
    inspected = stack.Inspect()
    assert "kernel.mode_magnitudes" in inspected
    assert "local_linear.lift_weights" in inspected
    assert "layer_0.kernel.mode_magnitudes" not in inspected
    assert np.asarray(inspected["last_application_norms"]).shape == (5,)


def Test_Weight_Tied_Shares_One_Copy_Of_Parameters_Across_Every_Application() -> None:
    """parameter_values carries the layer once, not once per application, which is the whole point of tying"""
    layer = Contractive_Layer(seed=3)
    stack = WeightTied(layer, depth=7)
    collected = stack.Parameter_Values()
    expected_count = len(layer.kernel.parameter_values) + len(layer.local_linear.parameter_values)
    assert len(collected) == expected_count
    assert {f"kernel.{name}" for name in layer.kernel.parameter_values} <= set(collected)
    assert {f"local_linear.{name}" for name in layer.local_linear.parameter_values} <= set(collected)


def Test_Forward_And_Apply_Agree_On_Weight_Tied() -> None:
    """the lifted path and the numpy wrapper around it read the same numbers off the same input"""
    layer = Contractive_Layer(seed=5)
    stack = WeightTied(layer, depth=4)
    field = Small_Field(2, seed=6)
    through_apply = np.asarray(stack.Apply(field).values, dtype=np.float64)
    through_forward = np.asarray(
        stack.Forward(stack.Parameter_Values(), np.asarray(field.values, dtype=np.float64)), dtype=np.float64
    )
    assert np.allclose(through_apply, through_forward, atol=1e-12)


def Weight_Tied_Loss(stack: WeightTied, field_values: Any, target: Any) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the tied stack's output and a fixed target, as a forward an engine can drive"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = stack.Forward(lifted, field_values) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_Gradients_Reach_Both_Weight_Groups_Through_Every_Application_Of_Weight_Tied() -> None:
    """a tape severed anywhere in the tied loop would leave the shared weights it repeats untrainable"""
    layer = Contractive_Layer(seed=7)
    stack = WeightTied(layer, depth=3)
    field_values = np.asarray(Small_Field(2, seed=8).values, dtype=np.float64)
    target = np.random.default_rng(9).random((2, 8, 8, 8))
    parameters = ParameterSet(values={name: value.copy() for name, value in stack.Parameter_Values().items()})
    engine = TorchEngine()
    value, gradients = engine.Value_And_Gradients(
        parameters, Weight_Tied_Loss(stack, engine.Lift_Constant(field_values), engine.Lift_Constant(target))
    )
    reference = NumpyEngine()
    reference_loss = Weight_Tied_Loss(stack, field_values, target)
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-8
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(reference_gradients)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-4, atol=1e-5), name
        assert float(np.abs(gradient).max()) > 1e-8, name


def Test_The_Fixed_Point_Converges_On_A_Contractive_Layer() -> None:
    """the canon's health floor read directly off inspect after a solve that should find its equilibrium"""
    layer = Contractive_Layer(seed=11)
    stack = FixedPoint(layer)
    field = Small_Field(2, seed=12)
    produced = stack.Apply(field)
    assert np.all(np.isfinite(np.asarray(produced.values)))
    inspected = stack.Inspect()
    assert float(np.asarray(inspected["last_final_residual"])) < 1e-3
    assert int(np.asarray(inspected["last_iterations_taken"])) <= 32
    assert bool(np.asarray(inspected["last_cap_was_hit"])) is False


def Test_The_Fixed_Point_Reports_The_Cap_Rather_Than_Silently_Returning_Garbage() -> None:
    """a map that is not a contraction still produces a finite answer, honestly flagged as unconverged"""
    layer = Divergent_Layer(seed=13)
    stack = FixedPoint(layer, iteration_cap=32)
    field = Small_Field(2, seed=14)
    produced = stack.Apply(field)
    assert np.all(np.isfinite(np.asarray(produced.values)))
    inspected = stack.Inspect()
    assert bool(np.asarray(inspected["last_cap_was_hit"])) is True
    assert int(np.asarray(inspected["last_iterations_taken"])) == 32


def Test_Anderson_Acceleration_Converges_In_Fewer_Iterations_Than_Plain_Picard() -> None:
    """the history the canon asks for earns its keep, or damping alone would have done as well"""
    layer = Contractive_Layer(seed=15)
    field = Small_Field(2, seed=16)
    accelerated = FixedPoint(layer, history_depth=5)
    accelerated.Apply(field)
    plain_picard = FixedPoint(layer, history_depth=1)
    plain_picard.Apply(field)
    assert accelerated.last_solve is not None
    assert plain_picard.last_solve is not None
    assert accelerated.last_solve.iterations_taken < plain_picard.last_solve.iterations_taken


def Test_Forward_And_Apply_Agree_On_The_Fixed_Point() -> None:
    """the lifted path and the numpy wrapper around it read the same numbers off the same input"""
    layer = Contractive_Layer(seed=17)
    stack = FixedPoint(layer, backward="phantom", phantom_depth=3)
    field = Small_Field(2, seed=18)
    through_apply = np.asarray(stack.Apply(field).values, dtype=np.float64)
    through_forward = np.asarray(
        stack.Forward(stack.Parameter_Values(), np.asarray(field.values, dtype=np.float64)), dtype=np.float64
    )
    assert np.allclose(through_apply, through_forward, atol=1e-12)


def Test_Jacobian_Free_Is_Phantom_Truncated_To_One_Reentry() -> None:
    """the debug floor is not a separate mechanism, only the tunable rule's cheapest setting"""
    layer = Contractive_Layer(seed=19)
    field = Small_Field(2, seed=20)
    jacobian_free = FixedPoint(layer, backward="jacobian_free")
    phantom_one = FixedPoint(layer, backward="phantom", phantom_depth=1)
    produced_jacobian_free = np.asarray(jacobian_free.Apply(field).values, dtype=np.float64)
    produced_phantom_one = np.asarray(phantom_one.Apply(field).values, dtype=np.float64)
    assert np.allclose(produced_jacobian_free, produced_phantom_one, atol=1e-12)


def Test_Phantom_Reentry_Stays_Near_The_Equilibrium_As_Its_Depth_Grows() -> None:
    """a few extra applications from a converged state barely move it, since it is already near-fixed"""
    layer = Contractive_Layer(seed=21)
    field = Small_Field(2, seed=22)
    shallow = FixedPoint(layer, backward="phantom", phantom_depth=1)
    deep = FixedPoint(layer, backward="phantom", phantom_depth=3)
    produced_shallow = np.asarray(shallow.Apply(field).values, dtype=np.float64)
    produced_deep = np.asarray(deep.Apply(field).values, dtype=np.float64)
    assert np.allclose(produced_shallow, produced_deep, atol=1e-2)


def Test_The_Implicit_Backward_Rule_Is_Not_Available_Yet() -> None:
    """the adjoint needs a vector-jacobian-product primitive substrate does not expose, so it fails loudly"""
    layer = Contractive_Layer(seed=23)
    stack = FixedPoint(layer, backward="implicit")
    field = Small_Field(2, seed=24)
    with pytest.raises(NotImplementedError):
        stack.Apply(field)


def Fixed_Point_Equilibrium_Loss(
    stack: FixedPoint, field_values: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the solved equilibrium and a fixed target, as a forward an engine can drive"""

    def Loss(lifted: dict[str, Any]) -> Any:
        produced, _ = stack.Resolved(lifted, field_values)
        difference = produced - target
        return (difference * difference).sum()

    return Loss


def Test_Finite_Differences_Through_The_Reference_Engine_Move_With_Both_Weight_Groups() -> None:
    """the equilibrium's gradient, owing nothing to any tape, is live in the kernel and the local linear map alike"""
    layer = Contractive_Layer(seed=31, channels=1)
    stack = FixedPoint(layer, backward="phantom")
    field_values = np.asarray(Small_Field(1, seed=33).values, dtype=np.float64)
    target = np.random.default_rng(34).random((1, 8, 8, 8)) * 0.1
    parameters = ParameterSet(values={name: value.copy() for name, value in stack.Parameter_Values().items()})
    gradients = NumpyEngine().Gradients(parameters, Fixed_Point_Equilibrium_Loss(stack, field_values, target))
    assert set(gradients) == set(stack.Parameter_Values())
    kernel_names = [name for name in gradients if name.startswith("kernel.")]
    local_linear_names = [name for name in gradients if name.startswith("local_linear.")]
    assert max(float(np.abs(gradients[name]).max()) for name in kernel_names) > 1e-8
    assert max(float(np.abs(gradients[name]).max()) for name in local_linear_names) > 1e-8


def Test_The_Solver_Reaches_What_A_Long_Weight_Tied_Unroll_Also_Converges_Toward() -> None:
    """the equilibrium the solver reports is a genuine attracting point of the same repeated application"""
    layer = Contractive_Layer(seed=41)
    field = Small_Field(2, seed=42)
    solved = FixedPoint(layer)
    produced = np.asarray(solved.Apply(field).values, dtype=np.float64)
    assert solved.last_solve is not None
    unrolled = WeightTied(layer, depth=solved.last_solve.iterations_taken + 10)
    produced_unrolled = np.asarray(unrolled.Apply(field).values, dtype=np.float64)
    assert np.allclose(produced, produced_unrolled, atol=1e-2)


def Test_Inspect_Exposes_The_Health_Signals_The_Canon_Requires() -> None:
    """iterations, residual and the cap flag all surface as named arrays, not just as python attributes"""
    layer = Contractive_Layer(seed=51)
    stack = FixedPoint(layer)
    field = Small_Field(2, seed=52)
    stack.Apply(field)
    inspected = stack.Inspect()
    for name in ("last_iterations_taken", "last_final_residual", "last_cap_was_hit", "last_residual_norm_history"):
        assert name in inspected
    history = np.asarray(inspected["last_residual_norm_history"])
    assert history.ndim == 1
    assert int(np.asarray(inspected["last_iterations_taken"])) == history.shape[0]


# the substrate primitives this stream added: detached here, the vector-jacobian product in the second commit


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_Detached_Severs_The_Foreign_Engines_Gradient_Path() -> None:
    """a value pulled through detached casts no gradient back, beside a control path that still carries one"""
    parameters = ParameterSet(values={"severed": np.asarray([2.0, 3.0]), "control": np.asarray([5.0, 7.0])})
    engine = TorchEngine()

    def Loss(lifted: dict[str, Any]) -> Any:
        return (Detached(lifted["severed"]) * 2.0).sum() + (lifted["control"] * 3.0).sum()

    _, gradients = engine.Value_And_Gradients(parameters, Loss)
    assert np.allclose(gradients["severed"], 0.0)
    assert np.allclose(gradients["control"], 3.0)


def Test_Detached_Is_The_Identity_On_The_Reference_Engine() -> None:
    """there is no tape to cut on a plain array, so detaching one returns the same values unchanged"""
    value = np.asarray([1.0, 2.0, 3.0])
    assert np.array_equal(Detached(value), value)


def Test_Anderson_Mixing_Weights_Declines_A_Near_Parallel_History() -> None:
    """a residual history whose differences are nearly collinear returns none rather than an unstable mix"""
    near_parallel_history = [
        np.asarray([2.0, 0.0, 0.0]),
        np.asarray([2.0000001, 0.0, 0.0]),
        np.asarray([1.0, 0.0, 0.0]),
    ]
    weights = Anderson_Mixing_Weights(near_parallel_history, regularization=1e-4, condition_ceiling=1e6)
    assert weights is None


def Test_Anderson_Mixing_Weights_Sums_To_One_On_A_Well_Conditioned_History() -> None:
    """the constraint the derivation depends on, checked directly on the small linear-algebra helper"""
    well_conditioned_history = [
        np.asarray([1.0, 0.0, 0.0]),
        np.asarray([0.0, 1.0, 0.0]),
        np.asarray([0.3, 0.3, 0.3]),
    ]
    weights = Anderson_Mixing_Weights(well_conditioned_history, regularization=1e-4, condition_ceiling=1e6)
    assert weights is not None
    assert abs(float(weights.sum()) - 1.0) < 1e-10


# the mandatory 8-cubed gradient audit -- phantom against finite differences and against the full unroll,
# both grounded on the same contractive layer as the health-floor tests above; implicit joins in the next commit


def Relative_Gap(candidate: dict[str, NDArray[np.float64]], ground_truth: dict[str, NDArray[np.float64]]) -> float:
    """how far one named gradient dict sits from another, as one fraction of the ground truth's own size"""
    flat_candidate = np.concatenate([value.reshape(-1) for value in candidate.values()])
    flat_truth = np.concatenate([value.reshape(-1) for value in ground_truth.values()])
    return float(np.linalg.norm(flat_candidate - flat_truth) / (np.linalg.norm(flat_truth) + 1e-12))


def Audit_Ground_Truths(
    layer: Layer[GridFunction], field_values: NDArray[np.float64], target: NDArray[np.float64]
) -> tuple[ParameterSet, dict[str, NDArray[np.float64]], dict[str, NDArray[np.float64]]]:
    """the audit's parameters beside its two ground truths: finite differences, and the depth-matched full unroll"""
    probe = FixedPoint(layer)
    parameters = ParameterSet(values={name: value.copy() for name, value in probe.Parameter_Values().items()})
    reference_loss = Fixed_Point_Equilibrium_Loss(probe, field_values, target)
    finite_difference_gradients = NumpyEngine().Gradients(parameters, reference_loss)
    kernel_lifted = Sliced_Lifted(probe.Parameter_Values(), "kernel.")
    local_linear_lifted = Sliced_Lifted(probe.Parameter_Values(), "local_linear.")
    depth = probe.Solved(kernel_lifted, local_linear_lifted, field_values).iterations_taken
    tied = WeightTied(layer, depth=depth)
    engine = TorchEngine()
    _, full_unroll_gradients = engine.Value_And_Gradients(
        parameters, Weight_Tied_Loss(tied, engine.Lift_Constant(field_values), engine.Lift_Constant(target))
    )
    return parameters, finite_difference_gradients, full_unroll_gradients


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_The_Audits_Two_Ground_Truths_Agree_With_Each_Other() -> None:
    """finite differences on the converged solve and a depth-matched full unroll measure the same gradient"""
    layer = Contractive_Layer(seed=71)
    field_values = np.asarray(Small_Field(2, seed=72).values, dtype=np.float64)
    target = np.random.default_rng(73).random((2, 8, 8, 8))
    _, finite_difference_gradients, full_unroll_gradients = Audit_Ground_Truths(layer, field_values, target)
    assert Relative_Gap(full_unroll_gradients, finite_difference_gradients) < 0.005


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
@pytest.mark.parametrize("phantom_depth", [1, 3])
def Test_Phantom_Gradient_Bias_Shrinks_As_Its_Depth_Grows(phantom_depth: int) -> None:
    """the mandatory audit column: phantom's measured disagreement with both ground truths, bounded and reported"""
    layer = Contractive_Layer(seed=71)
    field_values = np.asarray(Small_Field(2, seed=72).values, dtype=np.float64)
    target = np.random.default_rng(73).random((2, 8, 8, 8))
    parameters, finite_difference_gradients, full_unroll_gradients = Audit_Ground_Truths(layer, field_values, target)
    stack = FixedPoint(layer, backward="phantom", phantom_depth=phantom_depth)
    engine = TorchEngine()
    lifted_loss = Fixed_Point_Equilibrium_Loss(
        stack, engine.Lift_Constant(field_values), engine.Lift_Constant(target)
    )
    _, phantom_gradients = engine.Value_And_Gradients(parameters, lifted_loss)
    gap_to_finite_difference = Relative_Gap(phantom_gradients, finite_difference_gradients)
    gap_to_full_unroll = Relative_Gap(phantom_gradients, full_unroll_gradients)
    if phantom_depth == 1:
        # a real, bounded bias at the cheapest setting, not an exact match and not an unbounded one either
        assert 0.005 < gap_to_finite_difference < 0.08
        assert 0.005 < gap_to_full_unroll < 0.08
    else:
        # three reentries closes nearly all of the gap phantom's truncation opens at depth one
        assert gap_to_finite_difference < 0.005
        assert gap_to_full_unroll < 0.005
