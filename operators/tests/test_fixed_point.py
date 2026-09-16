"""the weight-tied and fixed-point rungs of the deep-equilibrium ladder"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import ContractionBudget, FixedPoint, WeightTied
from operators.compositions.activation import POINTWISE_ACTIVATIONS
from operators.compositions.contraction import STEM_NAMES, Normalized_Kernel_Lifted, Normalized_Local_Linear_Lifted
from operators.compositions.fixed_point import (
    Anderson_Gram,
    Anderson_Mixing_Weights,
    Applied_Once,
    Finite_Difference_Jacobian_Vector_Product,
    Hinge_Excess,
    Host_Inner_Product,
    JacobianPenalty,
    Jacobian_Probe_Estimate,
    Single_Layer_Parameter_Values,
    Sliced_Lifted,
)
from operators.encoders import PointwiseLift
from operators.framework import Domain, GridFunction, Layer, UniformGridQuadrature
from operators.kernels import SpectralKernel
from operators.substrate import (
    ACCELERATOR_DEVICE_NAME,
    Accelerator_Is_Available,
    Adam_Step,
    Detached,
    Fresh_Adam_State,
    NumpyEngine,
    ParameterSet,
    Torch_Is_Available,
    TorchEngine,
    Vector_Jacobian_Product,
)

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
    # a zero bias would leave the origin as the map's only fixed point, pinning most weights' true gradient at zero
    generator = np.random.default_rng(seed + 2)
    local_linear.parameter_values["lift_biases"] = generator.normal(size=channels) * 0.1
    return Layer(kernel=kernel, local_linear=local_linear)


def Separable_Layer(seed: int, channels: int = 2, scale: float = 0.05) -> Layer[GridFunction]:
    """a kernel-plus-local-linear layer built with the flagship's own separable mixing, the ladder's real form"""
    kernel = SpectralKernel(
        kept_modes=(1, 1, 1), output_channels=channels, input_channels=channels, seed=seed, mode_mixing="separable"
    )
    kernel.Hermitian_Symmetrize()
    kernel = Scaled(kernel, scale)
    local_linear = Scaled(PointwiseLift(hidden_channels=channels, input_channels=channels, seed=seed + 1), scale)
    generator = np.random.default_rng(seed + 2)
    local_linear.parameter_values["lift_biases"] = generator.normal(size=channels) * 0.1
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


def Test_The_Implicit_Rule_Applies_Through_The_Numpy_Path() -> None:
    """the declared backward is never reached off the foreign engine, so apply needs nothing but the forward"""
    layer = Contractive_Layer(seed=23)
    stack = FixedPoint(layer, backward="implicit")
    field = Small_Field(2, seed=24)
    produced = stack.Apply(field)
    assert np.all(np.isfinite(np.asarray(produced.values)))
    assert stack.last_solve is not None
    assert stack.last_solve.cap_was_hit is False


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_Forward_Agrees_With_Apply_On_The_Implicit_Rule_Across_Engines() -> None:
    """the equilibrium the declared backward's forward returns matches the numpy solve exactly, not approximately"""
    layer = Contractive_Layer(seed=23)
    stack = FixedPoint(layer, backward="implicit")
    field = Small_Field(2, seed=24)
    through_apply = np.asarray(stack.Apply(field).values, dtype=np.float64)
    engine = TorchEngine()
    field_values = engine.Lift_Constant(np.asarray(field.values, dtype=np.float64))
    lifted = engine.Lift(stack.Parameter_Values(), requires_gradient=False)
    through_engine = np.asarray(stack.Forward(lifted, field_values).detach().cpu().numpy(), dtype=np.float64)
    assert np.allclose(through_apply, through_engine, atol=1e-10)


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
    unrolled = WeightTied(layer, depth=solved.last_solve.iterations_taken + 10, input_injection=True)
    produced_unrolled = np.asarray(unrolled.Apply(field).values, dtype=np.float64)
    assert np.allclose(produced, produced_unrolled, atol=1e-2)


def Test_The_Lifted_Forward_Records_The_Solve_The_Health_Floor_Is_Read_From() -> None:
    layer = Contractive_Layer(seed=11)
    composition = FixedPoint(layer, backward="phantom")
    values = np.random.default_rng(11).normal(size=(2, 8, 8, 8))
    assert composition.last_solve is None
    composition.Forward(composition.Parameter_Values(), values)
    # training only ever runs the lifted path, so the convergence record must come from it too
    assert composition.last_solve is not None
    assert composition.last_solve.iterations_taken >= 1
    assert "last_iterations_taken" in composition.Inspect()


@pytest.mark.skipif(not Accelerator_Is_Available(), reason="no accelerator to hold the iterate on")
@pytest.mark.parametrize("backward", ["phantom", "jacobian_free", "implicit"])
def Test_Every_Backward_Rule_Solves_And_Differentiates_With_The_Iterate_On_The_Accelerator(backward: Any) -> None:
    """the solver's host-side checks must read an iterate that lives on the card without ever moving it there"""
    layer = Contractive_Layer(seed=21)
    composition = FixedPoint(layer, backward=backward)
    field_values = np.asarray(Small_Field(2, seed=22).values, dtype=np.float64)
    target = np.random.default_rng(23).random((2, 8, 8, 8))
    parameters = ParameterSet(values={name: value.copy() for name, value in composition.Parameter_Values().items()})
    engine = TorchEngine(device_name=ACCELERATOR_DEVICE_NAME, working_precision="single")
    lifted_field = engine.Lift_Constant(field_values)
    lifted_target = engine.Lift_Constant(target)

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = composition.Forward(lifted, lifted_field) - lifted_target
        return (difference * difference).sum()

    value, gradients = engine.Value_And_Gradients(parameters, Loss)
    assert np.isfinite(value)
    assert composition.last_solve is not None
    assert composition.last_solve.iterations_taken >= 1
    for name, gradient in gradients.items():
        assert np.all(np.isfinite(gradient)), name


def Test_The_Equilibrium_Depends_On_The_Input_Through_The_Injection() -> None:
    """a fixed point of the layer alone would forget its start; with the input injected it must move with the input"""
    layer = Contractive_Layer(seed=41)
    composition = FixedPoint(layer)
    first = np.asarray(Small_Field(2, seed=42).values, dtype=np.float64)
    second = np.asarray(Small_Field(2, seed=43).values, dtype=np.float64)
    lifted = composition.Parameter_Values()
    first_equilibrium = np.asarray(composition.Forward(lifted, first), dtype=np.float64)
    second_equilibrium = np.asarray(composition.Forward(lifted, second), dtype=np.float64)
    assert composition.last_solve is not None and not composition.last_solve.cap_was_hit
    relative_gap = float(np.linalg.norm(first_equilibrium - second_equilibrium) / np.linalg.norm(first_equilibrium))
    assert relative_gap > 1e-3


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
@pytest.mark.parametrize("backward", ["phantom", "implicit"])
def Test_The_Gradient_Reaches_The_Input_Through_The_Fixed_Point(backward: Any) -> None:
    """the parts upstream of a fixed point can only train if its output moves with its input on the tape"""
    layer = Contractive_Layer(seed=44)
    composition = FixedPoint(layer, backward=backward)
    engine = TorchEngine()
    lifted = {name: engine.Lift_Constant(value) for name, value in composition.Parameter_Values().items()}
    field_values = np.asarray(Small_Field(2, seed=45).values, dtype=np.float64)
    cotangent = engine.Lift_Constant(np.ones_like(field_values))

    def Through_The_Fixed_Point(input_values: Any) -> Any:
        """the fixed point as a function of its input alone, every parameter held"""
        return composition.Forward(lifted, input_values)

    input_gradient = Vector_Jacobian_Product(Through_The_Fixed_Point, engine.Lift_Constant(field_values), cotangent)
    host_gradient = np.asarray(input_gradient.detach().cpu().numpy(), dtype=np.float64)
    assert np.all(np.isfinite(host_gradient))
    assert float(np.abs(host_gradient).max()) > 1e-8


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


# the substrate primitives this stream added: detached, and the vector-jacobian product the adjoint needs


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


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_Vector_Jacobian_Product_Matches_A_Known_Jacobian_On_Both_Engines() -> None:
    """a linear map's jacobian is the matrix itself, so the pulled-back cotangent has a closed form to check"""
    generator = np.random.default_rng(41)
    matrix = generator.normal(size=(4, 3))
    point = generator.normal(size=(3,))
    cotangent = generator.normal(size=(4,))
    expected = matrix.T @ cotangent

    reference_result = Vector_Jacobian_Product(lambda value: matrix @ value, point, cotangent)
    assert np.allclose(reference_result, expected, atol=1e-8)

    engine = TorchEngine()
    lifted_matrix = engine.Lift_Constant(matrix)

    def Engine_Function(value: Any) -> Any:
        return lifted_matrix @ value

    engine_point = engine.Lift_Constant(point)
    engine_cotangent = engine.Lift_Constant(cotangent)
    engine_result = Vector_Jacobian_Product(Engine_Function, engine_point, engine_cotangent)
    engine_result_values = np.asarray(engine_result.detach().cpu().numpy(), dtype=np.float64)
    assert np.allclose(engine_result_values, expected, atol=1e-8)


def Test_Anderson_Mixing_Weights_Declines_A_Near_Parallel_History() -> None:
    """a residual history whose differences are nearly collinear returns none rather than an unstable mix"""
    near_parallel_history = [
        np.asarray([2.0, 0.0, 0.0]),
        np.asarray([2.0000001, 0.0, 0.0]),
        np.asarray([1.0, 0.0, 0.0]),
    ]
    weights = Anderson_Mixing_Weights(near_parallel_history, regularization=1e-4, condition_ceiling=1e6)
    assert weights is None


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_The_Anderson_Gram_Agrees_Across_Engines_So_Only_Scalars_Cross_To_The_Host() -> None:
    """the gram matrix and right-hand side from engine inner products must equal the host's own to round-off"""
    generator = np.random.default_rng(31)
    history = [generator.normal(size=(2, 4, 4, 4)) for _ in range(4)]
    host_gram, host_right_hand_side = Anderson_Gram(history)
    engine = TorchEngine()
    lifted_history = [engine.Lift_Constant(residual) for residual in history]
    foreign_gram, foreign_right_hand_side = Anderson_Gram(lifted_history)
    assert np.allclose(foreign_gram, host_gram, rtol=1e-10, atol=1e-12)
    assert np.allclose(foreign_right_hand_side, host_right_hand_side, rtol=1e-10, atol=1e-12)
    host_weights = Anderson_Mixing_Weights(history, regularization=1e-4, condition_ceiling=1e8)
    foreign_weights = Anderson_Mixing_Weights(lifted_history, regularization=1e-4, condition_ceiling=1e8)
    assert host_weights is not None and foreign_weights is not None
    assert np.allclose(foreign_weights, host_weights, rtol=1e-8, atol=1e-10)


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


# the mandatory 8-cubed gradient audit -- phantom and implicit against finite differences and the full unroll,
# all four grounded on the same contractive layer as the health-floor tests above


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
    tied = WeightTied(layer, depth=depth, input_injection=True)
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


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_Implicit_Gradient_Closes_The_Audit_Tighter_Than_Phantom_Against_Both_Ground_Truths() -> None:
    """the mandatory audit's fourth column: the exact adjoint, which the canon expects to beat phantom's bias"""
    layer = Contractive_Layer(seed=71)
    field_values = np.asarray(Small_Field(2, seed=72).values, dtype=np.float64)
    target = np.random.default_rng(73).random((2, 8, 8, 8))
    parameters, finite_difference_gradients, full_unroll_gradients = Audit_Ground_Truths(layer, field_values, target)
    stack = FixedPoint(layer, backward="implicit")
    engine = TorchEngine()
    lifted_loss = Fixed_Point_Equilibrium_Loss(
        stack, engine.Lift_Constant(field_values), engine.Lift_Constant(target)
    )
    _, implicit_gradients = engine.Value_And_Gradients(parameters, lifted_loss)
    gap_to_finite_difference = Relative_Gap(implicit_gradients, finite_difference_gradients)
    gap_to_full_unroll = Relative_Gap(implicit_gradients, full_unroll_gradients)
    # the exact adjoint sits at the two ground truths' own mutual distance, not at phantom's percent-scale bias
    assert gap_to_finite_difference < 0.0005
    assert gap_to_full_unroll < 0.0005
    assert gap_to_finite_difference < Relative_Gap(full_unroll_gradients, finite_difference_gradients) * 10.0


# the ladder's second stability rung: a hutchinson jacobian-gain estimate by a finite-difference jvp, penalized
# by a hinge in the training loss, grounded on the same contractive and divergent toy layers as the rungs above


def Test_Hinge_Excess_Is_Zero_At_Or_Below_The_Hinge_And_Linear_Above_It() -> None:
    """the exact shape of the penalty's own floor, checked directly against the arithmetic it stands for"""
    assert float(Hinge_Excess(np.asarray(0.5), 1.0)) == 0.0
    assert float(Hinge_Excess(np.asarray(2.0), 1.0)) == 1.0


def Test_Jacobian_Probe_Estimate_Is_The_Mean_Squared_Directional_Output_Over_The_States_Own_Size() -> None:
    """the reduction the estimate performs, checked against the same finite-difference jv computed independently"""
    layer = Contractive_Layer(seed=95, channels=2)
    parameter_values = Single_Layer_Parameter_Values(layer)
    kernel_lifted = Sliced_Lifted(parameter_values, "kernel.")
    local_linear_lifted = Sliced_Lifted(parameter_values, "local_linear.")
    state = np.asarray(Small_Field(2, seed=96).values, dtype=np.float64)
    probe = np.random.default_rng(97).normal(size=state.shape)
    estimate = Jacobian_Probe_Estimate(
        layer, kernel_lifted, local_linear_lifted, state, state, probe, POINTWISE_ACTIVATIONS, relative_step=1e-2
    )
    directional = Finite_Difference_Jacobian_Vector_Product(
        layer, kernel_lifted, local_linear_lifted, state, state, probe, POINTWISE_ACTIVATIONS, relative_step=1e-2
    )
    expected = float(np.sum(np.asarray(directional) ** 2)) / float(state.size)
    assert abs(float(estimate) - expected) < 1e-10


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_The_Finite_Difference_Jacobian_Vector_Product_Satisfies_The_Adjoint_Identity() -> None:
    """a forward-difference jv at a small step and the exact vjp must agree on the one number both sides can form"""
    layer = Contractive_Layer(seed=61)
    engine = TorchEngine()
    parameter_values = Single_Layer_Parameter_Values(layer)
    lifted = {name: engine.Lift_Constant(value) for name, value in parameter_values.items()}
    kernel_lifted = Sliced_Lifted(lifted, "kernel.")
    local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
    state = engine.Lift_Constant(np.asarray(Small_Field(2, seed=62).values, dtype=np.float64))
    injection = state
    probe = engine.Lift_Constant(np.random.default_rng(63).normal(size=(2, 8, 8, 8)))
    cotangent = engine.Lift_Constant(np.random.default_rng(64).normal(size=(2, 8, 8, 8)))

    directional = Finite_Difference_Jacobian_Vector_Product(
        layer, kernel_lifted, local_linear_lifted, state, injection, probe, POINTWISE_ACTIVATIONS, relative_step=1e-5
    )
    left_hand_side = Host_Inner_Product(cotangent, directional)

    def Applied_At_The_State(value: Any) -> Any:
        return Applied_Once(layer, kernel_lifted, local_linear_lifted, value, injection, POINTWISE_ACTIVATIONS)

    pulled_back = Vector_Jacobian_Product(Applied_At_The_State, state, cotangent)
    right_hand_side = Host_Inner_Product(pulled_back, probe)
    assert abs(left_hand_side - right_hand_side) < 1e-3 * (abs(right_hand_side) + 1.0)


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_The_Jacobian_Penaltys_Gradient_Reaches_Both_Weight_Groups_And_Matches_Finite_Differences() -> None:
    """the hinge's own gradient, taken through the probe estimate, must move both the kernel and the local matrix"""
    layer = Contractive_Layer(seed=81, channels=2)
    state_values = np.asarray(Small_Field(2, seed=82).values, dtype=np.float64)
    injection_values = np.asarray(Small_Field(2, seed=83).values, dtype=np.float64)
    probe_values = np.random.default_rng(84).normal(size=(2, 8, 8, 8))
    # a hinge of zero keeps the excess robustly positive, away from the hinge's own kink, for a stable comparison
    penalty = JacobianPenalty(weight=1.0, hinge=0.0, relative_step=1e-2, probe_count=1)
    parameters = ParameterSet(values={name: value.copy() for name, value in Single_Layer_Parameter_Values(layer).items()})

    def Loss(lifted: dict[str, Any], state: Any, injection: Any, probe: Any) -> Any:
        kernel_lifted = Sliced_Lifted(lifted, "kernel.")
        local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
        return penalty.Loss(layer, kernel_lifted, local_linear_lifted, state, injection, (probe,))

    engine = TorchEngine()
    lifted_state = engine.Lift_Constant(state_values)
    lifted_injection = engine.Lift_Constant(injection_values)
    lifted_probe = engine.Lift_Constant(probe_values)

    def Torch_Loss(lifted: dict[str, Any]) -> Any:
        return Loss(lifted, lifted_state, lifted_injection, lifted_probe)

    def Reference_Loss(lifted: dict[str, Any]) -> Any:
        return Loss(lifted, state_values, injection_values, probe_values)

    value, gradients = engine.Value_And_Gradients(parameters, Torch_Loss)
    reference = NumpyEngine()
    reference_value = reference.Evaluate(parameters, Reference_Loss)
    reference_gradients = reference.Gradients(parameters, Reference_Loss)

    assert abs(value - reference_value) < 1e-6
    kernel_names = [name for name in gradients if name.startswith("kernel.")]
    local_linear_names = [name for name in gradients if name.startswith("local_linear.")]
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-3, atol=1e-6), name
    assert max(float(np.abs(gradients[name]).max()) for name in kernel_names) > 1e-8
    assert max(float(np.abs(gradients[name]).max()) for name in local_linear_names) > 1e-8


def Test_The_Jacobian_Penalty_Refuses_A_Probe_Count_Mismatch() -> None:
    """the configured probe count is not a suggestion; a mismatched batch of probes is refused rather than truncated"""
    layer = Contractive_Layer(seed=85, channels=2)
    penalty = JacobianPenalty(probe_count=2)
    kernel_lifted = Sliced_Lifted(Single_Layer_Parameter_Values(layer), "kernel.")
    local_linear_lifted = Sliced_Lifted(Single_Layer_Parameter_Values(layer), "local_linear.")
    state = np.asarray(Small_Field(2, seed=86).values, dtype=np.float64)
    probe = np.random.default_rng(87).normal(size=(2, 8, 8, 8))
    with pytest.raises(ValueError):
        penalty.Loss(layer, kernel_lifted, local_linear_lifted, state, state, (probe,))


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_The_Jacobian_Penalty_Alone_Drives_A_Divergent_Toy_Layer_Back_To_Contractive() -> None:
    """thirty adam steps against nothing but the hinge turn a layer the solver cannot solve into one it can"""
    layer = Divergent_Layer(seed=91, channels=2)
    for name in layer.kernel.parameter_values:
        # a gentler-than-Divergent_Layer scale, chosen so the penalty alone has room to win within a short budget
        layer.kernel.parameter_values[name] = layer.kernel.parameter_values[name] / 50.0 * 3.0
    layer.local_linear.parameter_values["lift_weights"] = layer.local_linear.parameter_values["lift_weights"] / 50.0 * 3.0
    field = Small_Field(2, seed=92)

    baseline = FixedPoint(layer, iteration_cap=32)
    baseline.Apply(field)
    assert baseline.last_solve is not None
    assert baseline.last_solve.cap_was_hit is True

    penalty = JacobianPenalty(weight=2.0, hinge=0.1, relative_step=1e-2, probe_count=2)
    parameters = ParameterSet(values={name: value.copy() for name, value in Single_Layer_Parameter_Values(layer).items()})
    engine = TorchEngine()
    state_values = np.asarray(field.values, dtype=np.float64)
    generator = np.random.default_rng(93)
    adam_state = Fresh_Adam_State(parameters)
    for _ in range(80):
        lifted_state = engine.Lift_Constant(state_values)
        probes = tuple(engine.Lift_Constant(generator.normal(size=state_values.shape)) for _ in range(2))

        def Step_Loss(lifted: dict[str, Any], lifted_state: Any = lifted_state, probes: Any = probes) -> Any:
            kernel_lifted = Sliced_Lifted(lifted, "kernel.")
            local_linear_lifted = Sliced_Lifted(lifted, "local_linear.")
            return penalty.Loss(layer, kernel_lifted, local_linear_lifted, lifted_state, lifted_state, probes)

        _, gradients = engine.Value_And_Gradients(parameters, Step_Loss)
        parameters = Adam_Step(parameters, gradients, adam_state, learning_rate=0.1)

    for bare_name, value in parameters.values.items():
        if bare_name.startswith("kernel."):
            layer.kernel.parameter_values[bare_name[len("kernel."):]] = value
        elif bare_name.startswith("local_linear."):
            layer.local_linear.parameter_values[bare_name[len("local_linear."):]] = value

    after = FixedPoint(layer, iteration_cap=32)
    after.Apply(field)
    assert after.last_solve is not None
    assert after.last_solve.cap_was_hit is False


# the ladder's third stability rung: a differentiable per-forward normalization toward the budget rung one clips to


def Test_A_Hundred_Times_Scaled_Layer_Normalizes_Into_The_Budget() -> None:
    """the differentiable per-forward rescale brings every factor's own spectral norm under its own share, exactly"""
    layer = Separable_Layer(seed=101, channels=2, scale=100.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    parameter_values = Single_Layer_Parameter_Values(layer)
    kernel_lifted = Sliced_Lifted(parameter_values, "kernel.")
    local_linear_lifted = Sliced_Lifted(parameter_values, "local_linear.")
    normalized_kernel = Normalized_Kernel_Lifted(kernel_lifted, budget)
    normalized_local = Normalized_Local_Linear_Lifted(local_linear_lifted, budget)
    local_norm = float(np.linalg.svd(normalized_local["lift_weights"], compute_uv=False)[0])
    assert local_norm <= budget.Local_Bound() + 1e-8
    for stem in STEM_NAMES:
        complex_stem = normalized_kernel[f"{stem}_real"] + 1j * normalized_kernel[f"{stem}_imaginary"]
        stem_norm = float(np.max(np.linalg.svd(complex_stem, compute_uv=False)[..., 0]))
        assert stem_norm <= budget.Mode_Bound(len(STEM_NAMES)) + 1e-8


def Test_The_Budgeted_Forward_And_Apply_Agree_On_Weight_Tied() -> None:
    """the lifted path and the numpy wrapper around it read the same numbers once normalization is engaged"""
    layer = Separable_Layer(seed=102, channels=2, scale=20.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    stack = WeightTied(layer, depth=4, budget=budget)
    field = Small_Field(2, seed=103)
    through_apply = np.asarray(stack.Apply(field).values, dtype=np.float64)
    through_forward = np.asarray(
        stack.Forward(stack.Parameter_Values(), np.asarray(field.values, dtype=np.float64)), dtype=np.float64
    )
    assert np.allclose(through_apply, through_forward, atol=1e-10)


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_Gradients_Reach_Both_Weight_Groups_Through_The_Normalized_Forward() -> None:
    """the rescale is differentiable, so a tape running through it still reaches the kernel and the local matrix"""
    layer = Separable_Layer(seed=104, channels=2, scale=20.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    stack = WeightTied(layer, depth=3, budget=budget)
    field_values = np.asarray(Small_Field(2, seed=105).values, dtype=np.float64)
    target = np.random.default_rng(106).random((2, 8, 8, 8))
    parameters = ParameterSet(values={name: value.copy() for name, value in stack.Parameter_Values().items()})
    engine = TorchEngine()
    value, gradients = engine.Value_And_Gradients(
        parameters, Weight_Tied_Loss(stack, engine.Lift_Constant(field_values), engine.Lift_Constant(target))
    )
    reference = NumpyEngine()
    reference_loss = Weight_Tied_Loss(stack, field_values, target)
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-6
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(reference_gradients)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-3, atol=1e-5), name
        assert float(np.abs(gradient).max()) > 1e-8, name


def Test_The_Injected_Unroll_Matches_The_Fixed_Point_Under_The_Budget() -> None:
    """the same budget applied to both rungs keeps the unrolled and the solved equilibria in agreement"""
    layer = Separable_Layer(seed=107, channels=2, scale=20.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    field = Small_Field(2, seed=108)
    solved = FixedPoint(layer, budget=budget)
    produced = np.asarray(solved.Apply(field).values, dtype=np.float64)
    assert solved.last_solve is not None
    assert solved.last_solve.cap_was_hit is False
    unrolled = WeightTied(layer, depth=solved.last_solve.iterations_taken + 10, input_injection=True, budget=budget)
    produced_unrolled = np.asarray(unrolled.Apply(field).values, dtype=np.float64)
    assert np.allclose(produced, produced_unrolled, atol=1e-2)


def Budgeted_Audit_Ground_Truths(
    layer: Layer[GridFunction], budget: ContractionBudget, field_values: NDArray[np.float64], target: NDArray[np.float64]
) -> tuple[ParameterSet, dict[str, NDArray[np.float64]], dict[str, NDArray[np.float64]]]:
    """the budgeted audit's parameters beside its two ground truths: finite differences, and the depth-matched unroll"""
    probe = FixedPoint(layer, budget=budget)
    parameters = ParameterSet(values={name: value.copy() for name, value in probe.Parameter_Values().items()})
    reference_loss = Fixed_Point_Equilibrium_Loss(probe, field_values, target)
    finite_difference_gradients = NumpyEngine().Gradients(parameters, reference_loss)
    kernel_lifted = Normalized_Kernel_Lifted(Sliced_Lifted(probe.Parameter_Values(), "kernel."), budget)
    local_linear_lifted = Normalized_Local_Linear_Lifted(Sliced_Lifted(probe.Parameter_Values(), "local_linear."), budget)
    depth = probe.Solved(kernel_lifted, local_linear_lifted, field_values).iterations_taken
    tied = WeightTied(layer, depth=depth, input_injection=True, budget=budget)
    engine = TorchEngine()
    _, full_unroll_gradients = engine.Value_And_Gradients(
        parameters, Weight_Tied_Loss(tied, engine.Lift_Constant(field_values), engine.Lift_Constant(target))
    )
    return parameters, finite_difference_gradients, full_unroll_gradients


@pytest.mark.skipif(not Torch_Is_Available(), reason="the foreign engine is not installed yet")
def Test_The_Mandatory_Audits_Phantom_Three_And_Implicit_Columns_Hold_Under_The_Budget() -> None:
    """the audit's tightest two columns still agree with both ground truths once the forward carries a budget"""
    layer = Separable_Layer(seed=111, channels=2, scale=20.0)
    budget = ContractionBudget(target_lipschitz=0.9, local_share=0.2)
    field_values = np.asarray(Small_Field(2, seed=112).values, dtype=np.float64)
    target = np.random.default_rng(113).random((2, 8, 8, 8))
    parameters, finite_difference_gradients, full_unroll_gradients = Budgeted_Audit_Ground_Truths(
        layer, budget, field_values, target
    )
    engine = TorchEngine()

    phantom_three = FixedPoint(layer, backward="phantom", phantom_depth=3, budget=budget)
    lifted_phantom_loss = Fixed_Point_Equilibrium_Loss(
        phantom_three, engine.Lift_Constant(field_values), engine.Lift_Constant(target)
    )
    _, phantom_gradients = engine.Value_And_Gradients(parameters, lifted_phantom_loss)
    assert Relative_Gap(phantom_gradients, finite_difference_gradients) < 0.02
    assert Relative_Gap(phantom_gradients, full_unroll_gradients) < 0.02

    implicit = FixedPoint(layer, backward="implicit", budget=budget)
    lifted_implicit_loss = Fixed_Point_Equilibrium_Loss(
        implicit, engine.Lift_Constant(field_values), engine.Lift_Constant(target)
    )
    _, implicit_gradients = engine.Value_And_Gradients(parameters, lifted_implicit_loss)
    assert Relative_Gap(implicit_gradients, finite_difference_gradients) < 0.005
    assert Relative_Gap(implicit_gradients, full_unroll_gradients) < 0.005
