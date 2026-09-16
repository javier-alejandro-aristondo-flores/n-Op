"""the Galerkin attention kernel, the query-point decoder and the assembled member, against both engines"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

import operators.galerkin_transformer as galerkin_transformer
from operators.compositions import ExplicitStack
from operators.encoders import PointwiseLift
from operators.framework import (
    Coefficients,
    Domain,
    GridFunction,
    GridSpec,
    Operator,
    Output_Points,
    PointSpec,
    UniformGridQuadrature,
)
from operators.galerkin_transformer import (
    COORDINATE_FEATURES,
    LOCALIZATION_INPUT_FIELD_CHANNEL_COUNT,
    GalerkinAttentionKernel,
    GalerkinTransformer,
    Galerkin_Transformer_Network,
    QueryPointDecoder,
    Sliced_Lifted,
    Token_Axis_Normalized,
)
from operators.galerkin_transformer.report import Nearest_Angle_Copy_Rows
from operators.inspection.plots import Render_Inspection_Suite
from operators.metrics import Median_Per_Unit
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
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-8
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(reference_gradients)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-3, atol=1e-5), name
    return gradients


def Localization_Member(
    processing_shape: tuple[int, int, int], hidden_channels: int, layer_count: int, seed: int
) -> GalerkinTransformer:
    """a small localization-task member, gram statistics fixed at the identity for a deterministic test"""
    return Galerkin_Transformer_Network(
        "localization",
        processing_shape=processing_shape,
        hidden_channels=hidden_channels,
        head_count=2,
        layer_count=layer_count,
        reference_density=1.0,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        seed=seed,
    )


def Explicit_Galerkin_Attention(
    kernel: GalerkinAttentionKernel, input_values: Any, output_shape: tuple[int, int, int]
) -> Any:
    """the token-by-token double loop the fused two-GEMM forward must match to round-off"""
    grid_shape = input_values.shape[1:]
    token_count = grid_shape[0] * grid_shape[1] * grid_shape[2]
    flattened = input_values.reshape(kernel.hidden_channels, token_count)
    lifted = kernel.parameter_values
    query_full = kernel.query_projection.Forward(Sliced_Lifted(lifted, "query."), flattened)
    key_full = kernel.key_projection.Forward(Sliced_Lifted(lifted, "key."), flattened)
    value_full = kernel.value_projection.Forward(Sliced_Lifted(lifted, "value."), flattened)
    key_normalized = Token_Axis_Normalized(key_full, lifted["key_norm_scale"], lifted["key_norm_bias"])
    value_normalized = Token_Axis_Normalized(value_full, lifted["value_norm_scale"], lifted["value_norm_bias"])
    query_heads = kernel.Head_Split(query_full, token_count)
    key_heads = kernel.Head_Split(key_normalized, token_count)
    value_heads = kernel.Head_Split(value_normalized, token_count)
    merged = np.zeros((kernel.hidden_channels, token_count))
    for head in range(kernel.head_count):
        for target_token in range(token_count):
            accumulator = np.zeros(kernel.head_width)
            for source_token in range(token_count):
                score = float(key_heads[head, :, source_token] @ query_heads[head, :, target_token])
                accumulator = accumulator + value_heads[head, :, source_token] * score
            merged[head * kernel.head_width : (head + 1) * kernel.head_width, target_token] = accumulator / token_count
    produced = kernel.output_projection.Forward(Sliced_Lifted(lifted, "output."), merged)
    return produced.reshape(kernel.hidden_channels, *output_shape)


def Test_The_Gate_Class_Satisfies_The_Operator_Contract() -> None:
    """the built member is an Operator, its three parts wired to the framework's own template"""
    member = Localization_Member((3, 3, 3), hidden_channels=8, layer_count=2, seed=0)
    assert Operator in type(member).__mro__
    assert isinstance(member.encoder, PointwiseLift)
    assert isinstance(member.composition, ExplicitStack)
    assert isinstance(member.readout, QueryPointDecoder)
    assert len(member.composition.layers) == 2
    assert callable(member.Inspect)


def Test_Galerkin_Attention_Matches_The_Explicit_Pairwise_Form_At_Four_Cubed() -> None:
    """the fused two-GEMM forward equals a token-by-token double loop over every source and target, to round-off"""
    kernel = GalerkinAttentionKernel(hidden_channels=4, head_count=2, seed=12)
    generator = np.random.default_rng(13)
    grid_shape = (4, 4, 4)
    input_values = generator.normal(size=(4, *grid_shape))
    fused = np.asarray(kernel.Forward(kernel.parameter_values, input_values, grid_shape))
    explicit = Explicit_Galerkin_Attention(kernel, input_values, grid_shape)
    assert np.allclose(fused, explicit, atol=1e-10)


def Test_No_Token_By_Token_Tensor_Is_Ever_Built(monkeypatch: pytest.MonkeyPatch) -> None:
    """every Einstein summation the fused forward calls, encoder and decoder alike, is instrumented and recorded"""
    original = galerkin_transformer.Einstein_Summation
    recorded_shapes: list[tuple[int, ...]] = []

    def Recording_Einstein_Summation(subscripts: str, first: Any, second: Any) -> Any:
        result = original(subscripts, first, second)
        recorded_shapes.append(tuple(np.asarray(result).shape))
        return result

    monkeypatch.setattr(galerkin_transformer, "Einstein_Summation", Recording_Einstein_Summation)
    grid_shape = (8, 8, 8)
    token_count = grid_shape[0] * grid_shape[1] * grid_shape[2]
    kernel = GalerkinAttentionKernel(hidden_channels=4, head_count=2, seed=20)
    generator = np.random.default_rng(21)
    input_values = generator.normal(size=(4, *grid_shape))
    kernel.Forward(kernel.parameter_values, input_values, grid_shape)
    assert recorded_shapes, "the encoder forward never called Einstein_Summation"
    for shape in recorded_shapes:
        assert sum(1 for extent in shape if extent == token_count) <= 1, shape

    recorded_shapes.clear()
    decoder = QueryPointDecoder(hidden_channels=4, output_channels=1, channel_labels=("field",), head_count=2, seed=22)
    token_values = generator.normal(size=(4, *grid_shape))
    query_points = Output_Points(GridSpec((5, 5, 5)))
    query_count = query_points.shape[0]
    decoder.Forward(decoder.parameter_values, token_values, decoder.Coordinate_Features(query_points))
    assert recorded_shapes, "the decoder forward never called Einstein_Summation"
    for shape in recorded_shapes:
        assert not ({token_count, query_count} <= set(shape)), shape
        assert sum(1 for extent in shape if extent == token_count) <= 1, shape


def Test_The_Decoder_Answers_A_Grid_And_An_Explicit_Point_List_Identically() -> None:
    """the same coordinates, offered as a grid or as a shuffled explicit list evaluated in small chunks, agree"""
    decoder = QueryPointDecoder(
        hidden_channels=6, output_channels=2, channel_labels=("a", "b"), head_count=2, seed=5, query_chunk_size=3
    )
    generator = np.random.default_rng(6)
    token_values = generator.normal(size=(6, 3, 3, 3))
    grid_points = Output_Points(GridSpec((3, 3, 2)))
    permutation = generator.permutation(grid_points.shape[0])
    grid_features = decoder.Coordinate_Features(grid_points)
    grid_answer = np.asarray(decoder.Forward(decoder.parameter_values, token_values, grid_features))
    shuffled_points = np.asarray(Output_Points(PointSpec(grid_points[permutation])))
    point_answer = np.asarray(
        decoder.Forward(decoder.parameter_values, token_values, decoder.Coordinate_Features(shuffled_points))
    )
    assert np.allclose(grid_answer[permutation], point_answer, atol=1e-12)


def Test_The_Same_Weights_Answer_Two_Grid_Shapes() -> None:
    """one trained-shaped member answers two different, even non-cubic, query resolutions without rebuilding"""
    member = Localization_Member((3, 3, 3), hidden_channels=6, layer_count=1, seed=8)
    generator = np.random.default_rng(9)
    density = generator.uniform(0.1, 1.0, size=(5, 5, 5))
    magnetization = generator.uniform(-0.05, 0.05, size=(5, 5, 5))
    input_function = GridFunction(
        np.stack([density, magnetization]),
        ("charge_density", "magnetization"),
        CUBE,
        UniformGridQuadrature(cell_volume=8.0, point_count=125),
    )
    output_a = member(input_function, GridSpec((5, 5, 5)))
    output_b = member(input_function, GridSpec((7, 6, 5)))
    assert output_a.values.shape == (2, 5, 5, 5)
    assert output_b.values.shape == (2, 7, 6, 5)
    assert np.all(np.isfinite(np.asarray(output_a.values)))
    assert np.all(np.isfinite(np.asarray(output_b.values)))


def Member_Loss(
    member: GalerkinTransformer, combined_coarse_input: Any, query_features: Any, target: Any
) -> Callable[[dict[str, Any]], Any]:
    """the summed squared gap between the member's lifted forward and a fixed target"""

    def Loss(lifted: dict[str, Any]) -> Any:
        produced = member.Forward_From_Coarse_Input(lifted, combined_coarse_input, query_features)
        difference = produced - target
        return (difference * difference).sum()

    return Loss


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_Gradient_Reaches_Every_Parameter_On_Both_Engines() -> None:
    """a tape severed anywhere in the lift, the attention layers or the decoder shows as a zero gradient"""
    processing_shape = (3, 3, 3)
    member = Localization_Member(processing_shape, hidden_channels=4, layer_count=2, seed=15)
    generator = np.random.default_rng(16)
    input_channel_count = LOCALIZATION_INPUT_FIELD_CHANNEL_COUNT + COORDINATE_FEATURES.feature_count
    combined = generator.normal(size=(input_channel_count, *processing_shape))
    query_points = Output_Points(GridSpec((3, 3, 3)))
    query_features = member.decoder.Coordinate_Features(query_points)
    target = generator.normal(size=(query_points.shape[0], len(member.channel_labels)))
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    engine = TorchEngine()
    lifted_combined = engine.Lift_Constant(combined)
    lifted_query_features = engine.Lift_Constant(query_features)
    lifted_target = engine.Lift_Constant(target)
    gradients = Agreeing_Gradients(
        parameters,
        Member_Loss(member, lifted_combined, lifted_query_features, lifted_target),
        Member_Loss(member, combined, query_features, target),
    )
    prefixes = ["lift_weights", "lift_biases", "query.", "key.", "value.", "final.", "key_norm", "value_norm"]
    for layer_index in range(2):
        prefixes.append(f"layer_{layer_index}.kernel.")
        prefixes.append(f"layer_{layer_index}.local_linear.")
    for prefix in prefixes:
        matching = [name for name in gradients if name.startswith(prefix)]
        assert matching, prefix
        stacked = np.concatenate([gradients[name].reshape(-1) for name in matching])
        assert float(np.abs(stacked).max()) > 1e-8, prefix


def Test_The_Localization_Head_Stays_Bounded() -> None:
    """the bounded pointwise projection keeps every predicted value strictly inside zero and one"""
    member = Localization_Member((3, 3, 3), hidden_channels=6, layer_count=2, seed=18)
    generator = np.random.default_rng(19)
    density = generator.uniform(5.0, 50.0, size=(4, 4, 4))
    magnetization = generator.uniform(-20.0, 20.0, size=(4, 4, 4))
    input_function = GridFunction(
        np.stack([density, magnetization]),
        ("charge_density", "magnetization"),
        CUBE,
        UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    output = member(input_function, GridSpec((4, 4, 4)))
    values = np.asarray(output.values)
    assert np.all(values > 0.0) and np.all(values < 1.0)


def Test_The_Perovskite_Density_Renormalizes_To_The_Electron_Count() -> None:
    """the parametric task's whole-field conservation law lands exactly on the requested electron count"""
    member = Galerkin_Transformer_Network(
        "parametric", processing_shape=(3, 3, 3), hidden_channels=6, head_count=2, layer_count=1, seed=24
    )
    lattice = np.eye(3) * 3.0
    domain = Domain(lattice=lattice)
    vector = np.array([1.0, 1.01, 0.99, 0.02, -0.01, 0.03])
    input_function = GridFunction(
        galerkin_transformer.Constant_Channel_Field(vector, (1, 1, 1)),
        tuple(f"parameter_{component_number}" for component_number in range(6)),
        domain,
        UniformGridQuadrature(cell_volume=float(abs(np.linalg.det(lattice))), point_count=1),
    )
    condition = Coefficients(vector=np.array([48.0]), domain=domain)
    output = member(input_function, GridSpec((5, 5, 5)), condition)
    integral = float(np.sum(output.values)) * output.quadrature.cell_volume / output.quadrature.point_count
    assert abs(integral - 48.0) < 1e-6


def Test_Two_Step_Toy_Training_Is_Deterministic() -> None:
    """the same tiny configuration trained twice from the same seed reaches the same loss curve"""

    def Run() -> NDArray[np.float64]:
        processing_shape = (3, 3, 3)
        member = Localization_Member(processing_shape, hidden_channels=4, layer_count=1, seed=22)
        generator = np.random.default_rng(23)
        input_channel_count = LOCALIZATION_INPUT_FIELD_CHANNEL_COUNT + COORDINATE_FEATURES.feature_count
        combined = generator.normal(size=(input_channel_count, *processing_shape))
        query_points = Output_Points(GridSpec(processing_shape))
        query_features = member.decoder.Coordinate_Features(query_points)
        target = generator.normal(size=(query_points.shape[0], len(member.channel_labels)))

        def Forward_Loss(lifted_parameters: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
            produced = member.Forward_From_Coarse_Input(
                lifted_parameters, lifted_batch["combined"], lifted_batch["query_features"]
            )
            difference = produced - lifted_batch["target"]
            return (difference * difference).sum()

        batch = TrainingBatch({"combined": combined, "query_features": query_features, "target": target})
        result = Train(
            engine=Training_Engine(device="host"),
            parameters=ParameterSet(values=member.Parameter_Values()),
            forward_loss=Forward_Loss,
            batch_source=FixedBatches(batch),
            step_count=2,
            learning_rate=1e-3,
            validation_interval=1,
        )
        return result.loss_curve

    first_curve = Run()
    second_curve = Run()
    assert first_curve.shape == (2,)
    assert np.all(np.isfinite(first_curve))
    assert np.array_equal(first_curve, second_curve)


def Test_Every_Inspect_Key_Is_Drawn_By_The_Generic_Renderer(tmp_path: Path) -> None:
    """a member reached through its own forward path exposes nothing the generic renderer cannot draw"""
    member = Localization_Member((3, 3, 3), hidden_channels=4, layer_count=1, seed=25)
    generator = np.random.default_rng(26)
    density = generator.uniform(0.1, 1.0, size=(4, 4, 4))
    magnetization = generator.uniform(-0.05, 0.05, size=(4, 4, 4))
    input_function = GridFunction(
        np.stack([density, magnetization]),
        ("charge_density", "magnetization"),
        CUBE,
        UniformGridQuadrature(cell_volume=8.0, point_count=64),
    )
    member(input_function, GridSpec((4, 4, 4)))
    inspected = {name: np.asarray(value, dtype=np.float64) for name, value in member.Inspect().items()}
    suite = Render_Inspection_Suite(inspected, tmp_path)
    assert suite.skipped == ()


@pytest.mark.pool
def Test_The_Nearest_Angle_Copy_Floor_Reproduces_The_Built_Members_Own_Number() -> None:
    """the copy floor, recomputed here from the root-exported loader and metric alone, lands on 0.0853"""
    copy_rows = Nearest_Angle_Copy_Rows(evaluation_fold=0)
    assert len(copy_rows) == 25
    errors = np.asarray([row.errors["relative_l2"] for row in copy_rows], dtype=np.float64)
    unit_keys = [row.unit_key for row in copy_rows]
    median_error = float(np.median(Median_Per_Unit(errors, unit_keys)))
    assert abs(median_error - 0.0853) < 0.002
