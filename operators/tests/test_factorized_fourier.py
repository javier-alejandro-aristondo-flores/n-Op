"""the flagship member: its assembly, the discretization and commutation claims, and its recomputed floors"""

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from operators.compositions import Spectral_Resampled
from operators.data import Archive_Path
from operators.factorized_fourier import (
    Factorized_Fourier_Network,
    FactorizedFourier,
    Gram_Six,
    Gram_Statistics,
    Log_Compressed_Channels,
    Reference_Density,
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
