"""the codomain-attention kernel, its local linear term and its layer norm, against both engines"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import ExplicitStack
from operators.framework import (
    Dense_Reference_Integral,
    Domain,
    GridFunction,
    GridSpec,
    Layer,
    LiftedKernel,
    LocalLinearMap,
    UniformGridQuadrature,
)
from operators.inspection.plots import Render_Inspection_Suite
from operators.kernels.codomain_attention import (
    CodomainAttentionKernel,
    FunctionSpaceLayerNorm,
    Token_Count,
    TokenSharedLocalLinear,
)
from operators.substrate import NumpyEngine, ParameterSet, Torch_Is_Available, TorchEngine
from operators.training import FixedBatches, Train, Training_Engine, TrainingBatch

CUBE = Domain(lattice=np.eye(3) * 2.0)


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


def Test_Token_Count_Refuses_What_Does_Not_Divide_Evenly() -> None:
    """the helper both packages rely on to unflatten a channel axis into tokens"""
    assert Token_Count(6, 2) == 3
    with pytest.raises(ValueError):
        Token_Count(5, 2)


def Test_Parameter_Count_Is_Independent_Of_Token_Count() -> None:
    """the same kernel answers three and five tokens with identical parameters and no error"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), head_count=1, seed=1)
    parameter_names_before = set(kernel.parameter_values)
    parameter_arrays_before = {name: value.copy() for name, value in kernel.parameter_values.items()}
    generator = np.random.default_rng(2)
    grid_shape = (4, 4, 4)
    three_tokens = generator.random((3 * 2, *grid_shape))
    five_tokens = generator.random((5 * 2, *grid_shape))
    three_output = np.asarray(kernel.Forward(kernel.parameter_values, three_tokens, grid_shape))
    five_output = np.asarray(kernel.Forward(kernel.parameter_values, five_tokens, grid_shape))
    assert three_output.shape == (3 * 2, *grid_shape)
    assert five_output.shape == (5 * 2, *grid_shape)
    assert set(kernel.parameter_values) == parameter_names_before
    for name, value in kernel.parameter_values.items():
        assert np.array_equal(value, parameter_arrays_before[name])


def Test_Parameter_Count_Formula_Covers_Full_And_Separable_Mixing() -> None:
    """the built kernel's own count matches what the pricing function predicts, for both mixing modes"""
    full_kernel = CodomainAttentionKernel(
        hidden_channels=3, kept_modes=(1, 1, 2), head_count=1, seed=130, mode_mixing="full"
    )
    separable_kernel = CodomainAttentionKernel(
        hidden_channels=3, kept_modes=(1, 1, 2), head_count=1, seed=131, mode_mixing="separable"
    )
    full_priced = CodomainAttentionKernel.Parameter_Count_For(
        hidden_channels=3, kept_modes=(1, 1, 2), head_count=1, mode_mixing="full"
    )
    separable_priced = CodomainAttentionKernel.Parameter_Count_For(
        hidden_channels=3, kept_modes=(1, 1, 2), head_count=1, mode_mixing="separable"
    )
    assert full_kernel.Parameter_Count() == full_priced
    assert separable_kernel.Parameter_Count() == separable_priced
    assert separable_priced < full_priced

    generator = np.random.default_rng(132)
    # the third axis keeps modes minus two to plus two, so it needs at least five points
    grid_shape = (4, 4, 5)
    values = generator.random((2 * 3, *grid_shape))
    produced = np.asarray(separable_kernel.Forward(separable_kernel.parameter_values, values, grid_shape))
    assert produced.shape == (2 * 3, *grid_shape)
    assert np.all(np.isfinite(produced))


def Test_Permuting_Tokens_Permutes_The_Output_The_Same_Way() -> None:
    """attention over tokens is equivariant to their order, the encodings break the symmetry elsewhere"""
    kernel = CodomainAttentionKernel(hidden_channels=3, kept_modes=(1, 1, 2), head_count=1, seed=10)
    generator = np.random.default_rng(11)
    token_count = 4
    grid_shape = (4, 4, 6)
    values = generator.random((token_count * 3, *grid_shape))
    permutation = (2, 0, 3, 1)
    permuted_values = np.concatenate([values[token_index * 3:(token_index + 1) * 3] for token_index in permutation])
    output = np.asarray(kernel.Forward(kernel.parameter_values, values, grid_shape))
    permuted_output = np.asarray(kernel.Forward(kernel.parameter_values, permuted_values, grid_shape))
    expected = np.concatenate([output[token_index * 3:(token_index + 1) * 3] for token_index in permutation])
    assert np.allclose(permuted_output, expected, atol=1e-9)


def Test_Attention_Rows_Sum_To_One_And_Temperature_Sets_The_Concentration() -> None:
    """a sanity check on the inner-product scores and the softmax that turns them into weights"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), head_count=1, seed=20)
    generator = np.random.default_rng(21)
    token_count = 3
    grid_shape = (4, 4, 4)
    grid_point_count = grid_shape[0] * grid_shape[1] * grid_shape[2]
    values = generator.random((token_count * 2, *grid_shape))
    query_heads, key_heads, _ = kernel.Query_Key_Value(kernel.parameter_values, values, token_count)
    weights = np.asarray(kernel.Attention_Weights(kernel.parameter_values, query_heads, key_heads, grid_point_count))
    assert weights.shape == (1, token_count, token_count)
    assert np.allclose(weights.sum(axis=-1), 1.0, atol=1e-10)

    kernel.parameter_values["temperature"] = np.zeros(1)
    uniform_weights = np.asarray(
        kernel.Attention_Weights(kernel.parameter_values, query_heads, key_heads, grid_point_count)
    )
    assert np.allclose(uniform_weights, 1.0 / token_count, atol=1e-10)

    # a hand-built pair at a controlled scale, independent of the kernel's own small init, isolates the softmax alone
    forced_query_heads = np.zeros_like(np.asarray(query_heads))
    forced_query_heads[0] = 1.0
    # every other key zeroed and one key set to the query itself makes that pairing the unambiguous maximum
    forced_key_heads = np.zeros_like(np.asarray(key_heads))
    forced_key_heads[1] = forced_query_heads[0]
    kernel.parameter_values["temperature"] = np.asarray([50.0])
    sharp_weights = np.asarray(
        kernel.Attention_Weights(kernel.parameter_values, forced_query_heads, forced_key_heads, grid_point_count)
    )
    assert sharp_weights[0, 0, 1] > 0.99


def Test_Softmax_Is_Invariant_To_A_Large_Additive_Constant_And_Stays_Finite() -> None:
    """softmax is shift-invariant, so a huge additive constant on every score changes nothing but stays finite"""
    generator = np.random.default_rng(26)
    logits = generator.normal(0.0, 1.0, size=(2, 3, 3))
    baseline = np.asarray(CodomainAttentionKernel.Softmax_Over_Last_Axis(logits))
    shifted_logits = logits + 1e4
    shifted = np.asarray(CodomainAttentionKernel.Softmax_Over_Last_Axis(shifted_logits))
    assert np.all(np.isfinite(shifted))
    assert np.allclose(shifted, baseline, atol=1e-9)

    if Torch_Is_Available():
        engine = TorchEngine()
        torch_shifted = CodomainAttentionKernel.Softmax_Over_Last_Axis(engine.Lift_Constant(shifted_logits))
        torch_array = np.asarray(torch_shifted.detach().cpu().numpy(), dtype=np.float64)
        assert np.all(np.isfinite(torch_array))
        assert np.allclose(torch_array, baseline, atol=1e-6)

        # a common level past single precision's own exp overflow point, riding a modest and meaningful spread
        single_engine = TorchEngine(working_precision="single")
        leveled_logits = np.asarray([[1.0e4, 1.0e4 + 1.0, 1.0e4 - 1.0]])
        single_output = CodomainAttentionKernel.Softmax_Over_Last_Axis(single_engine.Lift_Constant(leveled_logits))
        single_array = np.asarray(single_output.detach().cpu().numpy(), dtype=np.float64)
        assert np.all(np.isfinite(single_array))

        # one spiked entry is a large spread inside the row, which only a maximum shift can defuse
        spiked_logits = np.asarray([[0.0, 1.0e4, 0.0]])
        spiked_output = CodomainAttentionKernel.Softmax_Over_Last_Axis(single_engine.Lift_Constant(spiked_logits))
        spiked_array = np.asarray(spiked_output.detach().cpu().numpy(), dtype=np.float64)
        assert np.all(np.isfinite(spiked_array))
        assert np.allclose(spiked_array, [[0.0, 1.0, 0.0]], atol=1e-6)
        assert np.allclose(single_array, [[0.24472847, 0.66524096, 0.09003057]], atol=1e-4)


def Test_Integrate_And_Forward_Agree_On_Both_Engines() -> None:
    """integrate on a grid function equals forward on its values, on the reference engine and the foreign one"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), head_count=1, seed=30)
    generator = np.random.default_rng(31)
    token_count = 2
    grid_shape = (4, 4, 4)
    field = GridFunction(
        values=generator.random((token_count * 2, *grid_shape)),
        channel_labels=tuple(f"channel_{channel_index}" for channel_index in range(token_count * 2)),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    integrated = kernel.Integrate(field, GridSpec(grid_shape))
    produced = np.asarray(kernel.Forward(kernel.parameter_values, np.asarray(field.values), grid_shape))
    assert np.allclose(produced, np.asarray(integrated.values), atol=1e-10)

    if Torch_Is_Available():
        engine = TorchEngine()
        lifted = engine.Lift(kernel.parameter_values, requires_gradient=False)
        lifted_values = engine.Lift_Constant(np.asarray(field.values, dtype=np.float64))
        torch_produced = kernel.Forward(lifted, lifted_values, grid_shape)
        torch_array = np.asarray(torch_produced.detach().cpu().numpy(), dtype=np.float64)
        assert np.allclose(torch_array, produced, atol=1e-8)


def Codomain_Attention_Loss(
    kernel: CodomainAttentionKernel, input_values: Any, output_shape: tuple[int, int, int], target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the attention kernel's lifted forward and a fixed target"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = kernel.Forward(lifted, input_values, output_shape) - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradient_Reaches_Every_Parameter_Of_The_Attention_Kernel() -> None:
    """a tape severed anywhere in the norm, the four spectral blocks or the temperature shows as a zero gradient"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), head_count=1, seed=40)
    generator = np.random.default_rng(41)
    token_count = 2
    grid_shape = (4, 4, 4)
    input_values = generator.random((token_count * 2, *grid_shape))
    target = generator.random((token_count * 2, *grid_shape))
    parameters = ParameterSet(values={name: value.copy() for name, value in kernel.parameter_values.items()})
    engine = TorchEngine()
    gradients = Agreeing_Gradients(
        parameters,
        Codomain_Attention_Loss(kernel, engine.Lift_Constant(input_values), grid_shape, engine.Lift_Constant(target)),
        Codomain_Attention_Loss(kernel, input_values, grid_shape, target),
    )
    for prefix in ("norm.", "query.", "key.", "value.", "output."):
        prefixed = np.concatenate([gradients[name].reshape(-1) for name in gradients if name.startswith(prefix)])
        assert float(np.abs(prefixed).max()) > 1e-6, prefix
    assert float(np.abs(gradients["temperature"]).max()) > 1e-6


def Test_Resolution_Change_Matches_The_Spectral_Kernels_Own_Resampling() -> None:
    """a single token collapses attention to the identity, so resizing reduces to the output kernel alone"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), head_count=1, seed=50)
    kernel.output_kernel.Hermitian_Symmetrize()
    generator = np.random.default_rng(51)
    values = generator.random((2, 4, 4, 4))
    field = GridFunction(
        values=values,
        channel_labels=("channel_0", "channel_1"),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    normalized = kernel.pre_norm.Forward(kernel.pre_norm.parameter_values, values)
    attended = np.asarray(kernel.value_kernel.Forward(kernel.value_kernel.parameter_values, normalized, (4, 4, 4)))
    attended_field = GridFunction(attended, field.channel_labels, CUBE, field.quadrature)
    for requested_shape in ((4, 4, 4), (6, 6, 6), (3, 3, 3)):
        reference = Dense_Reference_Integral(
            kernel.output_kernel.Dense_Kernel_Function(8.0), attended_field, GridSpec(requested_shape)
        )
        produced = kernel.Integrate(field, GridSpec(requested_shape))
        assert np.asarray(produced.values).shape == (2, *requested_shape)
        assert np.allclose(np.asarray(produced.values), reference, atol=1e-9)


def Test_Token_Shared_Local_Linear_Two_Path_And_Gradient() -> None:
    """the shared weight and bias agree between the lifted forward and its own values, and train on both engines"""
    local_linear = TokenSharedLocalLinear(hidden_channels=2, seed=60)
    generator = np.random.default_rng(61)
    token_count = 3
    grid_shape = (4, 4, 4)
    values = generator.random((token_count * 2, *grid_shape))
    produced = np.asarray(local_linear.Forward(local_linear.parameter_values, values))
    assert produced.shape == values.shape
    if Torch_Is_Available():
        engine = TorchEngine()
        lifted = engine.Lift(local_linear.parameter_values, requires_gradient=False)
        lifted_values = engine.Lift_Constant(values)
        torch_produced = local_linear.Forward(lifted, lifted_values)
        torch_array = np.asarray(torch_produced.detach().cpu().numpy(), dtype=np.float64)
        assert np.allclose(torch_array, produced, atol=1e-8)

        target = generator.random(values.shape)
        parameters = ParameterSet(values={name: value.copy() for name, value in local_linear.parameter_values.items()})

        def Loss_Over(lifted_values_here: Any, lifted_target: Any) -> Callable[[dict[str, Any]], Any]:
            def Loss(lifted_parameters: dict[str, Any]) -> Any:
                difference = local_linear.Forward(lifted_parameters, lifted_values_here) - lifted_target
                return (difference * difference).sum()

            return Loss

        gradients = Agreeing_Gradients(
            parameters,
            Loss_Over(engine.Lift_Constant(values), engine.Lift_Constant(target)),
            Loss_Over(values, target),
        )
        assert float(np.abs(gradients["weights"]).max()) > 1e-6


def Test_Function_Space_Layer_Norm_Two_Path_And_Gradient() -> None:
    """each token standardized over its channels and grid, then trained on both engines"""
    norm = FunctionSpaceLayerNorm(hidden_channels=2)
    generator = np.random.default_rng(70)
    token_count = 3
    grid_shape = (4, 4, 4)
    values = generator.random((token_count * 2, *grid_shape)) * 5.0 + 1.0
    produced = np.asarray(norm.Forward(norm.parameter_values, values))
    assert produced.shape == values.shape
    unflattened = produced.reshape(token_count, 2, *grid_shape)
    # a zero-centered scale of one and a zero bias leave a genuine per-token standardization visible
    per_token_mean = unflattened.reshape(token_count, -1).mean(axis=-1)
    per_token_variance = unflattened.reshape(token_count, -1).var(axis=-1)
    assert np.allclose(per_token_mean, 0.0, atol=1e-8)
    assert np.allclose(per_token_variance, 1.0, atol=1e-3)

    if Torch_Is_Available():
        engine = TorchEngine()
        lifted = engine.Lift(norm.parameter_values, requires_gradient=False)
        lifted_values = engine.Lift_Constant(values)
        torch_produced = norm.Forward(lifted, lifted_values)
        torch_array = np.asarray(torch_produced.detach().cpu().numpy(), dtype=np.float64)
        assert np.allclose(torch_array, produced, atol=1e-6)

        target = generator.random(values.shape)
        parameters = ParameterSet(values={name: value.copy() for name, value in norm.parameter_values.items()})

        def Loss_Over(lifted_values_here: Any, lifted_target: Any) -> Callable[[dict[str, Any]], Any]:
            def Loss(lifted_parameters: dict[str, Any]) -> Any:
                difference = norm.Forward(lifted_parameters, lifted_values_here) - lifted_target
                return (difference * difference).sum()

            return Loss

        gradients = Agreeing_Gradients(
            parameters,
            Loss_Over(engine.Lift_Constant(values), engine.Lift_Constant(target)),
            Loss_Over(values, target),
        )
        assert float(np.abs(gradients["scale"]).max()) > 1e-6
        assert float(np.abs(gradients["bias"]).max()) > 1e-6


def Test_The_Attention_Kernel_And_Local_Linear_Satisfy_Their_Protocols() -> None:
    """pyright strict is the judge of structural conformance, this exercises the assignment and layer it checks"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), seed=80)
    lifted_kernel: LiftedKernel[GridFunction, GridFunction] = kernel
    local_linear: LocalLinearMap = TokenSharedLocalLinear(hidden_channels=2, seed=81)
    layer = Layer(kernel=lifted_kernel, local_linear=local_linear)
    assert layer.kernel is kernel


def Test_Layer_In_An_Explicit_Stack_Runs_On_Both_Engines_And_Trains() -> None:
    """two stacked layers of attention and a local linear term, lifted forward agreeing, then two adam steps"""
    hidden_channels = 2
    token_count = 2
    grid_shape = (4, 4, 4)
    kept_modes = (1, 1, 1)
    stack = ExplicitStack(
        layers=(
            Layer(
                kernel=CodomainAttentionKernel(hidden_channels, kept_modes, head_count=1, seed=90),
                local_linear=TokenSharedLocalLinear(hidden_channels, seed=91),
            ),
            Layer(
                kernel=CodomainAttentionKernel(hidden_channels, kept_modes, head_count=1, seed=92),
                local_linear=TokenSharedLocalLinear(hidden_channels, seed=93),
            ),
        )
    )
    generator = np.random.default_rng(94)
    input_values = generator.random((token_count * hidden_channels, *grid_shape))
    target_values = generator.random((token_count * hidden_channels, *grid_shape))
    parameters = stack.Parameter_Values()

    numpy_output = np.asarray(stack.Forward(parameters, input_values))
    if Torch_Is_Available():
        engine = TorchEngine()
        lifted = engine.Lift(parameters, requires_gradient=False)
        lifted_values = engine.Lift_Constant(input_values)
        torch_output = stack.Forward(lifted, lifted_values)
        torch_array = np.asarray(torch_output.detach().cpu().numpy(), dtype=np.float64)
        assert np.allclose(torch_array, numpy_output, atol=1e-6)

    def Forward_Loss(lifted_parameters: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        produced = stack.Forward(lifted_parameters, lifted_batch["input_values"])
        difference = produced - lifted_batch["target_values"]
        return (difference * difference).sum()

    batch = TrainingBatch({"input_values": input_values, "target_values": target_values})
    result = Train(
        engine=Training_Engine(device="host"),
        parameters=ParameterSet(values=parameters),
        forward_loss=Forward_Loss,
        batch_source=FixedBatches(batch),
        step_count=2,
        learning_rate=1e-3,
        validation_interval=1,
    )
    assert result.loss_curve.shape == (2,)
    assert np.all(np.isfinite(result.loss_curve))


def Test_Inspect_Exposes_Attention_Scores_And_The_Renderer_Draws_Every_Key(tmp_path: Path) -> None:
    """last_attention_scores carries the head by token by token map and the renderer skips nothing"""
    kernel = CodomainAttentionKernel(hidden_channels=2, kept_modes=(1, 1, 1), head_count=2, seed=100)
    generator = np.random.default_rng(101)
    token_count = 3
    field = GridFunction(
        values=generator.random((token_count * 2, 4, 4, 4)),
        channel_labels=tuple(f"channel_{channel_index}" for channel_index in range(token_count * 2)),
        domain=CUBE,
        quadrature=UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    kernel.Integrate(field, GridSpec((4, 4, 4)))
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in kernel.Inspect().items()}
    assert inspected["last_attention_scores"].shape == (2, token_count, token_count)
    for prefix in ("norm.", "query.", "key.", "value.", "output."):
        assert any(name.startswith(prefix) for name in inspected), prefix
    suite = Render_Inspection_Suite(inspected, tmp_path)
    assert suite.skipped == ()
