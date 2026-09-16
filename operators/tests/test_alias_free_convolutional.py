"""the convolutional member: its fused activation, its assembly, and the pointwise twin the identity check needs"""

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.alias_free_convolutional import (
    AliasFreeConvolutional,
    Alias_Free_Convolutional_Network,
    Augmented_Training_Pair,
    StencilActivation,
)
from operators.alias_free_convolutional.activation import Alias_Free_Activation
from operators.alias_free_convolutional.report import (
    AugmentedMemberBatches,
    Grid_Shift_Probe_Set,
    Latest_Stage_Checkpoint_For_Prefix,
    MemberExample,
    Member_Loss,
    Write_Back_Parameters,
)
from operators.compositions import Downsampled_By_Two, Halved_Shape, Upsampled_By_Two
from operators.encoders import PointwiseLift
from operators.evaluation import CubicBlock, Elf_Ridge_Rows, Nearest_Run_Rows, Shell_Filter_Rows, Summarize, Training_Mean_Rows
from operators.framework import (
    Apply_Grid_Operation,
    Diamond_Grid_Operations,
    Domain,
    GridFunction,
    GridSpec,
    Inspectable,
    Operator,
    UniformGridQuadrature,
)
from operators.substrate import (
    ACCELERATOR_DEVICE_NAME,
    Accelerator_Is_Available,
    Adam_Step,
    Fresh_Adam_State,
    Gaussian_Error_Linear_Unit,
    NumpyEngine,
    ParameterSet,
    Torch_Is_Available,
    TorchEngine,
)
from operators.training import Train

CUBE = Domain(lattice=np.eye(3) * 3.57)

# a live training run on the shared card is left at least this much headroom, matching the suite's own house rule
MINIMUM_FREE_ACCELERATOR_BYTES = 1_000_000_000


def Toy_Member(
    hidden_channel_widths: tuple[int, int, int] = (2, 3, 4),
    activation: StencilActivation = "pointwise",
    seed: int = 1,
) -> AliasFreeConvolutional:
    """a small member sized to run fast on a toy grid"""
    return Alias_Free_Convolutional_Network(
        reference_density=0.05,
        gram_mean=np.zeros(6),
        gram_scale=np.ones(6),
        hidden_channel_widths=hidden_channel_widths,
        activation=activation,
        seed=seed,
    )


def Toy_Field(shape: tuple[int, int, int], seed: int) -> GridFunction:
    """a random two-channel density-and-magnetization field on the given grid"""
    generator = np.random.default_rng(seed)
    density = generator.uniform(0.01, 1.0, size=shape)
    magnetization = generator.uniform(-0.1, 0.1, size=shape)
    quadrature = UniformGridQuadrature(cell_volume=8.0, point_count=int(np.prod(shape)))
    values = np.stack([density, magnetization])
    return GridFunction(values, ("charge_density", "magnetization"), CUBE, quadrature)


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


def Test_The_Assembly_Satisfies_The_Operator_And_Inspection_Contracts() -> None:
    """the gate class is an Operator, is Inspectable, and Inspect grows a predicted field after a forward call"""
    assert Operator in AliasFreeConvolutional.__mro__
    assert Inspectable in AliasFreeConvolutional.__mro__
    member = Toy_Member()
    before = member.Inspect()
    assert "encoder.lift_weights" in before
    assert "last_predicted_values" not in before
    field = Toy_Field((16, 16, 16), seed=1)
    member(field, GridSpec((8, 8, 8)))
    after = member.Inspect()
    assert "last_predicted_values" in after
    assert "last_gram_vector" in after


def Test_The_Gradient_Agrees_With_The_Reference_Engines_Finite_Differences_At_Eight_Cubed() -> None:
    """the free conformance test: the reference engine ignores the backward and lands on the same slope anyway"""
    generator = np.random.default_rng(201)
    offset = generator.normal(size=(5, 8, 8, 8)) * 0.3

    def Loss_Of(offset_input: Any) -> Callable[[dict[str, Any]], Any]:
        def Loss(lifted: dict[str, Any]) -> Any:
            activated = Alias_Free_Activation(lifted["value"] * 1.3 + offset_input)
            return (activated * activated).sum()

        return Loss

    parameters = ParameterSet(values={"value": generator.normal(size=(5, 8, 8, 8)) * 0.2})
    engine = TorchEngine()
    value, gradients = engine.Value_And_Gradients(parameters, Loss_Of(engine.Lift_Constant(offset)))
    reference = NumpyEngine()
    assert abs(value - reference.Evaluate(parameters, Loss_Of(offset))) < 1e-8
    reference_gradients = reference.Gradients(parameters, Loss_Of(offset))
    assert np.allclose(gradients["value"], reference_gradients["value"], rtol=1e-4, atol=1e-5)


@pytest.mark.skipif(not Torch_Is_Available(), reason="torch is not installed yet")
def Test_The_Gradient_Agrees_With_The_Unfused_Graph_At_Sixteen_Cubed() -> None:
    """the fused custom-gradient path and plain autograd through the unchunked graph land on the same slope"""
    import torch

    generator = np.random.default_rng(211)
    values = generator.normal(size=(6, 16, 16, 16)) * 0.4
    fused_input = torch.tensor(values, dtype=torch.float64, requires_grad=True)
    unfused_input = torch.tensor(values, dtype=torch.float64, requires_grad=True)
    fused_output = Alias_Free_Activation(fused_input)
    unfused_output = Downsampled_By_Two(Gaussian_Error_Linear_Unit(Upsampled_By_Two(unfused_input)))
    assert torch.allclose(fused_output, unfused_output, atol=1e-10)
    (fused_output * fused_output * 1.7).sum().backward()
    (unfused_output * unfused_output * 1.7).sum().backward()
    assert fused_input.grad is not None
    assert unfused_input.grad is not None
    assert torch.allclose(fused_input.grad, unfused_input.grad, atol=1e-9)


def Test_The_Fused_Forward_Matches_The_Unfused_Forward_To_Round_Off_On_A_Band_Limited_Field() -> None:
    """chunking and the custom gradient rule are a memory optimization, not an approximation of the value"""
    field = Band_Limited_Field(channels=3, shape=(8, 8, 8), highest_mode=1, seed=221)
    fused = np.asarray(Alias_Free_Activation(field), dtype=np.float64)
    unfused = np.asarray(Downsampled_By_Two(Gaussian_Error_Linear_Unit(Upsampled_By_Two(field))), dtype=np.float64)
    assert float(np.abs(fused - unfused).max()) < 1e-12


def Test_The_Resampling_Transpose_Identities_Hold_Numerically() -> None:
    """the adjoint identities the closed-form backward depends on, checked directly against random fields"""
    generator = np.random.default_rng(231)
    coarse = generator.normal(size=(2, 4, 4, 4))
    fine = generator.normal(size=(2, 8, 8, 8))
    upsampled_transpose_check = float((fine * Upsampled_By_Two(coarse)).sum())
    downsampled_transpose_check = 8.0 * float((Downsampled_By_Two(fine) * coarse).sum())
    assert abs(upsampled_transpose_check - downsampled_transpose_check) < 1e-8 * max(
        abs(downsampled_transpose_check), 1.0
    )
    other_fine = generator.normal(size=(2, 8, 8, 8))
    downsampled_second_check = float((coarse * Downsampled_By_Two(other_fine)).sum())
    upsampled_second_check = float(((Upsampled_By_Two(coarse) / 8.0) * other_fine).sum())
    assert abs(downsampled_second_check - upsampled_second_check) < 1e-8 * max(abs(upsampled_second_check), 1.0)


@pytest.mark.skipif(not Accelerator_Is_Available(), reason="no accelerator card on this machine")
def Test_The_Fused_Path_Peaks_Far_Under_The_Unfused_Path_In_Accelerator_Memory() -> None:
    """the whole reason for the custom gradient rule, measured on the card rather than assumed"""
    import torch

    free_bytes, _ = torch.cuda.mem_get_info(ACCELERATOR_DEVICE_NAME)
    if free_bytes < MINIMUM_FREE_ACCELERATOR_BYTES:
        pytest.skip("under a gigabyte free on the shared card, leaving room for a live training run")
    generator = np.random.default_rng(241)
    values = generator.normal(size=(16, 32, 32, 32)).astype(np.float32) * 0.3

    def Peak_Bytes(forward: Callable[[Any], Any]) -> int:
        """the accelerator's own peak allocation of one forward-and-backward pass through the given function"""
        torch.cuda.reset_peak_memory_stats(ACCELERATOR_DEVICE_NAME)
        torch.cuda.synchronize(ACCELERATOR_DEVICE_NAME)
        tensor_input = torch.tensor(values, device=ACCELERATOR_DEVICE_NAME, requires_grad=True)
        output = forward(tensor_input)
        (output * output).sum().backward()
        torch.cuda.synchronize(ACCELERATOR_DEVICE_NAME)
        return torch.cuda.max_memory_allocated(ACCELERATOR_DEVICE_NAME)

    def Unfused(tensor_input: Any) -> Any:
        """the same nonlinearity with no chunking and no custom gradient rule"""
        return Downsampled_By_Two(Gaussian_Error_Linear_Unit(Upsampled_By_Two(tensor_input)))

    fused_peak = Peak_Bytes(Alias_Free_Activation)
    unfused_peak = Peak_Bytes(Unfused)
    assert fused_peak < 0.5 * unfused_peak


def Test_The_Assembly_Runs_From_Sixteen_Cubed_To_Eight_Cubed_With_Gradients_On_Every_Parameter() -> None:
    """the pointwise twin's own plumbing: skip connections, concatenation and the bounded head all carry gradient"""
    member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="pointwise", seed=3)
    generator = np.random.default_rng(251)
    log_density_values = generator.normal(size=(2, 8, 8, 8)) * 0.1
    gram_vector = generator.normal(size=(6,)) * 0.1
    target = generator.uniform(0.1, 0.9, size=(2, 4, 4, 4))

    def Loss_Of(density_input: Any, gram_input: Any, target_input: Any) -> Callable[[dict[str, Any]], Any]:
        def Loss(lifted: dict[str, Any]) -> Any:
            produced = member.Forward_Field(lifted, density_input, gram_input, (8, 8, 8))
            difference = produced - target_input
            return (difference * difference).sum()

        return Loss

    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    engine = TorchEngine()
    lifted_loss = Loss_Of(
        engine.Lift_Constant(log_density_values), engine.Lift_Constant(gram_vector), engine.Lift_Constant(target)
    )
    reference_loss = Loss_Of(log_density_values, gram_vector, target)
    value, gradients = engine.Value_And_Gradients(parameters, lifted_loss)
    reference = NumpyEngine()
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-8
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(parameters.values)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-4, atol=1e-5), name
        assert float(np.abs(gradient).max()) > 1e-8, name


def Test_The_Alias_Free_Assembly_Runs_From_Sixteen_Cubed_To_Eight_Cubed_With_Gradients_On_Every_Parameter() -> None:
    """the member's own configured activation, through the composition's own activation table"""
    member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="alias_free", seed=3)
    field = Toy_Field((16, 16, 16), seed=253)
    output = member(field, GridSpec((8, 8, 8)))
    assert output.values.shape == (2, 8, 8, 8)
    log_density_values, gram_vector = member.Input_Channels(field)
    target = np.random.default_rng(255).uniform(0.1, 0.9, size=(2, 8, 8, 8))

    def Loss_Of(density_input: Any, gram_input: Any, target_input: Any) -> Callable[[dict[str, Any]], Any]:
        def Loss(lifted: dict[str, Any]) -> Any:
            produced = member.Forward_Field(lifted, density_input, gram_input, (16, 16, 16))
            difference = produced - target_input
            return (difference * difference).sum()

        return Loss

    parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
    engine = TorchEngine()
    lifted_loss = Loss_Of(
        engine.Lift_Constant(log_density_values), engine.Lift_Constant(gram_vector), engine.Lift_Constant(target)
    )
    reference_loss = Loss_Of(log_density_values, gram_vector, target)
    value, gradients = engine.Value_And_Gradients(parameters, lifted_loss)
    reference = NumpyEngine()
    assert abs(value - reference.Evaluate(parameters, reference_loss)) < 1e-8
    reference_gradients = reference.Gradients(parameters, reference_loss)
    assert set(gradients) == set(parameters.values)
    for name, gradient in gradients.items():
        assert np.allclose(gradient, reference_gradients[name], rtol=1e-4, atol=1e-5), name
        assert float(np.abs(gradient).max()) > 1e-8, name


@pytest.mark.parametrize("shape", [(16, 16, 16), (16, 12, 16), (16, 20, 16)])
def Test_The_Three_Scale_Composition_Runs_On_Evenly_And_Oddly_Bottomed_Axis_Shapes(
    shape: tuple[int, int, int],
) -> None:
    """the pointwise twin on axis-stretched shapes: one halves evenly throughout, one lands odd at the bottom"""
    member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="pointwise", seed=5)
    field = Toy_Field(shape, seed=7)
    expected_shape = Halved_Shape(shape)
    output = member(field, GridSpec(expected_shape))
    assert output.values.shape == (2, *expected_shape)


@pytest.mark.parametrize("shape", [(16, 16, 16), (16, 12, 16), (16, 20, 16)])
def Test_The_Alias_Free_Composition_Runs_On_Evenly_And_Oddly_Bottomed_Axis_Shapes(shape: tuple[int, int, int]) -> None:
    """the member's own configured activation on the same axis-stretched shapes the grid-shift probe exercises"""
    member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="alias_free", seed=5)
    field = Toy_Field(shape, seed=7)
    expected_shape = Halved_Shape(shape)
    output = member(field, GridSpec(expected_shape))
    assert output.values.shape == (2, *expected_shape)


def Test_The_Output_Discretization_Must_Be_The_Compositions_Own_Second_Scale() -> None:
    """no extra resampling machinery exists, so a mismatched request is refused rather than silently served"""
    member = Toy_Member()
    field = Toy_Field((16, 16, 16), seed=9)
    with pytest.raises(ValueError, match="composition's own second scale"):
        member(field, GridSpec((4, 4, 4)))


def Test_The_Bounded_Head_Never_Leaves_Zero_To_One() -> None:
    """the localization head's own 1 over 1 plus softplus squared, read off a real forward pass"""
    member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="pointwise", seed=11)
    field = Toy_Field((16, 16, 16), seed=13)
    output = np.asarray(member(field, GridSpec((8, 8, 8))).values, dtype=np.float64)
    assert bool((output > 0.0).all())
    assert bool((output < 1.0).all())


def Test_Augmentation_Commutes_With_The_Lift_Over_Every_Diamond_Operation() -> None:
    """a pointwise map cannot see a spatial permutation, so applying it before or after changes nothing"""
    lift = PointwiseLift(hidden_channels=5, input_channels=8, seed=61)
    generator = np.random.default_rng(63)
    field = generator.normal(size=(8, 8, 8, 8))
    worst_commutation_error = 0.0
    for matrix, translation in Diamond_Grid_Operations():
        transformed_then_lifted = lift.Forward(lift.parameter_values, Apply_Grid_Operation(field, matrix, translation))
        lifted_then_transformed = Apply_Grid_Operation(lift.Forward(lift.parameter_values, field), matrix, translation)
        error = float(np.abs(np.asarray(transformed_then_lifted) - np.asarray(lifted_then_transformed)).max())
        worst_commutation_error = max(worst_commutation_error, error)
    assert worst_commutation_error < 1e-10


def Test_Augmented_Training_Pair_Applies_The_Same_Operation_To_Input_And_Target() -> None:
    """the drawn operation moves the input and the target identically, never independently"""
    generator = np.random.default_rng(65)
    input_values = generator.normal(size=(8, 8, 8, 8))
    target_values = generator.normal(size=(2, 4, 4, 4))
    augmented_input, augmented_target = Augmented_Training_Pair(input_values, target_values, generator)
    assert augmented_input.shape == input_values.shape
    assert augmented_target.shape == target_values.shape
    assert not np.array_equal(augmented_input, input_values) or not np.array_equal(augmented_target, target_values)


def Test_A_Two_Step_Toy_Training_Is_Deterministic() -> None:
    """the same seed through the same Adam steps reaches the same losses and the same parameters, bit for bit"""

    def Run_Two_Steps(seed: int) -> tuple[list[float], ParameterSet]:
        member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="pointwise", seed=seed)
        generator = np.random.default_rng(1000)
        log_density_values = generator.normal(size=(2, 8, 8, 8)) * 0.1
        gram_vector = generator.normal(size=(6,)) * 0.1
        target = generator.uniform(0.1, 0.9, size=(2, 4, 4, 4))
        engine = TorchEngine()
        lifted_density = engine.Lift_Constant(log_density_values)
        lifted_gram = engine.Lift_Constant(gram_vector)
        lifted_target = engine.Lift_Constant(target)

        def Loss(lifted: dict[str, Any]) -> Any:
            produced = member.Forward_Field(lifted, lifted_density, lifted_gram, (8, 8, 8))
            difference = produced - lifted_target
            return (difference * difference).sum()

        parameters = ParameterSet(values={name: value.copy() for name, value in member.Parameter_Values().items()})
        state = Fresh_Adam_State(parameters)
        losses: list[float] = []
        for _ in range(2):
            value, gradients = engine.Value_And_Gradients(parameters, Loss)
            losses.append(value)
            parameters = Adam_Step(parameters, gradients, state, learning_rate=0.01)
        return losses, parameters

    losses_one, parameters_one = Run_Two_Steps(seed=5)
    losses_two, parameters_two = Run_Two_Steps(seed=5)
    assert losses_one == losses_two
    for name in parameters_one.values:
        assert np.array_equal(parameters_one.values[name], parameters_two.values[name])


@pytest.mark.pool
def Test_The_Four_Floors_Land_Near_The_Flagships_Recorded_Numbers() -> None:
    """the same four floor recipes on the same block, checked against the flagship's own committed numbers"""
    block = CubicBlock()
    ridge_rows = Elf_Ridge_Rows(block)
    filter_rows = Shell_Filter_Rows(block)
    mean_rows = Training_Mean_Rows(block)
    copy_rows = Nearest_Run_Rows(block)
    recorded_by_floor = {
        "semilocal_ridge_floor": (ridge_rows, 0.0976),
        "per_shell_linear_filter": (filter_rows, 0.0830),
        "training_mean_trivial_floor": (mean_rows, 0.0160),
        "nearest_run_copy_floor": (copy_rows, 0.0062),
    }
    for floor_label, (rows, flagship_value) in recorded_by_floor.items():
        measured = Summarize(rows, "mean_absolute_error", floor_label).median
        assert abs(measured - flagship_value) < 0.002, floor_label


@pytest.mark.pool
def Test_The_Grid_Shift_Probe_Set_Is_Twenty_One_Valid_Cells_Spanning_Both_Campaigns() -> None:
    """21 distinct evaluation-block identifiers, both campaigns represented, every axis a multiple of four"""
    block = CubicBlock()
    probes = Grid_Shift_Probe_Set(block)
    assert len(probes) == 21
    assert len({probe.identifier for probe in probes}) == 21
    assert {probe.campaign for probe in probes} == {"supercell_strains", "defect_set"}
    for probe in probes:
        assert probe.identifier in block.evaluation
        assert all(axis % 4 == 0 for axis in probe.stretched_shape)
        assert all(72 <= axis <= 84 for axis in probe.stretched_shape)
    # the seed is fixed, so the same block reproduces the same probe set bit for bit
    assert Grid_Shift_Probe_Set(block) == probes


def Test_Latest_Stage_Checkpoint_For_Prefix_Finds_The_Newest_Runs_Furthest_Stage(tmp_path: Path) -> None:
    """among an older two-stage run and a newer one-stage run sharing a prefix, the newer run's own stage wins"""
    older_run_stage0 = tmp_path / "elf_fold0_cno_100_stage0_checkpoint.npz"
    older_run_stage1 = tmp_path / "elf_fold0_cno_100_stage1_checkpoint.npz"
    newer_run_stage0 = tmp_path / "elf_fold0_cno_200_stage0_checkpoint.npz"
    for path, mtime in ((older_run_stage0, 100.0), (older_run_stage1, 100.0), (newer_run_stage0, 200.0)):
        path.write_bytes(b"")
        os.utime(path, (mtime, mtime))
    found = Latest_Stage_Checkpoint_For_Prefix(tmp_path, "elf_fold0_cno")
    assert found == newer_run_stage0


def Test_Latest_Stage_Checkpoint_For_Prefix_Raises_When_Nothing_Matches(tmp_path: Path) -> None:
    """an empty directory, or one carrying only an unrelated prefix, fails clearly rather than answering nothing"""
    with pytest.raises(FileNotFoundError):
        Latest_Stage_Checkpoint_For_Prefix(tmp_path, "elf_fold0_cno")


def Test_The_Augmented_Batch_Source_And_Loss_Train_A_Toy_Member_And_Write_Back_Cleanly() -> None:
    """the driver's own batch source and loss, wired through Train(), and its write-back restores every part"""
    member = Toy_Member(hidden_channel_widths=(2, 3, 4), activation="pointwise", seed=11)
    generator = np.random.default_rng(13)
    training_examples = [
        MemberExample(
            identifier=f"toy_{draw}",
            unit_key=f"unit_{draw}",
            campaign="toy",
            log_density_values=(generator.normal(size=(2, 8, 8, 8)) * 0.1).astype(np.float32),
            gram_vector=(generator.normal(size=(6,)) * 0.1).astype(np.float32),
            target_values=generator.uniform(0.1, 0.9, size=(2, 4, 4, 4)).astype(np.float32),
        )
        for draw in range(3)
    ]
    batches = AugmentedMemberBatches(training_examples, training_examples[:1])
    initial_parameters = ParameterSet(
        values={name: value.copy() for name, value in member.Parameter_Values().items()}
    )
    result = Train(
        TorchEngine(device_name="cpu"), initial_parameters, Member_Loss(member, fine_shape=(8, 8, 8)), batches,
        step_count=3, learning_rate=0.01, seed=17,
    )
    assert any(
        not np.array_equal(initial_parameters.values[name], result.parameters.values[name])
        for name in initial_parameters.values
    )
    Write_Back_Parameters(member, result.parameters)
    for name, value in result.parameters.values.items():
        if name in member.lift.parameter_values:
            assert np.array_equal(member.lift.parameter_values[name], value)
        if name in member.projection.parameter_values:
            assert np.array_equal(member.projection.parameter_values[name], value)
    for descending_index, layer in enumerate(member.multi_scale.descending_layers):
        for bare_name, value in layer.kernel.parameter_values.items():
            prefixed_name = f"descending_{descending_index}.kernel.{bare_name}"
            assert np.array_equal(value, result.parameters.values[prefixed_name])
