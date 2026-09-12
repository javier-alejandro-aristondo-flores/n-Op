"""the flagship member: its assembly, the discretization and commutation claims, and its recomputed floors"""

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import ExplicitStack, FixedPoint, Spectral_Resampled, WeightTied
from operators.compositions.fixed_point import Sliced_Lifted
from operators.data import Archive_Path
from operators.factorized_fourier import (
    Combined_Coarse_Input,
    Factorized_Fourier_Network,
    FactorizedFourier,
    FactorizedFourierConfiguration,
    Gram_Six,
    Gram_Statistics,
    Log_Compressed_Channels,
    Reference_Density,
    Shared_Member_Layer,
    Standardized_Gram,
)
from operators.factorized_fourier.report import (
    CARD_METRIC_NAMES,
    CubicBlock,
    Elf_Ridge_Rows,
    Nearest_Run_Rows,
    Shell_Filter_Rows,
)
from operators.framework import Domain, GridFunction, GridSpec, UniformGridQuadrature
from operators.inspection import Render_Inspection_Suite
from operators.substrate import Concatenate_Channels, NumpyEngine, ParameterSet, TorchEngine, Zeros_Beside
from operators.training import BatchSource, Train, TrainingBatch

CUBE = Domain(lattice=np.eye(3) * 3.57)


def Toy_Member(processing_shape: tuple[int, int, int] = (4, 4, 4), hidden_channels: int = 4, seed: int = 1) -> FactorizedFourier:
    """a small member sized to run fast on a toy grid"""
    return Factorized_Fourier_Network(
        hidden_channels=hidden_channels,
        kept_modes=(1, 1, 1),
        layer_count=2,
        reference_density=0.05,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        processing_shape=processing_shape,
        seed=seed,
    )


def Toy_Input(shape: tuple[int, int, int], seed: int = 0) -> GridFunction:
    """a random charge density and magnetization on the given grid, in the cube cell"""
    generator = np.random.default_rng(seed)
    density = generator.random(shape) * 0.1 + 0.01
    magnetization = generator.random(shape) * 0.01
    values = np.stack([density, magnetization])
    point_count = shape[0] * shape[1] * shape[2]
    quadrature = UniformGridQuadrature(cell_volume=float(np.linalg.det(np.asarray(CUBE.lattice))), point_count=point_count)
    return GridFunction(values, ("charge_density", "magnetization_density"), CUBE, quadrature)


def Test_The_Numpy_Path_And_The_Lifted_Path_Agree_On_Both_Engines() -> None:
    """the member's own numpy call and the lifted forward, run through numpy and through the foreign engine, agree"""
    member = Toy_Member()
    input_function = Toy_Input((8, 8, 8), seed=2)
    numpy_output = member(input_function, GridSpec((4, 4, 4)))
    log_density_values, gram_vector = member.Input_Channels(input_function)
    parameters = member.Parameter_Values()

    numpy_forward = np.asarray(
        member.Forward_Field(parameters, log_density_values, gram_vector, (4, 4, 4)), dtype=np.float64
    )
    assert np.allclose(numpy_forward, np.asarray(numpy_output.values), atol=1e-10)

    torch_engine = TorchEngine()
    lifted_torch = torch_engine.Lift(parameters, requires_gradient=False)
    lifted_log_density = torch_engine.Lift_Constant(log_density_values)
    lifted_gram_vector = torch_engine.Lift_Constant(gram_vector)
    torch_forward = member.Forward_Field(lifted_torch, lifted_log_density, lifted_gram_vector, (4, 4, 4))
    torch_produced = np.asarray(torch_forward.detach().cpu().numpy(), dtype=np.float64)
    assert np.allclose(torch_produced, np.asarray(numpy_output.values), atol=1e-6)


def Loss_Closure(
    member: FactorizedFourier, log_density_values: Any, gram_vector: Any, target: Any, target_shape: tuple[int, int, int]
) -> Any:
    """mean squared error of the member's lifted forward against a fixed target, closed over one example"""

    def Loss(lifted: dict[str, Any]) -> Any:
        predicted = member.Forward_Field(lifted, log_density_values, gram_vector, target_shape)
        residual = predicted - target
        return (residual * residual).mean()

    return Loss


def Test_Every_Parameter_Receives_A_Gradient_On_Both_Engines() -> None:
    """no parameter of the assembly is orphaned from the loss, on the reference engine or on the foreign one"""
    member = Toy_Member(processing_shape=(4, 4, 4), hidden_channels=3, seed=5)
    generator = np.random.default_rng(6)
    log_density_values = Log_Compressed_Channels(
        generator.random((4, 4, 4)) * 0.1 + 0.01, generator.random((4, 4, 4)) * 0.01, member.reference_density
    )
    gram_vector = Standardized_Gram(Gram_Six(np.asarray(CUBE.lattice)), member.gram_mean, member.gram_scale)
    target = generator.random((2, 4, 4, 4))
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})

    reference = NumpyEngine()
    reference_loss = Loss_Closure(member, log_density_values, gram_vector, target, (4, 4, 4))
    reference_value, reference_gradients = reference.Value_And_Gradients(parameters, reference_loss)

    torch_engine = TorchEngine()
    torch_loss = Loss_Closure(
        member,
        torch_engine.Lift_Constant(log_density_values),
        torch_engine.Lift_Constant(gram_vector),
        torch_engine.Lift_Constant(target),
        (4, 4, 4),
    )
    torch_value, torch_gradients = torch_engine.Value_And_Gradients(parameters, torch_loss)

    assert abs(reference_value - torch_value) < 1e-8
    for name in parameters.values:
        assert np.allclose(reference_gradients[name], torch_gradients[name], rtol=1e-4, atol=1e-6), name
        assert float(np.abs(torch_gradients[name]).max()) > 0.0, name


def Test_The_Output_Lies_Strictly_Inside_Zero_One() -> None:
    """the bounded head never touches either end of the localization range"""
    member = Toy_Member()
    input_function = Toy_Input((8, 8, 8), seed=7)
    output = member(input_function, GridSpec((4, 4, 4)))
    values = np.asarray(output.values)
    assert bool(np.all(values > 0.0))
    assert bool(np.all(values < 1.0))


def Test_The_Same_Weights_Answer_Two_Different_Grid_Shapes() -> None:
    """one trained member, queried at two unrelated resolutions, with no retraining and no error"""
    member = Toy_Member()
    coarse_output = member(Toy_Input((16, 16, 16), seed=8), GridSpec((8, 8, 8)))
    fine_output = member(Toy_Input((8, 8, 8), seed=9), GridSpec((4, 4, 4)))
    assert np.asarray(coarse_output.values).shape == (2, 8, 8, 8)
    assert np.asarray(fine_output.values).shape == (2, 4, 4, 4)


def Test_Truncate_Early_Equals_Lift_Then_Truncate() -> None:
    """the cheaper truncate-then-lift order and the literal lift-then-truncate order agree to round-off"""
    member = Toy_Member(hidden_channels=5, seed=11)
    input_function = Toy_Input((8, 8, 8), seed=12)
    log_density_values, gram_vector = member.Input_Channels(input_function)
    parameters = member.Parameter_Values()

    coarse_density = Spectral_Resampled(log_density_values, (4, 4, 4))
    gram_field_coarse = gram_vector.reshape(6, 1, 1, 1) + Zeros_Beside(coarse_density, (6, 4, 4, 4))
    combined_coarse = Concatenate_Channels([coarse_density, gram_field_coarse])
    truncate_then_lift = member.lift.Forward(parameters, combined_coarse)

    gram_field_fine = gram_vector.reshape(6, 1, 1, 1) + Zeros_Beside(log_density_values, (6, 8, 8, 8))
    combined_fine = Concatenate_Channels([log_density_values, gram_field_fine])
    lifted_fine = member.lift.Forward(parameters, combined_fine)
    lift_then_truncate = Spectral_Resampled(lifted_fine, (4, 4, 4))

    assert np.allclose(truncate_then_lift, lift_then_truncate, atol=1e-10)


def Test_The_Cached_Coarse_Input_Path_Equals_The_On_The_Fly_Path() -> None:
    """precomputing the eight-channel coarse input once and skipping straight to the lift changes nothing"""
    member = Toy_Member(hidden_channels=5, seed=13)
    input_function = Toy_Input((8, 8, 8), seed=14)
    log_density_values, gram_vector = member.Input_Channels(input_function)
    parameters = member.Parameter_Values()

    on_the_fly = np.asarray(member.Forward_Field(parameters, log_density_values, gram_vector, (4, 4, 4)))
    combined_coarse_input = Combined_Coarse_Input(log_density_values, gram_vector, (4, 4, 4))
    from_the_cache = np.asarray(member.Forward_From_Coarse_Input(parameters, combined_coarse_input))

    assert np.allclose(on_the_fly, from_the_cache, atol=1e-12)


def Test_The_Weight_Tied_And_Fixed_Point_Configurations_Assemble() -> None:
    """the tied and implicit rungs answer a toy grid and carry a twelfth of the explicit stack's spectral weights"""

    def Toy_Network(configuration: FactorizedFourierConfiguration) -> FactorizedFourier:
        """a toy member of the named configuration, every other choice held fixed"""
        return Factorized_Fourier_Network(
            hidden_channels=8,
            kept_modes=(1, 1, 1),
            layer_count=5,
            reference_density=0.05,
            gram_mean=np.zeros(6),
            gram_scale=np.ones(6),
            processing_shape=(4, 4, 4),
            seed=3,
            configuration=configuration,
        )

    explicit = Toy_Network("explicit")
    weight_tied = Toy_Network("weight_tied")
    fixed_point = Toy_Network("fixed_point")
    assert isinstance(weight_tied.spectral_stack, WeightTied)
    assert isinstance(fixed_point.spectral_stack, FixedPoint)
    explicit_count = sum(value.size for value in explicit.Parameter_Values().values())
    tied_count = sum(value.size for value in weight_tied.Parameter_Values().values())
    fixed_point_count = sum(value.size for value in fixed_point.Parameter_Values().values())
    # the lift and readout are shared by all three, so only the spectral-plus-local-linear share is exactly a fifth
    assert tied_count == fixed_point_count
    assert tied_count < explicit_count

    for member in (weight_tied, fixed_point):
        output = member(Toy_Input((8, 8, 8), seed=40), GridSpec((4, 4, 4)))
        assert np.asarray(output.values).shape == (2, 4, 4, 4)


def Test_Fixed_Point_Inspect_Exposes_The_Health_Signals_After_A_Member_Call() -> None:
    """a bare forward call on the primitive records nothing, so the member captures the solve at its own level"""
    member = Factorized_Fourier_Network(
        hidden_channels=8,
        kept_modes=(1, 1, 1),
        layer_count=5,
        reference_density=0.05,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        processing_shape=(4, 4, 4),
        configuration="fixed_point",
        seed=3,
    )
    member(Toy_Input((8, 8, 8), seed=41), GridSpec((4, 4, 4)))
    inspected = member.Inspect()
    for name in (
        "last_fixed_point_iterations_taken",
        "last_fixed_point_final_residual",
        "last_fixed_point_cap_was_hit",
        "last_fixed_point_residual_history",
    ):
        assert name in inspected
    assert int(np.asarray(inspected["last_fixed_point_iterations_taken"])) <= 32
    history = np.asarray(inspected["last_fixed_point_residual_history"])
    assert history.ndim == 1
    assert int(np.asarray(inspected["last_fixed_point_iterations_taken"])) == history.shape[0]


def Test_The_Health_Metric_Is_A_Fraction_Of_Inputs_Converged_Read_Off_Inspect() -> None:
    """the canon's health floor, computed the only way Inspect allows: one call per input, one read per call"""
    member = Factorized_Fourier_Network(
        hidden_channels=8,
        kept_modes=(1, 1, 1),
        layer_count=5,
        reference_density=0.05,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        processing_shape=(4, 4, 4),
        configuration="fixed_point",
        seed=3,
    )
    converged_count = 0
    validation_input_count = 6
    for seed in range(validation_input_count):
        member(Toy_Input((8, 8, 8), seed=100 + seed), GridSpec((4, 4, 4)))
        inspected = member.Inspect()
        if not bool(np.asarray(inspected["last_fixed_point_cap_was_hit"])):
            converged_count += 1
    health = converged_count / validation_input_count
    assert 0.0 <= health <= 1.0
    # a well-scaled small instance is expected to converge on every one of a handful of random toy inputs
    assert health == 1.0


def Contractive_Member_Layer(seed: int, hidden_channels: int = 8, kept_mode: int = 1) -> Any:
    """a small instance of this member's own separable layer, scaled into a contraction with a nonzero bias"""
    layer = Shared_Member_Layer(hidden_channels, (kept_mode, kept_mode, kept_mode), seed)
    for name in layer.kernel.parameter_values:
        layer.kernel.parameter_values[name] *= 0.05
    for name in layer.local_linear.parameter_values:
        layer.local_linear.parameter_values[name] *= 0.05
    # a zero bias would leave the origin as the map's only fixed point, pinning most weights' true gradient at zero
    generator = np.random.default_rng(seed + 1000)
    layer.local_linear.parameter_values["lift_biases"] = generator.normal(size=hidden_channels) * 0.1
    return layer


def Relative_Gap(candidate: dict[str, NDArray[np.float64]], ground_truth: dict[str, NDArray[np.float64]]) -> float:
    """how far one named gradient dict sits from another, as one fraction of the ground truth's own size"""
    flat_candidate = np.concatenate([value.reshape(-1) for value in candidate.values()])
    flat_truth = np.concatenate([value.reshape(-1) for value in ground_truth.values()])
    return float(np.linalg.norm(flat_candidate - flat_truth) / (np.linalg.norm(flat_truth) + 1e-12))


def Equilibrium_Loss(stack: FixedPoint, field_values: Any, target: Any) -> Any:
    """the summed squared gap between the solved equilibrium and a fixed target, as a forward an engine can drive"""

    def Loss(lifted: dict[str, Any]) -> Any:
        produced, _ = stack.Resolved(lifted, field_values)
        difference = produced - target
        return (difference * difference).sum()

    return Loss


def Tied_Loss(stack: WeightTied, field_values: Any, target: Any) -> Any:
    """the summed squared gap between the depth-matched unroll's output and a fixed target"""

    def Loss(lifted: dict[str, Any]) -> Any:
        difference = stack.Forward(lifted, field_values) - target
        return (difference * difference).sum()

    return Loss


def Test_The_Mandatory_Gradient_Audit_On_This_Members_Own_Layer() -> None:
    """the canon's mandatory audit (I.3), run on the separable layer this member actually uses, not a generic one"""
    layer = Contractive_Member_Layer(seed=201, hidden_channels=2, kept_mode=1)
    generator = np.random.default_rng(202)
    field_values = generator.random((2, 8, 8, 8)) * 0.1
    target = generator.random((2, 8, 8, 8))

    probe = FixedPoint(layer)
    parameters = ParameterSet(values={name: value.copy() for name, value in probe.Parameter_Values().items()})
    finite_difference_gradients = NumpyEngine().Gradients(parameters, Equilibrium_Loss(probe, field_values, target))

    kernel_lifted = Sliced_Lifted(probe.Parameter_Values(), "kernel.")
    local_linear_lifted = Sliced_Lifted(probe.Parameter_Values(), "local_linear.")
    depth = probe.Solved(kernel_lifted, local_linear_lifted, field_values).iterations_taken
    tied = WeightTied(layer, depth=depth)
    engine = TorchEngine()
    lifted_field_values = engine.Lift_Constant(field_values)
    lifted_target = engine.Lift_Constant(target)
    _, full_unroll_gradients = engine.Value_And_Gradients(parameters, Tied_Loss(tied, lifted_field_values, lifted_target))

    natural_disagreement = Relative_Gap(full_unroll_gradients, finite_difference_gradients)

    implicit = FixedPoint(layer, backward="implicit")
    _, implicit_gradients = engine.Value_And_Gradients(
        parameters, Equilibrium_Loss(implicit, lifted_field_values, lifted_target)
    )
    implicit_gap_to_finite_difference = Relative_Gap(implicit_gradients, finite_difference_gradients)
    implicit_gap_to_full_unroll = Relative_Gap(implicit_gradients, full_unroll_gradients)
    # the exact adjoint sits at the two ground truths' own mutual distance, not at a percent-scale bias of its own
    assert implicit_gap_to_finite_difference < max(natural_disagreement, 1e-3)
    assert implicit_gap_to_full_unroll < max(natural_disagreement, 1e-3)

    for phantom_depth, label in ((1, "phantom_s1"), (3, "phantom_s3")):
        phantom = FixedPoint(layer, backward="phantom", phantom_depth=phantom_depth)
        _, phantom_gradients = engine.Value_And_Gradients(
            parameters, Equilibrium_Loss(phantom, lifted_field_values, lifted_target)
        )
        gap_to_finite_difference = Relative_Gap(phantom_gradients, finite_difference_gradients)
        gap_to_full_unroll = Relative_Gap(phantom_gradients, full_unroll_gradients)
        if phantom_depth == 3:
            # within an order of magnitude of the ground truths' own mutual disagreement
            assert gap_to_finite_difference < 10.0 * max(natural_disagreement, 1e-3), label
            assert gap_to_full_unroll < 10.0 * max(natural_disagreement, 1e-3), label


SHEARED_CUBE = Domain(lattice=np.asarray([[4.0, 0.0, 0.0], [1.0, 3.5, 0.0], [0.5, -0.5, 4.0]]))


def Toy_Potential_Member(seed: int = 5, layer_count: int = 3) -> FactorizedFourier:
    """a small metric-aware potential member, coarse trunk 4-cubed, sized to run fast on an 8-cubed toy"""
    return Factorized_Fourier_Network(
        hidden_channels=4,
        kept_modes=(1, 1, 1),
        layer_count=layer_count,
        reference_density=0.05,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        processing_shape=(4, 4, 4),
        seed=seed,
        task="potential",
        target_scale=2.0,
    )


def Perturbed_Gain_Parameters(member: FactorizedFourier, seed: int, spread: float = 0.3) -> None:
    """every kernel's own gain network, nudged off its zero-initialized last layer, mutated in the member itself"""
    generator = np.random.default_rng(seed)
    kernels = (
        [layer.kernel for layer in member.spectral_stack.layers]
        if isinstance(member.spectral_stack, ExplicitStack)
        else [member.spectral_stack.layer.kernel]
    )
    for kernel in kernels:
        for name in list(kernel.parameter_values):
            if "gain_layer_" in name:
                shape = kernel.parameter_values[name].shape
                kernel.parameter_values[name] = kernel.parameter_values[name] + generator.normal(0.0, spread, size=shape)


def Test_The_Potential_Head_Is_Unbounded_And_Resampled_To_The_Fine_Grid() -> None:
    """the potential readout carries no head, and the coarse trunk answers at whatever fine shape is requested"""
    member = Toy_Potential_Member()
    output = member(Toy_Input((8, 8, 8), seed=60), GridSpec((8, 8, 8)))
    values = np.asarray(output.values)
    assert values.shape == (2, 8, 8, 8)
    # a nonzero, zero-mean field cannot be entirely non-negative; only an unbounded head permits this
    assert bool(np.any(values < 0.0))


def Test_The_Potential_Output_Has_Zero_Mean_Per_Channel_To_Round_Off() -> None:
    """the whole-field conservation law pins each spin's own uniform mode, regardless of the readout underneath"""
    member = Toy_Potential_Member()
    output = member(Toy_Input((8, 8, 8), seed=61), GridSpec((8, 8, 8)))
    values = np.asarray(output.values)
    for channel in range(values.shape[0]):
        assert abs(float(values[channel].mean())) < 1e-10


def Test_The_Same_Lattice_Twice_Agrees_And_Two_Lattices_Disagree() -> None:
    """a metric-aware member is deterministic per lattice and genuinely reads the lattice it is given"""
    member = Toy_Potential_Member()
    Perturbed_Gain_Parameters(member, seed=62)
    cube_input = Toy_Input((8, 8, 8), seed=63)
    first = np.asarray(member(cube_input, GridSpec((8, 8, 8))).values)
    second = np.asarray(member(cube_input, GridSpec((8, 8, 8))).values)
    assert np.array_equal(first, second)
    sheared_input = GridFunction(cube_input.values, cube_input.channel_labels, SHEARED_CUBE, cube_input.quadrature)
    third = np.asarray(member(sheared_input, GridSpec((8, 8, 8))).values)
    assert not np.allclose(first, third)


def Test_The_Mode_Wavevector_Feature_Reaches_Every_Layer() -> None:
    """perturbing one layer's gain alone changes the output, for every layer index in the stack"""
    baseline_member = Toy_Potential_Member(seed=64, layer_count=3)
    input_function = Toy_Input((8, 8, 8), seed=65)
    baseline = np.asarray(baseline_member(input_function, GridSpec((8, 8, 8))).values)
    for layer_index in range(3):
        member = Toy_Potential_Member(seed=64, layer_count=3)
        assert isinstance(member.spectral_stack, ExplicitStack)
        kernel = member.spectral_stack.layers[layer_index].kernel
        generator = np.random.default_rng(70 + layer_index)
        for name in list(kernel.parameter_values):
            if "gain_layer_" in name:
                shape = kernel.parameter_values[name].shape
                kernel.parameter_values[name] = kernel.parameter_values[name] + generator.normal(0.0, 0.3, size=shape)
        perturbed = np.asarray(member(input_function, GridSpec((8, 8, 8))).values)
        assert not np.allclose(baseline, perturbed), layer_index


def Test_Gradients_Reach_The_Gain_Parameters_On_Both_Engines() -> None:
    """the coarse trunk, the resample and the zero-mean pin all carry a tape back into every gain network"""
    member = Toy_Potential_Member(seed=80, layer_count=2)
    Perturbed_Gain_Parameters(member, seed=81)
    input_function = Toy_Input((8, 8, 8), seed=82)
    log_density_values, gram_vector = member.Input_Channels(input_function)
    mode_wavevector_features = member.Mode_Wavevector_Features_For(input_function)
    assert mode_wavevector_features is not None
    generator = np.random.default_rng(83)
    target = generator.random((2, 8, 8, 8))
    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})

    def Make_Loss(lifted_log_density: Any, lifted_gram_vector: Any, lifted_feature: Any, lifted_target: Any) -> Any:
        def Loss(lifted: dict[str, Any]) -> Any:
            predicted = member.Forward_Field(
                lifted, lifted_log_density, lifted_gram_vector, (4, 4, 4), lifted_feature, (8, 8, 8)
            )
            residual = predicted - lifted_target
            return (residual * residual).mean()

        return Loss

    reference = NumpyEngine()
    reference_gradients = reference.Gradients(
        parameters, Make_Loss(log_density_values, gram_vector, mode_wavevector_features, target)
    )
    torch_engine = TorchEngine()
    torch_value, torch_gradients = torch_engine.Value_And_Gradients(
        parameters,
        Make_Loss(
            torch_engine.Lift_Constant(log_density_values),
            torch_engine.Lift_Constant(gram_vector),
            torch_engine.Lift_Constant(mode_wavevector_features),
            torch_engine.Lift_Constant(target),
        ),
    )
    reference_value = reference.Evaluate(parameters, Make_Loss(log_density_values, gram_vector, mode_wavevector_features, target))
    assert abs(torch_value - reference_value) < 1e-8
    gain_names = [name for name in torch_gradients if "gain_layer_" in name]
    assert gain_names
    for name in gain_names:
        assert float(np.abs(torch_gradients[name]).max()) > 1e-8, name
        assert np.allclose(torch_gradients[name], reference_gradients[name], rtol=1e-4, atol=1e-6), name


def Test_The_Cached_Coarse_Input_Path_Equals_The_On_The_Fly_Path_For_Potential() -> None:
    """the caching split holds for the potential task too, resample, conservation and gain feature included"""
    member = Toy_Potential_Member(seed=90, layer_count=2)
    Perturbed_Gain_Parameters(member, seed=91)
    input_function = Toy_Input((8, 8, 8), seed=92)
    log_density_values, gram_vector = member.Input_Channels(input_function)
    mode_wavevector_features = member.Mode_Wavevector_Features_For(input_function)
    parameters = member.Parameter_Values()

    on_the_fly = np.asarray(
        member.Forward_Field(parameters, log_density_values, gram_vector, (4, 4, 4), mode_wavevector_features, (8, 8, 8))
    )
    combined_coarse_input = Combined_Coarse_Input(log_density_values, gram_vector, (4, 4, 4))
    hidden_carried = member.Forward_From_Coarse_Input(parameters, combined_coarse_input, mode_wavevector_features)
    resampled = Spectral_Resampled(hidden_carried, (8, 8, 8))
    assert member.conservation is not None
    from_the_cache = np.asarray(member.conservation.Forward(resampled, 1.0))

    assert np.allclose(on_the_fly, from_the_cache, atol=1e-12)


def Test_Inspection_Keys_Are_Covered_By_The_Generic_Renderer(tmp_path: Any) -> None:
    """every array the member exposes is shaped like what it names, and the generic renderer draws all of them"""
    member = Toy_Member()
    member(Toy_Input((8, 8, 8), seed=13), GridSpec((4, 4, 4)))
    inspected = member.Inspect()
    assert inspected["reference_density"].shape == ()
    assert inspected["gram_standardization_mean"].shape == (6,)
    assert inspected["last_gram_vector"].shape == (6,)
    assert inspected["last_predicted_values"].shape == (2, 4, 4, 4)
    assert inspected["encoder.lift_weights"].shape == (4, 8)
    assert inspected["readout.projection_weights"].shape == (2, 4)
    numeric = {name: np.asarray(value, dtype=np.float64) for name, value in inspected.items()}
    suite = Render_Inspection_Suite(numeric, tmp_path, "factorized_fourier toy")
    assert suite.skipped == ()


class TwoExampleBatches(BatchSource):
    """one fixed pair of toy examples, handed back unchanged on every step"""


    def __init__(self, batch: TrainingBatch) -> None:
        self.batch = batch


    def Next_Batch(self, generator: np.random.Generator) -> TrainingBatch:
        return self.batch


    def Validation_Batches(self) -> tuple[tuple[str, TrainingBatch], ...]:
        return (("toy_unit", self.batch),)


    def Inspect(self) -> dict[str, Any]:
        return dict(self.batch.arrays)


def Toy_Training_Batch(seed: int) -> TrainingBatch:
    """two examples of log-compressed channels, gram vectors and coarse targets, rectangular across the pair"""
    generator = np.random.default_rng(seed)
    log_density_values = np.stack(
        [
            Log_Compressed_Channels(
                generator.random((8, 8, 8)) * 0.1 + 0.01, generator.random((8, 8, 8)) * 0.01, 0.05
            )
            for _ in range(2)
        ]
    )
    gram_vectors = np.stack([Standardized_Gram(Gram_Six(np.asarray(CUBE.lattice)), np.zeros(6), np.ones(6)) for _ in range(2)])
    targets = generator.random((2, 2, 4, 4, 4))
    return TrainingBatch(
        {
            "log_density_values": np.asarray(log_density_values, dtype=np.float64),
            "gram_vectors": np.asarray(gram_vectors, dtype=np.float64),
            "targets": np.asarray(targets, dtype=np.float64),
        }
    )


def Batch_Loss(member: FactorizedFourier) -> Any:
    """mean squared error over every example a batch carries, looped since the lifted path takes one at a time"""

    def Loss(lifted: dict[str, Any], lifted_batch: dict[str, Any]) -> Any:
        example_count = lifted_batch["log_density_values"].shape[0]
        total = 0.0
        for example_index in range(example_count):
            predicted = member.Forward_Field(
                lifted,
                lifted_batch["log_density_values"][example_index],
                lifted_batch["gram_vectors"][example_index],
                (4, 4, 4),
            )
            residual = predicted - lifted_batch["targets"][example_index]
            total = total + (residual * residual).mean()
        return total / example_count

    return Loss


def Test_A_Toy_Training_Run_Is_Deterministic_From_One_Seed() -> None:
    """two steps of training from the same seed reach the identical parameters, on the host alone"""
    batches = TwoExampleBatches(Toy_Training_Batch(seed=21))

    def Run() -> dict[str, NDArray[np.float64]]:
        member = Toy_Member(hidden_channels=4, seed=22)
        parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
        result = Train(
            TorchEngine(device_name="cpu"),
            parameters,
            Batch_Loss(member),
            batches,
            step_count=2,
            learning_rate=1e-2,
            seed=99,
        )
        return result.parameters.values

    first_run = Run()
    second_run = Run()
    for name in first_run:
        assert np.array_equal(first_run[name], second_run[name]), name


@pytest.mark.pool
def Test_The_Recomputed_Floors_Land_Near_Stage_Zeros_Own_Numbers() -> None:
    """both stage-zero floor recipes, recomputed on this exact block, land close to the numbers stage zero committed"""
    block = CubicBlock()
    assert len(block.floor_train) == 261
    assert len(block.evaluation) == 76
    ridge_rows = Elf_Ridge_Rows(block)
    filter_rows = Shell_Filter_Rows(block)
    for rows in (ridge_rows, filter_rows):
        for scored_run in rows:
            assert set(scored_run.errors) == set(CARD_METRIC_NAMES)
    ridge_mean_absolute_errors = np.asarray([row.errors["mean_absolute_error"] for row in ridge_rows])
    filter_mean_absolute_errors = np.asarray([row.errors["mean_absolute_error"] for row in filter_rows])
    # stage zero's own committed numbers: ridge 0.0964, filter 0.0816, both loosely bracketed here
    assert 0.06 < float(np.median(ridge_mean_absolute_errors)) < 0.14
    assert 0.05 < float(np.median(filter_mean_absolute_errors)) < 0.13


@pytest.mark.pool
def Test_The_Nearest_Run_Copy_Floor_Is_A_Genuine_Memorization_Null() -> None:
    """the copy floor answers every evaluation run, from a training run only, on every card metric and both spins"""
    block = CubicBlock()
    copy_rows = Nearest_Run_Rows(block)
    # both spin channels of every evaluation run, each carrying all three card metrics
    assert len(copy_rows) == 2 * len(block.evaluation)
    for scored_run in copy_rows:
        assert set(scored_run.errors) == set(CARD_METRIC_NAMES)
        assert 0.0 <= scored_run.errors["mean_absolute_error"] < 1.0
    copy_mean_absolute_errors = np.asarray([row.errors["mean_absolute_error"] for row in copy_rows])
    # a copy of an actual localization field is never worse than a wild guess, nor a perfect answer
    assert 0.0 < float(np.median(copy_mean_absolute_errors)) < 0.5


@pytest.mark.pool
def Test_Gram_Statistics_Come_Off_The_Trained_Blocks_Own_Lattices() -> None:
    """the reusable statistics helpers answer on the real block's lattices without raising"""
    block = CubicBlock()
    lattices: list[NDArray[np.float64]] = []
    densities: list[NDArray[np.float64]] = []
    magnetizations: list[NDArray[np.float64]] = []
    for identifier in block.floor_train[:5]:
        campaign = block.campaign_of[identifier]
        with np.load(Archive_Path(campaign, identifier)) as archive:
            lattices.append(np.asarray(archive["lattice"], dtype=np.float64))
            densities.append(np.asarray(archive["charge_density"], dtype=np.float64))
            magnetizations.append(np.asarray(archive["magnetization_density"], dtype=np.float64))
    mean, scale = Gram_Statistics(lattices)
    assert mean.shape == (6,)
    assert bool(np.all(scale > 0.0))
    reference_density = Reference_Density(densities, magnetizations)
    assert reference_density > 0.0
